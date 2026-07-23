# VibeMaxxing Planning Task Catalog

Updated: 2026-07-23

Statuses: `complete-planning`, `in-progress-planning`, `blocked-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when normative behavior and required planning-grade artifacts exist, references resolve, cross-contract invariants agree and applicable planning validation has passed. It does not imply implementation or production evidence.

## Historical completed planning groups

The following groups produced useful planning artifacts, but later P-1140 findings reopen dependent contracts. Historical completion does not make a contradictory schema implementation-ready.

| IDs | Scope | Historical status | Current qualification |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, metadata and research classification | complete-planning | superseded where P-1140A updated authority |
| P-051..055 | scope, staged delivery, glossary, journeys and launch gates | complete-planning | country launch scope corrected by D-052 |
| P-101..105 | accounting, pricing, comparability, periods and corrections | complete-planning | reopened by P-1140B/D |
| P-201..208 | compatibility, registry and certification governance | complete-planning | digest/provenance binding reopened |
| P-301..307 | VibeProof fields, encoding, signing, batching and recovery | complete-planning | superseded for implementation by P-1140C |
| P-401..409 | native topology, storage, IPC, devices and CLI | complete-planning | typed IPC, lineage, always-on lifecycle and updater reopened |
| P-501..505 | identity, auth, linked accounts and recovery | complete-planning | provider/session state machines reopened |
| P-601..606 | APIs, SQL, transactions, ranking and recovery | complete-planning | appraisal, idempotency and ranking views reopened |
| P-701..708 | social, boards, countries, presence, notifications and moderation | complete-planning | country removed; state machines reopened |
| P-801..808 | anti-cheat, detector and appeal planning | complete-planning | superseded by July 23 research and P-1140 |
| P-901..905 | routes, states, privacy UX and accessibility | complete-planning | evidence/country/platform corrections required |
| P-1001..1006 | updater, observability, deployment and governance | complete-planning | release trust graph and platform packaging reopened |
| P-1110..1114 | benchmarks, review lenses, decomposition and consolidation | complete-planning | retained as planning evidence |
| P-1120..1128 | schema hardening and repository doctor | complete-planning | structural validation only |
| P-1130A..F | T20 certification, selection, fixtures and maturity | complete-planning | D-046 provisional pending P-1140B/E |

## Active planning-repair program

### P-1140A — authority reset and launch-scope alignment

Status: `complete-planning`

Completed outputs:

- repository authority hierarchy and reconciliation record;
- aligned README, AGENTS, PROJECT, STATUS and documentation map;
- D-045 superseded and P-1140A–E activated;
- Standard/Hardened, local/offline, identity, country, SLM and VibeProof rewrite decisions applied;
- contradictory machine contracts explicitly blocked;
- PR #17 closed without merge;
- implementation handoff and PR-sized work breakdown rebuilt;
- issue #24 updated as the completed entrance-gate thread.

Evidence:

- `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`;
- `docs/project/STATUS.md`;
- `docs/project/DOCUMENTATION.md`;
- `docs/planning/DECISION_REGISTER.md`;
- `docs/implementation/IMPLEMENTATION_HANDOFF.md`;
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`.

Acceptance achieved:

- all repository entrypoints report planning contract repair;
- country is post-launch;
- SLM is post-launch research;
- GitHub/X launch provider scope and Google deferral are coherent;
- no top-level document says P-1104 is the only remaining gate;
- stale PR #17 is closed and superseded.

### P-1140B — core trust, privacy and accounting contracts

Status: `in-progress-planning`

Dependencies: P-1140A complete.

Completed planning inputs:

- detailed field/type/authority/state/transaction repair specification in `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`;
- expanded canonical privacy contract;
- expanded canonical threat model;
- exact blocked-schema inventory and initialization links;
- D-001 through D-061 implementation/platform/evidence mapping in `docs/planning/decision-traceability/`;
- cross-platform capability and integration audit in `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`.

