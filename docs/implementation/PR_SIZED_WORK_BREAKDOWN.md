# PR-Sized Implementation Work Breakdown

Status: canonical planning decomposition; inactive until P-1140F closes and P-1104 is explicitly authorized
Updated: 2026-08-04

This file decomposes `IMPLEMENTATION_HANDOFF.md`. It does not authorize product code. Units prefixed `PF-` are planning repairs permitted in the current phase. All other units are future implementation work and remain blocked.

## Global rules

Every unit must be independently reviewable and must name:

- dependency units;
- normative owner and decision IDs;
- schemas, state machines, persistence, and API surfaces affected;
- privacy and egress impact;
- migration, compatibility, and rollback/roll-forward behavior;
- positive, negative, adversarial, concurrency, and resource evidence;
- disable, revoke, recovery, or reversal path.

A unit cannot start because its predecessor document exists. Its dependency must be accepted on the exact branch/head and must not retain an open semantic P1.

## Current planning program

### PF-001 — Quarantine the shadow VibeProof protocol

Dependencies: PR #42 consolidation.

- classify `crates/vibeproof-core` and Go fixture codec as exploratory prototype;
- remove VibeProof v1 naming from incompatible 11-field fixtures or remove them;
- prohibit product imports from the shadow model;
- mark affected evaluations blocked or prototype-only.

Exit: one VibeProof v1 wire authority remains.

### PF-002 — Align normative protocol and conformance ownership

Dependencies: PF-001.

- inventory CDDL labels, COSE headers, external AAD, exact vectors, malformed/resource corpus;
- define generation boundaries for Rust/Go types;
- define exact independent implementation evidence expected after P-1104.

### PF-003 — Artifact/evidence maturity registry

Dependencies: PF-001.

- classify every executable suite and fixture as structural, semantic, prototype, runtime evidence, or certification;
- rename overclaiming suites;
- reject empty or mislabeled evidence in planning validators.

### PF-004 — Mutable aggregate ownership inventory

Dependencies: PR #42 consolidation.

- enumerate every aggregate named in API, SQL, Protobuf/CDDL, state registry, policy, reasons, and prose;
- require one persistence owner, lifecycle, revision model, transaction boundary, and event/outbox behavior;
- record missing and duplicate owners.

### PF-005 — OAuth provider configuration authority

Dependencies: PF-004.

- issuer, endpoints, client, exact redirect, PKCE, RFC 9207 capability, scopes, device-flow capability, revision and expiry;
- provider-specific positive and mix-up/redirect-confusion fixtures.

### PF-006 — Canonical OAuth transaction

Dependencies: PF-005.

- bind action, account/session, recent-auth grant, provider revision, redirect, state, PKCE, expiry and result;
- remove standalone authorization-code identity mutation semantics;
- define single consumption and ambiguous callback behavior.

### PF-007 — Linked identity and recovery lifecycle

Dependencies: PF-006.

- exact linked-identity ID and durable provider subject;
- candidate, linked, unlink-pending, lost, compromised, recovery-pending, unlinked, superseded;
- last-authentication-method invariant;
- token/session/device notification and cooling-off effects.

### PF-008 — Ranked identity and consolidation authority

Dependencies: PF-007; D-070.

- separate account and ranked identity;
- canonical survivor, retired duplicates, private investigation evidence, restrictions, appeal and reversal;
- immutable consolidation plan for identities, devices, claims, social state, boards, moderation, exports/deletions;
- historical score recomputation from valid non-overlapping claim contributions, never aggregate summation.

### PF-009 — Canonical challenge and lineage continuity

Dependencies: PF-004.

- one identifier/type model across CDDL, OpenAPI and SQL;
- expected lineage revision, sequence, commitment head, checkpoint, batch commitment, policy, issue/expiry;
- lineage-scoped rather than device-row-scoped continuity.

### PF-010 — Rotation, lost-key recovery, fork and requalification

Dependencies: PF-009; D-072.

- dual authorization for ordinary rotation;
- lost-key recovery authority;
- quarantine all post-fork branches;
- preserve pre-fork accepted claims;
- select/recover one survivor and resume in a new lineage generation;
- appeal, reversal, downgrade and notification.

### PF-011 — Native process and trust-domain model

Dependencies: PF-004.

- daemon, collector, sync, shell, CLI, dashboard, updater, privileged supervisor;
- executable identity, OS peer identity, user/session boundary, artifact/release identity;
- allowed capabilities and data classes per role.

