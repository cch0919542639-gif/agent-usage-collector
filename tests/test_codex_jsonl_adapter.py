"""Tests for the Codex JSONL fixture adapter.

All tests use synthetic fixture data only. No real provider files are inspected.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from usage_collector.codex_jsonl_adapter import (
    ParseResult,
    parse_fixture_file,
    parse_fixture_text,
)
from usage_collector.models import NormalizedUsageRecord

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ─── 1. Valid metadata parsing ────────────────────────────────────────


class TestValidMetadata:
    def test_parse_valid_fixture_text(self) -> None:
        text = (
            '{"timestamp": "2026-07-19T10:00:00Z", "type": "session_meta", '
            '"payload": {"session_id": "sess-001", "id": "evt-001", '
            '"model_provider": "gpt-4o"}}'
        )
        result = parse_fixture_text(text)
        assert len(result.records) == 1
        record = result.records[0]
        assert record.provider == "codex"
        assert record.event_id == "evt-001"
        assert record.model == "gpt-4o"
        assert record.occurred_at == "2026-07-19T10:00:00Z"
        assert record.tokens_input is None
        assert record.tokens_output is None
        assert record.cost is None
        assert record.quota is None

    def test_parse_valid_fixture_file(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        assert len(result.records) == 3
        event_ids = {r.event_id for r in result.records}
        assert event_ids == {"evt-001", "evt-002", "evt-003"}

    def test_all_records_have_codex_provider(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        for record in result.records:
            assert record.provider == "codex"

    def test_model_extracted_when_present(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        models = {r.event_id: r.model for r in result.records}
        assert models["evt-001"] == "gpt-4o"
        assert models["evt-002"] == "gpt-4o-mini"
        assert models["evt-003"] is None


# ─── 2. Ignored unsafe content ────────────────────────────────────────


class TestIgnoredUnsafeContent:
    def test_content_bearing_lines_ignored(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "content_bearing.jsonl")
        assert len(result.records) == 0
        assert result.lines_ignored == 3

    def test_prompt_field_causes_ignore(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "prompt": "secret"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_response_field_causes_ignore(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "response": "secret"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_content_field_causes_ignore(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "content": "secret"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_api_key_field_causes_ignore(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "api_key": "sk-xxx"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_cookie_field_causes_ignore(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "cookie": "session=abc"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_nested_payload_content_ignored(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001", "prompt": "secret"}}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_forbidden_keys_not_in_output(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        assert len(result.records) == 1
        record = result.records[0]
        row = record.to_row()
        forbidden = {"raw_prompt", "raw_response", "prompt", "response",
                     "instruction", "feedback", "content", "message",
                     "messages", "text", "api_key", "cookie", "cookies",
                     "account", "project_path", "source_code", "code",
                     "credentials"}
        assert not (set(row.keys()) & forbidden)


# ─── 3. Malformed input ──────────────────────────────────────────────


class TestMalformedInput:
    def test_invalid_json_ignored(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "malformed_input.jsonl")
        # Only 2 valid JSON lines out of 3
        assert len(result.records) == 2
        assert result.lines_ignored == 1

    def test_empty_text_returns_empty(self) -> None:
        result = parse_fixture_text("")
        assert len(result.records) == 0
        assert result.lines_processed == 0

    def test_whitespace_only_text_returns_empty(self) -> None:
        result = parse_fixture_text("   \n  \n  ")
        assert len(result.records) == 0

    def test_non_dict_json_ignored(self) -> None:
        text = '"just a string"\n123\ntrue\nnull'
        result = parse_fixture_text(text)
        assert len(result.records) == 0
        assert result.lines_ignored == 4

    def test_array_json_ignored(self) -> None:
        text = '[1, 2, 3]'
        result = parse_fixture_text(text)
        assert len(result.records) == 0


# ─── 4. Unknown values ───────────────────────────────────────────────


class TestUnknownValues:
    def test_missing_timestamp_ignored(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "unknown_values.jsonl")
        # Only lines with valid timestamps and event_ids are parsed
        # Line 1: no timestamp → ignored
        # Line 2: has timestamp but no event_id in payload → ignored
        # Line 3: has timestamp but no payload → ignored
        assert len(result.records) == 0
        assert result.lines_ignored == 3

    def test_missing_event_id_ignored(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "type": "session_meta"}'
        result = parse_fixture_text(text)
        assert len(result.records) == 0

    def test_none_model_preserved(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        assert len(result.records) == 1
        assert result.records[0].model is None

    def test_tokens_always_none(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        record = result.records[0]
        assert record.tokens_input is None
        assert record.tokens_output is None
        assert record.cost is None
        assert record.quota is None


# ─── 5. Deterministic dedupe identity ─────────────────────────────────


class TestDeterministicDedupeIdentity:
    def test_same_event_id_same_provider_dedupes(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "dedupe_identity.jsonl")
        assert len(result.records) == 3
        # All have the same event_id, so dedupe_key is identical
        keys = [r.dedupe_key for r in result.records]
        assert all(k == ("codex", "evt-001") for k in keys)

    def test_dedupe_key_is_tuple(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        key = result.records[0].dedupe_key
        assert isinstance(key, tuple)
        assert key == ("codex", "evt-001")

    def test_different_event_ids_different_keys(self) -> None:
        text = (
            '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}\n'
            '{"timestamp": "2026-07-19T10:01:00Z", "payload": {"id": "evt-002"}}'
        )
        result = parse_fixture_text(text)
        keys = [r.dedupe_key for r in result.records]
        assert keys[0] != keys[1]


# ─── 6. Cursor behavior ──────────────────────────────────────────────


class TestCursorBehavior:
    def test_cursor_always_present(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "cursor_lines.jsonl")
        assert result.next_cursor is not None
        assert result.next_cursor.startswith("cursor:")

    def test_cursor_is_deterministic(self) -> None:
        r1 = parse_fixture_file(FIXTURES_DIR / "cursor_lines.jsonl")
        r2 = parse_fixture_file(FIXTURES_DIR / "cursor_lines.jsonl")
        assert r1.next_cursor == r2.next_cursor

    def test_cursor_changes_with_different_input(self) -> None:
        r1 = parse_fixture_file(FIXTURES_DIR / "cursor_lines.jsonl")
        r2 = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        # Different line counts → different cursors
        assert r1.next_cursor != r2.next_cursor

    def test_cursor_changes_with_ignored_lines(self) -> None:
        text_valid = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        text_with_ignore = (
            '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}\n'
            '{"prompt": "ignored"}'
        )
        r1 = parse_fixture_text(text_valid)
        r2 = parse_fixture_text(text_with_ignore)
        assert r1.next_cursor != r2.next_cursor

    def test_empty_text_cursor(self) -> None:
        result = parse_fixture_text("")
        assert result.next_cursor is not None
        assert result.next_cursor.startswith("cursor:")

    def test_line_counts_accurate(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "cursor_lines.jsonl")
        assert result.lines_processed == 3
        assert result.lines_ignored == 0

    def test_line_counts_with_ignores(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "malformed_input.jsonl")
        assert result.lines_processed == 3
        assert result.lines_ignored == 1


# ─── 7. Source label sanitization ─────────────────────────────────────


class TestSourceLabelSanitization:
    def test_default_source_label_is_logical(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        assert result.records[0].source_identifier == "synthetic-codex-fixture"

    def test_custom_source_label_used(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text, source_label="my-test-fixture")
        assert result.records[0].source_identifier == "my-test-fixture"

    def test_file_stem_used_as_label(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        assert result.records[0].source_identifier == "valid_metadata"


# ─── 8. ParseResult structure ─────────────────────────────────────────


class TestParseResultStructure:
    def test_parse_result_has_required_fields(self) -> None:
        result = parse_fixture_text('{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}')
        assert hasattr(result, "records")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "lines_processed")
        assert hasattr(result, "lines_ignored")

    def test_records_are_normalized_usage_records(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        for record in result.records:
            assert isinstance(record, NormalizedUsageRecord)

    def test_to_row_produces_valid_dict(self) -> None:
        result = parse_fixture_file(FIXTURES_DIR / "valid_metadata.jsonl")
        for record in result.records:
            row = record.to_row()
            assert isinstance(row, dict)
            assert "provider" in row
            assert "event_id" in row
            assert "occurred_at" in row
            assert "captured_at" in row


# ─── 9. Epoch timestamp conversion ────────────────────────────────────


class TestEpochTimestampConversion:
    def test_epoch_seconds_converted_to_iso(self) -> None:
        text = '{"ts": 1721376000, "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        assert len(result.records) == 1
        assert "2024-07-19" in result.records[0].occurred_at

    def test_string_timestamp_preserved(self) -> None:
        text = '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}'
        result = parse_fixture_text(text)
        assert result.records[0].occurred_at == "2026-07-19T10:00:00Z"
