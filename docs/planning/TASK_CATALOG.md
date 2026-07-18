# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `ready`, `in-progress`, `blocked-planning`, `complete-planning`, `deferred`.

## P-000 — Repository truth and phase gate

| ID | Task | Status | Output |
|---|---|---|---|
| P-001 | Align authority order across root files | in-progress | consistent precedence |
| P-002 | Enforce planning-only phase in prompts and agent instructions | in-progress | no accidental implementation |
| P-003 | Define evidence labels and completion rules | complete-planning | model operating manual |
| P-004 | Define decision register and dependency map | complete-planning | planning control docs |
| P-005 | Define artifact lifecycle and generated-file policy | ready | artifact policy |
| P-006 | Define branch protection and required-check policy | ready | repository operations spec |

## P-100 — Product, metrics, and accounting

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-101 | Freeze product glossary and consumer terminology | ready | P-001 | canonical glossary |
| P-102 | Resolve Token Burn category semantics | ready | P-101 | versioned accounting rules |
| P-103 | Define retries, failures, streaming, cache, reasoning, tools, images, compaction, and subagents | ready | P-102 | edge-case matrix |
| P-104 | Define Cash Burn estimation and subscription/local-model policy | ready | P-102 | pricing interpretation contract |
| P-105 | Freeze time periods, time zones, late events, streaks, ties, and resets | ready | P-101 | ranking policy ADR/update |

## P-200 — Adapter system

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-201 | Freeze adapter manifest schema | ready | P-102 | JSON Schema and examples |
| P-202 | Freeze normalized agent event schema | ready | P-102 | versioned event contract |
| P-203 | Define source authority and reconciliation rules | ready | P-202 | source precedence matrix |
| P-204 | Define capability degradation and unsupported-mode behavior | ready | P-201 | state machine |
| P-205 | Define certification, upgrade, privacy-negative, and double-count tests | ready | P-201..204 | conformance plan |

## P-300 — VibeProof protocol

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-301 | Freeze claim field inventory and invariants | ready | P-202 | field-level specification |
| P-302 | Freeze canonical CBOR profile and CDDL | blocked-planning | P-301 | canonical schema |
| P-303 | Freeze COSE algorithms, protected headers, key IDs, and algorithm agility | ready | P-301 | signing profile |
| P-304 | Define claim, parser, verifier, and rejection error taxonomy | ready | P-301..303 | stable error registry |
| P-305 | Define sequence, replay, duplicate, clock, session, and crash semantics | ready | P-301 | protocol state machines |
| P-306 | Define golden vectors, malformed vectors, fuzz, resource, and differential test plans | ready | P-302..305 | conformance plan |

## P-400 — Local collector, IPC, storage, identity

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-401 | Freeze local process and privilege separation model | ready | P-301 | component contract |
| P-402 | Freeze collector local database schema and retention | ready | P-301, P-305 | storage specification |
| P-403 | Define crash consistency, checkpoints, retries, and offline queue | ready | P-402 | state machine |
| P-404 | Freeze IPC message schemas, authentication, limits, and errors | ready | P-401 | IPC protocol |
| P-405 | Freeze macOS, Windows, Linux, WSL, and container capability matrix | ready | P-401, P-404 | platform matrix |
| P-406 | Freeze device enrollment, rotation, revocation, clone, and loss flows | ready | P-303, P-305 | identity state machine |
| P-407 | Define CPU, memory, battery, disk, startup, and throughput benchmark plans | ready | P-401..405 | benchmark protocol |

## P-500 — Server, data, and ranking

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-501 | Freeze ingestion API requests, responses, auth, limits, and rejection codes | ready | P-304, P-406 | API contract |
| P-502 | Freeze PostgreSQL entities, keys, constraints, and migrations | ready | P-501 | logical schema |
| P-503 | Freeze claim acceptance transaction and idempotency boundaries | ready | P-502 | transaction specification |
| P-504 | Freeze outbox, worker, aggregate, rollover, late-event, and rebuild behavior | ready | P-503 | worker state machine |
| P-505 | Freeze leaderboard queries, tie policy, pagination, current-user rank, and cache | ready | P-105, P-504 | query contract |
| P-506 | Define capacity, load, duplicate-storm, crash, and rebuild benchmarks | ready | P-502..505 | benchmark protocol |

## P-600 — Web and privacy UX

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-601 | Freeze routes and information architecture | ready | P-101, P-505 | route map |
| P-602 | Freeze leaderboard data contract and all UI states | ready | P-505 | frontend contract |
| P-603 | Freeze privacy-verification payload, copy, and local audit UX | ready | P-301, P-401 | UX specification |
| P-604 | Freeze evidence-state presentation and explanation | ready | P-204 | content and component spec |
| P-605 | Define accessibility, responsive, browser, visual, and performance test plans | ready | P-601..604 | QA plan |

## P-700 — Authentication, social, and abuse

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-701 | Freeze account, passkey, session, recovery, and revocation state machines | ready | P-406 | auth contract |
| P-702 | Freeze friends, rivals, presence, groups, private boards, and notifications | ready | P-505, P-701 | social domain model |
| P-703 | Freeze privacy and authorization matrix for profiles and boards | ready | P-702 | permission matrix |
| P-704 | Freeze abuse signals, quarantine, restrictions, device revocation, and appeals | ready | P-503, P-701 | moderation state machine |
| P-705 | Freeze retention, audit, deletion, and export behavior | ready | P-502, P-704 | lifecycle contract |

## P-800 — Packaging and operations

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-801 | Freeze supported platform and installation matrix | ready | P-405 | packaging matrix |
| P-802 | Freeze TUF roles, bootstrap root, rotation, update, rollback, and uninstall | ready | P-801 | updater state machine |
| P-803 | Freeze observability event allowlist, fields, sampling, access, and retention | ready | all domains | telemetry schema |
| P-804 | Freeze environments, configuration, secrets, migrations, and release promotion | ready | P-501, P-502 | deployment contract |
| P-805 | Freeze backup, restore, disaster recovery, incident, rollback, and key-compromise playbooks | ready | P-802..804 | operations plan |

## P-900 — Final readiness review

| ID | Task | Status | Dependencies | Required output |
|---|---|---|---|---|
| P-901 | Cross-document contradiction audit | blocked-planning | P-100..800 | zero unresolved P0 contradictions |
| P-902 | Privacy and threat-control traceability review | blocked-planning | P-100..800 | traceability matrix |
| P-903 | Schema, API, state-machine, and task completeness review | blocked-planning | P-100..800 | implementation handoff report |
| P-904 | User approval to enter implementation phase | blocked-planning | P-901..903 | explicit phase change |

## Task completion rule

A task is `complete-planning` only when its output is committed, cross-linked, internally consistent, and contains implementation interfaces, negative cases, limits, evidence, and unresolved questions. Prose that merely restates goals does not complete a task.