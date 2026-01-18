import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def new_run_id(prefix: str | None = None) -> str:
    run_id = str(uuid.uuid4())
    if prefix:
        safe_prefix = "_".join(str(prefix).split())
        if safe_prefix:
            return f"{safe_prefix}_{run_id}"
    return run_id


def make_run_dir(base_out_dir: str, component_name: str, run_id: str) -> Path:
    run_dir = Path(base_out_dir) / component_name / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_meta(
    run_dir: Path,
    component_name: str,
    run_id: str,
    argv: list[str],
    extra: dict | None = None,
) -> Path:
    payload = {
        "run_id": run_id,
        "component": component_name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "argv": argv,
    }
    if extra:
        payload.update(extra)
    meta_path = run_dir / "meta.json"
    meta_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return meta_path


def write_latest(component_root: Path, run_id: str) -> Path:
    component_root.mkdir(parents=True, exist_ok=True)
    latest_path = component_root / "LATEST.txt"
    latest_path.write_text(f"{run_id}\n", encoding="utf-8")
    return latest_path
