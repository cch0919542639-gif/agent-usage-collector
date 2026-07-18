---
task_id: usage-mvp-01-fix
phase: usage-mvp-foundation
status: READY
owner: external-agent-research-01
reviewer: ORCHESTRATOR
priority: high
dependencies:
  - usage-mvp-01
allowed_scope:
  - docs/**
  - coordination/**
forbidden_scope:
  - src/**
  - tests/**
  - pyproject.toml
  - scripts/**
acceptance:
  - For OpenCode, Hermes, Reasonix, MiMo Code, Antigravity, and Claude, explicitly record source location category, machine-readable format, available fields, freshness, privacy risk, and redaction rule; use N/A only where local evidence is unavailable.
  - Preserve the existing Codex recommendation and all no-secret/no-raw-content boundaries.
  - Update the privacy checklist only if needed and provide a delivery report with a manual privacy recheck.
expected_artifacts:
  - corrected_source_inventory
  - delivery_report
---
# Task Packet

## Objective

Close the field-completeness review finding for `usage-mvp-01` without
re-inspecting private content or expanding into collector implementation.

## Context

Read `AGENTS.md`, `PLAN.md`, `PROGRESS.md`, `TASKS.md`, the original
`usage-mvp-01` task card, `coordination/reviews/review-usage-mvp-01.md`, and
the submitted source inventory and privacy checklist.

## Constraints

- Do not access credentials, cookies, prompt/response content, account data,
  or source-code contents.
- Do not add code, dependencies, source paths, or unverified claims.
- Treat missing local evidence as explicitly unavailable/N/A; do not infer data.

## Validation Steps

1. Manually check the revised matrix covers every required field for all seven
   providers.
2. Manually scan revised artifacts for secrets, raw session content, account
   IDs, and absolute user paths.
3. Submit on a dedicated worker branch with task card in `review/`, progress,
   and delivery report.

## Escalation Rules

Create an incident and stop if filling the matrix requires private data access,
network calls, or any code change.
