# Progress

## Current State

- `usage-mvp-02` storage and normalization foundation is accepted on `main`.
- `usage-mvp-01` provider source inventory and `usage-mvp-01-fix` field-matrix
  correction are accepted.
- The accepted inventory preserves unknown token, cost, and quota fields and
  permits only fixture-backed, sanitized collection work.

## Active Work

- `usage-mvp-03` resubmitted after P1 fix: recursive nested forbidden-key
  detection; 8 regression tests; all 72 tests pass.

## Known Risks

- Some providers may expose no trustworthy local token/cost data.
- Unknown values must remain `None`/unknown rather than estimated.
- Local source paths are sanitized before persistence and never committed.

## Next Action

Review the resubmitted `usage-mvp-03`, then open bounded collection work.
