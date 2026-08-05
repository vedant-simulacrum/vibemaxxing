# VibeMaxxing Implementation Handoff

Status: canonical implementation plan; active — P-1104 is `authorized-open` as of 2026-08-05 while P-1140F is still open
Version: 12
Updated: 2026-08-05

## Purpose

This file is the sole implementation handoff. It does not itself authorize implementation; authorization is recorded only in `conformance/p1140f/gate-authorization-v1.json`. It defines:

1. the remaining planning-closure program;
2. the dependency-safe build sequence under P-1104 authorization;
3. the evidence required before any support, security, production, or launch claim.

`docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` decomposes this plan into review-sized units. It is subordinate to this file, accepted decisions, ADRs, repaired normative contracts, and the exact-head P-1140F verdict.

## Audit basis and coverage

This revision follows a repository-wide authority audit covering:

- `AGENTS.md`, project authority, documentation map, decision and task registers;
- product, privacy, accounting, security, identity, integrity, adapter, native, state, release, and operations contracts;
- ADRs, platform profiles, schemas, registries, fixtures, evaluation declarations, SQL planning model, OpenAPI, Protobuf, CDDL, Rust and Go prototype paths;
- recent commits, issue #41, draft PR #42, and the stale review-head relationship;
- cross-domain authority, lifecycle, persistence, privacy, replay, correction, recovery, migration, and evidence claims.

The GitHub connector does not expose a reliable single recursive repository-tree/read-all-lines operation. Coverage was therefore constructed from canonical maps, referenced owners, code search, known implementation paths, recent commit diffs, and direct file reads. This plan must not be represented as an independent source-code security audit or proof that every unreferenced binary/generated file was manually inspected.

## Current reality

### Planning authority

- P-1140A through P-1140E are historical planning/structural stages.
- P-1140F owns current semantic closure.
- SR-005 through SR-017 are open semantic P1 clusters.
- P-1104 is `authorized-open`. The owner opened it on 2026-08-05 under GitHub issue 44, before P-1140F closed and with all 13 P1 clusters open. The gate's documented preconditions were accepted, not met. The clusters remain open, remain tracked, and are not waived.
- Authorization permits implementation work. It supplies no evidence: nothing in this repository is implemented, secure, certified, or launch-ready because P-1104 is open.

### Implemented artifacts

- fixture-backed hosted-web and Storybook prototype;
- planning validators and repository doctor;
- schemas, registries, synthetic fixtures, exact vectors, and symbolic race plans;
- bounded Rust and Go protocol/accounting prototypes added after the original review head.

### Not implemented

- production collector, daemon, sync, shell, local database, installers, updater, or platform packages;
- certified source adapters or universal competitive support;
- normative VibeProof v1 Rust/Go interoperability;
- OAuth, session, identity, recovery, ranked identity, challenge, verifier, ranking, social, presence, notification, moderation, export, deletion, release, or operations services;
- production PostgreSQL migrations and transaction evidence;
- deployed infrastructure, TUF repository, release signing, production telemetry, incident operations, or launch evidence.

The executable Rust/Go artifacts are exploratory prototypes. They are not normative protocol evidence and cannot silently become the production base.

## Non-negotiable product and trust invariants

### Privacy boundary

- Servers never receive prompts, responses, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights, or content-derived hashes.
- A process that can read raw source content has no network capability.
- Networked sync accepts only closed-schema aggregate claims, commitments, receipts, diagnostics, and explicitly allowlisted metadata.
- Logs, crashes, support tools, moderator tools, privileged supervisors, exports, notifications, and analytics obey the same boundary.

### Competition and accounting

- Token Burn is the default raw metric.
- Estimated Cash Burn is server interpreted, versioned, and labelled estimated.
- Imported history never contributes to active competition.
- Standard and Hardened accepted claims may count globally.
- Authentic but intentionally pointless usage counts when non-duplicated.
- Client code never selects public evidence class, competition eligibility, pricing authority, or final duplicate disposition.
- Consolidated duplicate accounts combine independently valid historical claim contributions; stored account totals are never added together.

### Identity and recovery

