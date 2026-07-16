# MVP Architecture

## Goal

Provide a quiet local Windows utility that reports per-agent usage from
trustworthy local evidence without increasing AI token spend or materially
consuming CPU while idle.

## Product Shape

```text
configured read-only source files
            |
            v
provider adapter -> normalized record -> SQLite dedupe/cursor
            |                              |
            +-> provider health             +-> aggregate snapshot
                                                   |
                                                   v
                                      Tkinter compact overlay
                                      (always-on-top, taskbar minimize)
```

## Core Contracts

### Normalized Usage Record

Every provider parser emits a record containing provider, source identifier,
event/session identifier, occurred/captured times, optional model/token/cost or
quota values, source reliability, and a deterministic dedupe key. Raw prompt,
response, credential, cookie, and unredacted absolute path fields are forbidden.

### Provider Adapter

An adapter receives only explicitly configured source roots. It first compares
the saved cursor with file modification metadata; unchanged files are skipped.
It isolates parsing errors and returns a health result rather than failing the
entire collection cycle.

### Scheduler

The UI process schedules one collection cycle with `tkinter.after`. The default
interval is 600 seconds and is configurable with a safe lower bound of 60
seconds. No polling occurs while a prior cycle is still active.

### Desktop Window

The first UI is a compact native Tkinter window. It displays each provider's
latest token/quota/cost values, freshness, and health state. It uses no browser
or Electron runtime. Closing the main window exits; minimizing sends it to the
normal Windows taskbar. A tray icon is a later optional enhancement because it
would add a native dependency or Win32 implementation surface.

## MVP Delivery Order

1. Source inventory and redaction rules for one candidate provider.
2. Data model, SQLite records, dedupe, cursor, and aggregate snapshot.
3. Collector protocol, scheduler, and one fixture-backed provider adapter.
4. Tkinter overlay wired to the local aggregate snapshot.
5. End-to-end low-resource verification and operator runbook.

## Non-Goals

- No automatic account discovery, login, API polling, or browser automation.
- No claims of precise usage where the source omits it.
- No always-running full-directory scan, cloud backend, or multi-machine sync.
- No system-tray implementation in the first release.
