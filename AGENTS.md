# Worker Rules

## Required Workflow

1. Pull the latest `main` in the correct repository.
2. Read the assigned task card and every referenced document before editing.
3. Move only your assigned card from `ready/` to `in_progress/` and update your
   progress record.
4. Work only within `allowed_scope`. Create an incident and stop when blocked.
5. Before submission, run the task's tests and the repository validation
   command, write a delivery report, move the card to `review/`, and push a
   dedicated branch.

## Safety Rules

- Local collectors are read-only. Never read API keys, cookies, prompts,
  responses, or source-code contents from provider files.
- Record an unavailable token/cost field as `unknown`; never manufacture a
  number.
- Prefer Python standard-library facilities before adding a dependency.
- Polling must be bounded and metadata/cursor driven. Do not introduce a busy
  loop, file watcher storm, browser automation, or remote request in the MVP.
- Do not change task lifecycle, owner, reviewer, or another worker's files.

## Delivery Evidence

Every submission includes changed files, validation commands/results, known
risks, handoff recommendation, and acceptance-criteria coverage in
`coordination/delivery/<task-id>-delivery-report.md`.
