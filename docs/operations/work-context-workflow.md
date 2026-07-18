# Work Context Workflow

This project uses a compact context kit to make work recoverable across agent
sessions without repeatedly loading every design or research document.

Read in order:

1. `AGENTS.md` for rules and safety boundaries.
2. `PLAN.md` for outcome and milestone.
3. `PROGRESS.md` for current factual state and blockers.
4. `TASKS.md` and the assigned task card for authoritative work status.
5. `DECISIONS.md`, `ARCHITECTURE.md`, and `MEMORY.md` only when required.

The task board remains authoritative. Context files summarize and route work;
they never replace task-card state, tests, delivery evidence, or review.

Every milestone follows:

```text
intake -> orient -> plan -> scoped task -> implement -> verify/review
       -> release/operate -> record learning
```

Before accepting a change, check data privacy, correctness, low resource use,
failure behavior, verification evidence, and compatibility with the MVP's
read-only local-data boundary.
