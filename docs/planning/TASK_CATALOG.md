# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `complete-planning`, `in-progress-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when its normative behavior and required planning-grade machine-readable artifacts exist, references resolve, and repository validation passes. It does not imply implementation or production evidence.

## Completed planning groups

| IDs | Scope | Status | Primary evidence |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, metadata, research classification | complete-planning | `AGENTS.md`, `docs/project/`, research README |
| P-051..055 | complete scope, staged delivery, glossary, journeys, launch gates | complete-planning | scope freeze and product/operations contracts |
| P-101..105 | accounting, pricing, comparability, periods, corrections | complete-planning | accounting and time contract |
| P-401..409 | native topology, storage, recovery, IPC, platforms, devices, CLI, budgets | complete-planning | native runtime/storage contract |
| P-501..505 | identity, native auth, linked accounts, recovery, authorization | complete-planning | ADR-006 and authentication contract |
| P-601..606 | server transactions, workers, ranking, recovery behavior | complete-planning | server API/data/ranking contract |
| P-901..905 | routes, states, privacy UX, evidence presentation, accessibility | complete-planning | social/UX and native contracts |
| P-1110..1114 | benchmarks, review lenses, work decomposition, defaults, consolidation | complete-planning | corresponding planning documents |

## Planning-hardening tasks

| ID | Task | Status | Completion evidence |
|---|---|---|---|
| P-1120 | Add planning-grade JSON Schema, CDDL, Protobuf, OpenAPI, SQL, reason-code, policy, and observability artifacts | in-progress-planning | files parse and repository doctor passes |
| P-1121 | Repair adversarial and adapter registries with schemas and consistent vocabularies | in-progress-planning | schema validation and reference checks pass |
| P-1122 | Close challenge batching, partial acceptance, sequence-gap, and recovery semantics | in-progress-planning | protocol contract and schemas agree |
| P-1123 | Centralize configurable defaults, ranges, ownership, versioning, and retroactivity | in-progress-planning | policy registry plus contract references |
| P-1124 | Resolve license, contribution, security-reporting, and CODEOWNERS contradictions | in-progress-planning | governance files and D-040 agree |
| P-1125 | Distinguish current repository tree from approved future target tree | in-progress-planning | implementation handoff updated |
| P-1126 | Add read-only repository doctor for canonical files, links, IDs, registries, placeholders, and phase consistency | in-progress-planning | manual planning workflow invokes doctor successfully |
| P-1127 | Define issue-generation plan without duplicating task authority | in-progress-planning | issue template/generator contract committed |
| P-1128 | Re-run full planning-hardening audit | in-progress-planning | zero unresolved P0/P1 planning defects |

## Evidence-gated future tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore and prove product CI, security, dependency, eval, and release checks | blocked-implementation | requires executable product code |
| P-1104 | Enter implementation phase | blocked-approval | requires explicit user instruction after P-1120..1128 pass |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing evidence |

## Current conclusion

The repository is in planning-hardening, not implementation. P-1104 is not the immediate gate until P-1120 through P-1128 are complete.