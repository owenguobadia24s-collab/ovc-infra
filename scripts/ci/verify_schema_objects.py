#!/usr/bin/env python3
"""
CI Schema Object Verification

Verifies that required database objects exist in the Neon database.
This is a gate check to ensure the DB schema matches repository expectations.

Exit codes:
  0 - All required objects exist
  1 - One or more required objects missing
  2 - Database connection failed
"""

import os
import sys

# Required objects that MUST exist for the pipeline to function
REQUIRED_OBJECTS = [
    # Canonical tables
    ("table", "ovc", "ovc_blocks_v01_1_min"),
    ("table", "ovc", "ovc_candles_m15_raw"),

    # Configuration tables
    ("table", "ovc_cfg", "threshold_pack"),
    ("table", "ovc_cfg", "threshold_pack_active"),

    # Derived feature views
    ("view", "derived", "v_ovc_l1_features_v0_1"),
    ("view", "derived", "v_ovc_l2_features_v0_1"),
    ("view", "derived", "v_ovc_l3_features_v0_1"),

    # Option C outcomes view (authoritative)
    ("view", "derived", "v_ovc_c_outcomes_v0_1"),

    # Path1 evidence view
    ("view", "derived", "v_path1_evidence_dis_v1_1"),
]


def get_dsn() -> str:
    """Get database connection string from environment."""
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not dsn:
        print("ERROR: DATABASE_URL or NEON_DSN environment variable required")
        sys.exit(2)
    return dsn


def check_object_exists(cursor, obj_type: str, schema: str, name: str) -> bool:
    """Check if a database object exists."""
    if obj_type == "table":
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            )
        """
    elif obj_type == "view":
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views
                WHERE table_schema = %s AND table_name = %s
            )
        """
    else:
        print(f"WARNING: Unknown object type: {obj_type}")
        return False

    cursor.execute(query, (schema, name))
    result = cursor.fetchone()
    return result[0] if result else False


def main():
    """Main entry point."""
    print("=== CI Schema Object Verification ===")
    print()

    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(2)

    dsn = get_dsn()

    try:
        conn = psycopg2.connect(dsn)
        cursor = conn.cursor()
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        sys.exit(2)

    print(f"Checking {len(REQUIRED_OBJECTS)} required objects...")
    print()

    missing = []
    found = []

    for obj_type, schema, name in REQUIRED_OBJECTS:
        full_name = f"{schema}.{name}"
        exists = check_object_exists(cursor, obj_type, schema, name)

        if exists:
            print(f"  OK    {obj_type:6} {full_name}")
            found.append(full_name)
        else:
            print(f"  MISS  {obj_type:6} {full_name}")
            missing.append(full_name)

    print()
    print(f"Found: {len(found)}/{len(REQUIRED_OBJECTS)}")
    print(f"Missing: {len(missing)}")

    cursor.close()
    conn.close()

    if missing:
        print()
        print("FAILED: The following required objects are missing:")
        for obj in missing:
            print(f"  - {obj}")
        print()
        print("Please ensure all SQL migrations have been applied.")
        sys.exit(1)

    print()
    print("PASSED: All required schema objects exist.")
    sys.exit(0)


if __name__ == "__main__":
    main()
