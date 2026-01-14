import { neon } from "@neondatabase/serverless";

type Env = {
  DATABASE_URL: string;
  OVC_TOKEN: string;
  RAW_EVENTS: R2Bucket;
};

type Envelope = {
  schema?: string;
  contract_version?: string;
  token?: string;
  export?: string;
  bid?: string;
  source?: string;
  sent_ms?: number;
};

export function parseExport(exportStr: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const part of exportStr.split("|")) {
    if (!part) continue;
    const idx = part.indexOf("=");
    if (idx <= 0) continue;
    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();
    if (!k) continue;
    out[k] = v;
  }
  return out;
}

function requireField(m: Record<string, string>, key: string): string {
  const v = m[key];
  if (!v || v.trim().length === 0) throw new Error(`Missing export field: ${key}`);
  return v;
}

export function msToTimestamptzStart2H(barCloseMs: number): string {
  // block_start = bar_close_ms - 2 hours
  const startMs = barCloseMs - 2 * 60 * 60 * 1000;
  // Send ISO string; Postgres will cast to timestamptz
  return new Date(startMs).toISOString();
}

function formatDateUTC(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function sanitizeKeyPart(value: string): string {
  return value.replace(/[^a-zA-Z0-9._-]/g, "_");
}

function uniqueKeySuffix(): string {
  if (crypto.randomUUID) return crypto.randomUUID();
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

async function writeRawEvent(
  env: Env,
  raw: string,
  bid: string | undefined,
  now: Date,
): Promise<void> {
  if (!env.RAW_EVENTS) {
    console.error("RAW_EVENTS binding missing; skipping raw event write");
    return;
  }
  const day = formatDateUTC(now);
  const iso = now.toISOString().replace(/[:]/g, "-");
  const keyBid = bid ? sanitizeKeyPart(bid) : "";
  const key = keyBid
    ? `tv/${day}/${keyBid}_${uniqueKeySuffix()}.txt`
    : `tv/${day}/${iso}_${uniqueKeySuffix()}.txt`;
  try {
    await env.RAW_EVENTS.put(key, raw, { httpMetadata: { contentType: "text/plain" } });
  } catch (err) {
    console.error("Failed to write raw event to R2", err);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      const url = new URL(request.url);

      // ✅ Health check
      if (url.pathname === "/") return new Response("OVC webhook OK", { status: 200 });

      // ✅ Only accept POST /tv or /tv_secure
      const isTv = url.pathname === "/tv";
      const isTvSecure = url.pathname === "/tv_secure";
      if (!isTv && !isTvSecure) return new Response("Not Found", { status: 404 });
      if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

      // ✅ Require env vars
      if (!env.DATABASE_URL) return new Response("Missing DATABASE_URL", { status: 500 });
      if (!env.OVC_TOKEN) return new Response("Missing OVC_TOKEN", { status: 500 });

      const raw = await request.text();
      const receivedAt = new Date();
      if (!raw || raw.trim().length === 0) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        return new Response("Empty body", { status: 400 });
      }

      const trimmed = raw.trim();

      // Support:
      // A) JSON envelope (recommended): {schema, contract_version, token, export, bid?}
      // B) Plain export string: "ver=...|sym=...|...|bid=..."
      let schema = "";
      let contractVersion = "";
      let token = "";
      let exportStr = "";
      let bidFromEnvelope = "";
      let source = isTvSecure ? "tv_secure" : "tv_plain";
      let envelopeProvided = false;

      if (trimmed.startsWith("{")) {
        let body: Envelope;
        try {
          body = JSON.parse(trimmed) as Envelope;
        } catch {
          await writeRawEvent(env, raw, undefined, receivedAt);
          return new Response("Invalid JSON body", { status: 400 });
        }

        envelopeProvided = true;
        schema = String(body.schema ?? "");
        contractVersion = String(body.contract_version ?? "");
        token = String(body.token ?? "");
        exportStr = String(body.export ?? "");
        bidFromEnvelope = String(body.bid ?? "");
      } else {
        if (isTvSecure) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          return new Response("Invalid body: /tv_secure requires JSON", { status: 400 });
        }
        exportStr = trimmed;
      }

      if (!exportStr || exportStr.trim().length === 0) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        return new Response("Missing export string", { status: 400 });
      }

      // ✅ MIN-only enforcement
      if (isTvSecure) {
        if (!envelopeProvided) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          return new Response("Invalid body: /tv_secure requires JSON", { status: 400 });
        }
        if (schema !== "OVC_MIN_V01") {
          await writeRawEvent(env, raw, undefined, receivedAt);
          return new Response("Invalid schema: must be OVC_MIN_V01", { status: 400 });
        }
        if (!token || token !== env.OVC_TOKEN) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          return new Response("Rejected: bad token", { status: 401 });
        }
      } else if (schema && schema !== "OVC_MIN_V01") {
        await writeRawEvent(env, raw, undefined, receivedAt);
        return new Response("Invalid schema: must be OVC_MIN_V01", { status: 400 });
      }

      // ✅ Parse export string
      const m = parseExport(exportStr);

      // Required keys for timing + identity
      let sym = "";
      let barCloseMsStr = "";
      try {
        sym = requireField(m, "sym");
        barCloseMsStr = requireField(m, "bar_close_ms");
      } catch (err: any) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        return new Response(`Invalid export: ${err?.message ?? String(err)}`, { status: 400 });
      }
      const bid = (m["bid"] && m["bid"].trim()) || (bidFromEnvelope && bidFromEnvelope.trim());
      if (!bid) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        return new Response("Missing bid (in export or envelope)", { status: 400 });
      }
      await writeRawEvent(env, raw, bid, receivedAt);

      const barCloseMs = Number(barCloseMsStr);
      if (!Number.isFinite(barCloseMs) || barCloseMs <= 0) {
        return new Response("Invalid bar_close_ms", { status: 400 });
      }

      // Your v0.1-min table design
      const schema_ver = "v0.1-min";
      const block_type = "2H";
      const block_start_iso = msToTimestamptzStart2H(barCloseMs);

      // Optional metadata (store as parsed JSONB)
      const payloadMin = {
        envelope: {
          schema: schema || "OVC_MIN_V01",
          contract_version: contractVersion || "1.0.0",
          token_present: Boolean(token),
          source,
        },
        bid,
        export: exportStr,
        parsed: m,
      };

      const sql = neon(env.DATABASE_URL);

      // ✅ Idempotent upsert into your real core table
      // PK: (symbol, block_start, block_type, schema_ver)
      // OHLC nullable (you already altered), so TV can insert NULLs.
      await sql`
        INSERT INTO ovc_blocks_v01 (
          schema_ver, source, symbol, block_type, block_start,
          open, high, low, close, volume,
          bid, export_min, payload_min, ingested_at
        )
        VALUES (
          ${schema_ver}, ${source}, ${sym}, ${block_type}, ${block_start_iso}::timestamptz,
          NULL, NULL, NULL, NULL, NULL,
          ${bid}, ${exportStr}, ${JSON.stringify(payloadMin)}::jsonb, now()
        )
        ON CONFLICT (symbol, block_start, block_type, schema_ver)
        DO UPDATE SET
          source = EXCLUDED.source,
          bid = EXCLUDED.bid,
          export_min = EXCLUDED.export_min,
          payload_min = EXCLUDED.payload_min,
          ingested_at = now()
      `;

      return new Response(JSON.stringify({ ok: true, bid, symbol: sym, block_start: block_start_iso }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (err: any) {
      return new Response(`Worker error: ${err?.message ?? String(err)}`, { status: 500 });
    }
  },
};
