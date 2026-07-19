# Progress

## Current State

- `usage-mvp-02` storage and normalization foundation is accepted on `main`.
- `usage-mvp-01` provider source inventory and `usage-mvp-01-fix` field-matrix
  correction are accepted.
- The accepted inventory preserves unknown token, cost, and quota fields and
  permits only fixture-backed, sanitized collection work.

## Active Work

- `usage-mvp-03` is accepted after recursive content-key and alias privacy
  fixes; 40 focused and 76 total tests pass in isolated-source verification.
- `usage-mvp-04` is assigned to `external-agent-platform-32` for a bounded,
  explicit-input collection service. It is the controlled end-to-end proof of
  local worker activation, claim, delivery, and review.

## Known Risks

- Some providers may expose no trustworthy local token/cost data.
- Unknown values must remain `None`/unknown rather than estimated.
- Local source paths are sanitized before persistence and never committed.

## Next Action

Monitor `usage-mvp-04` through its worker handoff and review its repository
evidence when submitted.