- OAuth proves provider-account control, not unique humanity.
- Account, linked provider identity, device lineage, installation, and ranked identity are separate aggregates.
- One detected/resolved person has one active ranked identity.
- Provider subjects are durable provider IDs; usernames and display names are mutable metadata.
- Provider identities are never silently reassigned between accounts.
- Recovery, consolidation, restriction, and appeals preserve evidence and enforcement history.

### Anti-cheat

- Deterministic accounting, canonicalization, signatures, challenge binding, sequence continuity, duplicate domains, exact replay, corrections, and eligibility policy are authoritative.
- Kernel anti-cheat and mandatory inference proxying are rejected.
- SLM/statistical detection remains local-only, advisory, post-launch research and cannot rewrite totals, raise evidence tier, or permanently ban.
- Hardware-backed keys prove key continuity and device posture, not semantic truth of arbitrary usage values.

### Platform and local runtime

- Candidate native scope: macOS arm64/x86_64, Windows x64/ARM64, maintained Linux desktop/headless/remote, WSL, containers, and CI/ephemeral runners.
- Android, iOS, iPadOS, and ChromeOS have no native product lane.
- Daemon, collector, sync, CLI, shell, updater, and optional supervisor are separate trust domains.
- Shell exit never stops the daemon.
- Presence is server-derived from qualifying native activity: 30-second pulse, idle after 90 seconds, offline after 300 seconds; private is a visibility policy.

### Release and migration

- TUF/project authorization, platform-native signing, provenance, compatibility, migration safety, and server competitive eligibility are separate controls.
- Automatic binary rollback is permitted only while the prior release remains read/write compatible with committed state.
- After an irreversible migration, recovery is roll-forward or restoration of a verified pre-migration snapshot.

## Phase boundary: planning closure before implementation

No product code, generated production binding, production migration, deployment, or workflow activation may begin during the following program.

### P-1140F-1 — Re-establish sole authority

Objectives:

- make normative CDDL/COSE and `conformance/vibeproof/v1/` the sole VibeProof v1 authority;
- remove, rename, or quarantine the unsigned 11-field shadow protocol and its misleading conformance labels;
- classify every artifact as specification, fixture, prototype, production implementation, or executable evidence;
- align status, task catalog, schema inventory, handoff, work breakdown, issue #41, and review packet;
- inventory every mutable aggregate and verify one lifecycle and one persistence owner.

Exit criteria:

- no file or suite can reasonably be read as a second VibeProof v1 authority;
- no suite claims ranking, protocol, security, or conformance evidence it does not execute;
- all current semantic findings and accepted decisions are traceable from canonical entrypoints.

### P-1140F-2 — Close identity, OAuth, lineage, replay, and recovery

Objectives:

- one provider-configuration registry and one persisted OAuth transaction authority;
- bind account/session/recent-auth/action/provider/redirect/state/PKCE/callback/result;
- exact linked-identity lifecycle, last-method protection, provider-loss and compromise recovery;
- immutable duplicate-account consolidation plan using claim-level historical recomputation;
- separate ranked-identity, investigation, restriction, retirement, appeal, and reversal authorities;
- lineage-scoped continuity and one canonical challenge/checkpoint/rotation/fork contract;
- quarantine every post-fork branch, preserve pre-fork accepted claims, select or recover one survivor, resume through a new lineage generation, and keep the decision appealable.

Exit criteria:

- no raw authorization code can mutate identity outside its initiating transaction;
- no account or device recovery path resets competitive or enforcement history;
- all replay, challenge, rotation, fork, recovery, and appeal outcomes have stable reason codes and persistence.

### P-1140F-3 — Close local trust boundary, adapters, and accounting inputs

Objectives:

- split shell process state from daemon, collection, sync, authentication, permission, update, and connectivity projections;
- define authenticated local channels using OS peer identity, release/artifact identity, daemon-assigned role, generation, nonce, sequence window, capabilities, and revocation;
- define local database ownership, migration generations, crash consistency, queue bounds, and content-free diagnostics;
- define one atomic compatibility tuple per product/source/version/platform/mode/artifact/accounting/privacy profile;
- define certification result, expiry, suspension, downgrade, and reinstatement;
- make source observation carry or inherit an authenticated tuple before normalization;
- close operation identity, parent/child, retry, observer equivalence, checked arithmetic, contradictions, and duplicate-domain semantics;
- keep generic ACP, OpenTelemetry, proxy, wrapper, and unknown-version support private until an exact tuple is exercised.

