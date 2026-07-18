# ChatGPT Continuous Research and Repository Audit Workflow

Updated: 2026-07-19
Status: planning workflow; no product implementation authorized

## Purpose

Provide a repeatable workflow for ChatGPT or another strong research model to audit the repository, verify current external facts, identify better technical approaches, close planning decisions, and update the repository without relying on chat history.

## Operating rule

The workflow is research-first and repository-grounded. The model must inspect existing files before proposing new work. It must distinguish accepted decisions, provisional choices, unresolved research, placeholders, and implementation evidence.

During the current phase it may improve planning documents, ADRs, schemas, threat models, task definitions, benchmark designs, test plans, and acceptance gates. It must not implement the product unless the user explicitly changes the phase.

## Inputs

Read in this order:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `docs/planning/PLANNING_AUDIT.md`
6. `docs/planning/DECISION_REGISTER.md`
7. `docs/planning/DEPENDENCY_MAP.md`
8. `docs/planning/TASK_CATALOG.md`
9. `docs/planning/SPECIFICATION_INDEX.md`
10. Relevant product, architecture, privacy, security, engineering, operations, and research files
11. Recent repository commits, issues, and pull requests when available

## Audit cycle

### Step 1 — Repository truth audit

Determine:

- what exists;
- what is specification-only;
- what is executable;
- what is placeholder scaffolding;
- which generated artifacts are stale;
- which files contradict each other;
- which decisions lack IDs or owners;
- which tasks lack dependencies, outputs, or completion gates;
- whether the current phase and launch scope are represented consistently.

Do not infer implementation from directory names or README files.

### Step 2 — Assumption and contradiction audit

List every material assumption that could cause wasted implementation or security/privacy failure. Classify each as:

- accepted and supported;
- accepted but insufficiently specified;
- provisional;
- research-required;
- contradicted;
- stale external fact;
- unsupported claim.

Update the planning audit and decision register when appropriate.

### Step 3 — External research

Research only questions that can close a named decision or improve a named contract. Prefer primary sources:

- official documentation;
- standards and RFCs;
- upstream repositories and conformance suites;
- peer-reviewed or authoritative security research;
- vendor platform security documentation;
- official pricing and product documentation;
- maintained benchmark or interoperability projects.

For each finding record:

- question investigated;
- sources and dates;
- evidence quality;
- conclusion;
- uncertainty;
- implications for VibeMaxxing;
- decision/task IDs affected;
- executable validation still required.

Do not perform broad trend research without a decision target.

### Step 4 — Architecture and product challenge

Act as a skeptical founding CTO, security architect, privacy engineer, product lead, and operations reviewer. Challenge:

- unnecessary complexity;
- missing interfaces and state machines;
- unrealistic launch gates;
- hidden privacy leakage;
- weak anti-cheat assumptions;
- platform-specific gaps;
- brittle adapter strategies;
- unverifiable support claims;
- poor recovery and appeal behavior;
- cost, battery, memory, and latency risks;
- open-source maintenance burden;
- user experience that does not match the Competitive Ledger thesis.

A critique must include a concrete correction or research task.

### Step 5 — Decision closing

For each research question, produce one of:

- accept a decision;
- reject a candidate;
- keep provisional with a clear reopen/closure condition;
- require an executable spike, benchmark, conformance test, or user study;
- defer with explicit reason and dependency.

Update ADRs or the decision register. Never silently turn a recommendation into an accepted fact.

### Step 6 — Repository update

When authorized to write, update the minimum authoritative files needed. Every update must preserve:

- one consistent authority order;
- current planning-only phase;
- complete public-launch scope with staged internal delivery;
- privacy boundary;
- evidence honesty;
- open-source independence;
- stable task and decision IDs.

Avoid creating duplicate reports. Amend the current canonical document or clearly supersede it.

### Step 7 — Output report

Produce:

1. Executive summary.
2. Highest-risk findings.
3. Contradictions and stale assumptions.
4. New research findings with sources.
5. Decisions closed or reopened.
6. Repository files changed.
7. Next five highest-value planning tasks in dependency order.
8. Questions requiring user product judgment.
9. Things explicitly not done because the project remains in planning.

## Research lanes

Rotate through these lanes while prioritizing current blockers:

1. Product scope, glossary, user journeys, and launch completeness.
2. Universal agent/provider compatibility and adapter certification.
3. Token accounting and Estimated Cash Burn semantics.
4. Anti-cheat, SLM feasibility, attestation, replay, cloning, and appeals.
5. VibeProof encoding, signing, versioning, interoperability, and fuzzing.
6. Collector, local daemon, CLI, menu-bar/tray client, IPC, storage, and updates.
7. OAuth authentication, account recovery, sessions, and identity abuse.
8. Database, ingestion, aggregation, ranking, periods, ties, and rebuilds.
9. Social graph, rivals, presence, boards, organizations, communities, and countries.
10. Web dashboard, accessibility, mobile behavior, privacy verification, and design quality.
11. Deployment, observability, moderation, incident response, deletion, backup, and recovery.
12. Open-source governance, contributor safety, release process, and maintainability.

## Quality bar

A research cycle is useful only when it produces at least one of:

- a closed decision;
- a clarified implementation contract;
- a new attack/control mapping;
- a benchmark or conformance plan;
- a removed contradiction;
- a discovered privacy/security risk;
- a better staged dependency order;
- a user decision that is now precisely framed.

A long report without one of these outcomes is not completion.

## Research log

Each substantial cycle should add or update a dated report under `docs/research/` and link affected decision and task IDs. The canonical decision register, task catalog, planning audit, and specification index must remain current after the report is written.