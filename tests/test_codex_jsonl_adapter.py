from __future__ import annotations

import json
from pathlib import Path

from usage_collector.codex_jsonl_adapter import (
    FORBIDDEN_CONTENT_KEYS,
    parse_codex_jsonl,
    parse_codex_jsonl_file,
)

# ─── Synthetic fixture helpers ───────────────────────────────────────


def _meta_line(
    event_id: str = "evt-001",
    timestamp: str = "2026-07-19T10:00:00",
    model_provider: str | None = "openai",
    **extra_payload,
) -> str:
    payload = {"id": event_id}
    if model_provider:
        payload["model_provider"] = model_provider
    payload.update(extra_payload)
    obj = {"timestamp": timestamp, "type": "session_meta", "payload": payload}
    return json.dumps(obj)


def _content_line() -> str:
    return json.dumps({
        "timestamp": "2026-07-19T10:01:00",
        "type": "completion",
        "payload": {"id": "evt-content", "content": "this is a prompt"},
    })


def _mixed_line() -> str:
    return json.dumps({
        "timestamp": "2026-07-19T10:02:00",
        "type": "message",
        "payload": {"id": "evt-mixed", "model_provider": "anthropic", "content": "hidden"},
    })


def _malformed_line() -> str:
    return '{"timestamp": "2026-07-19T10:03:00", "type": "session_meta", "payload": {"id": "evt-bad-json"'


def _no_event_id_line() -> str:
    return json.dumps({
        "timestamp": "2026-07-19T10:04:00",
        "type": "session_meta",
        "payload": {"session_id": None, "id": None},
    })


FIXTURE_TEXT = "\n".join([
    _meta_line("evt-001", model_provider="openai"),
    _content_line(),
    _meta_line("evt-002", model_provider="anthropic"),
    _mixed_line(),
    _meta_line("evt-003", model_provider=None),
    _malformed_line(),
    _meta_line("evt-004", model_provider="google"),
    _no_event_id_line(),
    _meta_line("evt-005", model_provider="openai", estimated_bytes=1024),
    "",
    _meta_line("evt-006", model_provider="mistral"),
])


# ─── Tests ───────────────────────────────────────────────────────────


