# Memory

## Durable Constraints

- Never read or persist prompts, responses, source-code contents, API keys,
  cookies, or unredacted absolute source paths.
- Each provider adapter receives only explicitly configured local sources and
  must skip unchanged content using cursor/metadata evidence.
- The normal scan interval is ten minutes; one minute is debugging-only.
- Provider failure is isolated; one broken source must not stop aggregation or
  the desktop display.

## Provider Evidence To Date

- Codex: local JSONL sessions and SQLite logs are candidate evidence sources;
  acceptance depends on the approved inventory's field and privacy analysis.
- Other initially checked providers either had no local evidence on this
  machine or configuration without trustworthy usage records.

## Deep References

- `docs/architecture/mvp-architecture.md`
- `docs/data-contract.md`
- `docs/research/reference-decisions.md`
- `docs/operations/first-live-phase-rollout.md`