### PF-012 — Local channel protocol

Dependencies: PF-011.

- handshake, daemon-assigned role, generation, nonce, sequence window, capability grant, deadline, revocation;
- typed request/response per role rather than one universal message union;
- same-user impersonation and stale-process fixtures.

### PF-013 — Shell and subsystem state separation

Dependencies: PF-011.

- shell owns process/connection state only;
- daemon, collection, sync, auth, permission, update and connectivity are independent projections;
- pre-auth startup and restart after crash;
- UI exit, pause collection, pause sync, stop daemon, logout, uninstall are distinct.

### PF-014 — Local persistence and migration contract

Dependencies: PF-011.

- local DDL ownership, encryption, key references, schema generation, crash consistency, queues, commitments, receipts, migrations and recovery;
- forbidden-content boundaries for logs, backups, diagnostics and corruption reports.

### PF-015 — Atomic compatibility tuple

Dependencies: PF-004.

- product/source, exact version/artifact, platform profile, mode, adapter/collector artifacts, protocol/telemetry profile, accounting profile, privacy profile and evidence ceiling;
- canonical digest construction.

### PF-016 — Certification lifecycle and revocation

Dependencies: PF-015.

- candidate, testing, active, degraded, suspended, expired, superseded, retired;
- signed result bundle, suite/case digests, validity interval, signer/verifier policy;
- narrow per-tuple emergency downgrade and reinstatement.

### PF-017 — Source observation and operation identity

Dependencies: PF-015.

- authenticated tuple selection before normalization;
- provider/model/source facts;
- operation, parent/child, retry generation, observer identity, cumulative/incremental semantics;
- direct/proxy/ACP/OTel equivalence.

### PF-018 — Accounting reconciliation and bounds

Dependencies: PF-017.

- per-operation grouping;
- source authority, containment, cache/reasoning/modality semantics;
- equal-authority contradiction handling;
- deterministic tie-breaking independent of array order;
- checked arithmetic and practical event/period bounds.

### PF-019 — Idempotency authority

Dependencies: PF-004.

- typed principal, operation/API version, key and request fingerprint;
- exact stored status, content type, safe headers, bytes and result references;
- executing, committed, replayable-failure, conflict, expired and abandoned semantics;
- retention: at least 30 days for high-impact mutations; claim-batch responses until later acknowledged checkpoint supersession.

### PF-020 — Transaction and ambiguous-commit model

Dependencies: PF-019.

- idempotency, business effect, audit, outbox and exact response commit together;
- crash before commit, crash after commit, dropped response, takeover and expiry cases;
- expired high-impact keys reject reuse rather than becoming fresh mutations.

### PF-021 — Ranking definition and audience authorization

Dependencies: PF-004.

- stable ranking definition separate from viewer/board audience;
- metric/version, period, evidence/source/agent/provider/model filters, tie and projection policy;
- viewer, friend/rival cohort, block/privacy, board membership/visibility revisions;
- only global public by default.

### PF-022 — Ranking generations, entries, snapshots and cursors

Dependencies: PF-021.

- generation included in entry keys;
- isolated build/validation/promotion and one active pointer;
- immutable retained entries;
- viewer-bound signed cursor with authorization revision and expiry;
- score-only `rank()` peer groups and separate deterministic display key.

### PF-023 — Periods, seasons, contributions and corrections

Dependencies: PF-022; D-070.

- exact calendar/timezone, open/frozen/closed/corrected/archived states;
- late-claim and correction windows;
- immutable contribution ledger;
- inverse/replacement corrections and rebuild equivalence;
- movement, overtake, streak and season event/retraction references.

### PF-024 — Social relationship authority

Dependencies: PF-004.

- canonical friendship pair and directional request lifecycle;
- directional blocks separate from friendship;
- rivals separate from blocks/friendship;
- decline, cancel, expiry, unblock, generation and current authorization.

### PF-025 — Board ownership and role authority

Dependencies: PF-024; D-071.

- atomic board creation plus initial owner;
- invitations grant only non-privileged membership;
- separate recent-authenticated revision-checked admin promotion;
- paired ownership transfer preserving exactly one owner;
- role/action authorization matrix and recovery.

### PF-026 — Presence evidence and projection

Dependencies: PF-011, PF-024; D-073.

