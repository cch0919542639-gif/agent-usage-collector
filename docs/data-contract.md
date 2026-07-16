# Usage Record Data Contract

## Normalized Usage Record

Every provider adapter emits a `NormalizedUsageRecord` with these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | `str` | yes | Source provider name (e.g. `opencode`, `claude-code`) |
| `source_identifier` | `str` | yes | Identifies the specific source file or config |
| `event_id` | `str` | yes | Unique event or session ID within provider scope |
| `occurred_at` | `str` | yes | ISO 8601 timestamp of when the event occurred |
| `captured_at` | `str` | yes | ISO 8601 timestamp of collection time |
| `model` | `str \| None` | no | AI model identifier; `None` if unknown |
| `tokens_input` | `int \| None` | no | Input token count; `None` if unavailable |
| `tokens_output` | `int \| None` | no | Output token count; `None` if unavailable |
| `cost` | `float \| None` | no | Cost in USD or equivalent; `None` if unavailable |
| `quota` | `str \| None` | no | Quota or rate-limit metadata; `None` if absent |
| `source_reliability` | `str` | yes | One of `exact`, `estimated`, `unknown` |
| `source_provenance` | `str \| None` | no | Origin path or metadata; `None` if redacted |

### Dedupe Key

The deterministic dedupe identity is `(provider, event_id)`. Two records with the
same provider and event_id are considered identical regardless of other field
values.

### Forbidden Fields

Raw prompt content, raw response content, API keys, cookies, and unredacted
absolute paths must never appear in a usage record.

## SQLite Schema

### `usage_records`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `provider` | TEXT | NOT NULL |
| `source_identifier` | TEXT | NOT NULL |
| `event_id` | TEXT | NOT NULL |
| `occurred_at` | TEXT | NOT NULL |
| `captured_at` | TEXT | NOT NULL |
| `model` | TEXT | |
| `tokens_input` | INTEGER | |
| `tokens_output` | INTEGER | |
| `cost` | REAL | |
| `quota` | TEXT | |
| `source_reliability` | TEXT | NOT NULL DEFAULT 'unknown' |
| `source_provenance` | TEXT | |

Unique constraint: `(provider, event_id)`

### `provider_cursors`

| Column | Type | Constraints |
|--------|------|-------------|
| `provider` | TEXT | PRIMARY KEY |
| `cursor_value` | TEXT | NOT NULL |
| `updated_at` | TEXT | NOT NULL |

### `aggregate_snapshots`

| Column | Type | Constraints |
|--------|------|-------------|
| `provider` | TEXT | NOT NULL |
| `snapshot_at` | TEXT | NOT NULL |
| `total_tokens_input` | INTEGER | |
| `total_tokens_output` | INTEGER | |
| `total_cost` | REAL | |
| `record_count` | INTEGER | NOT NULL DEFAULT 0 |

Primary key: `(provider, snapshot_at)`

## Database Location

Runtime database files belong under the gitignored `data/` directory and must
never be committed. Test databases use `pytest tmp_path` and are never created
under tracked paths.
