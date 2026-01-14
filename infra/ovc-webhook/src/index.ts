import { neon } from "@neondatabase/serverless";

type Env = {
  DATABASE_URL: string;
  OVC_TOKEN: string;
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

function parseExport(exportStr: string): Record<string, string> {
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

function msToTimestamptzStart2H(barCloseMs: number): string {
  // block_start = bar_close_ms - 2 hours
  const startMs = barCloseMs - 2 * 60 * 60 * 1000;
  // Send ISO string; Postgres will cast to timestamptz
  return new Date(startMs).toISOString();
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      const url = new URL(request.url);

      // ✅ Health check
      if (url.pathname === "/") return new Response("OVC webhook OK", { status: 200 });

      // ✅ Only accept POST /tv
      if (url.pathname !== "/tv") return new Response("Not Found", { status: 404 });
      if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

      // ✅ Require env vars
      if (!env.DATABASE_URL) return new Response("Missing DATABASE_URL", { status: 500 });
      if (!env.OVC_TOKEN) return new Response("Missing OVC_TOKEN", { status: 500 });

      const raw = await request.text();
      if (!raw || raw.trim().length === 0) return new Response("Empty body", { status: 400 });

      const trimmed = raw.trim();

      // Support:
      // A) JSON envelope (recommended): {schema, contract_version, token, export, bid?}
      // B) Plain export string: "ver=...|sym=...|...|bid=..."
      let schema = "";
      let contractVersion = "";
      let token = "";
      let exportStr = "";
      let bidFromEnvelope = "";
      let source = "tv_plain";

      if (trimmed.startsWith("{")) {
        let body: Envelope;
        try {
          body = JSON.parse(trimmed) as Envelope;
        } catch {
          return new Response("Invalid JSON body", { status: 400 });
        }

        schema = String(body.schema ?? "");
        contractVersion = String(body.contract_version ?? "");
        token = String(body.token ?? "");
        exportStr = String(body.export ?? "");
        bidFromEnvelope = String(body.bid ?? "");
        source = String(body.source ?? "tv");
      } else {
        exportStr = trimmed;
      }

      if (!exportStr || exportStr.trim().length === 0) {
        return new Response("Missing export string", { status: 400 });
      }

      // ✅ MIN-only enforcement (if schema is provided it MUST be MIN)
      if (schema && schema !== "OVC_MIN_V01") {
        return new Response("Rejected: schema must be OVC_MIN_V01", { status: 403 });
      }

      // ✅ Token enforcement only when using JSON envelope
      if (schema) {
        if (!token || token !== env.OVC_TOKEN) {
          return new Response("Rejected: bad token", { status: 403 });
        }
      }

      // ✅ Parse export string
      const m = parseExport(exportStr);

      // Required keys for timing + identity
      const sym = requireField(m, "sym");
      const barCloseMsStr = requireField(m, "bar_close_ms");
      const bid = (m["bid"] && m["bid"].trim()) || (bidFromEnvelope && bidFromEnvelope.trim());
      if (!bid) return new Response("Missing bid (in export or envelope)", { status: 400 });

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
        schema: schema || "OVC_MIN_V01",
        contract_version: contractVersion || "1.0.0",
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
          bid, export_min, payload_min
        )
        VALUES (
          ${schema_ver}, ${source}, ${sym}, ${block_type}, ${block_start_iso}::timestamptz,
          NULL, NULL, NULL, NULL, NULL,
          ${bid}, ${exportStr}, ${JSON.stringify(payloadMin)}::jsonb
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
