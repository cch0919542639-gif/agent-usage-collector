# Review: usage-mvp-04

- Task ID: `usage-mvp-04`
- Reviewer: `ORCHESTRATOR`
- Decision: `accepted`
- Reviewed commit: `fa2f470`
- Reviewed: `2026-07-19`

## Evidence Checked

- The task card's owner, scope, dependencies, acceptance criteria, delivery
  report, and worker progress record.
- `src/usage_collector/collection_service.py`: explicit single-path API;
  repository cursor read/write; no directory enumeration, scheduling, network,
  watcher, dependency, or schema changes.
- `tests/test_collection_service.py`: first pass, unchanged cursor no-op,
  duplicate persistence, malformed/content-bearing synthetic input, unknown
  values, and unreadable-source safe health result.
- Validation recorded by the worker: 5 focused tests and 81 total tests pass;
  `git diff --check` passes.

## Decision Rationale

Accepted. The collection service stays behind the existing adapter's privacy
boundary, takes an explicit input rather than discovering sources, and records
only safe aggregate result metadata. The delivery report documents the
provider-scoped cursor limitation and does not conceal test-runtime setup.

## Follow-up

Choose the next product interface deliberately: an explicit collection command
or the aggregate display. Neither may introduce automatic source discovery.
