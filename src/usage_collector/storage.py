from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path
from typing import Any

from usage_collector.models import FIELD_ORDER, NormalizedUsageRecord

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS usage_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    provider    TEXT NOT NULL,
    source_identifier TEXT NOT NULL,
    event_id    TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    model       TEXT,
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    cost        REAL,
    quota       TEXT,
    source_reliability TEXT NOT NULL DEFAULT 'unknown',
    source_provenance   TEXT,
    UNIQUE(provider, event_id)
);

CREATE TABLE IF NOT EXISTS provider_cursors (
    provider    TEXT PRIMARY KEY,
    cursor_value TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aggregate_snapshots (
    provider          TEXT NOT NULL,
    snapshot_at       TEXT NOT NULL,
    total_tokens_input   INTEGER,
    total_tokens_output  INTEGER,
    total_cost        REAL,
    record_count      INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (provider, snapshot_at)
);
"""


class UsageRepository:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def insert_record(self, record: NormalizedUsageRecord) -> bool:
        row = record.to_row()
        columns = ", ".join(row)
        placeholders = ", ".join("?" for _ in row)
        values = tuple(row.values())
        sql = f"INSERT OR IGNORE INTO usage_records ({columns}) VALUES ({placeholders})"
        cursor = self._conn.execute(sql, values)
        self._conn.commit()
        return cursor.rowcount > 0

    def insert_records(self, records: list[NormalizedUsageRecord]) -> int:
        count = 0
        for record in records:
            if self.insert_record(record):
                count += 1
        return count

    def get_cursor(self, provider: str) -> str | None:
        cursor = self._conn.execute(
            "SELECT cursor_value FROM provider_cursors WHERE provider = ?",
            (provider,),
        )
        row = cursor.fetchone()
        return str(row["cursor_value"]) if row else None

    def set_cursor(self, provider: str, cursor_value: str) -> None:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO provider_cursors (provider, cursor_value, updated_at) VALUES (?, ?, ?)",
            (provider, cursor_value, now),
        )
        self._conn.commit()

    def _compute_aggregate(self, provider: str) -> dict[str, Any]:
        cursor = self._conn.execute(
            "SELECT COUNT(*) as count, "
            "SUM(tokens_input) as sum_input, "
            "SUM(tokens_output) as sum_output, "
            "SUM(cost) as sum_cost "
            "FROM usage_records WHERE provider = ?",
            (provider,),
        )
        row = cursor.fetchone()
        return {
            "provider": provider,
            "record_count": row["count"],
            "total_tokens_input": row["sum_input"],
            "total_tokens_output": row["sum_output"],
            "total_cost": row["sum_cost"],
        }

    def get_aggregate(self, provider: str) -> dict[str, Any]:
        return self._compute_aggregate(provider)

    def get_all_aggregates(self) -> list[dict[str, Any]]:
        cursor = self._conn.execute("SELECT DISTINCT provider FROM usage_records")
        providers = [row["provider"] for row in cursor.fetchall()]
        return [self._compute_aggregate(p) for p in providers]

    def write_aggregate_snapshot(self, provider: str) -> dict[str, Any]:
        agg = self._compute_aggregate(provider)
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO aggregate_snapshots "
            "(provider, snapshot_at, total_tokens_input, total_tokens_output, total_cost, record_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                provider,
                now,
                agg["total_tokens_input"],
                agg["total_tokens_output"],
                agg["total_cost"],
                agg["record_count"],
            ),
        )
        self._conn.commit()
        return agg

    def get_records_by_provider(self, provider: str) -> list[NormalizedUsageRecord]:
        cursor = self._conn.execute(
            "SELECT * FROM usage_records WHERE provider = ? ORDER BY occurred_at",
            (provider,),
        )
        return [NormalizedUsageRecord.from_row(dict(row)) for row in cursor.fetchall()]

    def get_record_count(self, provider: str) -> int:
        cursor = self._conn.execute(
            "SELECT COUNT(*) as count FROM usage_records WHERE provider = ?",
            (provider,),
        )
        return cursor.fetchone()["count"]

    def close(self) -> None:
        self._conn.close()
