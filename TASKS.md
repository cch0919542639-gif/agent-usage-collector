# Tasks

## Authoritative Board

Task lifecycle is stored in `coordination/task-board/`:

- `ready/` assigned but not claimed
- `in_progress/` active execution
- `review/` submitted delivery
- `done/` accepted work
- `blocked/` incident or dependency

## Current Work Groups

- `usage-mvp-01`: provider source inventory and privacy checklist; accepted
  after the `usage-mvp-01-fix` field-matrix correction.
- `usage-mvp-02`: storage and normalization foundation; accepted.
- `usage-mvp-03`: ready for implementation of the fixture-backed Codex JSONL
  metadata adapter; submitted work is currently in `needs_fix` review.

Do not duplicate individual task status here. Read the actual task card before
dispatching, implementing, or reviewing.
