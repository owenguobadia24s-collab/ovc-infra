import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "path1"))

import build_evidence_pack_v0_2 as builder
import overlays_v0_3


def make_m15_block(block_start_ms: int, base_price: float):
    rows = []
    for idx in range(8):
        bar_start_ms = block_start_ms + idx * builder.M15_STEP_MS
        o = base_price + idx * 0.0001
        h = o + 0.0004
        l = o - 0.0002
        c = o + 0.00005
        rows.append(
            {
                "bar_start_ms": bar_start_ms,
                "bar_close_ms": bar_start_ms + builder.M15_STEP_MS,
                "o": o,
                "h": h,
                "l": l,
                "c": c,
                "volume": 1000 + idx,
            }
        )
    return rows


def build_synthetic_pack(pack_dir: Path, *, overlays_enabled: bool, meta_generated_at: str) -> dict:
    blocks = []
    m15_by_block = {}
    all_m15 = []

    base_start_ms = 1672531200000  # 2023-01-01T00:00:00Z
    for idx, suffix in enumerate(["A", "B", "C"]):
        block_start_ms = base_start_ms + idx * builder.TWO_H_MS
        block_id = f"20230101-{suffix}-TEST"
        block = {
            "block_id": block_id,
            "bar_open_ms": block_start_ms,
            "bar_close_ms": block_start_ms + builder.TWO_H_MS,
        }
        blocks.append(block)
        rows = make_m15_block(block_start_ms, 1.1000 + idx * 0.0010)
        m15_by_block[block_id] = rows
        all_m15.extend(rows)

    all_m15.sort(key=lambda row: int(row["bar_start_ms"]))

    (pack_dir / "strips" / "2h").mkdir(parents=True, exist_ok=True)
    (pack_dir / "context" / "4h").mkdir(parents=True, exist_ok=True)

    for block in blocks:
        strip_path = pack_dir / "strips" / "2h" / f"{block['block_id']}.csv"
        builder.write_candles_csv(m15_by_block[block["block_id"]], strip_path)

    backbone_path = pack_dir / "backbone_2h.csv"
    with backbone_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["block_id", "bar_close_ms", "strip_path", "m15_count"])
        for block in blocks:
            strip_rel = Path("strips/2h") / f"{block['block_id']}.csv"
            writer.writerow(
                [
                    block["block_id"],
                    block["bar_close_ms"],
                    strip_rel.as_posix(),
                    8,
                ]
            )

    context_rows = builder.aggregate_rows(
        m15_by_block[blocks[0]["block_id"]] + m15_by_block[blocks[1]["block_id"]],
        2,
        builder.M15_STEP_MS,
    )
    assert context_rows is not None
    context_path = pack_dir / "context" / "4h" / "AB_2023-01-01.csv"
    builder.write_candles_csv(context_rows, context_path)

    qc_report = {
        "generated_at": "2026-01-22T00:00:00Z",
        "summary": {
            "blocks_total": len(blocks),
            "strips_written": len(blocks),
            "context_written": 1,
        },
    }
    (pack_dir / "qc_report.json").write_text(
        json.dumps(qc_report, indent=2, sort_keys=True), encoding="utf-8"
    )

    if overlays_enabled:
        overlays_v0_3.write_overlay_outputs(
            pack_root=pack_dir,
            blocks=blocks,
            m15_by_block=m15_by_block,
            all_m15_candles=all_m15,
        )

    hashes = builder.write_manifest_files(pack_dir)

    meta = {
        "version": "evidence_pack_v0_2",
        "run_id": "test_run",
        "symbol": "TEST",
        "date_from": "2023-01-01",
        "date_to": "2023-01-01",
        "generated_at": meta_generated_at,
        "pack_sha256": hashes["pack_sha256"],
        "data_sha256": hashes["data_sha256"],
        "overlays_v0_3": overlays_v0_3.build_overlay_metadata(enabled=overlays_enabled),
    }
    (pack_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8"
    )

    return hashes


def assert_meta_only_timestamp_diff(meta_path_a: Path, meta_path_b: Path) -> None:
    meta_a = json.loads(meta_path_a.read_text(encoding="utf-8"))
    meta_b = json.loads(meta_path_b.read_text(encoding="utf-8"))
    if meta_a == meta_b:
        return
    meta_a.pop("generated_at", None)
    meta_b.pop("generated_at", None)
    assert meta_a == meta_b


def collect_overlay_files(pack_dir: Path):
    overlays_root = pack_dir / "overlays_v0_3"
    if not overlays_root.exists():
        return []
    return sorted(
        path.relative_to(pack_dir)
        for path in overlays_root.rglob("*")
        if path.is_file()
    )


def test_pack_rebuild_equivalence(tmp_path):
    pack_a1 = tmp_path / "pack_a1"
    pack_a2 = tmp_path / "pack_a2"
    hashes_a1 = build_synthetic_pack(
        pack_a1, overlays_enabled=False, meta_generated_at="2026-01-22T10:00:00Z"
    )
    hashes_a2 = build_synthetic_pack(
        pack_a2, overlays_enabled=False, meta_generated_at="2026-01-22T10:00:01Z"
    )

    assert hashes_a1["data_sha256"] == hashes_a2["data_sha256"]
    assert (pack_a1 / "data_manifest.json").read_bytes() == (pack_a2 / "data_manifest.json").read_bytes()
    assert_meta_only_timestamp_diff(pack_a1 / "meta.json", pack_a2 / "meta.json")

    pack_b1 = tmp_path / "pack_b1"
    pack_b2 = tmp_path / "pack_b2"
    hashes_b1 = build_synthetic_pack(
        pack_b1, overlays_enabled=True, meta_generated_at="2026-01-22T10:00:00Z"
    )
    hashes_b2 = build_synthetic_pack(
        pack_b2, overlays_enabled=True, meta_generated_at="2026-01-22T10:00:01Z"
    )

    assert hashes_b1["data_sha256"] == hashes_b2["data_sha256"]
    assert (pack_b1 / "data_manifest.json").read_bytes() == (pack_b2 / "data_manifest.json").read_bytes()
    assert_meta_only_timestamp_diff(pack_b1 / "meta.json", pack_b2 / "meta.json")

    overlay_files_b1 = collect_overlay_files(pack_b1)
    overlay_files_b2 = collect_overlay_files(pack_b2)
    assert overlay_files_b1 == overlay_files_b2
    for rel_path in overlay_files_b1:
        assert (pack_b1 / rel_path).read_bytes() == (pack_b2 / rel_path).read_bytes()