Remaining deliverables:

1. **Evidence/appraisal separation**
   - revise evidence-profile and adapter/VibeProof prose;
   - replace client-owned evidence state with source facts, deterministic local result and server appraisal;
   - define dimensional policy and downgrade tables.
2. **Typed local data stages**
   - draft schemas for `SourceObservation`, `NormalizedAccountingEvent` and `LocalDetectorResult`;
   - define retention, process role and IPC direction for each;
   - remove opaque JSON/byte transport.
3. **Accounting profiles**
   - add immutable profile schema and registry;
   - define provider/runtime/API-mode category containment;
   - define canonical mutually exclusive Token Burn outputs;
   - cover cache, reasoning, modality, retry, cancellation and nested execution.
4. **Time and delayed sync**
   - define server-anchored interval and uncertainty;
   - define monotonic clock domain/generation/reset;
   - replace universal 24-hour lateness with profile policy.
5. **Device and source trust**
   - define lineage, enrollment, rotation, recovery, restore and requalification objects;
   - bind exact artifact, provenance and certification digests;
   - define capability-based evidence ceiling.
6. **Pricing authority**
   - remove pricing authority from claims;
   - define immutable event-time alias resolution;
   - define typed pricing rules and line items.
7. **Privacy machine contract**
   - create fixed egress allowlist schema;
   - create privacy-negative fixtures for every local/network boundary;
   - ensure no raw alias, request ID, unrestricted metadata or content-derived hash crosses.

P-1140B acceptance:

- prose and planning schemas define identical typed boundaries;
- no arbitrary JSON/bytes cross a privileged or network boundary;
- accounting is reproducible for representative cloud and local sources;
- every support/evidence claim has a machine-readable ceiling;
- pricing and public evidence state are server-owned;
- privacy canary plan covers every boundary.

### P-1140C — VibeProof v1 protocol rewrite

Status: `blocked-planning`

Dependencies: P-1140B.

Deliverables:

- normative `EvidenceClaim`, `VerifierAppraisal`, `CheckpointReceipt`, `KeyRotationTransition`, `GapDeclaration` and `CorrectionRecord`;
- exact deterministic CBOR and complete COSE profile;
- separate local commitment and server checkpoint state;
- offline precommitment/reconnect semantics;
- atomic batch, challenge, retry and replay-result state machine;
- dual-authorized rotation and lost-key recovery;
- server-authorized corrections;
- no generic extension map;
- checked numeric/time ranges across Rust, Go, TypeScript and PostgreSQL;
- exact-byte vectors and malformed/resource corpus.

Acceptance:

- no client field self-awards evidence or pricing;
- byte-identical replay returns stored result and conflicting reuse rejects/quarantines;
- one non-contradictory batch/sequence/checkpoint state machine exists;
- clone, fork, rollback, rotation, recovery and delayed sync are representable;
- CDDL and prose are mutually complete.

### P-1140D — identity, API, ranking, social, native and release state machines

Status: `blocked-planning`

Dependencies: P-1140B; protocol-facing work also depends on P-1140C.

Deliverables:

1. OAuth transaction, PKCE, issuer/redirect/client-instance and native browser-handoff state.
2. Web/native token families, rotation, replay, revoke-all, DPoP decision and recovery.
3. Ranked-identity eligibility, investigation, restriction, consolidation, anti-reenrollment, appeal and reversal.
4. Transactional idempotency ledger and exact response replay.
5. Immutable `ranking_view_id`, snapshots, cursors, corrections and rebuild semantics.
6. Server pricing interpretations and immutable model aliases.
7. Canonical friendship, block, rival, board, membership, invitation, role and ownership state machines.
8. Collector-derived presence, audience precedence and multi-device aggregation.
9. Typed notifications/preferences, deduplication, hysteresis, quiet hours and retraction.
10. Moderation/appeals bound to exact claims, periods, ranking views and reversible effects.
11. Typed export manifest, recent-auth, encrypted delivery and purge receipt.
12. Separate server and per-device local deletion state machines.
13. Endpoint-specific API resources, authorization, quotas, concurrency, polling and load shedding.
14. macOS/Windows/Linux process, privilege, IPC, storage, packaging and recovery state machines.
15. ADR-010 always-on service registration, OS supervision, child watchdog, crash-loop, pause/degrade, update handoff and uninstall state machines.
16. WSL, container, CI and remote/headless environment profiles with explicit lifecycle/evidence ceilings.
17. TUF root/roles, release-set compatibility, rollback/freeze defense, provenance, transparency and compromise recovery.
18. Resolve and freeze exact launch baselines for CPU architectures, OS versions, Linux distributions/desktops and environment eligibility.
19. Remove country routes, tasks and launch gates.

