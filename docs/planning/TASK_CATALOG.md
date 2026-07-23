# VibeMaxxing Planning Task Catalog

Updated: 2026-07-24

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
| P-401..409 | native topology, storage, IPC, devices and CLI | complete-planning | typed IPC, lineage, universal platform, privilege and updater work reopened |
| P-501..505 | identity, auth, linked accounts and recovery | complete-planning | provider/session state machines reopened |
| P-601..606 | APIs, SQL, transactions, ranking and recovery | complete-planning | appraisal, idempotency and ranking views reopened |
| P-701..708 | social, boards, countries, presence, notifications and moderation | complete-planning | country removed; state machines reopened |
| P-801..808 | anti-cheat, detector and appeal planning | complete-planning | superseded by July 23 research and P-1140 |
| P-901..905 | routes, states, privacy UX and accessibility | complete-planning | evidence/country/platform corrections required |
| P-1001..1006 | updater, observability, deployment and governance | complete-planning | mandatory update and release trust graph reopened |
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
- issue #24 closed as the completed entrance-gate thread.

### P-1140B — core trust, privacy and accounting contracts

Status: `complete-planning`

Dependencies: P-1140A complete.

Completed planning inputs:

- detailed field/type/authority/state/transaction repair specification in `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`;
- expanded canonical privacy contract;
- expanded canonical threat model;
- exact blocked-schema inventory and initialization links;
- D-001 through D-069 implementation/platform/evidence mapping in `docs/planning/decision-traceability/`;
- frozen cross-platform capability and integration audit;
- accepted ADR-011 universal platform baseline;
- accepted ADR-012 optional privileged supervision;
- accepted ADR-013 mandatory automatic updates;
- accepted ADR-014 prototype visual-validation automation;
- issue #26 platform questions resolved.

Candidate deliverables merged through PR #35:

1. **Evidence/appraisal separation**
   - server-owned dimensional policy, named minimums, fatal conditions and deterministic downgrade order;
   - adapter/device claims bind facts, capability ceilings and digests without selecting public state.
2. **Typed local data stages and IPC**
   - closed schemas for `SourceObservation`, `NormalizedAccountingEvent` and `LocalDetectorResult`;
   - typed Protobuf observation, acknowledgement, claim, queue, receipt, export and deletion bodies;
   - process role, nonce, sequence and deadline in every envelope; opaque domain payloads removed.
3. **Accounting profiles**
   - immutable schema and representative registry;
   - category containment and mutually exclusive canonical outputs;
   - cloud-exclusive, cloud-inclusive, local-tokenizer, cache, reasoning, retry, cancellation, nested and contradiction semantics.
4. **Time and delayed sync**
   - bounded wall observation plus monotonic domain/generation;
   - server/checkpoint anchoring and profile-specific delayed-sync policy; universal 24-hour rule removed.
5. **Device and source trust**
   - enrollment, rotation, recovery, restore, clone, retirement and requalification transitions;
   - adapter artifact, manifest, build provenance, SBOM, certification and platform-profile binding.
6. **Pricing authority**
   - claims carry no pricing authority;
   - server-owned immutable event-time alias resolution, typed line items, rounding and unpriced reasons.
7. **Privacy machine contract**
   - schema-validated deny-by-default claim-egress registry;
   - positive/negative canaries across adapter, IPC, local store, detector, claim, HTTP, telemetry, notification, moderation and export.

Validation: Planning checks run #211 passed on exact candidate head `9165fcb38ea2a4c26c8e539ff15de97fa59f59c2`; the gate-transition head also passed before merge. The artifacts remain planning contracts, not implementation or executable security evidence.

P-1140B acceptance:

- prose and planning schemas define identical typed boundaries;
- no arbitrary JSON/bytes cross a privileged or network boundary;
- accounting is reproducible for representative cloud and local sources;
- every support/evidence claim has a machine-readable ceiling;
- pricing and public evidence state are server-owned;
- privacy canary plan covers every boundary.

