# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `complete-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` when committed contracts define ownership, interfaces, fields, invariants, limits, failures, recovery, compatibility, privacy/security behavior, tests, and acceptance evidence. It does not imply implemented or production-proven.

## Completed planning groups

| IDs | Scope | Status | Primary evidence |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, artifacts, metadata, research classification, and governance | complete-planning | `AGENTS.md`, `docs/project/`, metadata generator, research README |
| P-051..055 | complete scope, staged delivery, glossary, journeys, and launch gates | complete-planning | scope freeze and product/operations contracts |
| P-101..105 | accounting, pricing, comparability, periods, and corrections | complete-planning | accounting and time contract |
| P-201..208 | universal adapters, registry, schemas, reconciliation, certification, and governance | complete-planning | compatibility and adapter/VibeProof contracts; agent registry |
| P-301..307 | VibeProof fields, encoding, signing, errors, state, and conformance | complete-planning | adapter and VibeProof contract |
| P-401..409 | native topology, storage, recovery, IPC, platforms, devices, CLI, and budgets | complete-planning | native runtime/storage contract |
| P-501..505 | identity, native auth, linked accounts, recovery, and authorization | complete-planning | ADR-006 and authentication contract |
| P-601..606 | APIs, PostgreSQL, transactions, workers, ranking, and benchmarks | complete-planning | server API/data/ranking contract |
| P-701..708 | social graph, boards, countries, presence, notifications, moderation, and lifecycle | complete-planning | social/integrity/UX contract |
| P-801..808 | anti-cheat controls, campaigns, detector/SLM gates, calibration, and red-team | complete-planning | attack catalog, adversarial registry/tabletops, and integrity contracts |
| P-901..905 | routes, states, local privacy UX, evidence presentation, and accessibility | complete-planning | social/UX and native contracts |
| P-1001..1006 | packages, TUF, observability, deployment, recovery, and open-source governance | complete-planning | operations/open-source/launch contract |
| P-1101 | contradiction and stale-claim review | complete-planning | final planning-exit audit and repository consolidation |
| P-1102 | privacy/threat/control traceability | complete-planning | traceability audit and adversarial evidence plan |
| P-1103 | schema/interface/state/migration/recovery completeness | complete-planning | schema inventory, dry run, and mock handoff |
| P-1110 | benchmark and evidence procedure design | complete-planning | benchmark and evidence protocols |
| P-1111 | independent architecture review lenses | complete-planning | independent architecture reviews |
| P-1112 | PR-sized implementation decomposition | complete-planning | implementation handoff and PR-sized work breakdown |
| P-1113 | provisional defaults and reversal thresholds | complete-planning | provisional defaults contract |
| P-1114 | consolidate repository authority, research, and implementation planning | complete-planning | `docs/project/DOCUMENTATION.md`, canonical `AGENTS.md`, duplicate-file removal |

## Evidence-gated future tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore and prove automated CI, security, dependency, eval, and release checks | blocked-implementation | requires executable code and workflows |
| P-1104 | Enter implementation phase | blocked-approval | requires explicit user instruction |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing evidence |

## Planning conclusion

The repository may remain in planning mode indefinitely. Additional research or review must reopen a named decision with evidence or improve a committed contract; it must not restart broad planning without a discovered defect. No implementation or deployment is authorized until P-1104 is explicitly approved.
