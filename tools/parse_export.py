"""
Compatibility shim for archived parse_export.

Provides: parse_export_string
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


_ARCHIVE_PATH = Path(__file__).resolve().parents[1] / "_archive" / "tools" / "parse_export.py"


def _load_archive_module():
    if not _ARCHIVE_PATH.is_file():
        raise ImportError(
            "Archived parse_export not found at _archive/tools/parse_export.py. "
            "Restore the archived tool or update imports to the new location."
        )
    spec = importlib.util.spec_from_file_location(
        "ovc_archive_parse_export", _ARCHIVE_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "Unable to load archived parse_export module. "
            "Restore the archived tool or update imports to the new location."
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    _mod = _load_archive_module()
    parse_export_string = _mod.parse_export_string
except Exception as exc:  # pragma: no cover - import-time failure path
    raise ImportError(
        "parse_export_string import failed. "
        "Restore archived _archive/tools/parse_export.py or update imports."
    ) from exc


__all__ = ["parse_export_string"]
