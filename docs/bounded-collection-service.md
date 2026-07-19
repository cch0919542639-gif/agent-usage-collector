# Bounded Collection Service

`collect_codex_fixture` performs one on-demand collection pass for exactly one
caller-supplied JSONL fixture or pre-approved source path. It uses the accepted
Codex JSONL adapter and persists only the adapter's `NormalizedUsageRecord`
output through `UsageRepository`.

## Explicit-input boundary

The service never searches directories, derives paths from a user profile, or
opens a real provider session by itself. The caller provides the path for each
single pass. The default logical source label is `codex-fixture`; no absolute
path is included in the collection result.

## Cursor behaviour

The repository stores the adapter's opaque byte-offset cursor under the
`codex` provider after a successful bounded parse. A later call begins at that
cursor, so an unchanged input returns `health="unchanged"` and does not insert
records. Database uniqueness still reports repeated event IDs in one input as
skipped rather than storing duplicates.

## Safety and limitations

- No scheduler, watcher, polling loop, network request, source discovery, or
  new dependency is introduced.
- Malformed and content-bearing JSONL records are ignored by the adapter.
- An unreadable path returns `source_unavailable` without embedding the path
  in result metadata.
- Token, cost, and quota values remain unknown (`None`); activity bytes are
  not converted into a token estimate.
