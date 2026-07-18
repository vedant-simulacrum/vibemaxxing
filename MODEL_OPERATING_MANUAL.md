# VibeMaxxing Model Operating Manual

## Purpose

This is the canonical entrypoint for any model, coding agent, researcher, or reviewer working from this repository without prior conversation history.

VibeMaxxing is currently in **planning and decision-closing mode**. Do not begin product implementation unless the user explicitly opens an implementation phase. Planning work may add or revise specifications, ADRs, threat models, research plans, schemas, task definitions, test plans, benchmark designs, and acceptance criteria.

## Authority and precedence

When materials disagree, use this order:

1. The user's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. `PROJECT_INSTRUCTIONS.md`.
4. `CURRENT_STATUS.md`.
5. This manual.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. The nearest `AGENTS.md`.
9. Accepted ADRs and current specifications.
10. Historical research documents.

Never silently choose between contradictory sources. Record the contradiction in `docs/planning/PLANNING_AUDIT.md`, resolve it through the precedence above, and update the stale source when authorized.

## Mandatory reading order

Before planning or changing anything, read:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `IMPLEMENTATION_ROADMAP.md`
6. `RESEARCH_AND_EVIDENCE_BACKLOG.md`
7. `docs/planning/DECISION_REGISTER.md`
8. `docs/planning/DEPENDENCY_MAP.md`
9. `docs/planning/TASK_CATALOG.md`
10. The nearest `AGENTS.md`
11. Relevant ADRs, product specifications, privacy contract, threat model, acceptance gates, and research audits

## Current phase boundary

Allowed now:

- audit and reconcile repository context;
- close product, protocol, security, privacy, architecture, data, UX, operations, and release decisions;
- research current technical facts using primary sources;
- produce implementation-ready specifications;
- define APIs, schemas, state machines, invariants, fixtures, benchmarks, adversarial cases, and acceptance tests;
- turn ambiguous roadmap items into atomic tasks with owners, dependencies, evidence, and completion gates;
- improve CI and repository policy only when it validates planning artifacts and does not implement the product.

Not allowed now without a new explicit instruction:

- implementing production adapters, collectors, APIs, database workers, authentication, social features, web product, native packages, or deployment infrastructure;
- claiming an implementation exists because a design, README, fixture declaration, or placeholder exists;
- turning planning artifacts into fake passing evals;
- changing the product thesis, privacy boundary, core metrics, evidence language, or accepted stack without an ADR and explicit approval.

## Required planning workflow

For every planning task:

1. Identify the exact decision or ambiguity being closed.
2. Read all relevant current and historical repository material.
3. Verify unstable external facts with primary sources.
4. State constraints, invariants, non-goals, and threat assumptions.
5. Compare credible alternatives and explain rejection reasons.
6. Produce an implementation contract: interfaces, data model, state transitions, errors, limits, migrations, compatibility, observability, privacy, and security behavior.
7. Define deterministic fixtures, negative tests, performance tests, adversarial tests, and acceptance evidence.
8. Update the decision register, dependency map, task catalog, roadmap, status, and relevant ADR/specification.
9. Leave no hidden dependency on chat history.

## Definition of planning-ready

A component is planning-ready only when the repository defines:

- purpose and user-visible behavior;
- trust boundaries and threat assumptions;
- inputs, outputs, schemas, invariants, and error semantics;
- platform-specific behavior and capability degradation;
- privacy allowlist and forbidden data;
- authentication and authorization expectations where relevant;
- storage, retention, migration, deletion, and recovery behavior;
- performance and resource budgets;
- observability that cannot leak prohibited content;
- dependency order and integration boundaries;
- deterministic test fixtures and acceptance criteria;
- unresolved questions, named owners, and the evidence needed to resolve them.

If any of these are missing, mark the task as `blocked-planning`, not implementation-ready.

## Evidence discipline

Use these evidence labels consistently:

- `specified`: behavior is documented but not implemented.
- `prototyped`: a disposable experiment exists; no production claim.
- `implemented`: production-target code exists and has unit/integration tests.
- `exercised`: behavior passed tests against a real supported system or platform.
- `hardened`: adversarial, privacy, recovery, performance, and upgrade evidence passes.
- `not_applicable`: the owning milestone has not begun; include an owner and activation condition.

Never upgrade an evidence label from prose alone.

## Model output contract

At the start of a session, report:

- current phase;
- authoritative files read;
- highest-priority unblocked planning task;
- contradictions or stale facts found;
- files that will be updated;
- explicit confirmation that product implementation will not begin.

At the end, report:

- decisions closed;
- files changed;
- remaining uncertainties;
- newly unblocked tasks;
- tasks still blocked and why;
- next exact planning task.

Do not stop with a generic plan. Produce repository changes that make a later implementation agent safer and more deterministic.