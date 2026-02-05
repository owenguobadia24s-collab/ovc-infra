"""
Compatibility shim for archived validate_contract.

Provides: validate_export_string
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


_ARCHIVE_PATH = Path(__file__).resolve().parents[1] / "_archive" / "tools" / "validate_contract.py"


def _load_archive_module():
    if not _ARCHIVE_PATH.is_file():
        raise ImportError(
            "Archived validate_contract not found at _archive/tools/validate_contract.py. "
            "Restore the archived tool or update imports to the new location."
        )
    spec = importlib.util.spec_from_file_location(
        "ovc_archive_validate_contract", _ARCHIVE_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "Unable to load archived validate_contract module. "
            "Restore the archived tool or update imports to the new location."
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    _mod = _load_archive_module()
    validate_export_string = _mod.validate_export_string
except Exception as exc:  # pragma: no cover - import-time failure path
    raise ImportError(
        "validate_export_string import failed. "
        "Restore archived _archive/tools/validate_contract.py or update test imports."
    ) from exc


__all__ = ["validate_export_string"]
