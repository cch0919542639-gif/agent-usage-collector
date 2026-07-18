# Tasks

## Authoritative Board

Task lifecycle is stored in `coordination/task-board/`:

- `ready/` assigned but not claimed
- `in_progress/` active execution
- `review/` submitted delivery
- `done/` accepted work
- `blocked/` incident or dependency

## Current Work Groups

- `usage-mvp-01`: provider source inventory and privacy checklist; submitted on
  the worker branch, awaiting review.
- `usage-mvp-02`: storage and normalization foundation; accepted.
- Next: fixture-backed provider adapter after source inventory acceptance.

Do not duplicate individual task status here. Read the actual task card before
dispatching, implementing, or reviewing.