Exit criteria:

- no broad manifest certification can authorize an untested Cartesian product;
- no collector invents provider/model/profile/certification identity from undocumented configuration;
- no same-user untrusted client can impersonate another local role merely by claiming a role field.

### P-1140F-4 — Close server product state and privacy projection

Objectives:

- exact idempotency replay with typed principals, operation scope, request canonicalization, stored bounded response, crash recovery, expiry, and business-effect/outbox linkage;
- separate ranking definition, audience, immutable generation, snapshot, cursor, contribution, correction, period, and season authorities;
- current viewer authorization for friends, rivals, private/unlisted boards, presence, notifications, exports, and cached projections;
- canonical friendship, directional block, rivalry, board membership, role, invitation, and ownership transfer;
- invitations grant only non-privileged roles; admin promotion and ownership transfer are separate recent-authenticated audited operations;
- device-bound presence pulses and separate viewer visibility;
- immutable notification source event, recipient inbox item, channel attempts, preferences, read/dismiss, expiry, and retraction;
- durable export/deletion status resources, immutable plans, per-effect and per-device results, tombstones, legal holds, and backup propagation.

Default planning decisions:

- retain exact high-impact mutation replay for at least 30 days;
- retain claim-batch replay until a later acknowledged checkpoint safely supersedes it;
- reject expired-key reuse for high-impact operations;
- report hosted deletion separately from each local device and never claim all local data erased while a device is unreachable or unverified.

Exit criteria:

- every private display/delivery boundary rechecks current authorization;
- immutable historical facts coexist with immediate privacy invalidation through projections and retractions;
- no asynchronous job returns an unusable dead-end identifier;
- no committed mutation can lose its exact result after a dropped connection.

### P-1140F-5 — Close release trust and exact-head review

Objectives:

- make release manifests authenticated TUF targets rather than self-authorizing signature containers;
- define component IDs, target paths, architecture, provenance, native signing, compatibility, migration chain, health checks, rollback class, and server eligibility;
- persist trusted TUF client state and canonical metadata;
- align release, update, migration, rollback, local IPC, platform profile, and installer state vocabularies;
- update structural validators without claiming semantic proof;
- pin one exact repaired head and obtain an independent zero-P0/P1 semantic verdict.

Exit criteria:

- SR-005 through SR-017 are closed in every normative and machine-readable owner;
- planning validators pass from a clean checkout;
- P-1104 is a separate explicit user decision, granted on 2026-08-05.

## P-1104 implementation entrance gate

State: `authorized-open`. Owner: `vedant-simulacrum`. Date: 2026-08-05. Reference: GitHub issue 44. Machine-readable record: `conformance/p1140f/gate-authorization-v1.json`.

The gate as originally written required all of the following:

1. P-1140F is `complete-planning`;
2. SR-005 through SR-017 are closed;
3. one exact commit is recorded as the approved implementation base;
4. canonical docs, schemas, SQL, Protobuf/CDDL, fixtures, decisions, tasks, and review issue agree;
5. all planning-only checks pass from a clean checkout;
6. no stale branch, prototype, generated artifact, or issue comment is treated as authority;
7. the user explicitly authorizes P-1104.

Only 5, 6 and 7 held at authorization. Conditions 1, 2, 3 and 4 did not, and 1 and 2 still do not. The owner opened the gate anyway, with that stated, on the reasoning that the 13 open findings are contradictions between documents whose closure is largely unfalsifiable without running code, and that most become testable once behaviour exists.

Consequences that remain in force:

- SR-005 through SR-017 stay open and tracked in `conformance/p1140f/semantic-findings-v1.json`. Closing them is still required for P-1140F; they are not waived, deferred, or reclassified.
- No claim of support, security, privacy conformance, certification, production readiness, or launch readiness is authorized by this gate. Those are governed by `P-1105` and `P-1131` and are unmet.
- The **Not implemented** list above is unchanged.
- Product, security, evaluation, release, signing and deployment automation stays disabled under `P-1007`.
- Work performed under this authorization is prototype-grade until it carries its own evidence. Authorization is not evidence.

