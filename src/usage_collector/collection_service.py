"""Bounded, explicit-input collection for the approved Codex JSONL adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from usage_collector.codex_jsonl_adapter import parse_codex_jsonl_file
from usage_collector.storage import UsageRepository


CODEX_PROVIDER = "codex"
DEFAULT_SOURCE_LABEL = "codex-fixture"


@dataclass(frozen=True)
class CollectionResult:
    """Safe summary of one on-demand collection attempt."""

    inserted: int
    skipped: int
    cursor: str | None
    health: str


def collect_codex_fixture(
    fixture_path: str | Path,
    repository: UsageRepository,
    *,
    source_label: str = DEFAULT_SOURCE_LABEL,
) -> CollectionResult:
    """Parse one caller-supplied fixture and persist its accepted records.

    This function neither discovers files nor schedules itself.  It intentionally
    returns a generic health state for unreadable input so a local path is never
    surfaced through a report or exception message.
    """
    cursor = repository.get_cursor(CODEX_PROVIDER)
    try:
        records, next_cursor = parse_codex_jsonl_file(
            fixture_path,
            cursor=cursor,
            source_label=source_label,
        )
    except (OSError, UnicodeError):
        return CollectionResult(inserted=0, skipped=0, cursor=cursor, health="source_unavailable")

    inserted = repository.insert_records(records)
    repository.set_cursor(CODEX_PROVIDER, next_cursor)
    return CollectionResult(
        inserted=inserted,
        skipped=len(records) - inserted,
        cursor=next_cursor,
        health="unchanged" if not records else "ok",
    )
