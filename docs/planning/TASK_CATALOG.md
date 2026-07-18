# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `complete-planning`, `in-progress-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when normative behavior and required planning-grade artifacts exist, references resolve and applicable planning validation has been performed. It does not imply implementation or production evidence.

## Stable completed planning groups

| IDs | Scope | Status | Primary evidence |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, metadata and research classification | complete-planning | `AGENTS.md`, `docs/project/`, research README |
| P-051..055 | complete scope, staged delivery, glossary, journeys and launch gates | complete-planning | scope freeze and product/operations contracts |
| P-101..105 | accounting, pricing, comparability, periods and corrections | complete-planning | accounting and time contract |
| P-401..409 | native topology, storage, recovery, IPC, platforms, devices, CLI and budgets | complete-planning | native runtime/storage contract |
| P-501..505 | identity, native auth, linked accounts, recovery and authorization | complete-planning | ADR-006 and authentication contract |
| P-601..606 | server transactions, workers, ranking and recovery behavior | complete-planning | server API/data/ranking contract |
| P-901..905 | routes, states, privacy UX, evidence presentation and accessibility | complete-planning | social/UX and native contracts |
| P-1110..1114 | benchmarks, review lenses, work decomposition, defaults and consolidation | complete-planning | corresponding planning documents |

## Planning-hardening tasks

| ID | Task | Status | Current evidence |
|---|---|---|---|
| P-1120 | Planning-grade JSON Schema, CDDL, Protobuf, OpenAPI, SQL, reason, policy and observability artifacts | in-progress-planning | drafts committed; parser/toolchain validation and coverage review still required |
| P-1121 | Repair adversarial and adapter registries with schemas and consistent vocabularies | complete-planning | schema-backed canonical registries; obsolete registry removed |
| P-1122 | Close challenge batching, partial acceptance, sequence-gap and recovery semantics | complete-planning | ADR-007 plus claim, API and SQL drafts |
| P-1123 | Centralize configurable defaults, ranges, ownership, versioning and retroactivity | complete-planning | ADR-008 and policy registry; defaults document reconciled |
| P-1124 | Resolve license, contribution, security reporting and CODEOWNERS contradictions | complete-planning | ADR-009, LICENSES, CONTRIBUTING, SECURITY and real CODEOWNERS |
| P-1125 | Distinguish current repository tree from approved future tree | complete-planning | `REPOSITORY_LAYOUT.md` and updated handoff |
| P-1126 | Add read-only repository doctor for files, links, IDs, registries, governance and phase consistency | in-progress-planning | doctor and pinned planning workflow committed; clean-checkout run evidence pending |
| P-1127 | Define deterministic issue-generation plan without duplicating task authority | complete-planning | issue-generation contract and offline generator |
| P-1128 | Re-run full planning-hardening audit | in-progress-planning | repair report and stale-string sweep complete; clean-checkout doctor and independent review pending |

## Evidence-gated future tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore and prove product CI, security, dependency, eval and release checks | blocked-implementation | requires executable product code |
| P-1104 | Enter implementation phase | blocked-approval | requires P-1120, P-1126 and P-1128 completion plus explicit user instruction |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing evidence |

## Current conclusion

The repository remains in planning-hardening. The remaining work is validation and coverage closure, not product implementation.
