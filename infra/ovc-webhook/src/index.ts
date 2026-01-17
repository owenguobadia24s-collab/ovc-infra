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
  source?: string;
  sent_ms?: number;
};

const CONTRACT_VERSION = "0.1.1";
const SCHEMA_MIN = "export_contract_v0.1.1_min";
const PROFILE_MIN = "MIN";

// Enums
const DIR_ENUM = new Set(["UP", "DOWN", "NEUTRAL"]);

// Contract typing
type FieldType = "string" | "string_or_empty" | "int" | "int_or_empty" | "float" | "bool_01" | "enum_dir";

type FieldSpec = {
  key: string;
  type: FieldType;
  required: boolean;
};

const FIELDS: FieldSpec[] = [
  { key: "ver", type: "string", required: true },
  { key: "profile", type: "string", required: true },
  { key: "scheme_min", type: "string", required: true },

  { key: "block_id", type: "string", required: true },
  { key: "sym", type: "string", required: true },
  { key: "tz", type: "string", required: true },
  { key: "date_ny", type: "string", required: true },
  { key: "bar_close_ms", type: "int", required: true },
  { key: "block2h", type: "string", required: true },
  { key: "block4h", type: "string", required: true },

  { key: "o", type: "float", required: true },
  { key: "h", type: "float", required: true },
  { key: "l", type: "float", required: true },
  { key: "c", type: "float", required: true },

  { key: "rng", type: "float", required: true },
  { key: "body", type: "float", required: true },
  { key: "dir", type: "int", required: true },
  { key: "ret", type: "float", required: true },

  { key: "state_tag", type: "string", required: true },
  { key: "value_tag", type: "string", required: true },
  { key: "event", type: "string_or_empty", required: false },
  { key: "tt", type: "int", required: true },
  { key: "cp_tag", type: "string", required: true },
  { key: "tis", type: "int_or_empty", required: false },

  { key: "rrc", type: "float", required: true },
  { key: "vrc", type: "float", required: true },

  { key: "trend_tag", type: "string", required: true },
  { key: "struct_state", type: "string", required: true },
  { key: "space_tag", type: "string", required: true },

  { key: "htf_stack", type: "string_or_empty", required: false },
  { key: "with_htf", type: "bool_01", required: true },

  { key: "rd_state", type: "string_or_empty", required: false },
  { key: "regime_tag", type: "string_or_empty", required: false },
  { key: "trans_risk", type: "string_or_empty", required: false },

  { key: "bias_mode", type: "string", required: true },
  { key: "bias_dir", type: "enum_dir", required: true },
  { key: "perm_state", type: "string", required: true },
  { key: "rail_loc", type: "string_or_empty", required: false },

  { key: "tradeable", type: "bool_01", required: true },
  { key: "conf_l3", type: "string", required: true },

  { key: "play", type: "string", required: true },
  { key: "pred_dir", type: "enum_dir", required: true },
  { key: "pred_target", type: "string_or_empty", required: false },
  { key: "timebox", type: "string", required: true },
  { key: "invalidation", type: "string_or_empty", required: false },

  { key: "source", type: "string", required: true },
  { key: "build_id", type: "string", required: true },
  { key: "note", type: "string_or_empty", required: false },
  { key: "ready", type: "bool_01", required: true },
];

const SPEC_BY_KEY: Record<string, FieldSpec> = Object.fromEntries(FIELDS.map(f => [f.key, f]));

type ParseFailCode =
  | "E_DUPLICATE_KEY"
  | "E_BAD_KV"
  | "E_REQUIRED_MISSING"
  | "E_EMPTY_NOT_ALLOWED"
  | "E_TYPE_COERCION"
  | "E_ENUM"
  | "E_SEM_OHLC"
  | "E_SEM_RNG"
  | "E_SEM_BODY"
  | "E_SEM_DIR"
  | "E_SEM_RET";

type ParseResult = {
  ok: true;
  values: Record<string, any>; // coerced
} | {
  ok: false;
  codes: ParseFailCode[];
  message: string;
};

function parseKvStrict(exportStr: string): Record<string, string> {
  const out: Record<string, string> = {};
  const parts = exportStr.split("|");

  for (const part of parts) {
    if (!part) continue;
    const idx = part.indexOf("=");
    if (idx <= 0) throw new Error("E_BAD_KV: missing '=' or empty key");

    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();

    if (!k) throw new Error("E_BAD_KV: empty key");

    if (Object.prototype.hasOwnProperty.call(out, k)) {
      throw new Error(`E_DUPLICATE_KEY: ${k}`);
    }
    out[k] = v;
  }

  return out;
}

