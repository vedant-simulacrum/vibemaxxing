# Prompt for a new VibeMaxxing model

Read, in order:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `IMPLEMENTATION_ROADMAP.md`
6. `RESEARCH_AND_EVIDENCE_BACKLOG.md`
7. `docs/planning/PLANNING_AUDIT.md`
8. `docs/planning/DECISION_REGISTER.md`
9. `docs/planning/DEPENDENCY_MAP.md`
10. `docs/planning/TASK_CATALOG.md`
11. The nearest `AGENTS.md` and relevant ADRs/specifications

## Current phase

VibeMaxxing is in **planning and decision-closing mode**. Do not implement the product, execute deployment, build production adapters, or create placeholder scaffolding unless the user explicitly changes the phase.

The repository must become sufficient for a future implementation model to work without prior chat context.

## First response

Report:

1. Files read and current phase.
2. Highest-priority unblocked planning task ID from `TASK_CATALOG.md`.
3. Contradictions, stale assumptions, unresolved decisions, or missing contracts found.
4. Exact files you will update.
5. Confirmation that no product implementation will begin.

## Planning work standard

For the selected task:

- close a named decision or ambiguity;
- verify unstable technical facts with primary sources;
- define interfaces, schemas, state machines, invariants, limits, failures, privacy, security, storage, migration, recovery, compatibility, and observability behavior;
- define deterministic fixtures, negative tests, adversarial cases, performance tests, and acceptance evidence;
- update the decision register, dependency map, task catalog, roadmap, status, and affected specifications;
- leave no dependency on hidden chat context.

Do not mark planning complete from broad prose. A planning task is complete only when a later implementation agent can build it without inventing critical behavior.

## Non-negotiable constraints

- No prompts, responses, transcripts, code, diffs, filenames, paths, repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights may be sent to VibeMaxxing servers.
- Historical imports never enter active competitive rankings.
- Token Burn is the default ranking metric.
- Cash Burn is always explicitly estimated.
- Weak evidence never masquerades as strong evidence.
- Development remains local-first; cancelled remote control-plane plans must not be revived.
- Current accepted stack and ADRs remain binding unless reopened through an evidence-backed ADR.

At the end, report decisions closed, files changed, remaining blockers, newly unblocked task IDs, and the next exact planning task.