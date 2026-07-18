# Prompt for a new VibeMaxxing model

Read, in order:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `docs/planning/DECISION_REGISTER.md`
5. `docs/planning/TASK_CATALOG.md`
6. `docs/planning/SPECIFICATION_INDEX.md`
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md`
8. The relevant normative subsystem contracts and nearest `AGENTS.md`

## Phase

Technical planning is complete. Product implementation is blocked until the user explicitly approves P-1104. Do not repeat broad planning or invent missing scope; the normative contract set is the source of truth.

## First response

Report:

1. Files read and whether explicit implementation approval exists.
2. Current task/gate.
3. Any genuine contradiction found, with exact files.
4. Exact implementation slice or planning correction proposed.
5. Confirmation that executable evidence will not be claimed before it exists.

## After implementation approval

Follow the build order in `docs/implementation/IMPLEMENTATION_HANDOFF.md`: contract workspaces, synthetic vertical slice, native boundary, identity, adapter platform, ranking/social, full UX, integrity hardening, operations, open-source release and launch.

Preserve the privacy boundary, complete launch scope, tiered support, OAuth identity, evidence policy, accounting semantics, state machines, data lifecycle and launch gates. Material changes require the decision register and an ADR.

At the end of each task report code/files changed, tests and benchmarks run, privacy/security results, migrations and rollback, remaining risks, and next unblocked task.
