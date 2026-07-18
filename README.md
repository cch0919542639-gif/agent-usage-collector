# Agent Usage Collector

Low-overhead Windows desktop collector for local AI-agent usage evidence.

The MVP reads only explicitly configured local files, normalizes trustworthy
usage records, stores deduplicated aggregates in SQLite, and shows a compact
always-on-top summary window. The window can be minimized to the Windows taskbar
when it is not needed. It never sends prompts, source code, credentials, or
usage data to a remote service.

## MVP Boundary

- Python 3.12 standard library only: `sqlite3`, `tkinter`, `pathlib`, and
  `json`; no background browser, cloud service, or LLM calls.
- One proven structured local source first. Missing token values remain
  `unknown`; the app must never invent an estimate.
- Default scan interval: 10 minutes. Scans use a persisted cursor and file
  metadata to avoid repeated full parsing.
- One compact desktop window, always-on-top while visible, and normal Windows
  taskbar minimization.
- Provider adapters are additive. Each provider owns its source parser and
  health state; one failed provider cannot stop the rest.

## Not Yet Implemented

- System-tray icon behavior (taskbar minimization is the MVP behavior).
- Automatic discovery of private session locations.
- Direct API polling, account sign-in, or credential access.
- Precise token reporting for a provider that does not expose trustworthy local
  token data.

## Project Workflow

Read [AGENTS.md](AGENTS.md), [PLAN.md](PLAN.md), and
[PROGRESS.md](PROGRESS.md) before working. Active work is recorded in
`coordination/task-board/`; delivery requires a task-card transition, progress
record, delivery report, tests, and a pushed branch. The complete context
workflow is in [docs/operations/work-context-workflow.md](docs/operations/work-context-workflow.md).

## Initial Plan

The architecture and safety decisions are in
[`docs/architecture/mvp-architecture.md`](docs/architecture/mvp-architecture.md).
The referenced-project evaluation is in
[`docs/research/reference-decisions.md`](docs/research/reference-decisions.md).
