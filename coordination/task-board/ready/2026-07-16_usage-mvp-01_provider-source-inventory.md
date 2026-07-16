---
task_id: usage-mvp-01
phase: usage-mvp-foundation
status: READY
owner: external-agent-research-01
reviewer: ORCHESTRATOR
priority: high
dependencies: []
allowed_scope:
  - docs/**
  - coordination/**
forbidden_scope:
  - src/**
  - tests/**
  - pyproject.toml
  - scripts/**
acceptance:
  - Create a provider source-inventory document covering Codex, OpenCode, Hermes, Reasonix, MiMo Code, Antigravity, and Claude only where locally observable evidence exists.
  - For every candidate source, record source location category, machine-readable format, fields available, freshness, privacy risk, redaction rule, and whether token values are official, estimated, or unavailable.
  - Include only sanitized examples or schema descriptions; do not commit tokens, prompts, source code, cookies, credentials, account identifiers, or absolute user paths.
  - Recommend exactly one first-provider candidate backed by structured, reproducible local evidence, or explicitly report that no candidate is safe enough.
  - Add a verification checklist proving the research artifacts contain no secrets or raw session content.
expected_artifacts:
  - source_inventory
  - privacy_checklist
  - delivery_report
---
# Task Packet

## Objective

Create the evidence-based provider source inventory that determines the first
real collector. This is a read-only research task; it must not parse or import
real usage data into the application.

## Context

Read:

- `README.md`
- `AGENTS.md`
- `docs/architecture/mvp-architecture.md`
- `docs/research/reference-decisions.md`
- `docs/operations/first-live-phase-rollout.md`

The product must preserve privacy and low overhead. A provider can be shown as
activity-only or unavailable when exact token data is not trustworthy.

## Constraints

- Inspect only local, readable, explicitly relevant configuration/session/log
  metadata. Do not access browser cookies, credential stores, API keys, prompt
  text, source-code content, or private account data.
- Never copy raw filenames containing personal paths into the repository.
- Do not add code or dependencies. Do not state that an unverified path or
  format is supported.

## Validation Steps

1. Manually scan every new document for credentials, prompt text, account IDs,
   and absolute user paths.
2. Confirm every provider row distinguishes verified, inferred, and unavailable
   fields.
3. Confirm the selected first provider has a documented structured source and
   at least two sanitized fixture-shaped examples or schema samples.

## Escalation Rules

Create an incident and stop if identifying a source would require credentials,
browser storage, network API calls, or copying private session contents.