- device-bound qualifying pulse every 30 seconds;
- active, idle at 90 seconds, offline at 300 seconds;
- lease generations and sleep/resume;
- deterministic multi-device merge;
- private/block/relationship/board visibility as separate viewer projection.

### PF-027 — Notification source, inbox and channel model

Dependencies: PF-024, PF-026.

- immutable source event and revision;
- recipient inbox item, grouping, authorization revision, read/dismiss/expiry/retraction;
- per-channel queued/deferred/accepted/acknowledged/failed/expired attempts;
- preferences, quiet hours, security-critical policy and subscription lifecycle;
- push provider acceptance is not user read or guaranteed delivery.

### PF-028 — Export authority

Dependencies: PF-004, PF-019.

- durable status resource and cancellation/purge;
- frozen recent-auth grant and coherent snapshot cutoff;
- versioned package, manifest, included/excluded domains, counts, checksums, encryption and short-lived revocable grants;
- rights-of-others filtering and download audit.

### PF-029 — Deletion plan, per-effect outcomes and tombstones

Dependencies: PF-028, PF-023, PF-024, PF-027.

- hosted and local device deletion separated;
- immutable domain/effect plan;
- account mutation restrictions during execution;
- public profile/social/ranking/notification corrections;
- per-device command/result: complete, pending, expired, unreachable, waived;
- execution receipt does not claim forensic erasure;
- legal holds, retention and backup tombstone reapplication.

### PF-030 — Release authorization and component manifest

Dependencies: PF-015.

- TUF root/delegated roles own authorization;
- release manifest is an authenticated target;
- component IDs, target paths, architecture, hashes, provenance, native signing, compatibility and update class.

### PF-031 — Migration, health and rollback policy

Dependencies: PF-014, PF-030; D-074.

- ordered migration chain and compatibility window;
- pre/post health checks;
- binary rollback only while prior version remains read/write compatible;
- irreversible migration recovery by roll-forward or verified pre-migration snapshot.

### PF-032 — Platform supervision and installer truth table

Dependencies: PF-011, PF-030.

- exact macOS, Windows, Linux, WSL, container and CI mechanisms;
- disclose session and restart limitations honestly;
- separate installation capability from competitive eligibility;
- install, upgrade, reboot, repair, uninstall and orphan cleanup states.

### PF-033 — Privacy projection and invalidation matrix

Dependencies: PF-021, PF-024, PF-026, PF-027, PF-028, PF-029.

- immutable historical facts versus current authorization;
- block, privacy, board removal, moderation reversal, identity consolidation and deletion invalidation;
- cursor/grant/cache invalidation and append-only retraction.

### PF-034 — Schema/interface inventory repair

Dependencies: PF-005 through PF-033.

- update every interface maturity and owner;
- remove stale “closed-world/complete” claims;
- register all new schemas, tables, messages, policies and fixtures;
- validate cross-file enum and identifier mappings.

### PF-035 — P-1140E validator repair

Dependencies: PF-034.

- verify owner existence and reachable lifecycle;
- detect SQL/state/API vocabulary mismatch;
- detect missing generation keys and authority revisions;
- verify content digests and tuple/certification references;
- remain structural and never claim runtime proof.

### PF-036 — P-1140F exact-head review

Dependencies: PF-001 through PF-035.

- pin exact commit;
- independent manual review of SR-005 through SR-016;
- record any P0/P1 with exact normative owner;
- require zero open P0/P1 before considering P-1104.

## Future implementation epics — blocked until P-1104

## Epic F — Reproducible foundation

### F-001 Toolchain and lockfile pins
Dependencies: PF-036, P-1104.

### F-002 Workspace initialization and package boundaries
Dependencies: F-001.

### F-003 Authoritative generated bindings
Dependencies: F-001, PF-034.

### F-004 Byte-identical regeneration and drift detection
Dependencies: F-003.

### F-005 Checked numeric/time/digest/identifier primitives
Dependencies: F-002.

### F-006 Privacy canary library and fixtures
Dependencies: F-002.

### F-007 Feature disable and emergency-revoke framework
Dependencies: F-002.

### F-008 Narrow format/lint/unit automation restoration
Dependencies: F-001 through F-007; separate automation authorization.

## Epic P — Normative VibeProof

### P-001 Rust canonical normative model
Dependencies: F-003.

### P-002 Rust deterministic CBOR encoder/decoder
Dependencies: P-001.