class TestParseCodexJsonl:
    def test_parses_valid_metadata_records(self) -> None:
        records, cursor = parse_codex_jsonl(FIXTURE_TEXT)
        assert len(records) >= 4
        for r in records:
            assert r.provider == "codex"

    def test_ignores_content_bearing_records(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        event_ids = {r.event_id for r in records}
        assert "evt-content" not in event_ids
        assert "evt-mixed" not in event_ids

    def test_ignores_malformed_json_lines(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        assert "evt-bad-json" not in {r.event_id for r in records}

    def test_skips_lines_without_event_id(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        assert None not in {r.event_id for r in records}

    def test_tokens_cost_quota_are_none(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        for r in records:
            assert r.tokens_input is None
            assert r.tokens_output is None
            assert r.cost is None
            assert r.quota is None

    def test_source_reliability_is_estimated(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        for r in records:
            assert r.source_reliability == "estimated"

    def test_model_extracted_when_present(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT, source_label="test-session")
        record_map = {r.event_id: r for r in records}
        assert record_map["evt-001"].model == "openai"
        assert record_map["evt-002"].model == "anthropic"
        assert record_map["evt-004"].model == "google"

    def test_model_is_none_when_absent(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        record_map = {r.event_id: r for r in records}
        assert record_map["evt-003"].model is None

    def test_source_identifier_matches_label(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT, source_label="my-session-label")
        for r in records:
            assert r.source_identifier == "my-session-label"

    def test_occurred_at_preserved(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT)
        record_map = {r.event_id: r for r in records}
        assert record_map["evt-001"].occurred_at == "2026-07-19T10:00:00"

    def test_empty_text_returns_empty(self) -> None:
        records, cursor = parse_codex_jsonl("")
        assert records == []
        assert cursor == "0"

    def test_only_forbidden_lines_returns_empty(self) -> None:
        text = "\n".join([_content_line(), _mixed_line(), json.dumps({"payload": {"content": "bad"}})])
        records, cursor = parse_codex_jsonl(text)
        assert records == []
        assert int(cursor) > 0


class TestCursorBehavior:
    def test_cursor_from_start_returns_same_as_no_cursor(self) -> None:
        records1, _ = parse_codex_jsonl(FIXTURE_TEXT)
        records2, _ = parse_codex_jsonl(FIXTURE_TEXT, cursor="0")
        assert len(records1) == len(records2)

    def test_cursor_resume_returns_remaining(self) -> None:
        _, cursor = parse_codex_jsonl(FIXTURE_TEXT, cursor="0")
        records_resume, _ = parse_codex_jsonl(FIXTURE_TEXT, cursor=cursor)
        assert len(records_resume) == 0

    def test_cursor_midway_returns_partial(self) -> None:
        _, cursor = parse_codex_jsonl(FIXTURE_TEXT)
        mid = int(cursor) // 2
        records_first, _ = parse_codex_jsonl(FIXTURE_TEXT, cursor="0")
        records_second, cursor2 = parse_codex_jsonl(FIXTURE_TEXT, cursor=str(mid))
        assert len(records_first) > len(records_second) or len(records_second) >= 0

    def test_cursor_returns_deterministic_string(self) -> None:
        _, cursor1 = parse_codex_jsonl(FIXTURE_TEXT)
        _, cursor2 = parse_codex_jsonl(FIXTURE_TEXT)
        assert cursor1 == cursor2

    def test_negative_cursor_treated_as_zero(self) -> None:
        records, _ = parse_codex_jsonl(FIXTURE_TEXT, cursor="-1")
        assert len(records) > 0

    def test_cursor_past_end_returns_empty(self) -> None:
        records, cursor = parse_codex_jsonl(FIXTURE_TEXT, cursor="999999999")
        assert records == []
        assert int(cursor) == len(FIXTURE_TEXT.encode("utf-8"))


class TestDedupeIdentity:
    def test_same_event_id_both_emitted(self) -> None:
        line1 = _meta_line("dedupe-1", model_provider="openai")
        line2 = _meta_line("dedupe-1", model_provider="anthropic")
        text = f"{line1}\n{line2}"
        records, _ = parse_codex_jsonl(text)
        assert len(records) == 2
        assert records[0].dedupe_key == records[1].dedupe_key

    def test_different_event_ids_both_kept(self) -> None:
        line1 = _meta_line("evt-a")
        line2 = _meta_line("evt-b")
        text = f"{line1}\n{line2}"
        records, _ = parse_codex_jsonl(text)
        assert len(records) == 2


class TestForbiddenKeys:
    def test_every_forbidden_key_is_checked(self) -> None:
        for key in FORBIDDEN_CONTENT_KEYS:
            line = json.dumps({
                "timestamp": "2026-07-19T10:00:00",
                "type": "session_meta",
                "payload": {"id": f"evt-{key}", key: "value"},
            })
            records, _ = parse_codex_jsonl(line)
            assert len(records) == 0, f"Key '{key}' was not filtered"

    def test_forbidden_at_top_level_rejected(self) -> None:
        for key in list(FORBIDDEN_CONTENT_KEYS)[:3]:
            line = json.dumps({
                "timestamp": "2026-07-19T10:00:00",
                "type": "session_meta",
                "prompt": "should be ignored",
                "payload": {"id": f"evt-top-{key}"},
            })
            records, _ = parse_codex_jsonl(line)
            assert len(records) == 0

    def test_unknown_non_forbidden_keys_allowed(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "type": "session_meta",
            "unknown_field": "some_value",
            "payload": {"id": "evt-unknown-ok", "model_provider": "openai"},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 1


class TestNestedForbiddenKeys:
    def test_payload_metadata_message_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "type": "session_meta",
            "payload": {"id": "evt-nested-msg", "metadata": {"message": "hidden"}},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_payload_metadata_content_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {"id": "evt-nested-content", "metadata": {"content": "hidden"}},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_payload_metadata_prompt_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {"id": "evt-nested-prompt", "meta": {"nested": {"prompt": "secret"}}},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_payload_list_contains_forbidden_dict_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {"id": "evt-list-content", "messages": [{"content": "hello"}]},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_nested_list_of_objects_with_prompt_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {
                "id": "evt-deep-list",
                "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
            },
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_top_level_deeply_nested_source_code_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "metadata": {"nested": {"source_code": "def foo(): pass"}},
            "payload": {"id": "evt-top-deep"},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_three_levels_deep_feedback_ignored(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {"id": "evt-deep3", "a": {"b": {"feedback": "bad"}}},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 0

    def test_safe_nested_field_preserved(self) -> None:
        line = json.dumps({
            "timestamp": "2026-07-19T10:00:00",
            "payload": {"id": "evt-safe", "metadata": {"model_provider": "gpt-4"}},
        })
        records, _ = parse_codex_jsonl(line)
        assert len(records) == 1


class TestFileBasedParsing:
    def test_parse_file(self, tmp_path: Path) -> None:
        fp = tmp_path / "fixture.jsonl"
        fp.write_text(FIXTURE_TEXT, encoding="utf-8")
        records, cursor = parse_codex_jsonl_file(str(fp))
        assert len(records) >= 4
        assert int(cursor) > 0

    def test_parse_file_default_label_is_filename(self, tmp_path: Path) -> None:
        fp = tmp_path / "my-session.jsonl"
        fp.write_text(_meta_line(), encoding="utf-8")
        records, _ = parse_codex_jsonl_file(str(fp))
        for r in records:
            assert r.source_identifier == "my-session.jsonl"

    def test_parse_file_with_custom_label(self, tmp_path: Path) -> None:
        fp = tmp_path / "session.jsonl"
        fp.write_text(_meta_line(), encoding="utf-8")
        records, _ = parse_codex_jsonl_file(str(fp), source_label="custom-label")
        for r in records:
            assert r.source_identifier == "custom-label"

    def test_parse_file_with_cursor(self, tmp_path: Path) -> None:
        fp = tmp_path / "fixture.jsonl"
        fp.write_text(FIXTURE_TEXT, encoding="utf-8")
        _, cursor = parse_codex_jsonl_file(str(fp))
        records2, _ = parse_codex_jsonl_file(str(fp), cursor=cursor)
        assert len(records2) == 0

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        fp = tmp_path / "nonexistent.jsonl"
        import pytest
        with pytest.raises(FileNotFoundError):
            parse_codex_jsonl_file(str(fp))
