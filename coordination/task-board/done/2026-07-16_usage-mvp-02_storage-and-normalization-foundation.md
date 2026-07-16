---
task_id: usage-mvp-02
phase: usage-mvp-foundation
status: DONE
owner: external-agent-platform-25
reviewer: ORCHESTRATOR
priority: high
dependencies: []
allowed_scope:
  - src/**
  - tests/**
  - docs/**
  - pyproject.toml
  - coordination/**
forbidden_scope:
  - provider_samples/**
  - .github/**
  - scripts/**
acceptance:
  - Define a provider-neutral normalized usage record with explicit optional/unknown token, quota, and cost fields plus source provenance and reliability metadata.
  - Add SQLite schema and repository operations for insert-or-ignore dedupe, provider isolation, cursor/checkpoint persistence, and compact aggregate snapshots.
  - Ensure the deterministic dedupe identity includes provider scope so equal session/event IDs cannot collide across providers.
  - Add tests for dedupe, provider isolation, cursor restart behavior, missing usage fields, and no persistence of forbidden raw content fields.
  - Document the public data contract and local database location policy without committing runtime data.
expected_artifacts:
  - code_changes
  - focused_tests
  - data_contract
  - delivery_report
---
# Task Packet

## Objective

Build the provider-neutral storage foundation for the MVP. This task deliberately
does not implement a real provider parser, scheduler, or desktop UI.

## Context

Read:

- `README.md`
- `AGENTS.md`
- `docs/architecture/mvp-architecture.md`
- `docs/research/reference-decisions.md`
- `docs/operations/first-live-phase-rollout.md`

The application is standard-library-first and must support unknown values
truthfully. Runtime database files belong under ignored `data/` and must never
be committed.

## Constraints

- Use Python 3.12 standard library only unless a dependency is proven essential
  and approved through an incident.
- Store normalized fields only. Do not create columns for raw prompt, response,
  API key, cookie, unredacted absolute path, or provider raw payload.
- Keep the public interface independent of a particular provider or UI toolkit.
- Do not add polling, filesystem discovery, browser automation, or UI code.

## Validation Steps

1. Run focused tests for repository/model behavior.
2. Run the full project test suite using `python -m pytest`.
3. Confirm test data uses temporary directories and leaves no database under the
   repository's tracked paths.
4. Include exact commands/results and acceptance mapping in the delivery report.

## Escalation Rules

Create an incident and stop if the data contract requires a real provider file,
credential access, a non-standard dependency, or conflicts with the privacy
rules in `AGENTS.md`.
