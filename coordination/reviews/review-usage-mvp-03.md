# Review: usage-mvp-03

## Decision

needs_fix

## Summary

The fixture-backed adapter is well-scoped and its isolated test suite passes,
but it cannot be accepted until nested content-bearing fields fail closed and
the submitted task card reflects its `review/` lifecycle state.

## Findings

- The adapter is fixture-only, dependency-free, and preserves unknown token,
  cost, and quota values as `None`.
- Independent verification with `PYTHONPATH=src` loaded the isolated branch
  implementation and passed `39` focused tests and `67` total tests.
- **P1 privacy boundary:** `_has_forbidden_keys()` checks only the top-level
  object and direct `payload`. A synthetic line containing
  `payload.metadata.message` produced one accepted record. Content-bearing keys
  at any nested dictionary or list depth must cause the line to be ignored or
  safely rejected.
- **P2 lifecycle metadata:** the task card is under `task-board/review/` but
  its front matter still says `status: READY`; it must say `REVIEW` when
  resubmitted.

## Validation

- `PYTHONPATH=src python -m pytest tests/test_codex_jsonl_adapter.py -q` ->
  `39 passed`.
- `PYTHONPATH=src python -m pytest -q` -> `67 passed`.
- Synthetic nested-content check returned `{"records": 1, "ignored": 0}` for
  a line containing `payload.metadata.message`; this is the blocking failure.

## Required Changes

1. Traverse nested dictionaries and lists when detecting forbidden
   content-bearing keys. Do not inspect, log, or preserve their values.
2. Add synthetic fixtures and regression tests proving nested keys such as
   `message`, `content`, `prompt`, and `source_code` are ignored at multiple
   depths, including inside a list.
3. Restore task-card front matter to `status: REVIEW` while the card remains in
   `coordination/task-board/review/`.
4. Update the delivery report with the fix and rerun focused plus full tests
   with `PYTHONPATH=src` (or an equivalent isolated import path).

## Accepted Artifacts

- None pending the required privacy correction.