function coerceValue(key: string, raw: string): { value: any; isNull: boolean } {
  const spec = SPEC_BY_KEY[key];
  if (!spec) {
    // Unknown keys are allowed to exist in RAW only, but they should not break parsing.
    // If you want unknown keys to be a hard error, flip this to throw.
    return { value: raw, isNull: false };
  }

  const isEmpty = raw.length === 0;

  if (isEmpty) {
    if (spec.type.endsWith("_or_empty")) return { value: null, isNull: true };
    throw new Error(`E_EMPTY_NOT_ALLOWED: ${key}`);
  }

  switch (spec.type) {
    case "string":
    case "string_or_empty":
      return { value: raw, isNull: false };

    case "int":
    case "int_or_empty": {
      const n = Number(raw);
      if (!Number.isInteger(n)) throw new Error(`E_TYPE_COERCION: ${key}`);
      return { value: n, isNull: false };
    }

    case "float": {
      const n = Number(raw);
      if (!Number.isFinite(n)) throw new Error(`E_TYPE_COERCION: ${key}`);
      return { value: n, isNull: false };
    }

    case "bool_01": {
      if (raw !== "0" && raw !== "1") throw new Error(`E_TYPE_COERCION: ${key}`);
      return { value: raw === "1" ? 1 : 0, isNull: false };
    }

    case "enum_dir": {
      if (!DIR_ENUM.has(raw)) throw new Error(`E_ENUM: ${key}`);
      return { value: raw, isNull: false };
    }

    default:
      return { value: raw, isNull: false };
  }
}

function semanticChecks(v: Record<string, any>): ParseFailCode[] {
  const codes: ParseFailCode[] = [];
  const o = v.o as number;
  const h = v.h as number;
  const l = v.l as number;
  const c = v.c as number;

  // OHLC sanity
  if (!(Number.isFinite(o) && Number.isFinite(h) && Number.isFinite(l) && Number.isFinite(c))) {
    codes.push("E_SEM_OHLC");
    return codes;
  }
  if (h < l) codes.push("E_SEM_OHLC");
  if (h < Math.max(o, c)) codes.push("E_SEM_OHLC");
  if (l > Math.min(o, c)) codes.push("E_SEM_OHLC");

  // rng = h - l
  const rng = v.rng as number;
  if (!Number.isFinite(rng) || Math.abs(rng - (h - l)) > 1e-9) codes.push("E_SEM_RNG");

  // body = abs(c - o)
  const body = v.body as number;
  if (!Number.isFinite(body) || Math.abs(body - Math.abs(c - o)) > 1e-9) codes.push("E_SEM_BODY");

  // dir consistency: 1 if c>o, -1 if c<o, 0 if equal
  const dir = v.dir as number;
  const expectedDir = c > o ? 1 : c < o ? -1 : 0;
  if (!Number.isInteger(dir) || dir !== expectedDir) codes.push("E_SEM_DIR");

  // ret = (c - o) / o
  const ret = v.ret as number;
  const expectedRet = o !== 0 ? (c - o) / o : NaN;
  if (!Number.isFinite(ret) || !Number.isFinite(expectedRet) || Math.abs(ret - expectedRet) > 1e-9) {
    codes.push("E_SEM_RET");
  }

  return codes;
}

