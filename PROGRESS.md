# Progress

## Current State

- `usage-mvp-02` storage and normalization foundation is accepted on `main`.
- `usage-mvp-01` provider source inventory is submitted on
  `agent/external-agent-research-01/usage-mvp-01` and awaits orchestrator
  review.
- The coordination monitor currently scans the product default branch only, so
  the worker-branch review still requires direct orchestrator inspection until
  branch-aware monitoring is delivered.

## Active Work

- `usage-mvp-01` received a field-completeness `needs_fix` review; dispatch
  `usage-mvp-01-fix` before selecting the first collector adapter.
- Choose the first approved structured source, then create the collector-adapter
  task packet.

## Known Risks

- Some providers may expose no trustworthy local token/cost data.
- Unknown values must remain `None`/unknown rather than estimated.
- Local source paths are sanitized before persistence and never committed.

## Next Action

Review `usage-mvp-01` branch evidence. If accepted, dispatch the first
fixture-backed provider adapter against the approved source contract.
