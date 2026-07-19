---
task_id: usage-mvp-03
phase: usage-mvp-foundation
status: REVIEW
owner: external-agent-platform-32
reviewer: ORCHESTRATOR
priority: high
dependencies:
  - usage-mvp-01
  - usage-mvp-02
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
  - Add a fixture-backed Codex JSONL metadata adapter that emits NormalizedUsageRecord values using only the accepted inventory fields.
  - Ignore or reject content-bearing records and never persist raw prompt, response, instruction, feedback, credential, cookie, account, project-path, or source-code fields.
  - Keep input/output tokens, cost, and quota as None; activity-byte metadata must not become a token estimate.
  - Support a deterministic opaque cursor or checkpoint result suitable for a later bounded poller, without adding a loop, watcher, network call, or runtime scheduler.
  - Add tests using only synthetic fixture data for valid metadata, ignored unsafe content, malformed input, unknown values, deterministic dedupe identity, and cursor behavior.
  - Document the adapter's accepted metadata boundary, unsupported sources, and residual privacy limitations.
expected_artifacts:
  - codex_jsonl_adapter
  - synthetic_fixtures
  - adapter_tests
  - adapter_documentation
  - delivery_report
---

# Task Packet

## Objective

Implement the first trusted provider adapter: a fixture-backed parser for the
approved Codex JSONL metadata shape. The adapter is a bounded parsing component,
not a live collector, directory scanner, or scheduler.

## Context

Read before editing:

- `AGENTS.md`, `PLAN.md`, `PROGRESS.md`, and `TASKS.md`
- `docs/research/provider-source-inventory.md`
- `docs/data-contract.md`
- `src/usage_collector/models.py`
- `src/usage_collector/storage.py`
- `tests/test_storage.py`

The accepted source contract permits only provider, sanitized source identifier,
opaque event identifier, timestamp, optional model metadata, and activity-byte
proxy. Token, cost, and quota values are unknown.

## Constraints

- Use synthetic fixtures only. Do not inspect, copy, commit, or require any
  real local Codex session, log, SQLite, TOML, credential, or configuration
  file.
- Do not introduce dependencies, network calls, browser automation, a file
  watcher, a daemon, or a polling loop.
- Treat unsupported, malformed, or content-bearing input as ignored or safely
  rejected according to the documented API; never copy its raw content into a
  record, exception, test assertion, or report.
- Preserve the data contract's `None` representation for unknown token, cost,
  and quota fields. Do not convert activity bytes to tokens.
- Do not change storage schema or the accepted persistence boundary without an
  incident and explicit orchestration decision.

## Implementation Notes

- Prefer a small adapter API that accepts an explicit fixture path or text and
  returns records plus a deterministic next cursor/checkpoint.
- Use logical source labels in fixtures. The existing persistence boundary will
  sanitize an unsafe path if a caller later provides one.
- A safe design may ignore lines whose metadata shape includes forbidden
  content-bearing keys rather than attempting to redact their values.

## Token And Resource Impact (If Applicable)

Not applicable. This task adds an on-demand, fixture-backed parser only. It
must not add a background process, polling schedule, watcher, or model call.

## Validation Steps

1. Run the new focused adapter tests.
2. Run `python -m pytest -q`.
3. Manually inspect synthetic fixtures and delivery evidence for prohibited
   content and absolute user paths.
4. Verify every accepted record has `tokens_input`, `tokens_output`, `cost`,
   and `quota` set to `None`.

## Escalation Rules

Create an incident and stop if valid parsing requires real local provider data,
an unknown source schema, a storage migration, a dependency, a network call, or
any attempt to store content-bearing fields.