### P-1140C — VibeProof v1 protocol rewrite

Status: `complete-planning`

Dependencies: P-1140B.

Candidate deliverables merged through PR #36:

- closed integer-label CDDL for EvidenceClaim, VerifierAppraisal, CheckpointReceipt, Challenge, atomic batch/result, KeyRotationTransition, GapDeclaration and CorrectionRecord;
- exact deterministic CBOR rules, numeric/time/size/depth/allocation limits and no extension map;
- mandatory COSE tag 18, exact protected headers, empty unprotected map, Ed25519 COSE_Key, external AAD and Sig_structure;
- separate local commitment and server checkpoint state with offline/reconnect semantics;
- one atomic challenge/batch/idempotency/replay transaction;
- dual-signature rotation, lost-key recovery, clone/fork quarantine and gap policy;
- append-only server-authorized corrections;
- fixed claim and receipt exact-byte Ed25519 vectors plus malformed/resource/transaction corpus;
- validator checks for CDDL coverage, prohibited client authority, digests, lengths and cryptographic signatures.

Validation: Planning checks run #219 passed on exact candidate head `e6f334772f05d4f3806935a7d8a701a2a8bb32d0`; the gate-transition head also passed before merge. These are planning vectors, not independent runtime interoperability evidence.

Acceptance:

- no client field self-awards evidence or pricing;
- byte-identical replay returns stored result and conflicting reuse rejects/quarantines;
- one non-contradictory batch/sequence/checkpoint state machine exists;
- clone, fork, rollback, rotation, recovery and delayed sync are representable;
- CDDL and prose are mutually complete.

### P-1140D — identity, API, ranking, social, native and release state machines

Status: `complete-planning`

Dependencies: P-1140B; protocol-facing work also depends on P-1140C.

Completed planning contract set:

- one JSON Schema-validated registry for 23 authoritative mutable-state machines;
- one exact launch platform registry with 34 uncertified/unadvertised profiles and a complete 16-case failure matrix per profile;
- endpoint-specific OpenAPI resources with authorization, recent-auth, durable idempotency, typed rate limits and bounded VibeProof CBOR input;
- PostgreSQL 16 ownership/constraint contract with canonical friendship pairs, membership-owned board authority, token families, lineage, appraisal, receipts, ranking views, typed social state, deletion effects and release trust;
- closed social/integrity Protobuf event union;
- typed signed release-set, immutable ranking-view and export-manifest schemas;
- enriched reason-code and policy lifecycle authority;
- normative OAuth/session/device-bound proof, ranked-identity, API, ranking, social, native lifecycle, privileged supervision and update/release contract.

Validation: Planning checks run #234 passed on exact candidate head `366691f8e1f06c03915652209dc83adb3a40af0c`. The gate-transition head must also pass before merge.

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
14. macOS Apple-silicon and Intel service, key, IPC, packaging, update and recovery state machines.
15. Windows native x64/ARM64 desktop/server service, key, IPC, packaging, update and recovery state machines.
16. Linux distro/package/architecture/desktop/headless/init/key/update state machines.
17. WSL, container and CI globally eligible profiles with lineage, duplicate, lifecycle and evidence ceilings.
18. ADR-010 always-on service registration, child watchdog, crash-loop, pause/degrade and uninstall state machines.
19. ADR-012 optional privileged supervisor identity, ACL, consent, downgrade and uninstall state machines.
20. ADR-013 mandatory update classes, deadlines, maintenance leases, blocked versions, environment-specific mechanisms and rollback.
21. TUF root/roles, release-set compatibility, rollback/freeze defense, provenance, transparency and compromise recovery.
22. Remove country routes/tasks/gates and prohibit Android/iOS/iPadOS/ChromeOS native work under D-066.
23. Keep Storybook automation constrained to ADR-014 and outside product release evidence.

Acceptance:

