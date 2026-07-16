# Review: usage-mvp-02

## Decision

accepted

## Summary

The provider-neutral record and SQLite foundation meets the MVP privacy and
isolation requirements after the path-sanitization correction.

## Validation

- Independent test run: `python -m pytest` -> `36 passed`.
- Dedupe is provider-scoped through `UNIQUE(provider, event_id)`.
- Cursors are provider-scoped and survive a repository reopen.
- Unknown token, quota, and cost values remain `NULL`/`None`, not fabricated
  zero values.
- Absolute Windows, POSIX, UNC, and traversal paths are converted to a stable
  `path-hash:` representation at the persistence boundary.

## Scope

Changes remain within the assigned model, storage, tests, data contract, and
coordination evidence. No provider parser, scheduler, UI, or external
dependency was introduced.

## Accepted Artifacts

- `src/usage_collector/models.py`
- `src/usage_collector/storage.py`
- `tests/test_storage.py`
- `docs/data-contract.md`
- `coordination/delivery/usage-mvp-02-delivery-report.md`

## Residual Risks

- A deterministic hash protects stored path text but is not a substitute for
  access controls on the local database.
- Database schema migration/versioning is deferred to a later task.
- UI code must represent aggregate `None` values as unknown, not zero.
