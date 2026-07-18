# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `complete-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` when the committed normative contract defines ownership, interfaces, schemas/fields, invariants, limits, negative cases, failures, recovery, compatibility, privacy/security behavior, tests and acceptance evidence. It does not imply implemented or production-proven.

## Repository truth and governance

| ID | Task | Status | Output |
|---|---|---|---|
| P-001..006 | Authority, phase, evidence, decisions, artifacts and repository operations | complete-planning | root control files and planning system |
| P-007 | Deterministic repository metadata | complete-planning | `scripts/repository/generate_repository_metadata.py` |
| P-008 | Historical research provenance | complete-planning | `docs/research/RESEARCH_PROVENANCE_INDEX.md` |
| P-009 | License, contribution, trademark, maintainer, release and security governance | complete-planning | operations/open-source contract |

## Product scope, journeys and gates

| ID | Task | Status | Output |
|---|---|---|---|
| P-051..055 | Complete public scope, staged delivery, terminology, journeys and launch gates | complete-planning | scope freeze, product/social contracts, operations launch gate |

## Accounting, pricing and time

| ID | Task | Status | Output |
|---|---|---|---|
| P-101..105 | Token formula, edge cases, comparability, Estimated Cash Burn, periods/ties/corrections | complete-planning | `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md` |

## Universal agent compatibility

| ID | Task | Status | Output |
|---|---|---|---|
| P-201..208 | Agent census, manifest/event contracts, source reconciliation, support lifecycle, certification, community governance and generated claims | complete-planning | universal compatibility docs, adapter/protocol contract and machine registry |

## VibeProof protocol

| ID | Task | Status | Output |
|---|---|---|---|
| P-301..307 | Claim fields, deterministic CBOR/CDDL, COSE, errors, sequence/replay/corrections, transport and conformance | complete-planning | `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md` |

## Native runtime

| ID | Task | Status | Output |
|---|---|---|---|
| P-401..409 | Process boundary, topology, storage, crash recovery, IPC, platform matrix, devices, CLI/shell/update and budgets | complete-planning | native architecture and runtime/storage contract |

## Identity and authorization

| ID | Task | Status | Output |
|---|---|---|---|
| P-501..505 | GitHub/X identity, account/session/recovery, native authorization, provider compromise and permissions | complete-planning | ADR-006 and authentication contract |

## Server, database and ranking

| ID | Task | Status | Output |
|---|---|---|---|
| P-601..606 | APIs, PostgreSQL schema, acceptance transaction, outbox/workers, ranking/cache and benchmarks | complete-planning | `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` |

## Social, boards, presence, notifications and lifecycle

| ID | Task | Status | Output |
|---|---|---|---|
| P-701..708 | Profiles, friends/blocks/rivals, boards/orgs/communities, countries, presence, notifications, moderation/appeals and lifecycle | complete-planning | `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` |

## Anti-cheat and evidence integrity

| ID | Task | Status | Output |
|---|---|---|---|
| P-801..808 | Attack/control catalog, reason/evidence policy, attack lab design, safe features, detector bakeoff, SLM gate, calibration and red-team operations | complete-planning | anti-cheat program/catalog, adversarial registry and social/integrity contract |

The SLM remains conditional on implementation-phase measured lift. That is a closed planning decision, not a missing contract.

## Web and native UX

| ID | Task | Status | Output |
|---|---|---|---|
| P-901..905 | Route/state map, component/data behavior, local privacy UX, evidence presentation, accessibility/browser/performance plan | complete-planning | product/social UX and native runtime contracts |

## Packaging, production and open-source launch

| ID | Task | Status | Output |
|---|---|---|---|
| P-1001..1006 | Platform packages, TUF, observability, deployment, SLO/recovery and open-source governance | complete-planning | `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` |
| P-1007 | Restore and prove automated CI/security/dependency/eval/release checks | blocked-implementation | requires executable implementation and user-approved phase change |

## Final reviews

| ID | Task | Status | Output |
|---|---|---|---|
| P-1101 | Cross-document contradiction and stale-claim audit | complete-planning | planning audit, provenance index and repaired authority files |
| P-1102 | Privacy/threat/control traceability review | complete-planning | normative contract set and anti-cheat mapping |
| P-1103 | Schema/API/state/migration/recovery completeness review | complete-planning | `docs/implementation/IMPLEMENTATION_HANDOFF.md` |
| P-1104 | User approval to enter implementation | blocked-approval | explicit phase change required |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing evidence |

## Planning conclusion

The technical planning phase is complete at contract level. The next legal action is P-1104: explicit user approval to enter implementation. Planning documents cannot satisfy P-1007 or P-1105 because those gates require executable evidence.