## Post-approval implementation program

### Wave 0 — Reproducible engineering foundation

Deliver:

- pinned Rust, Go, Node/package manager, Buf, CDDL, OpenAPI, JSON Schema, PostgreSQL, migration, cross-compilation, signing, and packaging toolchains;
- repository workspaces and generated-binding boundaries;
- byte-identical regeneration;
- checked numeric/time/digest/identifier primitives;
- privacy-canary framework;
- explicit feature flags and emergency disable paths;
- only narrow format/lint/unit automation initially.

Do not deliver user-facing support or production deployment.

### Wave 1 — Normative VibeProof reference implementations

Deliver independent Rust and Go implementations of:

- canonical claim/appraisal/receipt/challenge/batch/gap/rotation/correction records;
- deterministic CBOR and COSE_Sign1 profile;
- exact external AAD and protected headers;
- resource bounds, malformed rejection, unknown-field behavior, and checked arithmetic;
- byte-exact official vectors and cross-language differential tests.

Exit: both languages verify the same normative bytes without sharing a hand-written shadow model.

### Wave 2 — Accounting and deterministic integrity core

Deliver:

- immutable accounting profile registry;
- source authority and containment semantics;
- cache, reasoning, modality, total, retry, cancellation, nested-agent, and cumulative/incremental reconciliation;
- operation and observer equivalence model;
- duplicate-domain engine;
- deterministic rule result and reason registry;
- server pricing interpretation boundary.

Exit: multiple legitimate operations aggregate; equal-authority contradictions quarantine; ordering does not change results; overflow cannot produce maximum score.

### Wave 3 — Local secure spine

Deliver:

- isolated non-network collector;
- source-blind network sync;
- OS-supervised daemon;
- encrypted local database, ordered migrations, commitments, receipts, queues, and crash recovery;
- authenticated local channels and capability grants;
- protected key lifecycle;
- CLI and shell control clients;
- sleep, resume, reboot, login/logout, offline, disk-full, permission-loss, corruption, and update behavior.

Exit: components fail independently and forbidden content cannot cross any networked boundary.

### Wave 4 — Server secure spine

Deliver:

- Go modular service boundary;
- ordered PostgreSQL migrations, roles, constraints, recovery, and transaction helpers;
- typed idempotency ledger with exact replay;
- challenge, claim acceptance, appraisal, checkpoint, correction, outbox, and rebuild facts;
- lineage/fork quarantine;
- source/compatibility policy service.

Exit: exact retry cannot add score; ambiguous commits recover the exact original result; rebuild matches source facts.

### Wave 5 — OAuth, sessions, recovery, and ranked identity

Deliver:

- provider-capability-aware GitHub and X browser OAuth;
- limited-input interactive device flow only where accepted;
- token-family rotation and replay revocation;
- linked identity, recent-auth, provider loss/compromise recovery;
- ranked identity, investigation, restriction, consolidation, retirement, appeal, and reversal;
- claim-level historical consolidation without aggregate summation.

Exit: provider conflicts cannot transfer an identity or reset score history.

### Wave 6 — Two-source vertical slice

Select one local runtime source and one cloud structured-usage source.

Each requires:

- immutable compatibility tuple;
- artifact/provenance/SBOM verification;
- source-version and capability probes;
- accounting/privacy profiles;
- duplicate, retry, cancellation, upgrade-break, malformed, and privacy fixtures;
- certification result and emergency disable.

Exit: one complete end-to-end local path and one cloud path produce ranked claims under honest evidence ceilings.

### Wave 7 — Ranking, periods, pricing, and corrections

Deliver:

- ranking definitions and audience instances;
- exact period and season lifecycle;
- immutable contribution ledger;
- generation-keyed entries, validation, atomic promotion, rollback pointer, snapshots, and viewer-bound cursors;
- tie rank from score only plus deterministic display ordering;
- estimated pricing aliases and line items;
- corrections, rebuild equivalence, movement, overtakes, streaks, and retractions.

Exit: private scopes are authorized, pagination is immutable, and every score is explainable.

