from __future__ import annotations

import json

from usage_collector.collection_service import collect_codex_fixture
from usage_collector.storage import UsageRepository


def _safe_line(event_id: str) -> str:
    return json.dumps({
        "timestamp": "2026-07-19T10:00:00Z",
        "type": "session_meta",
        "payload": {"id": event_id, "model_provider": "openai"},
    })


def _repository(tmp_path) -> UsageRepository:
    return UsageRepository(tmp_path / "usage.sqlite")


def test_first_collection_persists_accepted_records_and_cursor(tmp_path) -> None:
    fixture = tmp_path / "synthetic.jsonl"
    fixture.write_text(f"{_safe_line('evt-1')}\n{_safe_line('evt-2')}\n", encoding="utf-8")
    repository = _repository(tmp_path)

    result = collect_codex_fixture(fixture, repository)

    assert result.health == "ok"
    assert result.inserted == 2
    assert result.skipped == 0
    assert result.cursor == repository.get_cursor("codex")
    assert repository.get_record_count("codex") == 2
    for record in repository.get_records_by_provider("codex"):
        assert record.tokens_input is None
        assert record.tokens_output is None
        assert record.cost is None
        assert record.quota is None
    repository.close()


def test_unchanged_input_is_a_bounded_no_op(tmp_path) -> None:
    fixture = tmp_path / "synthetic.jsonl"
    fixture.write_text(f"{_safe_line('evt-1')}\n", encoding="utf-8")
    repository = _repository(tmp_path)

    first = collect_codex_fixture(fixture, repository)
    second = collect_codex_fixture(fixture, repository)

    assert first.inserted == 1
    assert second.health == "unchanged"
    assert second.inserted == 0
    assert second.skipped == 0
    assert repository.get_record_count("codex") == 1
    repository.close()


def test_duplicate_persistence_is_reported_without_duplication(tmp_path) -> None:
    fixture = tmp_path / "synthetic.jsonl"
    fixture.write_text(f"{_safe_line('evt-1')}\n{_safe_line('evt-1')}\n", encoding="utf-8")
    repository = _repository(tmp_path)

    result = collect_codex_fixture(fixture, repository)

    assert result.inserted == 1
    assert result.skipped == 1
    assert repository.get_record_count("codex") == 1
    repository.close()


def test_malformed_and_unsafe_input_is_ignored_without_persistence(tmp_path) -> None:
    fixture = tmp_path / "synthetic.jsonl"
    unsafe = json.dumps({"payload": {"id": "evt-unsafe", "content": "synthetic"}})
    fixture.write_text(f"not-json\n{unsafe}\n", encoding="utf-8")
    repository = _repository(tmp_path)

    result = collect_codex_fixture(fixture, repository)

    assert result.health == "unchanged"
    assert result.inserted == 0
    assert repository.get_record_count("codex") == 0
    repository.close()


def test_missing_source_returns_safe_health_without_path_details(tmp_path) -> None:
    repository = _repository(tmp_path)

    result = collect_codex_fixture(tmp_path / "missing.jsonl", repository)

    assert result.health == "source_unavailable"
    assert result.cursor is None
    assert result.inserted == 0
    repository.close()
