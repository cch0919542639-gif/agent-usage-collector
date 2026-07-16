# Delivery Report: usage-mvp-02

## Summary

Built the provider-neutral SQLite storage foundation: normalized usage record
model, insert-or-ignore dedupe, provider-isolated cursor persistence, and
compact aggregate queries. No provider parsing, polling, filesystem discovery,
browser automation, or UI code was introduced.

## Changed Files

| File | Change |
|------|--------|
| `src/usage_collector/__init__.py` | New — package init |
| `src/usage_collector/models.py` | New — `NormalizedUsageRecord` frozen dataclass |
| `src/usage_collector/storage.py` | New — `UsageRepository` with SQLite schema, dedupe, cursor, aggregates |
| `tests/test_storage.py` | New — 24 focused tests across 8 test classes |
| `docs/data-contract.md` | New — public data contract and schema documentation |
| `coordination/progress/external-agent-platform-25.md` | Updated — progress tracking |
| `coordination/delivery/usage-mvp-02-delivery-report.md` | New — this report |

## Acceptance Criteria Coverage

1. **Provider-neutral normalized record** — `NormalizedUsageRecord` frozen
   dataclass with explicit `None` for unknown token, quota, and cost fields;
   `source_reliability` metadata (`exact`/`estimated`/`unknown`);
   `source_provenance` origin tracking.

2. **SQLite schema and repository operations** — `UsageRepository` with:
   - `insert_record` / `insert_records` with `INSERT OR IGNORE` dedupe
   - `get_cursor` / `set_cursor` with provider-scoped checkpoint persistence
   - `get_aggregate` / `get_all_aggregates` for compact aggregate queries
   - `write_aggregate_snapshot` for persisted snapshots

3. **Deterministic dedupe with provider scope** — `dedupe_key` property returns
   `(provider, event_id)`; `UNIQUE(provider, event_id)` constraint in schema;
   tests confirm same event_id across different providers are both stored.

4. **Focused tests** — 24 tests across 8 classes:
   - Dedupe (3 tests)
   - Provider isolation (2 tests)
   - Cursor persistence (5 tests)
   - Missing fields (3 tests)
   - No forbidden content (2 tests)
   - Aggregate queries (6 tests)
   - Temp directory isolation (1 test)
   - Batch operations (2 tests)

5. **Data contract documented** — `docs/data-contract.md` with field table,
   schema DDL, dedupe key definition, forbidden fields, and database location
   policy.

## Validation Results

```
python -m pytest tests/ -v
=> 24 passed in 0.94s
```

- All test data uses `pytest tmp_path`; no database files under tracked paths.
- Zero external dependencies added (stdlib only: `sqlite3`, `dataclasses`,
  `pathlib`, `datetime`).

## Residual Risks

- Aggregate `SUM` of `NULL` columns returns `NULL` rather than `0` — this is
  correct for honest unknown-value reporting, but UI code should handle `None`.
- `provider_cursors` stores an opaque string value; the format and semantics
  are the provider adapter's responsibility (e.g. file mtime, offset, or hash).
- No migration system exists yet; schema changes in future tasks will need
  either `CREATE TABLE IF NOT EXISTS` safety or explicit migration logic.

## Recommended Next Handoff

This foundation is ready for `usage-mvp-03` (collector protocol and first
fixture-backed provider adapter), which can import `NormalizedUsageRecord` and
`UsageRepository` directly.
