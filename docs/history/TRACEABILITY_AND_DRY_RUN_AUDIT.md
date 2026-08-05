# Specification Traceability and Implementation Dry-Run Audit

Status: historical planning evidence; superseded as current authority
Original date: 2026-07-19
Reclassified: 2026-07-24

## Authority warning

This file preserves the July 19 traceability and implementation dry-run snapshot. It is not the current traceability authority and must not be used to open implementation.

The later repository-wide audit found missing or contradictory machine contracts across evidence appraisal, accounting profiles, protocol batching and continuity, device lineage, OAuth/session state, ranking-view identity, social state machines, platform support and release/update behavior. Current authority is:

- `docs/planning/decision-traceability/` for D-001 through D-069 mappings;
- `docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md` for reconciliation;
- `docs/history/MACHINE_CONTRACT_REPAIR_SPEC.md` for required schema/state repairs;
- `docs/planning/TASK_CATALOG.md` for P-1140B through P-1140E gates;
- the implementation handoff only after those gates pass and P-1104 is explicitly approved.

## Historical purpose

The July 19 audit attempted to map each launch requirement to a decision, implementation contract, owner, privacy/security control, failure behavior and planned evidence. The table below remains useful as an inventory, but later findings invalidate its former completeness conclusion.

## Traceability matrix

| Requirement | Authority | Owner | Failure/recovery | Evidence |
|---|---|---|---|---|
| Token Burn | D-004; accounting contract | adapters, Rust core, Go aggregation | reject ambiguity; replay-safe rebuild | golden accounting vectors and reconciliation tests |
| Estimated Cash Burn | D-005; pricing contract | pricing registry, API, web | immutable dataset versions; corrections supersede | source-provenance and historical-price tests |
| Imports excluded | D-007 | importer, ranking | mark Imported; never aggregate competitively | negative ranking tests |
| Privacy boundary | D-006; privacy contract | collector, sync, server | fail closed; quarantine forbidden fields | packet capture and seeded-canary tests |
| Evidence tiers | D-008; integrity contracts | adapter registry, verifier, UI | deterministic downgrade | qualification matrix tests |
| Universal agent support | D-030 | registry, adapters, compatibility UI | unsupported/degraded states explicit | conformance and version-break tests |
| Signed claims | D-011; VibeProof contract | Rust encoder/signer, Go verifier | deterministic reject codes | exact-byte, malformed, differential, fuzz tests |
| Device identity | D-015 | native daemon, identity service | rotation/revocation/clone quarantine | lifecycle and snapshot tests |
| OAuth identity | D-028; ADR-006 | auth service, native flow, web | provider loss, merge, revocation | state-machine and takeover tests |
| Native daemon UX | D-031 | daemon, CLI, tray/menu shell | crash restart, disk full, rollback | platform lifecycle tests |
| Leaderboards | product and server contracts | aggregation, ranking API, web | late events, corrections, deterministic rebuild | SQL/query and rollover tests |
| Friends/rivals/overtakes | social contract | social service, notifications | blocks and privacy override | simulation and authorization tests |
| Boards/groups | social contract | board domain, API, web | ownership transfer and deletion | role matrix tests |
| Presence | social contract | daemon heartbeat, presence service | expiry and privacy fail closed | timeout/multi-device tests |
| Moderation/appeals | integrity and social contract | policy engine, moderator UI | reversible actions and audit trail | abuse simulation and appeal restoration tests |
| Deletion/export | lifecycle contracts | local runtime and server | resumable deletion, tombstones, aggregate correction | end-to-end deletion tests |
| Releases/updates | operations contract | release pipeline, updater | TUF rollback/freeze defense and atomic recovery | malicious-metadata and consumer verification tests |
| Accessibility/performance | UX and benchmark contracts | web/native clients | degraded feature not hidden | browser, keyboard, screen-reader, battery and latency gates |

## Implementation dry-run method

For each subsystem the implementation model was asked to identify modules to create, authoritative schema, interfaces consumed and produced, persisted state, transaction boundary, retries, idempotency key, privacy classification, logs allowed, migrations, rollback and tests. The July 19 dry run found no missing ownership class at a coarse level. The July 23 audit later proved that ownership labels alone were insufficient: several authoritative states, schema fields, transaction semantics and evidence gates were contradictory or absent.

## Dry-run build map

1. `crates/vibeproof-core`: normalized events, accounting, claim model, canonical encoding, signatures, errors.
2. `crates/vibeproof-adapters`: manifest loader, capability probes, source reconciliation, adapter SDK.
3. `crates/vibeproof-collector`: live observation and transcript-private processing.
4. `crates/vibeproof-sync`: safe-claim queue, challenge handling, acknowledgements.
5. Native daemon/CLI/shell: lifecycle, IPC, local audit, device enrollment, updates.
6. Go API: identity, device, claim ingestion, verification orchestration.
7. PostgreSQL: identities, devices, claims, sequences, outbox, aggregates, social, moderation.
8. Go workers: aggregation, rollover, correction, notification and rebuild.
9. Next.js web: onboarding, leaderboards, profiles, social, boards, devices, privacy, moderation.
10. Release/operations: packaging, signing, TUF, observability, backup and recovery.

## No-invention findings

After the relevant P-1140 repair closes, an implementation model may select minor internal names and refactor private code but may not invent accounting semantics, public schemas, ranking behavior, evidence meaning, identity recovery, privacy fields, moderation outcomes or lifecycle behavior. Until then, blocked draft contracts are inputs to repair, not permission to guess.

## Historical disposition

The former conclusion that all product-level launch requirements had a sufficient traceability path is superseded. P-1140B through P-1140E explicitly track the missing contract, schema, state-machine, platform and validation dimensions.

Keep this file for provenance. Do not add new requirements here. Consolidate durable traceability in the current decision-traceability directory, owning contracts, schemas, task catalog and inactive implementation handoff.