Acceptance:

- every mutable concept has one authoritative state machine and persistence owner;
- every high-impact action is authorized, idempotent where applicable, audited and reversible;
- presence and notifications cannot leak source content;
- launch contains no country dependency;
- every advertised platform has a complete capability profile, implementation owner and failure matrix;
- weaker platform modes disclose evidence and lifecycle ceilings;
- daemon/shell/collector/sync lifecycle independence is explicit;
- platform scope questions in `CROSS_PLATFORM_COMPLETENESS_AUDIT.md` are resolved.

### P-1140E — cross-contract planning validation

Status: `blocked-planning`

Dependencies: P-1140B, P-1140C and P-1140D.

Deliverables:

- machine-check D-001..D-061 decision-to-owner-to-work-unit-to-schema/state-to-platform-to-fixture traceability;
- failure if an accepted implementation-bearing decision lacks any traceability dimension;
- failure if a superseded decision retains an active implementation path;
- positive, negative and adversarial fixtures for every repaired invariant;
- protocol vectors and malformed/resource corpus;
- SQL constraint, race and transaction plans;
- OAuth/session/idempotency/social/moderation state-machine fixtures;
- privacy canaries across adapter, IPC, detector, claim, API, telemetry, notification and review boundaries;
- complete platform matrix for install/start/supervision/keys/storage/IPC/adapters/offline/update/rollback/uninstall;
- OS/version/architecture/distribution baseline registry;
- platform-specific reboot/login/logout/sleep/crash/disk/permission/update evidence plans;
- registry/schema/reference consistency;
- current/future path validation;
- clean-checkout repository doctor and validator outputs;
- final P0/P1 contradiction review.

Acceptance:

- every D-001..D-061 decision appears exactly once in traceability and has the correct active/superseded state;
- no contradictory normative owner remains;
- all references resolve;
- placeholders are repaired or explicitly deferred;
- no planning validator is presented as implementation/security evidence;
- handoff and work breakdown exactly match repaired contracts;
- no platform may be advertised before its exact profile and executable release gates are complete;
- implementation entry cannot proceed while platform scope remains ambiguous.

## Future implementation and launch tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore product CI, security, dependency, evaluation and release checks | blocked-implementation | requires executable product code |
| P-1104 | Enter implementation phase | blocked-approval | requires P-1140B–E, resolved platform baselines, clean validation, no P0/P1 contradiction and explicit approval |
| P-1105 | Public-launch readiness review | blocked-launch-evidence | requires implemented system and executable evidence on every advertised platform |
| P-1131 | Select current source/model golden paths and produce non-expired certifications | blocked-launch-evidence | requires real adapters, benchmarks and conformance |
| P-1150 | Country leaderboard research and planning | blocked-launch-evidence | post-launch only |
| P-1151 | SLM detector bakeoff | blocked-implementation | post-launch after deterministic baselines and data |

## Current conclusion

P-1140A is complete. P-1140B is active. P-1140C–E remain dependency-blocked. P-1104 remains blocked and is not the next task. Exact platform launch baselines must be answered and frozen during P-1140D before P-1140E can pass.