function parseAndValidate(exportStr: string): ParseResult {
  const codes: ParseFailCode[] = [];
  let kv: Record<string, string>;

  try {
    kv = parseKvStrict(exportStr);
  } catch (e: any) {
    const msg = String(e?.message ?? e);
    if (msg.startsWith("E_DUPLICATE_KEY")) return { ok: false, codes: ["E_DUPLICATE_KEY"], message: msg };
    if (msg.startsWith("E_BAD_KV")) return { ok: false, codes: ["E_BAD_KV"], message: msg };
    return { ok: false, codes: ["E_BAD_KV"], message: msg };
  }

  // Required presence
  for (const f of FIELDS) {
    if (!f.required) continue;
    if (!Object.prototype.hasOwnProperty.call(kv, f.key)) {
      return { ok: false, codes: ["E_REQUIRED_MISSING"], message: `Missing required key: ${f.key}` };
    }
  }

  // Coerce
  const values: Record<string, any> = {};
  for (const [k, raw] of Object.entries(kv)) {
    if (SPEC_BY_KEY[k]) {
      try {
        values[k] = coerceValue(k, raw).value;
      } catch (e: any) {
        const msg = String(e?.message ?? e);
        if (msg.startsWith("E_EMPTY_NOT_ALLOWED")) return { ok: false, codes: ["E_EMPTY_NOT_ALLOWED"], message: msg };
        if (msg.startsWith("E_ENUM")) return { ok: false, codes: ["E_ENUM"], message: msg };
        if (msg.startsWith("E_TYPE_COERCION")) return { ok: false, codes: ["E_TYPE_COERCION"], message: msg };
        return { ok: false, codes: ["E_TYPE_COERCION"], message: msg };
      }
    } else {
      // Unknown key: keep as string in payload only (does not block parse).
      values[k] = raw;
    }
  }

  // Contract identity checks
  if (values.ver !== CONTRACT_VERSION) return { ok: false, codes: ["E_TYPE_COERCION"], message: `ver must be ${CONTRACT_VERSION}` };
  if (values.profile !== PROFILE_MIN) return { ok: false, codes: ["E_TYPE_COERCION"], message: `profile must be ${PROFILE_MIN}` };
  if (values.scheme_min !== SCHEMA_MIN) return { ok: false, codes: ["E_TYPE_COERCION"], message: `scheme_min must be ${SCHEMA_MIN}` };

  // Semantic checks
  const sem = semanticChecks(values);
  if (sem.length) return { ok: false, codes: sem, message: `Semantic check failed: ${sem.join(",")}` };

  return { ok: true, values };
}