### Wave 8 — Social, boards, presence, and notifications

Deliver:

- profiles and visibility policy;
- canonical friendship and directional blocks;
- rivals;
- board creation with atomic initial owner;
- member invitations, separate admin promotion, and paired ownership transfer;
- device-bound presence pulses and viewer projections;
- notification source events, inbox, grouping, channel attempts, quiet hours, read/dismiss, expiry, and retraction.

Exit: block/privacy changes invalidate visibility immediately and stale notifications cannot reveal private state.

### Wave 9 — Moderation, appeals, export, and deletion

Deliver:

- typed moderation cases, evidence, effects, restrictions, reversals, and appeals;
- coherent encrypted export snapshots, manifests, checksums, grants, audit, revocation, and purge;
- immutable hosted deletion plan and per-effect outcomes;
- per-device local deletion commands and execution receipts;
- tombstones, backup propagation, legal holds, projection corrections, and completion wording.

Exit: users can monitor and recover every asynchronous workflow; deletion cannot resurrect data or overclaim remote erasure.

### Wave 10 — Packaging, TUF, updates, migration, and rollback

Deliver:

- exact macOS, Windows, Linux, WSL, container, and CI lifecycle packages;
- daemon/shell registration and uninstall;
- TUF repository and trusted client state;
- release manifests as authenticated targets;
- immutable artifacts, provenance, native signing, compatibility graph, migration chain, health checks, deadlines, compromise recovery, and rollback policy.

Exit: each platform installs, updates, migrates, recovers, and uninstalls under an exact certified profile.

### Wave 11 — Hosted web integration

Deliver:

- generated clients only;
- authentication/recovery, leaderboards, profiles, rivals, boards, privacy disclosures, evidence status, devices, updates, moderation, appeals, export, and deletion UX;
- responsive, accessible, loading, empty, conflict, degraded, offline, restricted, and correction states;
- no independent business-policy reimplementation.

Exit: the existing prototype becomes integrated implementation only after all data comes from implemented contracts.

### Wave 12 — Operations and open-source readiness

Deliver:

- cloud-portable reference infrastructure;
- secret and key management;
- observability allowlist and privacy canaries;
- backup/restore and tombstone reapplication drills;
- incident response, abuse operations, support boundaries, release key compromise recovery;
- reproducible builds, dependency/license/SBOM governance, DCO, security policy, contributor docs, and public repository preparation.

Exit: operational drills and recovery evidence exist without exposing forbidden content.

### Wave 13 — Compatibility expansion

Expand adapters and platform profiles only through exact atomic certification tuples. Generic ACP, OTel, proxies, wrappers, orchestrators, subagents, WSL host/guest, containers, and CI matrices require duplicate and lifecycle reconciliation before competitive eligibility.

### Wave 14 — Launch evidence and review

P-1105 may begin only after:

- every advertised source/platform tuple has non-expired executable evidence;
- threat, privacy, integrity, migration, backup, rollback, and incident drills pass;
- public support pages are generated from active certification records;
- no P0/P1 launch finding remains;
- open-source and legal/dependency reviews are complete.

Country leaderboards and SLM promotion remain post-launch.

## Cross-cutting implementation requirements

Every implementation PR must state:

- owning work-unit ID and accepted decision/contract;
- exact aggregate and persistence owner;
- privacy classification and egress impact;
- authorization and idempotency behavior;
- migrations and rollback/roll-forward behavior;
- compatibility and platform impact;
- tests and evidence actually produced;
- feature disable, emergency revoke, or recovery path;
- documentation and generated-artifact updates.

A contradiction found during implementation reopens its planning owner. It must never be hidden in a local workaround.

## Evidence taxonomy

- **Specification:** intended normative behavior.
- **Fixture:** synthetic input/output expectation.
- **Prototype:** executable exploratory artifact with incomplete authority.
- **Production implementation:** integrated code satisfying accepted contracts.
- **Executable evidence:** reproducible result supporting one precise claim.
- **Certification:** current signed result for one exact compatibility/platform tuple.

No lower category may be described as a higher category.

## Current next action

Complete P-1140F-1. Do not begin Wave 0 or any product implementation.