from __future__ import annotations

from pathlib import Path

import pytest

from usage_collector.models import NormalizedUsageRecord
from usage_collector.storage import UsageRepository


def _make_record(
    provider: str = "test-provider",
    event_id: str = "evt-001",
    tokens_input: int | None = 100,
    tokens_output: int | None = 50,
    cost: float | None = 0.01,
    **overrides,
) -> NormalizedUsageRecord:
    fields = dict(
        provider=provider,
        source_identifier="src/file.json",
        event_id=event_id,
        occurred_at="2026-07-16T10:00:00",
        captured_at="2026-07-16T10:05:00",
        source_reliability="exact",
        model="gpt-4",
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost=cost,
        quota=None,
        source_provenance="/home/user/.config/provider/log.json",
    )
    fields.update(overrides)
    return NormalizedUsageRecord(**fields)


@pytest.fixture
def repo(tmp_path: Path) -> UsageRepository:
    db_path = tmp_path / "test_usage.db"
    return UsageRepository(db_path)


# ─── 1. Dedupe ─────────────────────────────────────────────────────────


class TestDedupe:
    def test_insert_unique_record(self, repo: UsageRepository) -> None:
        record = _make_record()
        inserted = repo.insert_record(record)
        assert inserted is True
        assert repo.get_record_count("test-provider") == 1

    def test_insert_duplicate_skipped(self, repo: UsageRepository) -> None:
        record = _make_record()
        repo.insert_record(record)
        inserted = repo.insert_record(record)
        assert inserted is False
        assert repo.get_record_count("test-provider") == 1

    def test_same_event_id_different_data_still_deduplicated(self, repo: UsageRepository) -> None:
        r1 = _make_record(tokens_input=100)
        r2 = _make_record(tokens_input=200)
        repo.insert_record(r1)
        inserted = repo.insert_record(r2)
        assert inserted is False
        records = repo.get_records_by_provider("test-provider")
        assert len(records) == 1
        assert records[0].tokens_input == 100


# ─── 2. Provider isolation ─────────────────────────────────────────────


class TestProviderIsolation:
    def test_same_event_id_different_providers_both_stored(self, repo: UsageRepository) -> None:
        r1 = _make_record(provider="opencode", event_id="session-1")
        r2 = _make_record(provider="claude-code", event_id="session-1")
        repo.insert_record(r1)
        repo.insert_record(r2)
        assert repo.get_record_count("opencode") == 1
        assert repo.get_record_count("claude-code") == 1

    def test_provider_counts_independent(self, repo: UsageRepository) -> None:
        for i in range(3):
            repo.insert_record(_make_record(provider="prov-a", event_id=f"a-{i}"))
        for i in range(5):
            repo.insert_record(_make_record(provider="prov-b", event_id=f"b-{i}"))
        assert repo.get_record_count("prov-a") == 3
        assert repo.get_record_count("prov-b") == 5


# ─── 3. Cursor persistence ─────────────────────────────────────────────


class TestCursorPersistence:
    def test_set_and_get_cursor(self, repo: UsageRepository) -> None:
        repo.set_cursor("test-provider", "cursor-abc-123")
        assert repo.get_cursor("test-provider") == "cursor-abc-123"

    def test_nonexistent_provider_returns_none(self, repo: UsageRepository) -> None:
        assert repo.get_cursor("nonexistent") is None

    def test_cursor_overwrite(self, repo: UsageRepository) -> None:
        repo.set_cursor("test-provider", "cursor-v1")
        repo.set_cursor("test-provider", "cursor-v2")
        assert repo.get_cursor("test-provider") == "cursor-v2"

    def test_cursor_survives_close_and_reopen(self, tmp_path: Path) -> None:
        db_path = tmp_path / "cursor_test.db"
        repo1 = UsageRepository(db_path)
        repo1.set_cursor("test-provider", "persisted-cursor")
        repo1.close()

        repo2 = UsageRepository(db_path)
        assert repo2.get_cursor("test-provider") == "persisted-cursor"
        repo2.close()

    def test_multiple_provider_cursors_independent(self, repo: UsageRepository) -> None:
        repo.set_cursor("prov-a", "cursor-a")
        repo.set_cursor("prov-b", "cursor-b")
        assert repo.get_cursor("prov-a") == "cursor-a"
        assert repo.get_cursor("prov-b") == "cursor-b"


# ─── 4. Missing/unknown fields ─────────────────────────────────────────


class TestMissingFields:
    def test_tokens_none_stored(self, repo: UsageRepository) -> None:
        record = _make_record(tokens_input=None, tokens_output=None, cost=None)
        repo.insert_record(record)
        records = repo.get_records_by_provider("test-provider")
        assert len(records) == 1
        assert records[0].tokens_input is None
        assert records[0].tokens_output is None
        assert records[0].cost is None

    def test_partial_fields(self, repo: UsageRepository) -> None:
        record = _make_record(tokens_input=50, tokens_output=None, cost=None)
        repo.insert_record(record)
        records = repo.get_records_by_provider("test-provider")
        assert records[0].tokens_input == 50
        assert records[0].tokens_output is None

    def test_unknown_reliability_default(self, repo: UsageRepository) -> None:
        record = _make_record(source_reliability="unknown")
        repo.insert_record(record)
        records = repo.get_records_by_provider("test-provider")
        assert records[0].source_reliability == "unknown"


