# Provider Source Inventory

## Evidence Boundary

This inventory records only the already-submitted, sanitized local-observation
result. It does not re-inspect private content. No credentials, cookies, prompt
or response text, account data, source code, raw session content, or absolute
user paths are included.

`N/A` below means that no local evidence was available, not that a provider
cannot have data on another machine or configuration.

## Provider Field Matrix

| Provider | Source location category | Machine-readable format | Available fields | Freshness | Privacy risk | Redaction rule | Token values | Candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | Local application data | JSONL, SQLite, TOML | session/event metadata, timestamp, model-provider metadata, activity-byte proxy; token/cost/quota unavailable | session events are written during activity; index updates on session boundaries; logs grow during operation | paths, opaque identifiers, log messages, and config project entries can be sensitive | omit content-bearing fields and unredacted paths; retain only allowed metadata | unavailable, never estimated | **Yes** |
| OpenCode | Unavailable locally | N/A — no local artifact observed | N/A — no local usage evidence | N/A | N/A — no artifact inspected | N/A — nothing collected | unavailable | No |
| Hermes | Local configuration only | YAML configuration; no observed usage format | configuration schema only; no usage, session, token, cost, or quota fields observed | unknown for usage — configuration is not usage evidence | configuration values can be sensitive | do not copy configuration values; retain no raw configuration content | unavailable | No |
| Reasonix | Unavailable locally | N/A — no local artifact observed | N/A — no local usage evidence | N/A | N/A — no artifact inspected | N/A — nothing collected | unavailable | No |
| MiMo Code | Unavailable locally | N/A — no local artifact observed | N/A — no local usage evidence | N/A | N/A — no artifact inspected | N/A — nothing collected | unavailable | No |
| Antigravity | Unavailable locally | N/A — no local artifact observed | N/A — no local usage evidence | N/A | N/A — no artifact inspected | N/A — nothing collected | unavailable | No |
| Claude | Unavailable locally | N/A — no local artifact observed | N/A — no local usage evidence | N/A | N/A — no artifact inspected | N/A — nothing collected | unavailable | No |

## Codex: Selected First Provider

### Structured evidence and permitted fields

The existing recommendation remains Codex. Its already-observed structured
local sources are JSONL session metadata and SQLite log metadata. The adapter
may emit only these permitted fields:

| Field | Status | Reliability / handling |
| --- | --- | --- |
| provider | available | exact fixed value: `codex` |
| source identifier | available | sanitized or project-relative identifier only |
| event identifier | available | opaque identifier; never an account identifier |
| occurred/captured time | available | exact metadata timestamp / collection time |
| model-provider metadata | available | exact metadata when present |
| activity-byte proxy | available | estimated activity proxy; never tokens |
| input tokens, output tokens, cost, quota | unavailable | record as unknown; never estimate |

### Sanitized schema samples

```json
{
  "timestamp": "<ISO_8601_TIMESTAMP>",
  "type": "session_meta",
  "payload": {
    "session_id": "<SESSION_UUID>",
    "id": "<EVENT_UUID>",
    "model_provider": "<MODEL_PROVIDER>"
  }
}
```

```text
ts: <EPOCH_TIMESTAMP>
level: <LOG_LEVEL>
estimated_bytes: <INTEGER>
thread_id: <THREAD_UUID>
```

### Freshness, privacy, and redaction

- Session metadata is written while an active session runs; the index updates
  at session boundaries and log metadata accumulates during operation.
- Do not read or copy raw `content`, instruction, feedback, message, project
  path, configuration-value, credential, cookie, account, or source-code data.
- Omit unredacted paths and content-bearing fields. Opaque event identifiers,
  timestamps, allowed model metadata, and the activity proxy may be retained.

## Non-Codex Provider Notes

### OpenCode

No local usage artifact was observed. All required fields are explicitly N/A in
the matrix; no directory, project, or configuration content was inspected or
recorded.

### Hermes

Only local configuration presence was previously observed. It is not usage
evidence: no machine-readable usage record and no usage fields were observed.
Configuration values remain out of scope and are not copied.

### Reasonix, MiMo Code, Antigravity, and Claude

No local usage artifact was observed for these providers. Their required fields
are N/A in the matrix, with no unverified location, format, or field claim.

## Recommendation

Select exactly one first-provider candidate: **Codex**. It has reproducible,
machine-readable local metadata with a bounded redaction rule. The first adapter
must report token, cost, and quota as `unknown` and must not use an activity
proxy as a token estimate.
