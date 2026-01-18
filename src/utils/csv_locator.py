import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

AUTO_PICK = False


def set_auto_pick(enabled: bool) -> None:
    global AUTO_PICK
    AUTO_PICK = bool(enabled)


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CsvCandidate:
    path: Path
    rank: int
    mtime: float
    size: int


def _default_search_dirs() -> list[Path]:
    dirs = [
        REPO_ROOT / "data" / "tv",
        REPO_ROOT / "data",
        REPO_ROOT / "sql",
    ]
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        user_root = Path(user_profile)
    else:
        user_root = Path.home()
    dirs.extend([user_root / "Downloads", user_root / "Desktop"])
    return [path for path in dirs if path.exists()]


def _tokenize_basename(name: str) -> list[str]:
    if not name:
        return []
    stem = Path(name).stem
    tokens = re.split(r"[_\-\s]+", stem)
    return [token.lower() for token in tokens if token]


def _iter_csv_files(root: Path, pattern: Optional[str]) -> Iterable[Path]:
    if pattern:
        yield from root.rglob(pattern)
    else:
        yield from root.rglob("*.csv")


def _match_candidate(
    path: Path,
    base_name: Optional[str],
    tokens: list[str],
    symbol: str,
    timeframe_hint: str,
    pattern_active: bool,
) -> Optional[int]:
    name_lower = path.name.lower()
    stem_lower = path.stem.lower()
    base_match = bool(base_name) and name_lower == base_name.lower()
    symbol_lower = symbol.lower()
    timeframe_lower = timeframe_hint.lower()
    symbol_match = symbol_lower in stem_lower if symbol_lower else False
    timeframe_match = timeframe_lower in stem_lower if timeframe_lower else False
    token_match = bool(tokens) and all(token in stem_lower for token in tokens)

    if base_match:
        return 0
    if symbol_match and timeframe_match:
        return 1
    if token_match:
        return 2
    if pattern_active:
        return 3
    return None


def _collect_candidates(
    search_dirs: list[Path],
    pattern: Optional[str],
    base_name: Optional[str],
    tokens: list[str],
    symbol: str,
    timeframe_hint: str,
) -> list[CsvCandidate]:
    candidates: list[CsvCandidate] = []
    seen: set[str] = set()
    pattern_active = bool(pattern)

    for root in search_dirs:
        for path in _iter_csv_files(root, pattern):
            if not path.is_file() or path.suffix.lower() != ".csv":
                continue
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)

            rank = _match_candidate(path, base_name, tokens, symbol, timeframe_hint, pattern_active)
            if rank is None:
                continue
            stat = path.stat()
            candidates.append(
                CsvCandidate(
                    path=path,
                    rank=rank,
                    mtime=stat.st_mtime,
                    size=stat.st_size,
                )
            )
    return candidates


def _format_candidate(candidate: CsvCandidate, index: int) -> str:
    timestamp = datetime.fromtimestamp(candidate.mtime).strftime("%Y-%m-%d %H:%M:%S")
    return f"{index}) {candidate.path} (modified {timestamp}, size {candidate.size} bytes)"


def _sort_candidates(candidates: list[CsvCandidate]) -> list[CsvCandidate]:
    return sorted(
        candidates,
        key=lambda item: (item.rank, -item.mtime, str(item.path).lower()),
    )


def resolve_csv_path(
    user_path: Optional[str],
    pattern: Optional[str],
    symbol: str,
    timeframe_hint: str = "2h",
) -> str:
    if user_path:
        user_candidate = Path(user_path)
        if user_candidate.is_file():
            return str(user_candidate)

    if not user_path and not pattern:
        raise SystemExit("No CSV path or search pattern provided.")

    base_name = Path(user_path).name if user_path else None
    tokens = _tokenize_basename(base_name or "")
    search_dirs = _default_search_dirs()

    candidates = _collect_candidates(
        search_dirs=search_dirs,
        pattern=pattern,
        base_name=base_name,
        tokens=tokens,
        symbol=symbol,
        timeframe_hint=timeframe_hint,
    )

    if not candidates:
        if user_path:
            searched = ", ".join(str(path) for path in search_dirs)
            raise SystemExit(f"CSV not found at {user_path}. No matches found in: {searched}")
        searched = ", ".join(str(path) for path in search_dirs)
        raise SystemExit(f"No CSV matches found for pattern '{pattern}'. Searched: {searched}")

    candidates = _sort_candidates(candidates)

    if len(candidates) == 1:
        chosen = candidates[0]
        if user_path and not Path(user_path).is_file():
            print(f"CSV not found at {user_path}; using {chosen.path}")
        else:
            print(f"CSV resolved to {chosen.path}")
        return str(chosen.path)

    if user_path:
        print(f"CSV not found at {user_path}. Multiple candidates found:")
    else:
        print(f"Multiple CSV candidates found for pattern '{pattern}':")
    for idx, candidate in enumerate(candidates, start=1):
        print(_format_candidate(candidate, idx))

    if not AUTO_PICK:
        raise SystemExit("Pass --auto-pick to select the top-ranked file or provide an exact path.")

    chosen = candidates[0]
    print(f"Auto-pick enabled; using #1 {chosen.path}")
    return str(chosen.path)
