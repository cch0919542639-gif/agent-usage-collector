# Privacy Verification Checklist

## Purpose

Prove that the research artifacts in `docs/research/` contain no secrets,
raw session content, or private data that should not be committed to the
repository.

## Checklist

### 1. No Credentials or API Keys

- [x] No API keys, tokens, or secrets appear in any research document
- [x] No `auth.json`, `cap_sid`, or credential file contents referenced
- [x] No environment variable values containing secrets

### 2. No Prompt or Response Content

- [x] No raw `content` fields from session JSONL files copied
- [x] No `feedback_log_body` values from SQLite logs copied
- [x] No `base_instructions` content referenced
- [x] No conversation text or message history included

### 3. No Absolute User Paths

- [x] All absolute paths redacted to `<USER_HOME>` or project-relative form
- [x] No `cwd` field values with personal directory structures
- [x] No `config.toml` `projects` paths with personal directories

### 4. No Account Identifiers

- [x] No email addresses, usernames, or account IDs referenced
- [x] No `installation_id` values copied
- [x] No browser cookies or session tokens referenced

### 5. No Source Code Content

- [x] No `.rs`, `.py`, `.ts`, or other source file contents included
- [x] Only schema descriptions and field names referenced
- [x] No `module_path` or `file` field values from logs included

### 6. Schema Examples Are Sanitized

- [x] All JSON examples use placeholder UUIDs (`<SESSION_UUID>`, `<EVENT_UUID>`)
- [x] All SQLite examples use redacted thread IDs (`<THREAD_UUID>`)
- [x] No real timestamps from user sessions (only format descriptions)
- [x] No real model names or version strings from user config

### 7. No Browser or Network Data

- [x] No browser storage accessed (cookies, localStorage, IndexedDB)
- [x] No network requests made during research
- [x] No API responses captured

### 8. No Private Account Data

- [x] No billing information, subscription details, or account status
- [x] No usage quotas or limits from provider dashboards
- [x] No personal preferences or settings beyond config schema

## Verification Method

All checks were performed by:
1. Inspecting filesystem paths and directory structures only
2. Reading file schemas (keys, column names, event types) without content
3. Using `json.loads()` to parse structure, not display content
4. Using `sqlite3` PRAGMA and COUNT queries, not SELECT * on data

## Sign-Off

- [x] All items verified
- [x] No exceptions found
- [x] Ready for commit
