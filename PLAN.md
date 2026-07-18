# Plan

## Product Objective

Deliver a quiet Windows desktop utility that collects trustworthy local AI-agent
usage evidence, stores deduplicated aggregates, and shows a compact always-on-
top summary without remote calls, prompt collection, or unnecessary resource
use.

## Current Milestone

MVP foundation and first trusted provider adapter.

## Delivery Order

| Milestone | Outcome | Exit Criteria |
| --- | --- | --- |
| Source inventory | One provider source is proven safe and sufficiently structured. | Accepted inventory, privacy rules, fixture-shaped evidence. |
| Storage foundation | Normalized model, SQLite dedupe/cursor, aggregates. | Accepted as `usage-mvp-02`. |
| Collection adapter | Cursor-aware parser for the approved source. | Fixture-backed collector with health reporting. |
| Desktop overlay | Low-overhead Tkinter usage summary. | Handles unknown values and taskbar minimization. |
| MVP verification | End-to-end scan, persistence, display, and resource validation. | Operator runbook and known-limit review. |

## Non-Goals

- API polling, login, credential or cookie access
- browser automation or cloud backend
- invented token/cost estimates
- continuous full-directory scanning or high-frequency busy loops
