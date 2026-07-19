# Codex JSONL Metadata Adapter

## Purpose

The `CodexJsonlAdapter` (`parse_codex_jsonl` / `parse_codex_jsonl_file`)
parses Codex session metadata from JSONL text or a file path and emits
`NormalizedUsageRecord` values using only the accepted inventory fields.

The adapter is a bounded parsing component. It does not scan directories,
watch files, make network calls, or persist data.

## Accepted Metadata Boundary

The adapter accepts JSONL lines whose top-level object has:

- `timestamp` — ISO 8601 string
- `type` — any metadata type string (e.g. `session_meta`, `session`, `meta`)
- `payload` — a dict that may contain:
  - `id` — opaque event identifier (used as `event_id`)
  - `session_id` — fallback identifier if `id` is absent
  - `model_provider` or `model` — model identifier string (maps to `model`)
  - `estimated_bytes` — stored in `extra` only, never mapped to tokens

Every emitted record sets:
- `provider` to `"codex"`
- `source_reliability` to `"estimated"`
- `tokens_input`, `tokens_output`, `cost`, `quota` to `None`

## Forbidden Content

Lines whose payload or top-level object contains any of these keys
are silently skipped (never parsed, stored, or exposed):

- `content`, `prompt`, `response`
- `instruction`, `feedback`
- `messages`, `choices`
- `credential`, `cookie`, `account`
- `project-path`, `project_path`
- `source-code`, `source_code`

## Unsupported Sources

The adapter only parses Codex JSONL session metadata. It does not support:

- SQLite session logs
- TOML configuration files
- Non-JSONL provider formats
- Binary or compressed input

## Cursor / Checkpoint

Both `parse_codex_jsonl` and `parse_codex_jsonl_file` return a
deterministic cursor string (byte offset) as the second return value.

- Pass the cursor back on a subsequent call to resume from where the
  previous parse stopped.
- The cursor is opaque, deterministic, and suitable for a bounded poller.

## Privacy Limitations

- `source_identifier` and `source_provenance` use a caller-supplied
  logical label. If a caller passes an absolute path as the label, the
  persistence layer will hash it via `sanitize_path_field`.
- Event IDs are opaque but may correlate with user activity across
  sessions if the provider assigns stable identifiers.
- `estimated_bytes` (activity proxy) is stored in `extra` as an
  informational value; it must not be interpreted as a token count.
- No prompt, response, credential, or source-code content is ever
  parsed, exposed, or stored.
