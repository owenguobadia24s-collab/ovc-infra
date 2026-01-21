import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Add parent to path for local imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ovc_ops.run_artifact import RunWriter, detect_trigger


# Required env vars (NOTIOM_TOKEN is intentional spelling - canonical)
REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "NOTIOM_TOKEN",
    "NOTION_BLOCKS_DB_ID",
    "NOTION_OUTCOMES_DB_ID",
]

# Pipeline metadata
PIPELINE_ID = "D-NotionSync"
PIPELINE_VERSION = "0.1.0"


def check_required_env():
    """Check required env vars at startup. Print missing names (not values) and exit if any missing."""
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        print(f"NOTION_SYNC_MISSING_ENV={','.join(missing)}")
        print("NOTION_SYNC_STATUS=failed")
        sys.exit(1)


NOTION_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def notion_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def notion_request(method, url, token, payload=None, max_retries=5):
    headers = notion_headers(token)
    for attempt in range(max_retries):
        response = requests.request(
            method, url, headers=headers, json=payload, timeout=30
        )
        if response.status_code == 429:
            time.sleep(1.0 + random.random())
            continue
        if response.status_code >= 400:
            raise RuntimeError(
                f"Notion API {response.status_code}: {response.text}"
            )
        if response.text:
            return response.json()
        return {}
    raise RuntimeError("Notion API rate limit exceeded after retries")


def notion_find_page(db_id, token, title_property, title_value):
    url = f"{NOTION_BASE_URL}/databases/{db_id}/query"
    payload = {
        "filter": {"property": title_property, "title": {"equals": title_value}},
        "page_size": 1,
    }
    data = notion_request("POST", url, token, payload)
    results = data.get("results", [])
    if results:
        return results[0]["id"]
    return None


def notion_upsert_page(db_id, token, title_property, title_value, properties):
    page_id = notion_find_page(db_id, token, title_property, title_value)
    if page_id:
        url = f"{NOTION_BASE_URL}/pages/{page_id}"
        notion_request("PATCH", url, token, {"properties": properties})
        return "update"
    url = f"{NOTION_BASE_URL}/pages"
    payload = {"parent": {"database_id": db_id}, "properties": properties}
    notion_request("POST", url, token, payload)
    return "create"


def title_prop(name, value):
    return {name: {"title": [{"text": {"content": str(value)}}]}}


def select_prop(name, value):
    if value is None:
        return {}
    return {name: {"select": {"name": str(value)}}}


def date_prop(name, value):
    if value is None:
        return {}
    if isinstance(value, datetime):
        iso_value = value.astimezone(timezone.utc).isoformat()
    else:
        iso_value = value.isoformat()
    return {name: {"date": {"start": iso_value}}}


def text_prop(name, value):
    if value is None:
        return {}
    value = str(value)
    if not value:
        return {}
    return {name: {"rich_text": [{"text": {"content": value}}]}}


def number_prop(name, value):
    if value is None:
        return {}
    return {name: {"number": float(value)}}


def checkbox_prop(name, value):
    if value is None:
        return {}
    return {name: {"checkbox": bool(value)}}


def ensure_sync_state(cursor):
    cursor.execute("create schema if not exists ops;")
    cursor.execute(
        """
        create table if not exists ops.notion_sync_state (
          name text primary key,
          last_ts timestamptz,
          updated_at timestamptz not null default now()
        );
        """
    )
    cursor.execute(
        """
        insert into ops.notion_sync_state (name, last_ts, updated_at)
        values
          ('blocks_min', null, now()),
          ('outcomes', null, now()),
          ('eval_runs', null, now())
        on conflict (name) do nothing;
        """
    )


def get_watermark(cursor, name):
    cursor.execute(
        "select last_ts from ops.notion_sync_state where name = %s",
        (name,),
    )
    row = cursor.fetchone()
    if row:
        return row["last_ts"]
    return None


def update_watermark(cursor, name, last_ts):
    cursor.execute(
        "update ops.notion_sync_state set last_ts = %s, updated_at = now() where name = %s",
        (last_ts, name),
    )


def sync_blocks(cursor, token, db_id):
    last_ts = get_watermark(cursor, "blocks_min")
    base_ts = last_ts or datetime(1970, 1, 1, tzinfo=timezone.utc)
    cursor.execute(
        """
        select
          block_id,
          sym,
          date_ny,
          export_str,
          ingest_ts,
          to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as block_start
        from ovc.ovc_blocks_v01_1_min
        where ingest_ts > %s
        order by ingest_ts asc;
        """,
        (base_ts,),
    )
    rows = cursor.fetchall()

    synced = 0
    watermark = last_ts
    for row in rows:
        properties = {}
        properties.update(title_prop("Block ID", row["block_id"]))
        properties.update(select_prop("Symbol", row["sym"]))
        properties.update(date_prop("Date NY", row["date_ny"]))
        properties.update(date_prop("Block Start", row["block_start"]))
        properties.update(date_prop("Ingest TS", row["ingest_ts"]))
        properties.update(text_prop("Export Str", row["export_str"]))

        notion_upsert_page(
            db_id, token, "Block ID", row["block_id"], properties
        )
        synced += 1
        watermark = row["ingest_ts"]
        update_watermark(cursor, "blocks_min", watermark)

    final_ts = watermark or last_ts
    print(f"blocks_min synced {synced} rows, watermark -> {final_ts}")
    return synced


