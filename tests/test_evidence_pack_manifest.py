import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "path1"))

import build_evidence_pack_v0_2 as builder


def test_pack_sha256_stable(tmp_path):
    """Legacy test: build manifest hash is stable within same file content."""
    pack_root = tmp_path / "pack"
    (pack_root / "strips" / "2h").mkdir(parents=True)
    (pack_root / "context" / "4h").mkdir(parents=True)

    (pack_root / "meta.json").write_text('{"version":"0.2"}\n', encoding="utf-8")
    (pack_root / "qc_report.json").write_text('{"summary":{}}\n', encoding="utf-8")
    (pack_root / "backbone_2h.csv").write_text("block_id,bar_close_ms\n", encoding="utf-8")
    (pack_root / "strips" / "2h" / "block.csv").write_text("idx,time_utc\n1,0\n", encoding="utf-8")
    (pack_root / "context" / "4h" / "AB_2022-01-01.csv").write_text("idx,time_utc\n1,0\n", encoding="utf-8")

    manifest_first = builder.build_manifest(pack_root)
    pack_first = builder.compute_pack_sha256(manifest_first)
    manifest_second = builder.build_manifest(pack_root)
    pack_second = builder.compute_pack_sha256(manifest_second)

    assert pack_first == pack_second


def test_data_sha256_stable_across_timestamp_changes(tmp_path):
    """
    Data hash must remain identical across rebuilds even when generated_at changes.
    Build hash is allowed to change (due to meta.json/qc_report.json timestamps).
    """
    pack_root = tmp_path / "pack"
    (pack_root / "strips" / "2h").mkdir(parents=True)
    (pack_root / "context" / "4h").mkdir(parents=True)

    # Deterministic candle data (should produce stable data_sha256)
    (pack_root / "backbone_2h.csv").write_text(
        "block_id,bar_close_ms,strip_path,m15_count\n"
        "20220101-A-GBPUSD,1640998800000,strips/2h/20220101-A-GBPUSD.csv,8\n",
        encoding="utf-8",
    )
    (pack_root / "strips" / "2h" / "20220101-A-GBPUSD.csv").write_text(
        "idx,time_utc,bar_start_ms,bar_close_ms,o,h,l,c,volume\n"
        "1,2022-01-01T00:00:00Z,1640995200000,1640996100000,1.35,1.36,1.34,1.355,100\n",
        encoding="utf-8",
    )
    (pack_root / "context" / "4h" / "AB_2022-01-01.csv").write_text(
        "idx,time_utc,bar_start_ms,bar_close_ms,o,h,l,c,volume\n"
        "1,2022-01-01T00:00:00Z,1640995200000,1640998800000,1.35,1.36,1.34,1.355,200\n",
        encoding="utf-8",
    )

    # First build with timestamp T1
    (pack_root / "meta.json").write_text(
        '{"generated_at":"2026-01-22T10:00:00Z","version":"evidence_pack_v0_2"}\n',
        encoding="utf-8",
    )
    (pack_root / "qc_report.json").write_text(
        '{"generated_at":"2026-01-22T10:00:00Z","summary":{}}\n',
        encoding="utf-8",
    )

    hashes_build1 = builder.write_manifest_files(pack_root)

    # Second build with different timestamp T2
    (pack_root / "meta.json").write_text(
        '{"generated_at":"2026-01-22T11:00:00Z","version":"evidence_pack_v0_2"}\n',
        encoding="utf-8",
    )
    (pack_root / "qc_report.json").write_text(
        '{"generated_at":"2026-01-22T11:00:00Z","summary":{}}\n',
        encoding="utf-8",
    )

    hashes_build2 = builder.write_manifest_files(pack_root)

    # Data hashes MUST be identical (candle data unchanged)
    assert hashes_build1["data_sha256"] == hashes_build2["data_sha256"], (
        f"data_sha256 should be stable: {hashes_build1['data_sha256']} vs {hashes_build2['data_sha256']}"
    )
    assert hashes_build1["data_manifest_sha256"] == hashes_build2["data_manifest_sha256"], (
        f"data_manifest_sha256 should be stable"
    )

    # Build hashes are allowed to differ (timestamps changed)
    # Note: They WILL differ because meta.json and qc_report.json content changed
    assert hashes_build1["build_sha256"] != hashes_build2["build_sha256"], (
        f"build_sha256 should change when timestamps change"
    )


def test_is_data_file():
    """Test data file pattern matching."""
    assert builder.is_data_file("backbone_2h.csv") is True
    assert builder.is_data_file("strips/2h/20220101-A-GBPUSD.csv") is True
    assert builder.is_data_file("context/4h/AB_2022-01-01.csv") is True

    assert builder.is_data_file("meta.json") is False
    assert builder.is_data_file("qc_report.json") is False
    assert builder.is_data_file("manifest.json") is False
    assert builder.is_data_file("data_manifest.json") is False
    assert builder.is_data_file("build_manifest.json") is False

    # Edge cases
    assert builder.is_data_file("strips/2h/") is False  # Directory path, not file
    assert builder.is_data_file("strips/2h/block.txt") is False  # Wrong extension
    assert builder.is_data_file("context/2h/file.csv") is False  # Wrong context directory


def test_data_manifest_only_includes_data_files(tmp_path):
    """Data manifest should only include backbone, strips, and context CSVs."""
    pack_root = tmp_path / "pack"
    (pack_root / "strips" / "2h").mkdir(parents=True)
    (pack_root / "context" / "4h").mkdir(parents=True)

    # Data files
    (pack_root / "backbone_2h.csv").write_text("header\n", encoding="utf-8")
    (pack_root / "strips" / "2h" / "block.csv").write_text("data\n", encoding="utf-8")
    (pack_root / "context" / "4h" / "ctx.csv").write_text("data\n", encoding="utf-8")

    # Non-data files
    (pack_root / "meta.json").write_text("{}\n", encoding="utf-8")
    (pack_root / "qc_report.json").write_text("{}\n", encoding="utf-8")

    data_manifest = builder.build_manifest(pack_root, data_only=True)
    build_manifest = builder.build_manifest(pack_root, data_only=False)

    data_paths = {f["relative_path"] for f in data_manifest["files"]}
    build_paths = {f["relative_path"] for f in build_manifest["files"]}

    # Data manifest should only have 3 files
    assert data_paths == {"backbone_2h.csv", "strips/2h/block.csv", "context/4h/ctx.csv"}

    # Build manifest should have all 5 files
    assert build_paths == {
        "backbone_2h.csv",
        "strips/2h/block.csv",
        "context/4h/ctx.csv",
        "meta.json",
        "qc_report.json",
    }
