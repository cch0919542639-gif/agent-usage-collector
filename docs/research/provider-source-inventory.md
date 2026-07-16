# Provider Source Inventory

## Methodology

Local filesystem inspection on Windows 11. Only explicitly relevant
configuration, session, and log metadata were examined. No browser cookies,
credential stores, API keys, prompt text, source code, or private account data
were accessed. Absolute user paths have been redacted to `<USER_HOME>`.

## Provider Summary

| Provider | Local Data Found | Token Fields | First-Provider Candidate |
|---|---|---|---|
| Codex | Yes | Unavailable | **Yes** |
| OpenCode | No | N/A | No |
| Hermes | Config only | N/A | No |
| Reasonix | No | N/A | No |
| MiMo Code | No | N/A | No |
| Antigravity | No | N/A | No |
| Claude | No | N/A | No |

---

## 1. Codex

### Source Location Category

Local application data directory: `<USER_HOME>/.codex/`

### Machine-Readable Formats

| Source | Format | Description |
|---|---|---|
| `session_index.jsonl` | JSONL | Session index with `id`, `thread_name`, `updated_at` |
| `sessions/YYYY/MM/DD/*.jsonl` | JSONL | Session event logs (timestamp, type, payload) |
| `logs_2.sqlite` | SQLite | Application logs with `ts`, `level`, `target`, `estimated_bytes` |
| `config.toml` | TOML | Provider configuration (model, service_tier, plugins) |

### Fields Available

| Field | Source | Reliability | Notes |
|---|---|---|---|
| `provider` | Fixed | exact | Always `"codex"` |
| `source_identifier` | File path | exact | Session file path |
| `event_id` | Session JSONL | exact | `payload.id` from session_meta |
| `occurred_at` | Session JSONL | exact | `timestamp` field (ISO 8601) |
| `captured_at` | Collection time | exact | Set at parse time |
| `model` | Session JSONL | exact | `payload.model_provider` (e.g., `"openai"`) |
| `tokens_input` | **Unavailable** | N/A | Not exposed in local files |
| `tokens_output` | **Unavailable** | N/A | Not exposed in local files |
| `cost` | **Unavailable** | N/A | Not exposed in local files |
| `quota` | **Unavailable** | N/A | Not exposed in local files |
| `source_reliability` | Derived | exact | Always `"unknown"` for token/cost fields |
| `estimated_bytes` | SQLite logs | estimated | Proxy for activity volume, not token count |

### Sanitized Example — Session Meta Event

```json
{
  "timestamp": "2026-07-16T05:26:03.262Z",
  "type": "session_meta",
  "payload": {
    "session_id": "<SESSION_UUID>",
    "id": "<EVENT_UUID>",
    "timestamp": "2026-07-16T05:26:03.262Z",
    "originator": "Codex Desktop",
    "cli_version": "0.144.2",
    "model_provider": "openai",
    "thread_source": "subagent",
    "context_window": {}
  }
}
```

### Sanitized Example — SQLite Log Record

```
id: 5732585
ts: 1783479834
level: WARN
target: codex_core::shell_snapshot
estimated_bytes: 241
thread_id: <THREAD_UUID>
```

### Freshness

- Session JSONL files are written in real-time during active sessions.
- `session_index.jsonl` is updated on session start/end.
- SQLite `logs` table grows continuously during operation.

### Privacy Risk

| Risk | Severity | Mitigation |
|---|---|---|
| Absolute file paths in `cwd` field | Medium | Redact to project-relative or omit |
| Thread/session UUIDs | Low | Keep as opaque identifiers; no PII |
| Log message content | Medium | Never copy `feedback_log_body` to records |
| Config `projects` list | Medium | Contains project paths; redact or omit |

### Redaction Rules

1. **Never copy** `feedback_log_body`, `base_instructions`, or `content` fields
   from session JSONL files.
2. **Redact** `cwd` to a project name or omit entirely.
3. **Redact** `config.toml` `projects` paths to project names only.
4. **Keep** UUIDs as opaque identifiers (no PII risk).
5. **Keep** timestamps, model names, CLI version, and event types.

---

## 2. OpenCode

### Source Location Category

No local data directory found at `<USER_HOME>/.opencode/` or common AppData
locations.

### Status

**Not available** for local collection on this machine. May store data in
project-local `.opencode/` directories, which would require per-project
configuration.

---

## 3. Hermes

### Source Location Category

`<USER_HOME>/.hermes/` — contains `config.yaml` and `skills/` directory.

### Status

**Config only** — no usage logs, session data, or token tracking observed.
The `config.yaml` contains tool configuration, not usage evidence.

---

## 4. Reasonix

### Source Location Category

No local data directory found.

### Status

**Not available** for local collection on this machine.

---

## 5. MiMo Code

### Source Location Category

No local data directory found at `<USER_HOME>/.mimocode/` or common AppData
locations.

### Status

**Not available** for local collection on this machine. May store session data
in platform-specific locations not yet identified.

---

## 6. Antigravity

### Source Location Category

No local data directory found.

### Status

**Not available** for local collection on this machine.

---

## 7. Claude

### Source Location Category

No local data directory found at `<USER_HOME>/.claude/` or common AppData
locations.

### Status

**Not available** for local collection on this machine. Claude Code may store
session data in project-local `.claude/` directories.

---

## First-Provider Recommendation

### Selected: Codex

**Rationale:**

1. **Structured local evidence exists.** Codex stores session events as JSONL
   with consistent schemas (timestamp, type, payload) and maintains a SQLite
   log database with indexed fields.

2. **Machine-readable format.** Both JSONL and SQLite are directly parseable
   with Python standard library (`json`, `sqlite3`).

3. **Deterministic deduplication.** Each event has a UUID `id` field suitable
   for the `(provider, event_id)` dedupe key.

4. **Freshness metadata available.** Timestamps are ISO 8601 and written
   in real-time, enabling accurate freshness reporting.

5. **Privacy boundary is clear.** The risky fields (`content`,
   `feedback_log_body`, `base_instructions`) are identifiable and can be
   excluded by rule. UUIDs and timestamps are safe to retain.

6. **Token values are unavailable.** This is honest — the MVP will report
   `unknown` for token/cost fields, which aligns with the architecture's
   requirement to never invent estimates.

**First adapter scope:** Parse `sessions/YYYY/MM/DD/*.jsonl` session_meta
events to extract session IDs, timestamps, model provider, and CLI version.
Report token/cost as `unknown`. Use `estimated_bytes` from SQLite logs as an
optional activity proxy (source_reliability: `estimated`).

### Not Selected (and why)

| Provider | Reason |
|---|---|
| OpenCode | No local data found on this machine |
| Hermes | Config only; no usage evidence |
| Reasonix | No local data found |
| MiMo Code | No local data found |
| Antigravity | No local data found |
| Claude | No local data found on this machine |

These providers may have local data on other machines or configurations. The
inventory should be revisited when cross-platform evidence is available.