def sync_outcomes(cursor, token, db_id):
    last_ts = get_watermark(cursor, "outcomes")
    base_ts = last_ts or datetime(1970, 1, 1, tzinfo=timezone.utc)
    cursor.execute(
        """
        select
          o.block_id,
          o.run_id,
          o.eval_version,
          o.fwd_ret_1,
          o.fwd_ret_2,
          o.fwd_ret_6,
          o.fwd_ret_12,
          o.mfe_1,
          o.mae_1,
          o.hit_1,
          o.hit_2,
          o.hit_6,
          o.hit_12,
          r.computed_at
        from derived.ovc_outcomes_v0_1 o
        left join derived.eval_runs r on r.run_id = o.run_id
        where r.computed_at > %s
        order by r.computed_at asc, o.block_id asc;
        """,
        (base_ts,),
    )
    rows = cursor.fetchall()

    synced = 0
    watermark = last_ts
    for row in rows:
        properties = {}
        properties.update(title_prop("Block ID", row["block_id"]))
        properties.update(text_prop("Run ID", row["run_id"]))
        properties.update(text_prop("Eval Version", row["eval_version"]))
        properties.update(number_prop("Fwd Ret 1", row["fwd_ret_1"]))
        properties.update(number_prop("Fwd Ret 2", row["fwd_ret_2"]))
        properties.update(number_prop("Fwd Ret 6", row["fwd_ret_6"]))
        properties.update(number_prop("Fwd Ret 12", row["fwd_ret_12"]))
        properties.update(number_prop("MFE", row["mfe_1"]))
        properties.update(number_prop("MAE", row["mae_1"]))
        properties.update(checkbox_prop("Hit 1", row["hit_1"]))
        properties.update(checkbox_prop("Hit 2", row["hit_2"]))
        properties.update(checkbox_prop("Hit 6", row["hit_6"]))
        properties.update(checkbox_prop("Hit 12", row["hit_12"]))

        notion_upsert_page(
            db_id, token, "Block ID", row["block_id"], properties
        )
        synced += 1
        watermark = row["computed_at"]
        if watermark is not None:
            update_watermark(cursor, "outcomes", watermark)

    final_ts = watermark or last_ts
    print(f"outcomes synced {synced} rows, watermark -> {final_ts}")
    return synced


def sync_eval_runs(cursor, token, db_id):
    last_ts = get_watermark(cursor, "eval_runs")
    base_ts = last_ts or datetime(1970, 1, 1, tzinfo=timezone.utc)
    cursor.execute(
        """
        select run_id, eval_version, formula_hash, computed_at
        from derived.eval_runs
        where computed_at > %s
        order by computed_at asc;
        """,
        (base_ts,),
    )
    rows = cursor.fetchall()

    synced = 0
    watermark = last_ts
    for row in rows:
        properties = {}
        properties.update(title_prop("Run ID", row["run_id"]))
        properties.update(text_prop("Eval Version", row["eval_version"]))
        properties.update(text_prop("Formula Hash", row["formula_hash"]))
        properties.update(date_prop("Computed At", row["computed_at"]))

        notion_upsert_page(
            db_id, token, "Run ID", row["run_id"], properties
        )
        synced += 1
        watermark = row["computed_at"]
        update_watermark(cursor, "eval_runs", watermark)

    final_ts = watermark or last_ts
    print(f"eval_runs synced {synced} rows, watermark -> {final_ts}")
    return synced


def main(writer: RunWriter):
    database_url = require_env("DATABASE_URL")
    notion_token = require_env("NOTIOM_TOKEN")
    blocks_db_id = require_env("NOTION_BLOCKS_DB_ID")
    outcomes_db_id = require_env("NOTION_OUTCOMES_DB_ID")
    runs_db_id = os.getenv("NOTION_RUNS_DB_ID")
    
    writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")
    writer.add_input(type="neon_table", ref="derived.ovc_outcomes_v0_1")
    
    total_synced = 0

    with psycopg2.connect(database_url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            ensure_sync_state(cursor)
            
            blocks_synced = sync_blocks(cursor, notion_token, blocks_db_id)
            total_synced += blocks_synced
            writer.log(f"blocks_min synced {blocks_synced} rows")
            
            outcomes_synced = sync_outcomes(cursor, notion_token, outcomes_db_id)
            total_synced += outcomes_synced
            writer.log(f"outcomes synced {outcomes_synced} rows")
            
            if runs_db_id:
                runs_synced = sync_eval_runs(cursor, notion_token, runs_db_id)
                total_synced += runs_synced
                writer.log(f"eval_runs synced {runs_synced} rows")
            else:
                writer.log("eval_runs skipped (NOTION_RUNS_DB_ID not set)")
    
    writer.add_output(type="notion_db", ref=blocks_db_id, rows_written=total_synced)
    return total_synced


if __name__ == "__main__":
    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    run_id = writer.start(trigger_type, trigger_source, actor)
    
    # Check env (also emits check via RunWriter)
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        writer.log(f"NOTION_SYNC_MISSING_ENV={','.join(missing)}")
        writer.log("NOTION_SYNC_STATUS=failed")
        writer.finish("failed")
        sys.exit(1)
    
    try:
        total_synced = main(writer)
        writer.log("NOTION_SYNC_STATUS=success")
        writer.check("sync_completed", "Notion sync completed", "pass", ["run.json:$.outputs[0].rows_written"])
        writer.finish("success")
    except Exception as exc:
        writer.log(f"notion_sync failed: {exc}")
        writer.log("NOTION_SYNC_STATUS=failed")
        writer.check("sync_completed", f"Notion sync failed: {type(exc).__name__}", "fail", [])
        writer.finish("failed")
        sys.exit(1)
