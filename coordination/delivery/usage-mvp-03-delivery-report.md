# Delivery Report: usage-mvp-03

## Task Summary

- **Task ID**: usage-mvp-03
- **Phase**: usage-mvp-foundation
- **Agent**: external-agent-platform-32
- **Reviewer**: ORCHESTRATOR
- **Date**: 2026-07-19
- **Status**: READY_FOR_REVIEW

## Objective

Implement the first trusted provider adapter: a fixture-backed parser for the
approved Codex JSONL metadata shape. The adapter is a bounded parsing component,
not a live collector, directory scanner, or scheduler.

## Changed Files

| File | Description |
|------|-------------|
| `src/usage_collector/codex_jsonl_adapter.py` | Fixture-backed Codex JSONL parser |
| `tests/test_codex_jsonl_adapter.py` | 39 focused tests for the adapter |
| `tests/fixtures/valid_metadata.jsonl` | Valid metadata fixture |
| `tests/fixtures/content_bearing.jsonl` | Content-bearing records fixture |
| `tests/fixtures/malformed_input.jsonl` | Malformed JSON fixture |
| `tests/fixtures/unknown_values.jsonl` | Missing fields fixture |
| `tests/fixtures/dedupe_identity.jsonl` | Duplicate events fixture |
| `tests/fixtures/cursor_lines.jsonl` | Cursor behavior fixture |
| `docs/codex-jsonl-adapter.md` | Adapter documentation |

## Validation Commands

```bash
python -m pytest tests/test_codex_jsonl_adapter.py -v
# Result: 39/39 passed

python -m pytest -q
# Result: 67/67 passed
```

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Fixture-backed Codex JSONL metadata adapter | ✅ | `codex_jsonl_adapter.py` parses JSONL text/files |
| Emits NormalizedUsageRecord values | ✅ | All parsed lines produce `NormalizedUsageRecord` instances |
| Uses only accepted inventory fields | ✅ | Only provider, source_identifier, event_id, occurred_at, captured_at, model fields |
| Ignores/rejects content-bearing records | ✅ | Lines with forbidden keys silently ignored |
| Never stores prompts, responses, credentials, cookies, account data, project paths, or source code | ✅ | Forbidden key detection at parse time |
| Tokens, cost, quota remain None | ✅ | Hardcoded to None in adapter |
| Activity bytes not converted to tokens | ✅ | No token estimation logic |
| Deterministic opaque cursor | ✅ | SHA-256 based cursor from label + line counts |
| No polling loop, watcher, network call, dependency, or storage migration | ✅ | Pure function, stdlib only |
| Tests for valid metadata | ✅ | `TestValidMetadata` class |
| Tests for ignored unsafe content | ✅ | `TestIgnoredUnsafeContent` class |
| Tests for malformed input | ✅ | `TestMalformedInput` class |
| Tests for unknown values | ✅ | `TestUnknownValues` class |
| Tests for deterministic dedupe identity | ✅ | `TestDeterministicDedupeIdentity` class |
| Tests for cursor behavior | ✅ | `TestCursorBehavior` class |
| Documentation of adapter boundaries | ✅ | `docs/codex-jsonl-adapter.md` |

## Known Risks

- The adapter trusts that synthetic fixtures do not contain real user data.
- Content-bearing fields are ignored by key name, not by value inspection.
- Source identifiers provided as absolute paths will be sanitized by the
  persistence boundary, but the adapter itself does not sanitize inputs.

## Handoff Recommendation

This adapter provides the foundation for bounded local collection. The next
task should integrate this parser with a bounded poller that reads from a
configured fixture directory and persists results via `UsageRepository`.

## Files Touched

- `src/usage_collector/codex_jsonl_adapter.py` (new)
- `tests/test_codex_jsonl_adapter.py` (new)
- `tests/fixtures/*.jsonl` (6 new files)
- `docs/codex-jsonl-adapter.md` (new)
- `coordination/progress/external-agent-platform-32.md` (updated)
- `coordination/task-board/in_progress/2026-07-19_usage-mvp-03_codex-jsonl-fixture-adapter.md` (moved from ready/)
