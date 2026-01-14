import { neon } from "@neondatabase/serverless";

export default {
  async fetch(request: Request, env: any): Promise<Response> {
    try {
      const url = new URL(request.url);

      // ✅ Health check (NO DB call)
      if (url.pathname === "/") {
        return new Response("OVC webhook OK", { status: 200 });
      }

      // ✅ Only accept POST /tv
      if (url.pathname !== "/tv") {
        return new Response("Not Found", { status: 404 });
      }
      if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
      }

      // ✅ Require DATABASE_URL only here
      if (!env.DATABASE_URL) {
        return new Response("Missing DATABASE_URL", { status: 500 });
      }

      // ✅ Read raw body (TradingView will send plain text)
      const raw = await request.text();
      if (!raw || raw.trim().length === 0) {
        return new Response("Empty body", { status: 400 });
      }

      // TODO: replace this with your real parser
      // For now just prove prod insert works:
      const sql = neon(env.DATABASE_URL);

      // Example insert (match your schema)
      await sql`
        INSERT INTO ovc_record (instrument_id, timestamp, timeframe, version, payload)
        VALUES (1, now(), '2H', 1, ${JSON.stringify({ raw })}::jsonb)
      `;

      return new Response("DB insert OK", { status: 200 });
    } catch (err: any) {
      // ✅ Never throw uncaught — return the error text
      return new Response(`Worker error: ${err?.message ?? String(err)}`, {
        status: 500,
      });
    }
  },
};
