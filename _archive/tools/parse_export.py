import re
from typing import Dict, List, Tuple


_KEY_RE = re.compile(r"^[^=]+$")


def parse_export_string(
    export_str: str,
    delimiter: str = "|",
    kv_separator: str = "=",
) -> Tuple[List[str], Dict[str, str]]:
    if export_str is None:
        raise ValueError("export string is None")
    raw = export_str.strip()
    if not raw:
        raise ValueError("export string is empty")
    if not delimiter or not kv_separator:
        raise ValueError("delimiter and kv_separator must be non-empty")

    parts = raw.split(delimiter)
    keys: List[str] = []
    values: Dict[str, str] = {}
    for idx, part in enumerate(parts):
        if part == "":
            raise ValueError(f"empty segment at position {idx}")
        if kv_separator not in part:
            raise ValueError(f"missing kv separator in segment at position {idx}")
        key, value = part.split(kv_separator, 1)
        if key == "":
            raise ValueError(f"empty key at position {idx}")
        if not _KEY_RE.match(key):
            raise ValueError(f"invalid key '{key}' at position {idx}")
        if key in values:
            raise ValueError(f"duplicate key '{key}' at position {idx}")
        keys.append(key)
        values[key] = value

    return keys, values
