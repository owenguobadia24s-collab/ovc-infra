import { neon } from "@neondatabase/serverless";

type Env = {
  DATABASE_URL: string;
  OVC_TOKEN: string; // add as Cloudflare secret
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

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      const url = new URL(request.url);

      // ✅ Health check (NO DB call)
      if (url.pathname === "/") return new Response("OVC webhook OK", { status: 200 });

      // ✅ Only accept POST /tv
      if (url.pathname !== "/tv") return new Response("Not Found", { status: 404 });
      if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

      // ✅ Require env vars
      if (!env.DATABASE_URL) return new Response("Missing DATABASE_URL", { status: 500 });
      if (!env.OVC_TOKEN) return new Response("Missing OVC_TOKEN", { status: 500 });

      // ✅ Read raw body
      const raw = await request.text();
      if (!raw || raw.trim().length === 0) return new Response("Empty body", { status: 400 });

      // Support:
      // A) JSON envelope: {schema, contract_version, token, export, bid?}
      // B) Plain export string: "ver=...|sym=...|...|bid=..."
      const trimmed = raw.trim();

      let envelope: Envelope | null = null;
      let exportStr = "";
      let schema = "";
      let contractVersion = "";
      let token = "";
      let bidFromEnvelope = "";
      let source = "tradingview_plain";

      if (trimmed.startsWith("{")) {
        try {
          envelope = JSON.parse(trimmed) as Envelope;
        } catch {
          return new Response("Invalid JSON body", { status: 400 });
        }

        schema = String(envelope.schema ?? "");
        contractVersion = String(envelope.contract_version ?? "");
        token = String(envelope.token ?? "");
        exportStr = String(envelope.export ?? "");
        bidFromEnvelope = String(envelope.bid ?? "");
        source = String(envelope.source ?? "tradingview");
      } else {
        exportStr = trimmed;
      }

      if (!exportStr || exportStr.trim().length === 0) {
        return new Response("Missing export string", { status: 400 });
      }

      // ✅ MIN-only enforcement:
      // If schema is supplied, it MUST be MIN.
      // If schema is omitted (plain text), we infer MIN but still validate required export fields.
      if (schema && schema !== "OVC_MIN_V01") {
        return new Response("Rejected: schema must be OVC_MIN_V01", { status: 403 });
      }

      // ✅ Token enforcement: only possible when using JSON envelope
      if (schema) {
        if (!token || token !== env.OVC_TOKEN) {
          return new Response("Rejected: bad token", { status: 403 });
        }
      }

      // ✅ Parse export
      const m = parseExport(exportStr);

      // ✅ Required MIN keys (tighten/extend to match your frozen contract)
      const ver = requireField(m, "ver");
      const sym = requireField(m, "sym");
      const tz = requireField(m, "tz");
      const date_ny = requireField(m, "date_ny"); // YYYY-MM-DD
      const bar_close_ms_str = requireField(m, "bar_close_ms");
      const seg = requireField(m, "seg");
      const block4h = requireField(m, "block4h");

      const bid = (m["bid"] && m["bid"].trim()) || (bidFromEnvelope && bidFromEnvelope.trim());
      if (!bid) return new Response("Missing bid (in export or envelope)", { status: 400 });

      const bar_close_ms = Number(bar_close_ms_str);
      if (!Number.isFinite(bar_close_ms) || bar_close_ms <= 0) {
        return new Response("Invalid bar_close_ms", { status: 400 });
      }

      // (Optional) If you export exp_ready=1, enforce it:
      // if (m["exp_ready"] && m["exp_ready"] !== "1") return new Response("Rejected: exp_ready != 1", { status: 409 });

      const sql = neon(env.DATABASE_URL);

      // ✅ Idempotent upsert into core table
      await sql`
        INSERT INTO ovc_blocks_core_v01
          (bid, ver, sym, tz, date_ny, bar_close_ms, seg, block4h, export_min, schema_name, contract_version, source)
        VALUES
          (${bid}, ${ver}, ${sym}, ${tz}, ${date_ny}::date, ${bar_close_ms}, ${seg}, ${block4h}, ${exportStr},
           ${schema || "OVC_MIN_V01"}, ${contractVersion || "1.0.0"}, ${source})
        ON CONFLICT (bid)
        DO UPDATE SET
          ver = EXCLUDED.ver,
          sym = EXCLUDED.sym,
          tz = EXCLUDED.tz,
          date_ny = EXCLUDED.date_ny,
          bar_close_ms = EXCLUDED.bar_close_ms,
          seg = EXCLUDED.seg,
          block4h = EXCLUDED.block4h,
          export_min = EXCLUDED.export_min,
          schema_name = EXCLUDED.schema_name,
          contract_version = EXCLUDED.contract_version,
          source = EXCLUDED.source
      `;

      return new Response(JSON.stringify({ ok: true, bid }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (err: any) {
      return new Response(`Worker error: ${err?.message ?? String(err)}`, { status: 500 });
    }
  },
};
