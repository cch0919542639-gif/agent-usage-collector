# Coordination

This project uses repository-backed task cards.

- `task-board/ready/`: assigned but not yet claimed.
- `task-board/in_progress/`: claimed work.
- `task-board/review/`: submitted work awaiting orchestrator review.
- `task-board/done/`: accepted work.
- `progress/`: concise per-agent working state.
- `delivery/`: standardized evidence for a submitted task.
- `incidents/`: blockers that require an orchestrator decision.

Every task card defines the allowed scope, acceptance criteria, and validation
commands. A chat-only response is not a delivery.
