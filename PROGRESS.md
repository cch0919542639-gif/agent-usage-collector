# Progress

## Current State

- `usage-mvp-02` storage and normalization foundation is accepted on `main`.
- `usage-mvp-01` provider source inventory and `usage-mvp-01-fix` field-matrix
  correction are accepted.
- The accepted inventory preserves unknown token, cost, and quota fields and
  permits only fixture-backed, sanitized collection work.

## Active Work

- Select the first approved structured Codex source and create the
  fixture-backed collector-adapter task packet.

## Known Risks

- Some providers may expose no trustworthy local token/cost data.
- Unknown values must remain `None`/unknown rather than estimated.
- Local source paths are sanitized before persistence and never committed.

## Next Action

Create and dispatch the first fixture-backed Codex collector adapter against
the accepted source contract.