- every mutable concept has one authoritative state machine and persistence owner;
- every high-impact action is authorized, idempotent where applicable, audited and reversible;
- presence and notifications cannot leak source content;
- launch contains no country dependency;
- every advertised platform has a complete capability profile, implementation owner and failure matrix;
- native Mac, Windows and Linux release lanes are explicit;
- WSL/container/CI global eligibility and duplicate controls are explicit;
- privileged mode cannot inspect source content or merge users;
- mandatory update deadlines and safe rollback are explicit;
- no Android, iOS, iPadOS or ChromeOS native implementation path exists;
- daemon/shell/collector/sync lifecycle independence is explicit.

### P-1140E — cross-contract planning validation

Status: `complete-planning`

Dependencies: P-1140B, P-1140C and P-1140D.

Completed planning-validation set:

- schema-validated matrix binding all 69 decisions, every OpenAPI operation, 23 state machines, 34 exact platform profiles and 18 validation domains;
- positive and invalid-transition fixtures for every state machine;
- 14 deterministic PostgreSQL transaction/race plans;
- exact per-profile 16-case runtime evidence plans, all explicitly unexecuted and unadvertised;
- reason-code authority reference closure;
- final contradiction audit with zero open P0/P1 planning findings;
- a dedicated validator in the clean-checkout planning workflow.

Validation: Planning checks run #239 passed on exact candidate head `7b2a4225f3407f3c8c0097a8017d71d3aa9c5aa3`. The gate-transition head must also pass before merge.

Deliverables:

- machine-check D-001..D-069 decision-to-owner-to-work-unit-to-schema/state-to-platform-to-fixture traceability;
- failure if an accepted implementation-bearing decision lacks any traceability dimension;
- failure if a superseded decision retains an active implementation path;
- failure if out-of-scope mobile/ChromeOS native work appears;
- positive, negative and adversarial fixtures for every repaired invariant;
- protocol vectors and malformed/resource corpus;
- SQL constraint, race and transaction plans;
- OAuth/session/idempotency/social/moderation state-machine fixtures;
- privacy canaries across adapter, IPC, detector, claim, API, telemetry, notification, privileged supervisor and review boundaries;
- complete platform matrix for install/start/supervision/keys/storage/IPC/adapters/offline/update/rollback/uninstall;
- exact OS/version/architecture/distribution/environment baseline registry;
- reboot/login/logout/sleep/crash/disk/permission/update evidence plans;
- mandatory-update deadline, blocked-version, container and CI expiry fixtures;
- registry/schema/reference consistency;
- current/future path validation;
- clean-checkout repository doctor and validator outputs;
- final P0/P1 contradiction review.

Acceptance:

- every D-001..D-069 decision appears exactly once in traceability and has the correct active/superseded state;
- no contradictory normative owner remains;
- all references resolve;
- placeholders are repaired or explicitly deferred;
- no planning/prototype validator is presented as implementation or security evidence;
- handoff and work breakdown exactly match repaired contracts;
- no platform may be advertised before its exact profile and executable release gates are complete;
- the repository contains no stale open platform-scope question.

## Future implementation and launch tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore product CI, security, dependency, evaluation and release checks | blocked-implementation | requires executable product code and P-1104 |
| P-1104 | Enter implementation phase | blocked-approval | requires P-1140B–E, clean validation, no P0/P1 contradiction and explicit approval |
| P-1105 | Public-launch readiness review | blocked-launch-evidence | requires implemented system and executable evidence on every advertised profile |
| P-1131 | Select current source/model golden paths and produce non-expired certifications | blocked-launch-evidence | requires real adapters, benchmarks and conformance |
| P-1150 | Country leaderboard research and planning | blocked-launch-evidence | post-launch only |
| P-1151 | SLM detector bakeoff | blocked-implementation | post-launch after deterministic baselines and data |

## Current conclusion

P-1140A through P-1140E are complete-planning. Platform scope is frozen under D-062 through D-069. P-1104 is the sole implementation entrance decision and remains `blocked-approval` until the user explicitly authorizes implementation.
