---
task_id: usage-mvp-04
phase: usage-mvp-foundation
status: DONE
owner: external-agent-platform-32
reviewer: ORCHESTRATOR
priority: high
dependencies:
  - usage-mvp-03
allowed_scope:
  - src/usage_collector/**
  - tests/**
  - docs/**
  - coordination/**
forbidden_scope:
  - data/**
  - .github/**
  - pyproject.toml
acceptance:
  - Add one bounded, on-demand collection service that accepts an explicit synthetic or pre-approved fixture path and persists only records emitted by the accepted Codex JSONL adapter through UsageRepository.
  - The service must use the persisted provider cursor to avoid reprocessing unchanged fixture input and must expose deterministic inserted/skipped counts plus a safe health result.
  - The implementation must not discover source files, recursively scan directories, read a real local Codex session, add a polling loop, watcher, scheduler, network call, or dependency.
  - Malformed or content-bearing input must remain safely ignored or rejected without raw values reaching records, reports, exceptions, or test assertions.
  - Add focused synthetic-fixture tests for first collection, unchanged cursor no-op, duplicate persistence, malformed/unsafe input, and unknown token/cost/quota fields.
  - Document the explicit-input boundary, cursor semantics, and residual limitations.
expected_artifacts:
  - bounded_collection_service
  - collection_tests
  - collection_documentation
  - delivery_report
---

# Task Packet

## Objective

Turn the accepted fixture-backed Codex JSONL adapter into one bounded collection
operation that feeds `UsageRepository`. This is a real product increment and
the first live proof task for the local worker handoff; it is not a daemon,
automatic source discovery feature, or scheduler.

## Context

Read before editing:

- `AGENTS.md`, `PLAN.md`, `PROGRESS.md`, and `TASKS.md`
- `docs/data-contract.md`
- `docs/codex-jsonl-adapter.md`
- `src/usage_collector/codex_jsonl_adapter.py`
- `src/usage_collector/storage.py`
- `tests/test_codex_jsonl_adapter.py`
- `tests/test_storage.py`

`usage-mvp-03` is accepted. Its adapter is the only permitted parser input;
the collector must not bypass its safety boundary.

## Constraints

- The caller supplies one explicit fixture or approved path; do not enumerate
  directories or infer paths from user profiles, configuration, or sessions.
- Tests use synthetic data only. Never inspect, copy, commit, or require real
  session, credential, cookie, prompt, response, account, project, or source
  code data.
- Keep unknown token, cost, and quota fields as `None`. Activity bytes are not
  a token estimate.
- Do not change the storage schema, add dependencies, or add background work.
- Keep progress, incident, delivery, and review evidence task-specific.

## Implementation Notes

- Prefer a small explicit service API that accepts a fixture path/text and an
  injected `UsageRepository`, calls the adapter, persists accepted records,
  and updates the provider cursor only after a safe bounded pass.
- A deterministic input fingerprint or adapter checkpoint is acceptable for
  unchanged-input detection; it must contain no raw input content or absolute
  local path.
- Return structured counts and safe error/health metadata rather than logging
  raw rejected values.

## Validation Steps

1. Run the focused collection tests.
2. Run `python -m pytest -q`.
3. Inspect all newly added synthetic fixtures, test assertions, and delivery
   evidence for forbidden data and absolute paths.
4. Verify the second unchanged-input collection does not insert records.

## Escalation Rules

Create an incident and stop if implementation needs real provider data, a
storage migration, path discovery, a dependency, a network call, a watcher,
or the raw content of a rejected record.
