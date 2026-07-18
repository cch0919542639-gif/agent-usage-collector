# Architecture

## Product Flow

```text
explicit local source -> provider adapter -> normalized usage record
                      -> SQLite dedupe/cursor -> aggregate snapshot
                      -> compact Tkinter desktop overlay
```

## Boundaries

- Provider adapters are read-only and source-specific.
- Normalized records hold trustworthy metadata only; unavailable values remain
  unknown.
- SQLite owns dedupe, cursors, and local aggregates.
- The UI reads aggregates and must not trigger expensive scans.
- `coordination/` provides product-local task evidence and review flow.

## Deep Design

Read `docs/architecture/mvp-architecture.md` for MVP contracts and
`docs/data-contract.md` for persistence fields and sanitization policy.