# ─── 5. No forbidden content ───────────────────────────────────────────


class TestNoForbiddenContent:
    def test_raw_prompt_not_in_schema(self) -> None:
        """Verify the model has no field for raw prompt content."""
        assert not hasattr(NormalizedUsageRecord, "raw_prompt")
        assert not hasattr(NormalizedUsageRecord, "raw_response")
        assert not hasattr(NormalizedUsageRecord, "api_key")
        assert not hasattr(NormalizedUsageRecord, "cookie")

    def test_to_row_excludes_forbidden_keys(self, repo: UsageRepository) -> None:
        record = _make_record()
        row = record.to_row()
        assert "raw_prompt" not in row
        assert "raw_response" not in row
        assert "api_key" not in row
        assert "cookie" not in row

    def test_to_row_sanitizes_absolute_source_identifier(self) -> None:
        record = _make_record(source_identifier=r"C:\Users\me\sessions\opencode.json")
        row = record.to_row()
        raw = row["source_identifier"]
        assert "C:\\Users\\me\\sessions\\opencode.json" not in raw
        assert raw.startswith("path-hash:")

    def test_to_row_sanitizes_absolute_source_provenance(self) -> None:
        record = _make_record(source_provenance="/home/user/.cache/provider/log.json")
        row = record.to_row()
        raw = row.get("source_provenance", "")
        assert "/home/user/.cache/provider/log.json" not in raw
        assert raw.startswith("path-hash:")


# ─── 6. Aggregate queries ──────────────────────────────────────────────


class TestAggregates:
    def test_empty_provider_aggregate(self, repo: UsageRepository) -> None:
        agg = repo.get_aggregate("nonexistent")
        assert agg["record_count"] == 0
        assert agg["total_tokens_input"] is None

    def test_aggregate_sums_single_record(self, repo: UsageRepository) -> None:
        repo.insert_record(_make_record(tokens_input=100, tokens_output=50, cost=0.02))
        agg = repo.get_aggregate("test-provider")
        assert agg["record_count"] == 1
        assert agg["total_tokens_input"] == 100
        assert agg["total_tokens_output"] == 50
        assert agg["total_cost"] == 0.02

    def test_aggregate_sums_multiple_records(self, repo: UsageRepository) -> None:
        for i in range(3):
            repo.insert_record(_make_record(
                event_id=f"evt-{i}",
                tokens_input=100,
                tokens_output=50,
                cost=0.01,
            ))
        agg = repo.get_aggregate("test-provider")
        assert agg["record_count"] == 3
        assert agg["total_tokens_input"] == 300
        assert agg["total_tokens_output"] == 150
        assert agg["total_cost"] == 0.03

    def test_aggregate_all_providers(self, repo: UsageRepository) -> None:
        repo.insert_record(_make_record(provider="prov-a", event_id="a-1", tokens_input=10))
        repo.insert_record(_make_record(provider="prov-b", event_id="b-1", tokens_input=20))
        repo.insert_record(_make_record(provider="prov-b", event_id="b-2", tokens_input=30))
        aggs = repo.get_all_aggregates()
        assert len(aggs) == 2
        agg_map = {a["provider"]: a for a in aggs}
        assert agg_map["prov-a"]["record_count"] == 1
        assert agg_map["prov-a"]["total_tokens_input"] == 10
        assert agg_map["prov-b"]["record_count"] == 2
        assert agg_map["prov-b"]["total_tokens_input"] == 50

    def test_aggregate_snapshot_writes_and_reads(self, repo: UsageRepository) -> None:
        repo.insert_record(_make_record(tokens_input=100, tokens_output=50, cost=0.02))
        agg = repo.write_aggregate_snapshot("test-provider")
        assert agg["record_count"] == 1
        assert agg["total_tokens_input"] == 100

    def test_aggregate_with_nulls(self, repo: UsageRepository) -> None:
        repo.insert_record(_make_record(tokens_input=None, tokens_output=None, cost=None))
        agg = repo.get_aggregate("test-provider")
        assert agg["record_count"] == 1
        assert agg["total_tokens_input"] is None
        assert agg["total_tokens_output"] is None
        assert agg["total_cost"] is None


# ─── 7. Temp directory isolation ───────────────────────────────────────


class TestTempDirectoryIsolation:
    def test_database_created_in_temp(self, tmp_path: Path) -> None:
        db_path = tmp_path / "isolated.db"
        repo = UsageRepository(db_path)
        repo.insert_record(_make_record())
        repo.close()
        assert db_path.exists()
        assert not any(Path.cwd().glob("*.sqlite3"))


# ─── 8. Path sanitization ──────────────────────────────────────────────


