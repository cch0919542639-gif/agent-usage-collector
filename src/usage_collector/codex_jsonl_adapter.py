from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from usage_collector.models import NormalizedUsageRecord

METADATA_RECORD_TYPES = frozenset({"session_meta", "session", "meta"})

FORBIDDEN_CONTENT_KEYS: frozenset[str] = frozenset({
    "content", "prompt", "response", "instruction", "feedback",
    "message", "messages", "choices",
    "raw_prompt", "raw_response",
    "api_key",
    "credential", "credentials", "cookie", "cookies", "account",
    "project-path", "project_path", "source-code", "source_code",
})

ACCEPTED_PAYLOAD_KEYS: frozenset[str] = frozenset({
    "session_id", "id", "model_provider", "model",
})


def _has_forbidden_keys(line_data: dict[str, Any]) -> bool:
    return _has_forbidden_keys_deep(line_data)


def _has_forbidden_keys_deep(value: Any, seen: set[int] | None = None) -> bool:
    if seen is None:
        seen = set()
    obj_id = id(value)
    if obj_id in seen:
        return False
    seen.add(obj_id)

    if isinstance(value, dict):
        if FORBIDDEN_CONTENT_KEYS & set(value.keys()):
            return True
        for v in value.values():
            if _has_forbidden_keys_deep(v, seen):
                return True
    elif isinstance(value, list):
        for item in value:
            if _has_forbidden_keys_deep(item, seen):
                return True
    return False


def _extract_event_id(payload: dict[str, Any]) -> str:
    for key in ("id", "session_id"):
        val = payload.get(key)
        if val is not None:
            return str(val)
    return ""


def _extract_model(payload: dict[str, Any]) -> str | None:
    val = payload.get("model_provider") or payload.get("model")
    return str(val) if val is not None else None


def parse_codex_jsonl(
    text: str,
    cursor: str | None = None,
    source_label: str = "codex-session",
) -> tuple[list[NormalizedUsageRecord], str]:
    records: list[NormalizedUsageRecord] = []

    start_offset = int(cursor) if cursor else 0
    if start_offset < 0:
        start_offset = 0

    body = text.encode("utf-8")
    if start_offset > len(body):
        return [], str(len(body))

    body = body[start_offset:]
    text_at_offset = body.decode("utf-8")
    current_offset = start_offset

    for line in text_at_offset.splitlines(keepends=True):
        raw_line = line.rstrip("\n\r")
        line_bytes = len(line.encode("utf-8"))

        if not raw_line:
            current_offset += line_bytes
            continue

        try:
            obj = json.loads(raw_line)
        except json.JSONDecodeError:
            current_offset += line_bytes
            continue

        if not isinstance(obj, dict):
            current_offset += line_bytes
            continue

        if _has_forbidden_keys(obj):
            current_offset += line_bytes
            continue

        timestamp = obj.get("timestamp", "")
        payload = obj.get("payload")
        if not isinstance(payload, dict):
            current_offset += line_bytes
            continue

        event_id = _extract_event_id(payload)
        if not event_id:
            current_offset += line_bytes
            continue

        record = NormalizedUsageRecord(
            provider="codex",
            source_identifier=source_label,
            event_id=event_id,
            occurred_at=str(timestamp) if timestamp else "",
            captured_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            source_reliability="estimated",
            model=_extract_model(payload),
            source_provenance=source_label,
        )
        records.append(record)
        current_offset += line_bytes

    return records, str(current_offset)


def parse_codex_jsonl_file(
    path: str | Path,
    cursor: str | None = None,
    source_label: str | None = None,
) -> tuple[list[NormalizedUsageRecord], str]:
    path_obj = Path(path)
    label = source_label if source_label else path_obj.name
    text = path_obj.read_text(encoding="utf-8")
    return parse_codex_jsonl(text, cursor=cursor, source_label=label)