### P-003 Rust COSE_Sign1 and Ed25519 profile
Dependencies: P-002.

### P-004 Independent Go normative model and decoder
Dependencies: F-003.

### P-005 Go COSE verification and authorization binding
Dependencies: P-004.

### P-006 Exact claim/appraisal/receipt/challenge/batch vectors
Dependencies: P-003, P-005.

### P-007 Rotation/gap/correction/fork vectors
Dependencies: P-006.

### P-008 Malformed, mutation and resource corpus
Dependencies: P-003, P-005.

### P-009 Cross-language differential and byte-exact suite
Dependencies: P-006 through P-008.

### P-010 Fuzz/property harness activation
Dependencies: P-009; separate security/eval workflow authorization.

## Epic A — Accounting and deterministic integrity

### A-001 Immutable accounting-profile loader and digest verification
Dependencies: F-003, F-005.

### A-002 Operation/observer identity model
Dependencies: A-001.

### A-003 Category containment and source authority
Dependencies: A-002.

### A-004 Cache/reasoning/modality/total reconciliation
Dependencies: A-003.

### A-005 Retry/cancellation/nested-agent reconciliation
Dependencies: A-003.

### A-006 Duplicate-domain engine
Dependencies: A-002.

### A-007 Checked arithmetic and bounds
Dependencies: F-005.

### A-008 Deterministic contradiction/quarantine results
Dependencies: A-003 through A-007.

### A-009 Server pricing interpretation model
Dependencies: A-001.

### A-010 Accounting differential and order-invariance evidence
Dependencies: A-008.

## Epic N — Local runtime

### N-001 Local database schema and encrypted storage
Dependencies: F-002, F-005.

### N-002 Local migration and snapshot framework
Dependencies: N-001.

### N-003 Non-network collector process
Dependencies: A-008, N-001.

### N-004 Source-blind sync process
Dependencies: P-003, N-001.

### N-005 OS-supervised daemon
Dependencies: N-001.

### N-006 Authenticated channel handshake and peer identity
Dependencies: N-003 through N-005.

### N-007 Capability grants and typed local operations
Dependencies: N-006.

### N-008 Commitment, receipt and queue stores
Dependencies: P-003, N-001.

### N-009 Crash consistency and recovery
Dependencies: N-002, N-008.

### N-010 Protected key backend abstraction
Dependencies: P-003, N-001.

### N-011 macOS key and process integration
Dependencies: N-010.

### N-012 Windows key and process integration
Dependencies: N-010.

### N-013 Linux key and process integration
Dependencies: N-010.

### N-014 CLI control client
Dependencies: N-007.

### N-015 Interactive shell process/connection lifecycle
Dependencies: N-007.

### N-016 Shell subsystem projections and action separation
Dependencies: N-015.

### N-017 Optional privileged supervisor
Dependencies: N-006; separate privilege review.

### N-018 Sleep/resume/reboot/login/logout/offline suite
Dependencies: N-009, N-015.

### N-019 Disk-full/permission-loss/corruption suite
Dependencies: N-009.

### N-020 Content-egress and local-role adversarial suite
Dependencies: N-003 through N-017.

## Epic S — Server secure spine

### S-001 Go modular service foundation
Dependencies: F-002, F-003.

### S-002 PostgreSQL migration runner, roles and recovery
Dependencies: F-001.

### S-003 Typed idempotency persistence
Dependencies: S-002.

### S-004 Exact response replay and reservation recovery
Dependencies: S-003.

### S-005 Provider/OAuth transaction persistence
Dependencies: S-002.

### S-006 Account, linked identity and recent-auth persistence
Dependencies: S-002.

### S-007 Ranked identity, consolidation and appeal persistence
Dependencies: S-006.

### S-008 Device, key, installation and lineage persistence
Dependencies: S-002.

### S-009 Challenge and checkpoint persistence
Dependencies: S-008.

### S-010 Atomic claim acceptance and verifier transaction
Dependencies: P-009, A-010, S-003, S-009.

### S-011 Immutable claims/appraisals/receipts/corrections
Dependencies: S-010.

### S-012 Transactional outbox and worker checkpoints
Dependencies: S-011.

### S-013 Fork quarantine and requalification
Dependencies: S-008 through S-012.

### S-014 Compatibility/certification policy persistence
Dependencies: S-002.

### S-015 Crash-before/after-commit PostgreSQL evidence
Dependencies: S-010 through S-012.