class TestPathSanitization:
    """Absolute and traversal paths in source_identifier and source_provenance
    must be transformed to a safe hash before persistence."""

    UNSAFE_PATHS = [
        ("windows-abs", r"C:\Users\angel\.config\provider\log.json"),
        ("windows-abs-alt", r"D:\tools\agent\session.log"),
        ("posix-abs", "/home/user/.config/provider/log.json"),
        ("posix-abs-opt", "/opt/agent/data/session-123.json"),
        ("unc", r"\\server\share\provider\logs"),
        ("unc-alt", r"\\nas\team\agent-data\session.log"),
        ("traversal-up", "../../etc/passwd"),
        ("traversal-deep", "logs/../../../secret.key"),
        ("traversal-windows", r"..\..\config\credentials.json"),
    ]

    def _assert_sanitized(self, unsafe_value: str) -> None:
        from usage_collector.models import sanitize_path_field
        result = sanitize_path_field(unsafe_value)
        assert result is not None
        assert result != unsafe_value, f"Value was not transformed: {unsafe_value}"
        assert result.startswith("path-hash:"), f"Result does not start with path-hash: {result}"
        assert "/" not in result[10:], f"Hash segment contains path separator: {result}"
        assert "\\" not in result[10:], f"Hash segment contains backslash: {result}"
        assert ".." not in result, f"Hash segment contains traversal: {result}"

    def test_all_unsafe_path_types_are_transformed(self) -> None:
        for name, path in self.UNSAFE_PATHS:
            self._assert_sanitized(path)

    def test_safe_logical_label_preserved(self) -> None:
        from usage_collector.models import sanitize_path_field
        safe_labels = [
            "opencode-session-123",
            "provider:claude-code:session-456",
            "log-2026-07-16",
            "session_abc123",
            "event-001",
        ]
        for label in safe_labels:
            assert sanitize_path_field(label) == label

    def test_none_preserved(self) -> None:
        from usage_collector.models import sanitize_path_field
        assert sanitize_path_field(None) is None

    def test_same_path_produces_same_hash(self) -> None:
        from usage_collector.models import sanitize_path_field
        path = r"C:\Users\angel\.config\provider\log.json"
        h1 = sanitize_path_field(path)
        h2 = sanitize_path_field(path)
        assert h1 == h2

    def test_different_paths_produce_different_hashes(self) -> None:
        from usage_collector.models import sanitize_path_field
        h1 = sanitize_path_field(r"C:\path\one.log")
        h2 = sanitize_path_field(r"D:\path\two.log")
        assert h1 != h2

    def test_windows_abs_in_source_identifier_not_stored_raw(self, repo: UsageRepository) -> None:
        record = _make_record(source_identifier=r"C:\Users\me\session.log")
        repo.insert_record(record)
        stored = repo.get_records_by_provider("test-provider")
        assert len(stored) == 1
        assert "C:\\Users\\me\\session.log" not in stored[0].source_identifier
        assert stored[0].source_identifier.startswith("path-hash:")

    def test_posix_abs_in_source_provenance_not_stored_raw(self, repo: UsageRepository) -> None:
        record = _make_record(source_provenance="/home/user/.local/share/agent/data.json")
        repo.insert_record(record)
        stored = repo.get_records_by_provider("test-provider")
        assert len(stored) == 1
        assert "/home/user/.local/share/agent/data.json" not in str(stored[0].source_provenance)
        if stored[0].source_provenance:
            assert stored[0].source_provenance.startswith("path-hash:")

    def test_unc_path_not_stored_raw(self, repo: UsageRepository) -> None:
        record = _make_record(source_provenance=r"\\nas\team\agent-data\session.log")
        repo.insert_record(record)
        stored = repo.get_records_by_provider("test-provider")
        assert len(stored) == 1
        raw = str(stored[0].source_provenance or "")
        assert "\\\\nas\\team\\agent-data" not in raw
        assert raw.startswith("path-hash:")

    def test_traversal_path_not_stored_raw(self, repo: UsageRepository) -> None:
        record = _make_record(source_identifier="../../../etc/shadow")
        repo.insert_record(record)
        stored = repo.get_records_by_provider("test-provider")
        assert len(stored) == 1
        assert "../../../etc/shadow" not in stored[0].source_identifier
        assert stored[0].source_identifier.startswith("path-hash:")

    def test_deterministic_hash_enables_correct_dedupe(self, repo: UsageRepository) -> None:
        r1 = _make_record(event_id="dedupe-path-1", source_identifier=r"C:\Users\me\session.log")
        r2 = _make_record(event_id="dedupe-path-1", source_identifier=r"C:\Users\me\session.log")
        repo.insert_record(r1)
        repo.insert_record(r2)
        assert repo.get_record_count("test-provider") == 1


# ─── 9. Batch operations ───────────────────────────────────────────────


class TestBatchOperations:
    def test_insert_records_count(self, repo: UsageRepository) -> None:
        records = [_make_record(event_id=f"evt-{i}") for i in range(5)]
        count = repo.insert_records(records)
        assert count == 5
        assert repo.get_record_count("test-provider") == 5

    def test_insert_records_deduplicates(self, repo: UsageRepository) -> None:
        records = [_make_record(event_id="evt-1"), _make_record(event_id="evt-1")]
        count = repo.insert_records(records)
        assert count == 1
        assert repo.get_record_count("test-provider") == 1
