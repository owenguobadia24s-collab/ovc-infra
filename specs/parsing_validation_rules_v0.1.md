1) Input format (frozen)

Payload is a single string of key-value pairs.

Pair delimiter: |

KV separator: =

Example: key=value|key2=value2

Required invariants

Keys are ASCII and case-sensitive.

Order may be validated but parsing must not depend on order.

Duplicate keys are hard errors (reject event).

2) Key presence vs value presence (critical distinction)

Each field has two concepts:

Key must exist (present in payload)

Value may be empty (e.g. rail_loc=)

Definitions

Missing key: key is absent entirely → error if field is required=true

Empty value: key present but value is "" → allowed only for *_or_empty types

Rule: If a field is required and its type is not *_or_empty, empty value is a hard error.

3) Sanitization rules (producer-side + consumer-side)
Producer (Pine) must sanitize string values:

Replace | with /

Replace = with :

Replace newlines with space
(You already do this pattern.)

Parser must:

Accept already-sanitized values.

Not attempt to “unsanitize.”

Trim whitespace on both sides of values.

4) Type system & coercion rules (v0.1)
A) string

Accept any non-empty string after trim.

Empty → error.

B) string_or_empty

Accept any string, including empty.

Store empty as NULL (recommended) or "" (allowed).
v0.1 standard: store empty as NULL.

C) int

Accept optional leading -

Reject decimals ("3.0" invalid)

Reject non-numeric

Empty → error

D) int_or_empty

If empty → NULL

Else apply int rules

E) float

Accept decimal or integer representation

Reject NaN/Inf strings

Empty → error

F) bool_01

Accept only "0" or "1"

Empty → error

G) enum

Must match one of allowed values exactly (case-sensitive)

Empty → error unless enum_or_empty (not used in v0.1)

Enum constraints v0.1:

bias_dir ∈ UP, DOWN, NEUTRAL

pred_dir ∈ UP, DOWN, NEUTRAL

outcome_dir (outcome table) ∈ UP, DOWN, NEUTRAL

5) Duplicate / unknown keys
Duplicate keys

Example: tradeable=1|tradeable=0

Hard error: reject payload (do not insert).

Unknown keys

Any key not in the contract:

Default v0.1 behavior: ignore, but record unknown_keys_count in ingest metadata (recommended).

Optional strict mode: reject. (Not v0.1 default.)

Rationale: allows safe forward-compat when Pine adds new fields, while DB stays stable.

6) Required-field validation (v0.1)
Hard requirements before insert

The parser must confirm all required keys exist and are validly typed:

Identity: ver, profile, scheme_min, block_id, sym, tz, date_ny, bar_close_ms, block2h, block4h

OHLC primitives: o,h,l,c,rng,body,dir,ret

L3 core: bias_mode, bias_dir, perm_state, tradeable, conf_l3, play, pred_dir, timebox, source, build_id, ready

Fields that are allowed to be empty/null:

event, tis, htf_stack, rd_state, regime_tag, trans_risk, rail_loc, pred_target, invalidation, note

7) Semantic validation rules (post-parse checks)

After typing, apply these hard checks:

A) Price sanity

h >= max(o,c,l)

l <= min(o,c,h)

rng = h - l must be consistent within tolerance

Tolerance rule (v0.1):

abs(rng - (h-l)) <= 1e-9 (or a small epsilon like 1e-6)

B) Body sanity

body = abs(c - o) within tolerance

C) Direction sanity

if c > o then dir = 1

if c < o then dir = -1

if c = o then dir = 0

D) Return sanity (if computed in Pine)

ret = (c - o) / o within tolerance

if o = 0 → reject (should never happen in FX/indices)

If you later change ret definition, you must version the schema.

E) Identity sanity

block_id must match the pattern: YYYYMMDD-<block2h>-<sym>

date_ny must match YYYY-MM-DD

block2h must be one of A..L

block4h must be one of AB,CD,EF,GH,IJ,KL

8) Error handling contract (so failures are observable)

When a payload fails parsing/validation:

Do not insert into ovc_min_events

Still store raw event blob (RAW store) with:

parse_ok = 0

error_code (one of below)

error_detail (short string, max 200 chars)

Standard error codes (v0.1)

E_MISSING_REQUIRED_KEY

E_DUPLICATE_KEY

E_UNKNOWN_KEY_STRICT (only if strict mode on)

E_TYPE_COERCION

E_ENUM_INVALID

E_SEMANTIC_PRICE

E_SEMANTIC_DIR

E_SEMANTIC_RET

E_IDENTITY_FORMAT

9) Output formatting rules (typed row)

Store empty strings as NULL for all *_or_empty fields.

Enums stored as text (or native enum later).

bar_close_ms stored as bigint.

Booleans stored as smallint 0/1.

DoD — Parser Spec v0.1 is complete when:

 Input format rules are frozen

 Key presence vs value presence rules are explicit

 Type coercion rules are explicit

 Duplicate/unknown key handling is defined

 Post-parse semantic checks are defined

 Error codes and failure behavior are defined

Checklist (spec-only)

Confirm epsilon tolerance choice (1e-6 is practical).

Confirm unknown key policy: ignore + count (recommended) vs strict reject.

Confirm block_id pattern exactly (sym casing, separators).

Freeze this as parser_spec_v0.1_min.md in repo.