## Epic O — OAuth, sessions and ranked identity

### O-001 GitHub provider capability implementation
Dependencies: S-005.

### O-002 X provider capability implementation
Dependencies: S-005.

### O-003 Desktop browser Authorization Code + PKCE
Dependencies: O-001, O-002.

### O-004 Callback issuer/redirect/mix-up protection
Dependencies: O-003.

### O-005 Limited-input interactive device flow
Dependencies: provider capability; never CI default.

### O-006 Web/native session and refresh-family rotation
Dependencies: S-006.

### O-007 Linked identity and exact unlink
Dependencies: O-004, O-006.

### O-008 Provider loss/compromise recovery
Dependencies: O-007.

### O-009 Ranked eligibility and investigation
Dependencies: S-007, O-007.

### O-010 Duplicate-account consolidation execution
Dependencies: O-008, O-009, S-011.

### O-011 Restriction, appeal, reversal and retirement
Dependencies: O-009.

### O-012 OAuth, recovery and consolidation race suite
Dependencies: O-004 through O-011.

## Epic V — First source vertical slice and certification

### V-001 Select one local runtime source
Dependencies: A-010, N-020.

### V-002 Select one cloud structured-usage source
Dependencies: A-010, S-014.

### V-003 Compatibility tuple and capability probe runtime
Dependencies: V-001, V-002.

### V-004 Local adapter implementation
Dependencies: V-003.

### V-005 Cloud adapter implementation
Dependencies: V-003.

### V-006 Certification runner and signed result bundle
Dependencies: V-004, V-005.

### V-007 Source upgrade-break and privacy fixtures
Dependencies: V-006.

### V-008 Multi-observer duplicate reconciliation
Dependencies: V-004, V-005, A-006.

### V-009 Emergency suspend/degrade/reinstate
Dependencies: V-006, S-014.

### V-010 Support registry publication
Dependencies: V-006 through V-009.

## Epic R — Ranking and pricing

### R-001 Period and season registry
Dependencies: S-002.

### R-002 Immutable score contributions
Dependencies: S-011, R-001.

### R-003 Ranking definitions and audience instances
Dependencies: O-009, R-001.

### R-004 Generation-keyed entries and isolated build
Dependencies: R-002, R-003.

### R-005 Generation validation and atomic promotion
Dependencies: R-004.

### R-006 Immutable snapshots and viewer-bound cursors
Dependencies: R-005.

### R-007 Tie rank and deterministic display ordering
Dependencies: R-004.

### R-008 Evidence/source/environment filters
Dependencies: R-002, S-014.

### R-009 Estimated pricing line items
Dependencies: A-009, R-002.

### R-010 Corrections and rebuild equivalence
Dependencies: R-002 through R-009.

### R-011 Movement, overtakes, streaks and retractions
Dependencies: R-006, R-010.

### R-012 Authorization/pagination/correction concurrency suite
Dependencies: R-003 through R-011.

## Epic G — Social, boards, presence and notifications

### G-001 Profiles and visibility policy
Dependencies: O-009.

### G-002 Friendship requests and canonical pairs
Dependencies: G-001.

### G-003 Directional blocks and unblock
Dependencies: G-001.

### G-004 Rivals
Dependencies: G-002, G-003.

### G-005 Board creation and atomic owner
Dependencies: G-001.

### G-006 Member invitations and acceptance
Dependencies: G-005.

### G-007 Separate admin promotion
Dependencies: G-006.

### G-008 Paired ownership transfer
Dependencies: G-007.

### G-009 Device-bound presence pulses
Dependencies: N-006, O-009.

### G-010 Account presence projection and multi-device merge
Dependencies: G-009.

### G-011 Viewer-specific presence authorization
Dependencies: G-003, G-005, G-010.

### G-012 Typed notification source events and inbox
Dependencies: G-002 through G-008, R-011.

### G-013 Channel subscriptions and delivery attempts
Dependencies: G-012.

### G-014 Preferences, quiet hours, read/dismiss and expiry
Dependencies: G-012, G-013.

### G-015 Retraction and current-authorization recheck
Dependencies: G-003, G-012.

### G-016 Social/presence/notification race and privacy suite
Dependencies: G-002 through G-015.

## Epic M — Moderation, export and deletion

### M-001 Moderation case and effect authority
Dependencies: O-011, G-001.

