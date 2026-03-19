#!/usr/bin/env python3
"""
Migration script: Convert naive timestamp columns to timezone-aware (UTC).

This converts the `timestamp` columns in `messages` and `media` tables
from `TIMESTAMP` (naive) to `TIMESTAMPTZ` (timezone-aware), treating
existing values as UTC.

Usage:
    # Dry run (show what would be done):
    python scripts/migrate_timestamps_to_utc.py --dry-run

    # Actually run the migration:
    python scripts/migrate_timestamps_to_utc.py

    # With custom database URL (set DATABASE_URL env var):
    DATABASE_URL="postgresql://..." python scripts/migrate_timestamps_to_utc.py
"""

import argparse
import os
import sys

import psycopg2

# Only these tables are migrated — not user input
TABLES_TO_MIGRATE = ("messages", "media")


def get_database_url():
    """Get database URL from environment or .env file."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    # Try loading from .env in project root
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Default for docker-compose setup
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://historian:historian@db:5432/matrix_historian",
    )  # pragma: allowlist secret


def _count_rows(cur, table):
    """Count rows in a known-safe table name."""
    # table comes from TABLES_TO_MIGRATE constant, not user input
    cur.execute(f"SELECT COUNT(*) FROM {table}")  # nosec B608
    return cur.fetchone()[0]


def _alter_column(cur, table):
    """Alter timestamp column to TIMESTAMPTZ for a known-safe table."""
    # table comes from TABLES_TO_MIGRATE constant, not user input
    cur.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN "timestamp"
        TYPE TIMESTAMPTZ
        USING "timestamp" AT TIME ZONE 'UTC'
        """)  # nosec B608


def migrate(dry_run=False):
    url = get_database_url()
    print(f"Connecting to: {url.split('@')[-1]}")  # hide credentials

    conn = psycopg2.connect(url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        for table in TABLES_TO_MIGRATE:
            # Check current column type
            cur.execute(
                """
                SELECT data_type FROM information_schema.columns
                WHERE table_name = %s AND column_name = 'timestamp'
            """,
                (table,),
            )
            row = cur.fetchone()

            if not row:
                print(f"  [{table}] No 'timestamp' column found, skipping.")
                continue

            current_type = row[0]
            print(f"  [{table}] Current type: {current_type}")

            if current_type == "timestamp with time zone":
                print(f"  [{table}] Already TIMESTAMPTZ, skipping.")
                continue

            count = _count_rows(cur, table)
            print(f"  [{table}] {count} rows to migrate")

            if dry_run:
                print(f"  [{table}] DRY RUN — would ALTER COLUMN " f"to TIMESTAMPTZ")
            else:
                print(
                    f"  [{table}] Running: ALTER COLUMN timestamp "
                    f"TYPE TIMESTAMPTZ..."
                )
                _alter_column(cur, table)
                print(f"  [{table}] Done! {count} rows migrated.")

        if dry_run:
            print("\nDry run complete. No changes made.")
            conn.rollback()
        else:
            conn.commit()
            print("\nMigration complete! " "All timestamps are now TIMESTAMPTZ (UTC).")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate timestamps to UTC (TIMESTAMPTZ)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    migrate(dry_run=args.dry_run)
