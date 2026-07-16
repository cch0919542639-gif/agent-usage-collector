# First Live Phase Rollout

## Phase: MVP Foundation

This is the first live project using the coordination workflow. The objective is
to build a trustworthy, low-overhead base before reading any real provider log.

## Parallel Wave 1

| Task | Owner | Purpose | Dependency |
| --- | --- | --- | --- |
| `usage-mvp-01` | `external-agent-research-01` | Inventory and redact candidate local sources. | None |
| `usage-mvp-02` | `external-agent-platform-25` | Build provider-neutral records, SQLite dedupe, cursor, and aggregates. | None |

These tasks may run in parallel because `usage-mvp-01` changes only research
documents and `usage-mvp-02` must not implement a provider parser.

## Sequential Wave 2

1. Select the first provider only after the inventory evidence is reviewed.
2. Implement one read-only collector against a redacted fixture and confirmed
   source contract.
3. Add the Tkinter overlay using the provider-neutral aggregate interface.

## Gate

No collector may read a real source before its data fields, redaction boundary,
and file access rules are accepted. No UI may claim a value is precise when the
underlying record marks it unknown or estimated.
