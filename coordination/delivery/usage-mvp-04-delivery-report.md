# Delivery Report: usage-mvp-04

## Summary

Implemented `collect_codex_fixture`, one bounded, on-demand collection pass
for a caller-supplied JSONL fixture or approved path. It calls only the
accepted Codex JSONL adapter, persists its safe records through
`UsageRepository`, and stores the adapter cursor after a successful pass.
It introduces no discovery, scheduler, watcher, network request, dependency,
or storage schema change.

## Changed Files

| File | Change |
| --- | --- |
| `src/usage_collector/collection_service.py` | New explicit-input collection API and safe result type |
| `tests/test_collection_service.py` | New synthetic-fixture coverage for collection and safety boundaries |
| `docs/bounded-collection-service.md` | New operator/developer boundary and cursor documentation |
| `coordination/task-board/review/2026-07-19_usage-mvp-04_bounded-fixture-collection-service.md` | Task lifecycle submission |
| `coordination/progress/external-agent-platform-32.md` | Worker progress handoff |
| `coordination/delivery/usage-mvp-04-delivery-report.md` | This evidence report |

## Acceptance Coverage

1. **Bounded explicit-input service** — `collect_codex_fixture` takes exactly
   one caller-provided path plus an injected repository, then delegates parsing
   to `parse_codex_jsonl_file`.
2. **Cursor and result evidence** — the saved `codex` cursor produces an
   unchanged no-op on a second pass; result metadata contains inserted/skipped
   counts, cursor, and a safe health state.
3. **No unsafe runtime behaviour** — no scan, source discovery, real session
   input, loop, watcher, scheduler, network call, dependency, or schema change
   was added.
4. **Unsafe input boundary** — malformed and content-bearing synthetic lines
   are ignored by the existing adapter and create no persisted record. An
   unreadable source returns `source_unavailable` without exposing its path.
5. **Unknown values** — tests verify every stored record retains `None` for
   token, cost, and quota values.
6. **Documentation** — the new document states the explicit-input and cursor
   contract plus residual privacy limitations.

## Validation

```text
python -m pytest -p no:cacheprovider --basetemp <writable-temp> tests/test_collection_service.py -q
=> 5 passed

python -m pytest -p no:cacheprovider --basetemp <writable-temp> -q
=> 81 passed
```

`git diff --check` also passed. Pytest was installed only into an external
temporary runtime directory because no project test runtime was provisioned;
`pyproject.toml` and project dependencies were unchanged.

## Residual Risks

- The cursor is provider-scoped, so concurrent callers should be coordinated
  before they share one repository.
- A changed or truncated source behind an existing byte-offset cursor is not
  re-read automatically; this task intentionally does not add file metadata
  discovery or reset policy.

## Recommended Next Handoff

Review the service and tests, then decide whether the next MVP packet should
add an explicit caller-facing collection command or the desktop aggregate
overlay. Neither should add automatic source discovery.
