# Delivery Report: usage-mvp-03

## Summary

Implemented the fixture-backed Codex JSONL metadata adapter. The adapter is a
bounded parser that reads synthetic Codex session metadata from JSONL text or
file paths, emits `NormalizedUsageRecord` values, and returns a deterministic
byte-offset cursor for incremental parsing. No live scanning, polling, network
calls, or storage changes were introduced.

## Changed Files

| File | Change |
|------|--------|
| `src/usage_collector/codex_jsonl_adapter.py` | New — `parse_codex_jsonl` and `parse_codex_jsonl_file` functions |
| `tests/test_codex_jsonl_adapter.py` | New — 28 tests across 8 test classes |
| `docs/codex-jsonl-adapter.md` | New — accepted metadata boundary, unsupported sources, privacy limitations |
| `coordination/progress/external-agent-platform-32.md` | New — progress tracking |
| `coordination/delivery/usage-mvp-03-delivery-report.md` | New — this report |

## Acceptance Criteria Coverage

1. **Fixture-backed metadata adapter** — `parse_codex_jsonl` accepts text;
   `parse_codex_jsonl_file` accepts file paths. Both return
   `list[NormalizedUsageRecord]` using only accepted inventory fields.

2. **Content-bearing records rejected** — Lines containing forbidden keys
   (`content`, `prompt`, `response`, `instruction`, `feedback`, `messages`,
   `choices`, `credential`, `cookie`, `account`, `project-path`, `source-code`)
   at top level or in `payload` are silently skipped. Raw content is never
   parsed into records, assertions, or reports.

3. **Token/cost/quota always None** — Every emitted record has `tokens_input`,
   `tokens_output`, `cost`, and `quota` set to `None`. Activity-byte metadata
   is never converted to token estimates.

4. **Deterministic cursor** — Returns a byte-offset string. Passing the same
   cursor back resumes from the exact position. Suitable for a later bounded
   poller.

5. **Synthetic fixtures only** — All test data is generated inline or via
   temporary files. No real provider files are inspected, copied, or committed.

6. **Documentation** — `docs/codex-jsonl-adapter.md` documents the accepted
   metadata boundary, forbidden content handling, unsupported sources, cursor
   semantics, and residual privacy limitations.

## Fix Round 1 (needs_fix → resubmit)

Review **P1** required recursive traversal of nested dictionaries and lists
when detecting forbidden content-bearing keys.

- `_has_forbidden_keys_deep()` now recursively walks all dict values and list
  items, with cycle-safe tracking via `id()`.
- `message` was added to `FORBIDDEN_CONTENT_KEYS` (only `messages` existed).
- 8 new regression tests cover nested keys at multiple depths, list-of-object
  payloads, and top-level deeply nested keys.

## Fix Round 2 (needs_fix → resubmit)

Review identified five more missing forbidden-key aliases:
`raw_prompt`, `raw_response`, `api_key`, `cookies`, `credentials`.

- Added all five to `FORBIDDEN_CONTENT_KEYS`, including singular/plural pairs
  (`cookie`/`cookies`, `credential`/`credentials`).
- 4 new test methods (`TestMissingAliases`) covering each alias at top-level,
  nested dict depth, and nested list depth.

## Validation Results

```
python -m pytest tests/ -v
=> 76 passed in 1.10s
```

- 40 adapter tests (28 original + 8 nested-key + 4 alias regression); 0
  regressions in existing storage tests.
- Zero external dependencies added (stdlib only: `json`, `datetime`, `pathlib`).
- No storage schema changes.

## Residual Risks

- The cursor is an in-memory byte offset; it is not persisted by the adapter
  itself. A caller must save and restore the cursor via `UsageRepository`.
- Deduplication is deferred to the storage layer (`INSERT OR IGNORE`). The
  adapter emits all valid records; the repository handles dedupe.

## Recommended Next Handoff

The adapter is ready for integration into a bounded local collection command
that calls `parse_codex_jsonl_file`, persists records via `UsageRepository`,
and maintains cursor state across runs.