### M-002 Moderation appeal and reversal
Dependencies: M-001.

### M-003 Export status resource and snapshot
Dependencies: S-003, G-016, R-010.

### M-004 Export package, manifest, encryption and checksums
Dependencies: M-003.

### M-005 Download grants, audit, revocation and purge
Dependencies: M-004.

### M-006 Hosted deletion plan and account mutation freeze
Dependencies: M-001, M-003.

### M-007 Per-domain deletion/anonymization/retraction effects
Dependencies: M-006, R-010, G-015.

### M-008 Per-device local deletion commands and receipts
Dependencies: N-007, M-006.

### M-009 Tombstones, backup propagation and restore reapplication
Dependencies: M-007.

### M-010 Legal hold and minimal retained fraud/audit signals
Dependencies: M-006.

### M-011 Export/deletion concurrency and restore suite
Dependencies: M-003 through M-010.

## Epic L — Packaging, release and migration

### L-001 TUF repository roles and trusted client state
Dependencies: F-001.

### L-002 Authenticated release component manifest
Dependencies: L-001.

### L-003 Provenance and platform-native signature verification
Dependencies: L-002.

### L-004 Compatibility graph and migration chain
Dependencies: N-002, S-002, L-002.

### L-005 Health checks and staged activation
Dependencies: L-004.

### L-006 Compatible binary rollback
Dependencies: L-004, L-005.

### L-007 Irreversible migration roll-forward/snapshot recovery
Dependencies: L-004, L-005.

### L-008 macOS installer and supervision
Dependencies: N-011, N-015, L-003.

### L-009 Windows installer and supervision
Dependencies: N-012, N-015, L-003.

### L-010 Linux packages/systemd-user/headless
Dependencies: N-013, N-015, L-003.

### L-011 WSL/container/CI lifecycle packages
Dependencies: N-013, L-003.

### L-012 Update deadlines, deferral and eligibility
Dependencies: L-001 through L-011, S-014.

### L-013 Key compromise, freeze, rollback and mix-and-match suite
Dependencies: L-012.

### L-014 Uninstall, orphan cleanup and diagnostics
Dependencies: L-008 through L-011, M-008.

## Epic W — Hosted web integration

### W-001 Generated API clients and error/reason mapping
Dependencies: implemented OpenAPI and F-004.

### W-002 Authentication and recovery UX
Dependencies: O-012.

### W-003 Leaderboards and ranking context UX
Dependencies: R-012.

### W-004 Profiles, friends, rivals and boards UX
Dependencies: G-016.

### W-005 Presence and notification UX
Dependencies: G-016.

### W-006 Evidence, source, privacy and outbound disclosure UX
Dependencies: V-010, R-008.

### W-007 Device, lineage, fork, platform and update UX
Dependencies: S-013, L-012.

### W-008 Moderation and appeals UX
Dependencies: M-002.

### W-009 Export and deletion UX
Dependencies: M-011.

### W-010 Accessibility, responsive and exceptional-state matrix
Dependencies: W-002 through W-009.

## Epic X — Operations, open source and launch evidence

### X-001 Cloud-portable reference deployment
Dependencies: implemented server/web; separate deployment authorization.

### X-002 Secrets, signing keys and recovery procedures
Dependencies: L-013.

### X-003 Observability allowlist and privacy canaries
Dependencies: F-006, implemented services.

### X-004 Backup/restore and deletion tombstone drills
Dependencies: M-009.

### X-005 Incident response and abuse operations
Dependencies: M-002, X-003.

### X-006 Reproducible builds, SBOM and dependency/license governance
Dependencies: L-003.

### X-007 Public repository security/contribution documentation
Dependencies: X-006.

### X-008 Exact platform/source certification expansion
Dependencies: V-010, L-013.

### X-009 Performance, capacity and cost evidence
Dependencies: implemented product paths.

### X-010 Accessibility, privacy, security and recovery review
Dependencies: all launch paths.

### X-011 P-1105 launch-readiness review
Dependencies: X-001 through X-010; zero launch P0/P1.

## Explicit non-units

The following are not launch units:

- country leaderboards;
- SLM detector promotion;
- native Android, iOS, iPadOS or ChromeOS clients;
- kernel anti-cheat;
- mandatory inference proxy;
- unsupported claims generated from unexercised manifests;
- autonomous workflow activation during planning.

## Current next unit

PF-001 only. All `F-` through `X-` units remain blocked.