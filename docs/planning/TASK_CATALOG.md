# VibeMaxxing Planning Task Catalog

Updated: 2026-07-23

Statuses: `complete-planning`, `in-progress-planning`, `blocked-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when normative behavior and required planning-grade artifacts exist, references resolve, cross-contract invariants agree and applicable planning validation has passed. It does not imply implementation or production evidence.

## Historical completed planning groups

The following groups produced useful planning artifacts, but later P-1140 findings may reopen dependent contracts. “Historical complete-planning” does not make a contradictory schema implementation-ready.

| IDs | Scope | Historical status | Primary evidence |
|---|---|---|---|
| P-001..009 | authority, phase, decisions, metadata and research classification | complete-planning | `AGENTS.md`, `docs/project/`, research README |
| P-051..055 | scope, staged delivery, glossary, journeys and launch gates | complete-planning | scope freeze and product/operations contracts |
| P-101..105 | accounting, pricing, comparability, periods and corrections | complete-planning | accounting/time contract; reopened where P-1140B/D applies |
| P-201..208 | adapter compatibility, support registry, certification model and governance | complete-planning | compatibility contract and registry; artifact/provenance binding reopened |
| P-301..307 | VibeProof fields, encoding, signing, batching, recovery and conformance plan | complete-planning | protocol planning; superseded for implementation by P-1140C |
| P-401..409 | native topology, storage, recovery, IPC, platforms, devices, CLI and budgets | complete-planning | native contracts; typed IPC/lineage/updater details reopened |
| P-501..505 | identity, native auth, linked accounts, recovery and authorization | complete-planning | identity contracts; provider/session state machines reopened |
| P-601..606 | APIs, PostgreSQL, transactions, workers, ranking and recovery | complete-planning | API/DDL/server contracts; ranking views and ledgers reopened |
| P-701..708 | social graph, boards, countries, presence, notifications, moderation and lifecycle | complete-planning | social contracts; countries removed from launch and state machines reopened |
| P-801..808 | anti-cheat controls, cases, detector gates, calibration and appeals | complete-planning | prior integrity planning; superseded for implementation by July 23 research and P-1140B–E |
| P-901..905 | routes, states, privacy UX, evidence presentation and accessibility | complete-planning | UX/native contracts; country/evidence updates required |
| P-1001..1006 | packages, updates, observability, deployment, recovery and open-source governance | complete-planning | operations contract; updater/release trust details reopened |
| P-1110..1114 | benchmarks, review lenses, decomposition, defaults and consolidation | complete-planning | planning documents |
| P-1120..1128 | schema hardening, registry repair, validation, governance and repository doctor | complete-planning | structural validation only; later semantic audit found new contradictions |
| P-1130A..F | T20 certification, evidence, selection, accounting, fixtures and artifact maturity | complete-planning | T20 planning artifacts; D-046 is provisional pending P-1140B/E reconciliation |

## Active planning-repair program

### P-1140A — authority reset and launch-scope alignment

Status: `in-progress-planning`

Dependencies: none.

Deliverables:

- align README, AGENTS, project authority, status and documentation map;
- supersede D-045 and activate P-1140A–E;
- apply Standard/Hardened, local/offline, identity, country, SLM and VibeProof rewrite decisions;
- mark contradictory machine contracts as planning placeholders;
- close PR #17 without merge;
- align implementation entrance gates and top-level work breakdown;
- update issue #24 as the tracking thread.

Acceptance:

- all repository entrypoints report planning alignment and contract repair;
- country is post-launch in authority and implementation planning;
- SLM is post-launch research everywhere authoritative;
- GitHub/X launch provider scope and Google deferral are coherent;
- no top-level document says P-1104 is the only remaining gate;
- stale PR #17 is closed/superseded.

### P-1140B — core trust, privacy and accounting contracts

Status: `blocked-planning`

Dependencies: P-1140A.

Deliverables:

1. **Evidence/appraisal separation**
   - define source evidence facts, local rule results and server verifier appraisal as separate objects;
   - remove client-authoritative Standard/Hardened fields;
   - define dimensional profile policies and downgrade rules.
2. **Typed local data stages**
   - `SourceObservation` for ephemeral adapter-local data;
   - `NormalizedAccountingEvent` for collector-local facts;
   - `LocalDetectorResult` for bounded advisory output;
   - `EvidenceClaim` for outbound data;
   - exact retention and privilege boundary for each.
3. **Accounting profiles**
   - provider, API mode, runtime, model/tokenizer and version identity;
   - category containment, source totals, cache, reasoning, modality, retries and nested execution;
   - canonical mutually exclusive Token Burn components;
   - local-runtime and exact-tokenizer profiles;
   - estimated records private unless a separately certified deterministic profile permits competition.
4. **Time and delayed sync**
   - server-anchored event intervals and uncertainty;
   - local monotonic clock domain, generation, suspend and reset semantics;
   - profile-specific lateness/offline rules rather than one fixed 24-hour rule.
5. **Device and source trust**
   - device lineage, enrollment, rotation, recovery, restore and requalification;
   - digest-addressed collector/adapter/detector identity;
   - provenance and immutable certification result bundle;
   - capability-based support ceiling.
6. **Privacy**
   - fixed outbound field allowlist;
   - no raw aliases or unrestricted metadata crossing sensitive boundaries;
   - no content-derived hashes, embeddings or request identifiers by default;
   - post-detector egress scan and user-visible outbound preview.
7. **Pricing authority**
   - Estimated Cash Burn derived server-side;
   - immutable event-time alias resolution;
   - typed rule line items, units, modes, thresholds and rounding.

Acceptance:

- prose and draft schemas define the same typed boundaries;
- no arbitrary JSON/bytes cross a privileged or network boundary;
- accounting is reproducible for representative cloud and local sources;
- every support/evidence claim has a machine-readable ceiling;
- privacy canary plan covers every boundary.

### P-1140C — VibeProof v1 protocol rewrite

Status: `blocked-planning`

Dependencies: P-1140B.

Deliverables:

- normative `EvidenceClaim`, `VerifierAppraisal`, `CheckpointReceipt`, `KeyRotationTransition`, `GapDeclaration` and `CorrectionRecord`;
- exact deterministic CBOR profile and CDDL;
- complete COSE_Sign1 and COSE_Key profile: tags, protected/unprotected labels, algorithms, `kid`, external AAD, signed bytes and key encoding;
- separate previous local commitment and previous server checkpoint/accepted state;
- offline precommitment, checkpoint receipt and reconnect semantics;
- atomic batch, challenge consumption, retry and replay-result semantics;
- dual-authorized key rotation and lost-key recovery boundaries;
- correction authority retained by server append-only ledger;
- no unregistered generic extension map;
- checked numeric/time ranges compatible with Rust, Go, TypeScript and PostgreSQL;
- claim, batch and parser resource limits;
- cross-language exact-byte vectors, malformed corpus and independent decoder plan.

Acceptance:

- no client field can self-award evidence status or pricing;
- exact replay returns the original result and conflicting reuse rejects/quarantines;
- batch/sequence/checkpoint behavior has one non-contradictory state machine;
- clone, fork, rollback, rotation, recovery and delayed sync can be represented;
- protocol schema and prose are mutually complete.

### P-1140D — identity, API, ranking, social, native and release state machines

Status: `blocked-planning`

Dependencies: P-1140B; protocol-facing portions also depend on P-1140C.

Deliverables:

1. OAuth transaction, PKCE, issuer/redirect/client-instance binding, native browser handoff and device authorization.
2. Web/native sessions, token families, rotation, DPoP decision, replay, revoke-all and recovery.
3. Ranked-identity eligibility, duplicate investigation, restriction, merge, anti-reenrollment, appeal and reversal.
4. Transactional idempotency ledger with request fingerprint, scope, expiry and response replay.
5. Immutable `ranking_view_id`, period/scope/filter identity, snapshots, cursors, corrections and rebuild semantics.
6. Pricing interpretations and immutable model alias resolution.
7. Friend, block, rival, board, membership, invitation, role, ownership and governance state machines.
8. Collector-derived presence, audience/privacy precedence, multi-device aggregation and immediate revocation.
9. Typed notification event/preference schemas, deduplication, hysteresis, quiet hours and retraction.
10. Moderation and appeals bound to exact claims, periods, ranking views and reversible ledger effects.
11. Export manifest, recent-auth requirement, encrypted delivery, revocable grant and purge receipt.
12. Separate server deletion and per-device local deletion state machines.
13. Typed API resources, authorization matrix, quotas, concurrency, polling, `429`, `Retry-After`, load shedding and outstanding-object limits.
14. macOS/Windows/Linux process, privilege, IPC, storage, installer, updater, uninstall and recovery state machines.
15. TUF trust root/roles, release-set manifest, compatibility graph, rollback/freeze protection, provenance, transparency and compromise recovery.
16. Remove country routes, tasks and launch gates; retain only explicitly future-reserved schema hooks where harmless.

Acceptance:

- every mutable product concept has one authoritative state machine and persistence owner;
- every high-impact action is authorized, idempotent where applicable, audited and reversible;
- presence and notifications cannot leak source content;
- launch scope contains no country feature dependency;
- platform differences and evidence ceilings are explicit.

### P-1140E — cross-contract planning validation

Status: `blocked-planning`

Dependencies: P-1140B, P-1140C and P-1140D.

Deliverables:

- decision-to-contract-to-schema-to-fixture-to-launch-gate traceability;
- positive, negative and adversarial planning fixtures for every repaired invariant;
- protocol golden vectors and malformed/resource-limit corpus definitions;
- SQL constraints, race and transaction test plans;
- OAuth/session/idempotency/relationship/moderation state-machine fixtures;
- privacy canaries across adapters, IPC, local detector, claim construction, API, telemetry, notifications and review tooling;
- registry/schema/reference consistency checks;
- current/future path validation;
- clean-checkout repository doctor and planning-validator results;
- final P0/P1 contradiction review.

Acceptance:

- no contradictory normative owner remains;
- all references resolve;
- placeholder schemas are either repaired and authoritative or explicitly blocked/deferred;
- no planning validator is presented as product security or implementation evidence;
- implementation handoff and work breakdown exactly match the repaired contracts.

## Future implementation and launch tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore and prove product CI, security, dependency, evaluation and release checks | blocked-implementation | requires executable product code and implementation phase |
| P-1104 | Enter implementation phase | blocked-approval | requires P-1140A–E, clean planning validation, no open P0/P1 contradiction and explicit user approval |
| P-1105 | Comprehensive public-launch readiness review | blocked-launch-evidence | requires implemented system and passing executable evidence |
| P-1131 | Select current source/model golden paths and produce non-expired optimized certifications | blocked-launch-evidence | requires real usage inputs, implemented adapters, benchmarks and exercised conformance; D-046 remains provisional |
| P-1150 | Country leaderboard research and planning | blocked-launch-evidence | post-launch only; requires semantic, privacy, historical-attribution and moderation design |
| P-1151 | SLM detector bakeoff | blocked-implementation | post-launch research after deterministic controls produce data and baselines |

## Current conclusion

P-1140A is active. P-1140B–E are the dependency-ordered planning program. P-1104 is not the next task and remains blocked until the repair program completes and the user explicitly opens implementation.