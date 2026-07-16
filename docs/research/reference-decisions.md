# Reference Decisions

## Applied

### Ponytail: smallest safe solution

Use the dependency ladder: reuse standard-library SQLite, Tkinter, JSON, and
file metadata before adding libraries. This directly supports a low CPU/memory
desktop tool. Safety, privacy, validation, and data-loss protections are not
trade-offs for fewer lines of code.

### Grill-style challenge and document verification

Every provider claim must be challenged against an observed local source:
where it comes from, which fields are available, how fresh it is, whether it
contains sensitive data, and which values are unknown. A planned adapter cannot
be described as real until a redacted fixture and end-to-end evidence exist.

### Handoff: compact, repository-backed continuity

Task cards, delivery reports, incidents, and review records carry the essential
handoff state. They link to architecture and evidence rather than duplicating
large conversational context.

### Codebase-memory MCP: local structural cache, not repeated context loading

Adopt the principle, not the tool as an MVP dependency: persist compact local
indexes/cursors and query the smallest needed evidence. Full source files and
session transcripts are neither collected nor embedded in prompts.

### RTK: reduce expensive payloads at the boundary

The collector never calls an LLM. Its outputs are compact aggregate records and
freshness metadata, not raw logs. Any future diagnostics must summarize local
metadata before exposing data to an agent.

## Deliberately Not Applied in MVP

### Open Computer Use

Desktop automation needs broad screen/input permissions and may add API/compute
cost. The collector is read-only and must not control agent applications. It is
therefore out of scope except as a possible later manual UI-test tool.

## Sources

- https://github.com/DietrichGebert/ponytail
- https://github.com/DeusData/codebase-memory-mcp
- https://github.com/rtk-ai/rtk
- https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me
- https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs
- https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff
- https://github.com/iFurySt/open-codex-computer-use