function formatDateUTC(d: Date): string {
  return d.toISOString().slice(0, 10);
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

async function writeRawEvent(env: Env, raw: string, blockId: string | undefined, now: Date): Promise<string | null> {
  if (!env.RAW_EVENTS) return null;

  const day = formatDateUTC(now);
  const iso = now.toISOString().replace(/[:]/g, "-");
  const keyBid = blockId ? sanitizeKeyPart(blockId) : "";
  const key = keyBid
    ? `tv/${day}/${keyBid}_${uniqueKeySuffix()}.txt`
    : `tv/${day}/${iso}_${uniqueKeySuffix()}.txt`;

  try {
    await env.RAW_EVENTS.put(key, raw, { httpMetadata: { contentType: "text/plain" } });
    return key;
  } catch (err) {
    console.error("Failed to write raw event to R2", err);
    return null;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const startedAt = new Date();
    const sql = env.DATABASE_URL ? neon(env.DATABASE_URL) : null;

    // Defaults for run report
    let verdict: "PASS" | "WARN" | "FAIL" = "FAIL";
    let input_count = 1;
    let parse_ok_count = 0;
    let parse_fail_count = 0;
    let upsert_inserted = 0;
    let upsert_updated = 0;

    // Helper to always try writing run report
    async function writeRunReport(extra?: Record<string, any>) {
      if (!sql) return;
      try {
        await sql`
          INSERT INTO ovc.ovc_run_reports_v01 (
            verdict, input_count, parse_ok_count, parse_fail_count,
            upsert_inserted, upsert_updated, started_at, ended_at,
            meta
          )
          VALUES (
            ${verdict}, ${input_count}, ${parse_ok_count}, ${parse_fail_count},
            ${upsert_inserted}, ${upsert_updated}, ${startedAt.toISOString()}::timestamptz, now(),
            ${JSON.stringify(extra ?? {})}::jsonb
          )
        `;
      } catch (e) {
        // If your table doesn't have meta/ended_at yet, remove those cols in the INSERT above.
        console.error("Failed to write run report", e);
      }
    }

    try {
      const url = new URL(request.url);

      // Health
      if (url.pathname === "/") return new Response("OVC webhook OK", { status: 200 });

      const isTv = url.pathname === "/tv";
      const isTvSecure = url.pathname === "/tv_secure";
      if (!isTv && !isTvSecure) return new Response("Not Found", { status: 404 });
      if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

      if (!env.DATABASE_URL) return new Response("Missing DATABASE_URL", { status: 500 });
      if (!env.OVC_TOKEN) return new Response("Missing OVC_TOKEN", { status: 500 });

      const raw = await request.text();
      const receivedAt = new Date();

      if (!raw || raw.trim().length === 0) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        parse_fail_count = 1;
        verdict = "FAIL";
        await writeRunReport({ error: "Empty body" });
        return new Response("Empty body", { status: 400 });
      }

      const trimmed = raw.trim();

      // Envelope or plain export
      let envelope: Envelope | null = null;
      let exportStr = "";
      let token = "";
      let schema = "";
      let contractVersion = "";
      let source = isTvSecure ? "tv_secure" : "tv_plain";

      if (trimmed.startsWith("{")) {
        try {
          envelope = JSON.parse(trimmed) as Envelope;
        } catch {
          await writeRawEvent(env, raw, undefined, receivedAt);
          parse_fail_count = 1;
          verdict = "FAIL";
          await writeRunReport({ error: "Invalid JSON body" });
          return new Response("Invalid JSON body", { status: 400 });
        }
        exportStr = String(envelope.export ?? "");
        token = String(envelope.token ?? "");
        schema = String(envelope.schema ?? "");
        contractVersion = String(envelope.contract_version ?? "");
        if (envelope.source) source = String(envelope.source);
      } else {
        if (isTvSecure) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          parse_fail_count = 1;
          verdict = "FAIL";
          await writeRunReport({ error: "/tv_secure requires JSON envelope" });
          return new Response("Invalid body: /tv_secure requires JSON", { status: 400 });
        }
        exportStr = trimmed;
      }

      if (!exportStr || exportStr.trim().length === 0) {
        await writeRawEvent(env, raw, undefined, receivedAt);
        parse_fail_count = 1;
        verdict = "FAIL";
        await writeRunReport({ error: "Missing export string" });
        return new Response("Missing export string", { status: 400 });
      }

      // /tv_secure enforcement
      if (isTvSecure) {
        if (schema !== SCHEMA_MIN) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          parse_fail_count = 1;
          verdict = "FAIL";
          await writeRunReport({ error: `Invalid schema: must be ${SCHEMA_MIN}` });
          return new Response(`Invalid schema: must be ${SCHEMA_MIN}`, { status: 400 });
        }
        if (!token || token !== env.OVC_TOKEN) {
          await writeRawEvent(env, raw, undefined, receivedAt);
          parse_fail_count = 1;
          verdict = "FAIL";
          await writeRunReport({ error: "Rejected: bad token" });
          return new Response("Rejected: bad token", { status: 401 });
        }
      }

      // Parse/validate (strict)
      const parsed = parseAndValidate(exportStr);

      // Attempt to extract block_id for raw-key naming even on failure
      let blockIdForKey: string | undefined = undefined;
      try {
        const kv = parseKvStrict(exportStr);
        blockIdForKey = kv["block_id"];
      } catch {
        // ignore
      }
      const rawKey = await writeRawEvent(env, raw, blockIdForKey, receivedAt);

      if (!parsed.ok) {
        parse_fail_count = 1;
        verdict = "FAIL";
        await writeRunReport({
          error: parsed.message,
          codes: parsed.codes,
          raw_key: rawKey,
          schema,
          contract_version: contractVersion,
          source,
        });
        return new Response(`Invalid export: ${parsed.message}`, { status: 400 });
      }

      // Success
      parse_ok_count = 1;
      verdict = "PASS";

      const v = parsed.values;

      // Upsert into LOCKED MIN table: ovc.ovc_blocks_v01_1_min (PK: block_id)
      // Keep the raw export string for audit + parsed JSON for reprocessing.
      const payload = {
        schema: SCHEMA_MIN,
        contract_version: CONTRACT_VERSION,
        envelope: envelope ? { schema, contractVersion, source, sent_ms: envelope.sent_ms ?? null } : null,
        raw_key: rawKey,
        export: exportStr,
        parsed: v,
        received_at: receivedAt.toISOString(),
      };

      const upsertRows = await sql!`
        INSERT INTO ovc.ovc_blocks_v01_1_min (
          block_id, sym, tz, date_ny, bar_close_ms, block2h, block4h,
          o, h, l, c, rng, body, dir, ret,
          state_tag, value_tag, event, tt, cp_tag, tis,
          rrc, vrc,
          trend_tag, struct_state, space_tag,
          htf_stack, with_htf,
          rd_state, regime_tag, trans_risk,
          bias_mode, bias_dir, perm_state, rail_loc,
          tradeable, conf_l3,
          play, pred_dir, pred_target, timebox, invalidation,
          source, build_id, note, ready,
          export_str, payload, ingest_ts
        )
        VALUES (
          ${v.block_id}, ${v.sym}, ${v.tz}, ${v.date_ny}, ${v.bar_close_ms}, ${v.block2h}, ${v.block4h},
          ${v.o}, ${v.h}, ${v.l}, ${v.c}, ${v.rng}, ${v.body}, ${v.dir}, ${v.ret},
          ${v.state_tag}, ${v.value_tag}, ${v.event ?? null}, ${v.tt}, ${v.cp_tag}, ${v.tis ?? null},
          ${v.rrc}, ${v.vrc},
          ${v.trend_tag}, ${v.struct_state}, ${v.space_tag},
          ${v.htf_stack ?? null}, ${v.with_htf},
          ${v.rd_state ?? null}, ${v.regime_tag ?? null}, ${v.trans_risk ?? null},
          ${v.bias_mode}, ${v.bias_dir}, ${v.perm_state}, ${v.rail_loc ?? null},
          ${v.tradeable}, ${v.conf_l3},
          ${v.play}, ${v.pred_dir}, ${v.pred_target ?? null}, ${v.timebox}, ${v.invalidation ?? null},
          ${v.source}, ${v.build_id}, ${v.note ?? null}, ${v.ready},
          ${exportStr}, ${JSON.stringify(payload)}::jsonb, now()
        )
        ON CONFLICT (block_id)
        DO UPDATE SET
          sym = EXCLUDED.sym,
          tz = EXCLUDED.tz,
          date_ny = EXCLUDED.date_ny,
          bar_close_ms = EXCLUDED.bar_close_ms,
          block2h = EXCLUDED.block2h,
          block4h = EXCLUDED.block4h,
          o = EXCLUDED.o,
          h = EXCLUDED.h,
          l = EXCLUDED.l,
          c = EXCLUDED.c,
          rng = EXCLUDED.rng,
          body = EXCLUDED.body,
          dir = EXCLUDED.dir,
          ret = EXCLUDED.ret,
          state_tag = EXCLUDED.state_tag,
          value_tag = EXCLUDED.value_tag,
          event = EXCLUDED.event,
          tt = EXCLUDED.tt,
          cp_tag = EXCLUDED.cp_tag,
          tis = EXCLUDED.tis,
          rrc = EXCLUDED.rrc,
          vrc = EXCLUDED.vrc,
          trend_tag = EXCLUDED.trend_tag,
          struct_state = EXCLUDED.struct_state,
          space_tag = EXCLUDED.space_tag,
          htf_stack = EXCLUDED.htf_stack,
          with_htf = EXCLUDED.with_htf,
          rd_state = EXCLUDED.rd_state,
          regime_tag = EXCLUDED.regime_tag,
          trans_risk = EXCLUDED.trans_risk,
          bias_mode = EXCLUDED.bias_mode,
          bias_dir = EXCLUDED.bias_dir,
          perm_state = EXCLUDED.perm_state,
          rail_loc = EXCLUDED.rail_loc,
          tradeable = EXCLUDED.tradeable,
          conf_l3 = EXCLUDED.conf_l3,
          play = EXCLUDED.play,
          pred_dir = EXCLUDED.pred_dir,
          pred_target = EXCLUDED.pred_target,
          timebox = EXCLUDED.timebox,
          invalidation = EXCLUDED.invalidation,
          source = EXCLUDED.source,
          build_id = EXCLUDED.build_id,
          note = EXCLUDED.note,
          ready = EXCLUDED.ready,
          export_str = EXCLUDED.export_str,
          payload = EXCLUDED.payload,
          ingest_ts = now()
        RETURNING (xmax = 0) AS inserted
      `;

      if (upsertRows?.[0]?.inserted) upsert_inserted = 1;
      else upsert_updated = 1;

      await writeRunReport({
        block_id: v.block_id,
        sym: v.sym,
        schema: SCHEMA_MIN,
        contract_version: CONTRACT_VERSION,
        raw_key: rawKey,
        source,
      });

      return new Response(JSON.stringify({
        ok: true,
        block_id: v.block_id,
        sym: v.sym,
        inserted: Boolean(upsertRows?.[0]?.inserted),
      }), { status: 200, headers: { "Content-Type": "application/json" } });

    } catch (err: any) {
      verdict = "FAIL";
      parse_fail_count = parse_fail_count || 1;

      // Best-effort run report
      try {
        if (env.DATABASE_URL) {
          const sql2 = neon(env.DATABASE_URL);
          await sql2`
            INSERT INTO ovc.ovc_run_reports_v01 (
              verdict, input_count, parse_ok_count, parse_fail_count,
              upsert_inserted, upsert_updated, started_at, ended_at,
              meta
            )
            VALUES (
              ${verdict}, ${input_count}, ${parse_ok_count}, ${parse_fail_count},
              ${upsert_inserted}, ${upsert_updated}, ${startedAt.toISOString()}::timestamptz, now(),
              ${JSON.stringify({ error: err?.message ?? String(err) })}::jsonb
            )
          `;
        }
      } catch (e) {
        console.error("Failed to write run report in catch", e);
      }

      return new Response(`Worker error: ${err?.message ?? String(err)}`, { status: 500 });
    }
  },
};
