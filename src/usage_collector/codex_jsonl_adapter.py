"""Fixture-backed Codex JSONL metadata adapter.

This adapter parses synthetic Codex JSONL session metadata and emits
NormalizedUsageRecord values using only the accepted inventory fields.

Privacy boundaries:
- Only synthetic fixture data is accepted; real provider files are never inspected.
- Content-bearing fields (raw_prompt, raw_response, instruction, feedback,
  credential, cookie, account, project-path, source-code) are ignored.
- Token, cost, and quota are always None; activity bytes are never converted
  to token estimates.
- Source identifiers are sanitized by the persistence boundary.

The adapter is a bounded parsing component, not a live collector, directory
scanner, or scheduler.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from usage_collector.models import NormalizedUsageRecord

PROVIDER_NAME = "codex"

# Keys that indicate content-bearing or forbidden data in a JSONL payload.
# Lines containing any of these are ignored.
_FORBIDDEN_PAYLOAD_KEYS = frozenset({
    "raw_prompt",
    "raw_response",
    "prompt",
    "response",
    "instruction",
    "feedback",
    "content",
    "message",
    "messages",
    "text",
    "api_key",
    "cookie",
    "cookies",
    "account",
    "project_path",
    "source_code",
    "code",
    "credentials",
})


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a fixture file or text block."""
    records: list[NormalizedUsageRecord]
    next_cursor: str | None
    lines_processed: int
    lines_ignored: int


def _extract_event_id(payload: dict[str, Any]) -> str | None:
    """Extract an opaque event identifier from a Codex payload."""
    for key in ("id", "event_id", "session_id", "log_id"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _extract_model(payload: dict[str, Any]) -> str | None:
    """Extract model-provider metadata from a Codex payload."""
    for key in ("model_provider", "model", "model_name"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _extract_timestamp(line_data: dict[str, Any]) -> str | None:
    """Extract an ISO 8601 timestamp from a Codex JSONL line."""
    for key in ("timestamp", "ts", "occurred_at", "time"):
        val = line_data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, (int, float)):
            # Treat numeric as epoch seconds; convert to ISO 8601
            try:
                import datetime as dt
                return dt.datetime.fromtimestamp(val, tz=dt.timezone.utc).isoformat()
            except (OSError, ValueError):
                continue
    return None


def _has_forbidden_keys_recursive(obj: Any) -> bool:
    """Recursively check if an object contains any forbidden content-bearing keys.

    Checks all dictionaries at any nesting depth, and all items within lists.
    A record containing nested keys such as message, content, prompt, or
    source_code must be ignored or rejected without reading, logging, or
    preserving its value.
    """
    if isinstance(obj, dict):
        # Check if any key at this level is forbidden
        if set(obj.keys()) & _FORBIDDEN_PAYLOAD_KEYS:
            return True
        # Recurse into all values
        for value in obj.values():
            if _has_forbidden_keys_recursive(value):
                return True
    elif isinstance(obj, list):
        # Recurse into all list items
        for item in obj:
            if _has_forbidden_keys_recursive(item):
                return True
    return False


def _parse_jsonl_line(
    line: str,
    source_label: str,
) -> NormalizedUsageRecord | None:
    """Parse a single JSONL line into a NormalizedUsageRecord, or None if ignored."""
    line = line.strip()
    if not line:
        return None

    try:
        line_data = json.loads(line)
    except json.JSONDecodeError:
        return None

    if not isinstance(line_data, dict):
        return None

    # Skip content-bearing or forbidden records (recursive check)
    if _has_forbidden_keys_recursive(line_data):
        return None

    # Extract required fields
    event_id = _extract_event_id(line_data)
    if not event_id:
        # Also check nested payload
        payload = line_data.get("payload")
        if isinstance(payload, dict):
            event_id = _extract_event_id(payload)
    if not event_id:
        return None

    timestamp = _extract_timestamp(line_data)
    if not timestamp:
        # Try nested payload
        payload = line_data.get("payload")
        if isinstance(payload, dict):
            timestamp = _extract_timestamp(payload)
    if not timestamp:
        return None

    # Extract optional model metadata
    model = _extract_model(line_data)
    if not model:
        payload = line_data.get("payload")
        if isinstance(payload, dict):
            model = _extract_model(payload)

    return NormalizedUsageRecord(
        provider=PROVIDER_NAME,
        source_identifier=source_label,
        event_id=event_id,
        occurred_at=timestamp,
        captured_at=timestamp,
        model=model,
        tokens_input=None,
        tokens_output=None,
        cost=None,
        quota=None,
        source_reliability="exact",
        source_provenance=None,
    )


def _deterministic_cursor(
    source_label: str,
    line_count: int,
    ignored_count: int,
) -> str:
    """Produce a deterministic opaque cursor representing the parse checkpoint."""
    import hashlib
    raw = f"{source_label}:{line_count}:{ignored_count}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"cursor:{digest[:24]}"


def parse_fixture_text(
    text: str,
    source_label: str = "synthetic-codex-fixture",
) -> ParseResult:
    """Parse a block of JSONL text into NormalizedUsageRecord values.

    Args:
        text: JSONL-formatted text with one JSON object per line.
        source_label: Logical label for the source (no absolute paths).

    Returns:
        ParseResult with parsed records, deterministic next cursor,
        and line counts.
    """
    records: list[NormalizedUsageRecord] = []
    lines_processed = 0
    lines_ignored = 0

    for line in text.splitlines():
        lines_processed += 1
        record = _parse_jsonl_line(line, source_label)
        if record is not None:
            records.append(record)
        else:
            lines_ignored += 1

    next_cursor = _deterministic_cursor(source_label, lines_processed, lines_ignored)

    return ParseResult(
        records=records,
        next_cursor=next_cursor,
        lines_processed=lines_processed,
        lines_ignored=lines_ignored,
    )


def parse_fixture_file(
    path: str | Path,
    source_label: str | None = None,
) -> ParseResult:
    """Parse a JSONL fixture file into NormalizedUsageRecord values.

    Args:
        path: Path to the JSONL fixture file.
        source_label: Logical label for the source. If None, uses the
            filename without extension (no absolute paths stored).

    Returns:
        ParseResult with parsed records, deterministic next cursor,
        and line counts.
    """
    path = Path(path)
    if source_label is None:
        source_label = path.stem

    text = path.read_text(encoding="utf-8")
    return parse_fixture_text(text, source_label=source_label)
