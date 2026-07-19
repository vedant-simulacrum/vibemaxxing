# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `complete-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when normative behavior and required planning-grade artifacts exist, references resolve, and applicable planning validation has passed. It does not imply implementation or production evidence.

## Completed planning groups

| IDs | Scope | Status | Primary evidence |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, metadata and research classification | complete-planning | `AGENTS.md`, `docs/project/`, research README |
| P-051..055 | complete scope, staged delivery, glossary, journeys and launch gates | complete-planning | scope freeze and product/operations contracts |
| P-101..105 | accounting, pricing, comparability, periods and corrections | complete-planning | accounting and time contract |
| P-201..208 | adapter compatibility, support registry, certification model and governance | complete-planning | compatibility contract, schema-backed registry and validator |
| P-301..307 | VibeProof fields, encoding, signing, batching, recovery and conformance plan | complete-planning | protocol contract, ADR-007, CDDL and validators |
| P-401..409 | native topology, storage, recovery, IPC, platforms, devices, CLI and budgets | complete-planning | native runtime/storage contract and compiled Protobuf |
| P-501..505 | identity, native auth, linked accounts, recovery and authorization | complete-planning | ADR-006, ADR-008 and authentication contract |
| P-601..606 | APIs, PostgreSQL, transactions, workers, ranking and recovery | complete-planning | validated OpenAPI, PostgreSQL DDL and server contract |
| P-701..708 | social graph, boards, countries, presence, notifications, moderation and lifecycle | complete-planning | social contract, policy registry and event Protobuf |
| P-801..808 | anti-cheat controls, cases, detector gates, calibration and appeals | complete-planning | schema-backed adversarial registry and integrity contracts |
| P-901..905 | routes, states, privacy UX, evidence presentation and accessibility | complete-planning | social/UX and native contracts |
| P-1001..1006 | packages, updates, observability, deployment, recovery and open-source governance | complete-planning | operations contract, ADR-009 and allowlist |
| P-1110..1114 | benchmarks, review lenses, work decomposition, defaults and consolidation | complete-planning | corresponding planning documents |
| P-1120..1128 | schema hardening, registry repair, validation, governance, repository doctor and final audit | complete-planning | planning-hardening validation report and successful workflow |
| P-1130 | Define bespoke Hardened coverage for a rolling top-20 model cohort | complete-planning | D-046, `docs/integrations/T20_MODEL_HARDENING_CONTRACT.md`, and `conformance/models/t20-model-registry-v1.*` |

## Evidence-gated future tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore and prove product CI, security, dependency, eval and release checks | blocked-implementation | requires executable product code |
| P-1104 | Enter implementation phase | blocked-approval | requires a later explicit user instruction |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing evidence |
| P-1131 | Select the current T20 cohort and produce non-expired bespoke Hardened certifications for all 20 slots | blocked-launch-evidence | requires real usage inputs, exact provider versions, adapters, fixtures and exercised conformance |

## Current conclusion

Technical planning is complete at validated contract level. The project remains in planning mode until the user explicitly opens implementation under P-1104. Public launch is additionally blocked until P-1131 passes; generic compatibility cannot substitute for a T20 Hardened slot.