# Codex JSONL Fixture Adapter

## Overview

The `codex_jsonl_adapter` module provides a fixture-backed parser for Codex
JSONL session metadata. It emits `NormalizedUsageRecord` values using only
the accepted inventory fields from the provider source inventory.

## Privacy Boundary

- **Synthetic fixtures only**: The adapter accepts JSONL text or file paths
  to synthetic fixtures. It never inspects, copies, or requires real local
  Codex session, log, SQLite, TOML, credential, or configuration files.
- **Content-bearing fields ignored**: Lines containing any of these keys
  are silently ignored:
  - `raw_prompt`, `raw_response`, `prompt`, `response`
  - `instruction`, `feedback`, `content`, `message`, `messages`, `text`
  - `api_key`, `cookie`, `cookies`, `account`
  - `project_path`, `source_code`, `code`, `credentials`
- **Tokens, cost, quota are None**: The adapter always sets `tokens_input`,
  `tokens_output`, `cost`, and `quota` to `None`. Activity-byte metadata
  is never converted to token estimates.
- **Source identifiers are logical labels**: Fixture files use logical
  labels (e.g., `valid_metadata`, `synthetic-codex-fixture`) instead of
  absolute paths. The persistence boundary sanitizes any unsafe paths
  that a caller might provide.

## Accepted Metadata Fields

| Field | Source | Handling |
|-------|--------|----------|
| `provider` | Fixed value `"codex"` | Always set |
| `source_identifier` | Logical label or file stem | Sanitized by persistence |
| `event_id` | `payload.id`, `payload.event_id`, `payload.session_id`, `payload.log_id` | Required; line ignored if missing |
| `occurred_at` | `timestamp`, `ts`, `occurred_at`, `time` | Required; epoch seconds converted to ISO 8601 |
| `captured_at` | Same as `occurred_at` | Set equal to occurred_at |
| `model` | `payload.model_provider`, `payload.model`, `payload.model_name` | Optional; `None` if absent |
| `tokens_input` | N/A | Always `None` |
| `tokens_output` | N/A | Always `None` |
| `cost` | N/A | Always `None` |
| `quota` | N/A | Always `None` |
| `source_reliability` | Fixed value `"exact"` | Synthetic data is exact |
| `source_provenance` | N/A | Always `None` |

## Cursor Behavior

The adapter returns a deterministic opaque cursor in `ParseResult.next_cursor`.
The cursor is a SHA-256 hash of `{source_label}:{lines_processed}:{lines_ignored}`,
truncated to 24 hex characters with a `cursor:` prefix.

- Same input always produces the same cursor.
- Different line counts or ignore counts produce different cursors.
- The cursor is suitable for a later bounded poller but does not add a
  polling loop, watcher, or network call.

## Unsupported Sources

The following are explicitly out of scope:

- Real Codex session files, SQLite databases, or TOML configuration
- Live directory scanning or file watching
- Network calls, browser automation, or API polling
- Any provider other than Codex (until a new adapter is added)

## Residual Privacy Limitations

- The adapter trusts that synthetic fixtures do not contain real user data.
  If a caller passes a real Codex file, the adapter would parse it; however,
  content-bearing fields are ignored by key name, not by value inspection.
- Source identifiers provided as absolute paths will be sanitized by the
  persistence boundary, but the adapter itself does not sanitize inputs.
- The adapter does not validate that timestamps are plausible or that event
  IDs are truly unique across sessions.

## Usage

```python
from usage_collector.codex_jsonl_adapter import parse_fixture_text, parse_fixture_file

# Parse JSONL text
result = parse_fixture_text(
    '{"timestamp": "2026-07-19T10:00:00Z", "payload": {"id": "evt-001"}}',
    source_label="my-fixture"
)
for record in result.records:
    print(record.dedupe_key)

# Parse a JSONL file
result = parse_fixture_file("path/to/synthetic.jsonl")
print(f"Parsed {len(result.records)} records, cursor: {result.next_cursor}")
```
