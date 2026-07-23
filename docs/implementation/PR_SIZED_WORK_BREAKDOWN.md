# PR-Sized Implementation Work Breakdown

Status: normative planning-ready work breakdown; inactive until the user explicitly authorizes P-1104.
Updated: 2026-07-24

Each unit must be independently reviewable, tested, migration-aware and reversible where possible. Units may be combined only when risk, ownership and rollback remain clear.

Country leaderboards and the SLM detector are not launch implementation units. Android, iOS, iPadOS and ChromeOS have no native implementation units under D-066.

## Dependency rules

- Bind implementation to the P-1140B–E repaired schemas, registries, fixtures and state-machine IDs; changes require explicit authority updates.
- Foundation precedes the synthetic secure spine.
- The synthetic spine precedes real adapters and broad UX.
- Device/continuity and server-verifier units precede competitive ranking.
- One local and one cloud source precede broad adapter expansion.
- Identity/session correctness precedes social write operations.
- Ranking-view identity precedes overtakes, movement and notifications.
- Platform core precedes packaging breadth.
- Mandatory-update infrastructure precedes external competitive distribution.
- Privileged profiles cannot ship before unprivileged profiles and independent security review.
- Packaging/release integrity precedes external distribution.

## Epic F — contract workspaces and generation

### F-01 Pin implementation toolchains
Rust 2024, Go, Node/package manager, Buf/Protobuf, CDDL, OpenAPI, JSON Schema, migration and cross-compilation tooling.

### F-02 Authoritative schema workspaces
Repaired local event schemas, VibeProof CDDL/COSE, internal Protobuf, endpoint-specific OpenAPI, PostgreSQL migrations, reason/policy registries, state-machine registry, exact platform profiles, release sets, ranking views and export manifests.

### F-03 Generated binding pipeline
Generate Rust, Go and TypeScript bindings. Clean regeneration must be byte-identical.

### F-04 Breaking-change classification
Classify source-compatible, wire-compatible, migration-required and protocol-major changes.

### F-05 Privacy-canary framework
Seed forbidden values across source, IPC, logs, network, notifications, review, privileged supervisor and platform crash facilities.

### F-06 Checked numeric/time primitives
Cross-language safe token, sequence, timestamp, duration and money primitives.

### F-07 Platform-profile schema
Machine-readable OS family/release/architecture/distribution/environment/lifecycle/key/update/support tuple.

### F-08 Decision traceability validator
Run `validate_p1140e_contracts.py` to validate D-001..D-069 ownership, API/state/platform coverage, SQL race plans and reason references, and reject superseded paths or out-of-scope mobile/ChromeOS native work.

Acceptance: blocked schemas cannot enter builds; unsupported toolchains fail clearly; generated output and traceability are deterministic.

## Epic P — VibeProof protocol core

### P-01 EvidenceClaim domain model
No public evidence state or pricing authority.

### P-02 Deterministic CBOR profile
Exact ordering, shortest integers, definite lengths, tag policy, depth and size limits.

### P-03 COSE key/signature profile
Protected headers, key IDs, Ed25519/EdDSA, external AAD and exact signed bytes.

### P-04 Go independent decoder/verifier
Independent parser implementation.

### P-05 TypeScript diagnostic decoder
Read-only developer/privacy inspection only.

### P-06 Exact-byte golden vectors
Claims, receipts, appraisals, rotations, corrections and gaps.

### P-07 Malformed parser corpus
Duplicate keys, non-minimal values, wrong tags, algorithm confusion, truncation, nesting and allocation attacks.

### P-08 VerifierAppraisal model
Server-owned dimensions, profile, public state, outcome, reasons and policy version.

### P-09 CheckpointReceipt model
Bind lineage, accepted local head, server state, receipt sequence and policy.

### P-10 KeyRotationTransition
Old/new authorization, boundary sequence and recovery variant.

### P-11 CorrectionRecord
Append-only server-authorized correction and supersession.

### P-12 Atomic batch envelope
One challenge/batch/replay state machine without partial acceptance ambiguity.

Acceptance: independent Rust/Go verification agrees exactly and malformed input fails without resource exhaustion.

## Epic A — accounting and deterministic integrity

### A-01 Accounting-profile registry
Provider/runtime/API-mode/model/tokenizer profiles with immutable versions.

### A-02 Canonical token categories
Mutually exclusive components and source containment mappings.

### A-03 Source-total reconciliation
Prevent nested/cache/reasoning/modality double counting.

### A-04 Retry/cancellation accounting
Distinct execution, internal retry, aborted stream and unknown remainder.

### A-05 Nested-agent accounting
Parent/child attribution and duplicate prevention.

### A-06 Cache/reasoning profiles
Provider-specific semantics and fixtures.

### A-07 Local tokenizer profile
Exact model/tokenizer digest and reconstruction ceiling.

### A-08 Runtime-native profile
Local inference counters, token IDs and runtime-generation semantics.

### A-09 Deterministic rules engine
Versioned fatal, quarantine and diagnostic outcomes.

### A-10 Clock/generation rules
Monotonic domain, suspend/resume, process reset and rollback.

### A-11 Duplicate-domain engine
Keyed non-content structural domains and collision behavior.

### A-12 Throughput-envelope registry
Transparent source/runtime physical and protocol bounds.

### A-13 Pricing rule engine
Server-side immutable datasets, alias resolution, conditions, line items, rounding and provenance.

Acceptance: representative cloud/local/WSL/container/CI fixtures reconcile without double counting or client-controlled cost.

## Epic N — native collector, daemon and local state

### N-01 Typed SourceObservation IPC
Replace arbitrary JSON/bytes with bounded generated messages.

### N-02 Collector process
Adapter supervision, normalization, accounting and deterministic rules; no network.

### N-03 Sync process
Challenges, claims, receipts, retries and sessions; no source-content access.

### N-04 Daemon/control process
Lifecycle, configuration, health and capability routing without content access.

### N-05 Authenticated local IPC
Peer identity, ACLs, challenge-response, version negotiation, deadlines, limits and replay controls.

### N-06 Encrypted local database
Separate source cursors, normalized facts, commitments, pending claims, receipts, audit and diagnostics.

### N-07 Append-only commitment store
Local sequence, heads, monotonic generation and checkpoint receipt.

### N-08 Crash consistency
Transactional normalized event, rule result, commitment and queue writes.

### N-09 Offline queue/backpressure
Bounded storage, batching, retry, expiry and visible backlog.

### N-10 Disk-full behavior
Stop safely without corrupting state or silently dropping ranked activity.

### N-11 Sleep/resume and clock recovery
Deterministic generation changes and diagnostics.

### N-12 Corrupt-state recovery
Quarantine, gap declaration where allowed and explicit new lineage where required.

### N-13 Local outbound audit ledger
Exact sent fields and receipt status without content.

### N-14 Privacy preview
Render exact outbound data before/after serialization.

### N-15 CLI core
Install, status, pause, adapters, privacy, export/delete, update/rollback and doctor.

### N-16 Always-on supervisor
Desired state, OS registration, child heartbeats, crash-loop isolation and maintenance handoff under ADR-010.

### N-17 Optional privileged-supervisor protocol
Separate identity, typed ACL-bound IPC, lifecycle-only capabilities and user isolation under ADR-012.

### N-18 Mandatory-update coordinator
Update classes, signed deadlines, maintenance lease, safe checkpoint, blocked-version and rollback behavior under ADR-013.

### N-19 Environment identity
Native/WSL/container/CI environment kind, lifecycle class and support tuple.

### N-20 Platform status diagnostics
Expose exact profile, service mode, key class, update deadline, evidence ceiling and repair actions.

Acceptance: daemon remains resident in degraded states; shell and children fail independently; privileged boundary cannot read source content.

## Epic D — device identity and platform keys

### D-01 Device-lineage schema
Separate installation, key and lineage identity.

### D-02 Enrollment protocol
Bind account, session, key, collector build and challenge.

### D-03 macOS key backend
Keychain/Secure Enclave capability and migration behavior on Apple silicon and Intel.

### D-04 Windows key backend
CNG/TPM non-exportable path and DPAPI fallback on native x64/ARM64.

### D-05 Linux key backend
TPM/keyring/Secret Service and encrypted fallback matrix.

### D-06 Rotation flow
Old/new authorization and exact sequence boundary.

### D-07 Lost-key recovery
Revoke old key, new lineage and no silent trust inheritance.

### D-08 Restore/clone inputs
Backup, home restore, credential migration, VM/WSL/container volume snapshot signals.

### D-09 Requalification policy
Recovered/migrated lineages cannot inherit Hardened automatically.

### D-10 Optional attestation adapters
Issuer-specific nonce/freshness/revocation evidence, never blanket truth.

### D-11 CI ephemeral identity
Short-lived key, workflow/run binding and no implicit cross-job continuity.

### D-12 Container workload identity
Replica/state-volume ownership and duplicate prevention.

Acceptance: clone, export/import, runner retry and architecture migration never silently duplicate score or preserve stronger trust.

## Epic S — server secure spine

### S-01 Go modular service skeleton
HTTP, auth callbacks, verifier, workers and admin CLI around PostgreSQL.

### S-02 PostgreSQL migration baseline
Ordered migrations, roles, constraints and recovery.

### S-03 Device/key/environment persistence
Lineages, keys, status, environment profiles, attestation and recovery events.

### S-04 Challenge service
Random account/device-bound single-use challenges with limits.

### S-05 Idempotency ledger
Scoped key, principal, fingerprint, outcome, expiry and conflicts.

### S-06 Atomic claim acceptance
Decode through appraisal, ledger, checkpoint and outbox in one transaction.

### S-07 Exact replay response
Stored outcome for byte-identical retry.

### S-08 Conflict/fork quarantine
Registered conflict outcomes for reused identities/domains.

### S-09 Privacy-safe rejection records
Digest and bounded metadata only.

### S-10 Immutable claim/appraisal/checkpoint ledger
Facts immutable; projections/cases separate.

### S-11 Transactional outbox
Ranking/social events only after accepted transaction.

### S-12 Worker idempotency/checkpoints
Crash-safe deterministic processing.

### S-13 Synthetic ranking projection
Canonical ranking view.

### S-14 Rebuild equivalence
Replay facts/corrections and hash compare.

### S-15 Compatibility/update policy service
Signed minimum versions, deadlines, environment-specific restrictions and safe blocked-version responses.

### S-16 Environment eligibility policy
Global WSL/container/CI eligibility plus board minimum-profile overrides.

Acceptance: exact retry cannot add score; expired tools/versions fail with signed actionable outcomes; environment restrictions are policy-driven and auditable.

## Epic V — first sources and universal compatibility

### V-01 Local runtime selection spike
Compare current Ollama, llama.cpp and vLLM structured counters and version identity.

### V-02 Cloud source selection spike
Compare current official structured usage interfaces without calling metadata signed receipts.

### V-03 Local adapter
Manifest, probe, observation, accounting, duplicate domain and fixtures.

### V-04 Cloud adapter
Manifest, local response-metadata observation, accounting, duplicate domain and fixtures.

### V-05 Certification runner
Exact artifact/source/version/platform/mode/profile bundle and immutable result digest.

### V-06 Support registry publication
Generate honest support ceiling from exercised results.

### V-07 Emergency disable/sunset
Signed state, diagnostics and downgrade behavior.

### V-08 Upgrade-break fixtures
Changed source versions fail closed for stronger profiles.

### V-09 WSL host/guest reconciliation
Prevent Windows and WSL duplicate capture.

### V-10 Container replica reconciliation
Prevent duplicated scoring from cloned volumes/replicas.

### V-11 CI retry/matrix reconciliation
Prevent retry/cache/workspace/matrix double counting.

## Epic I — authentication, sessions and ranked identity

### I-01 GitHub App web authorization
### I-02 GitHub native device authorization
### I-03 X Authorization Code + PKCE
### I-04 OAuth transaction schema
### I-05 Web session families
### I-06 Native token families
### I-07 DPoP implementation decision
### I-08 Linked identity state machine
### I-09 Optional stronger factors
### I-10 Recovery flow
### I-11 Ranked eligibility
### I-12 Duplicate-identity case model
### I-13 Restriction/consolidation
### I-14 Anti-reenrollment retention

Acceptance: provider/session/recovery operations cannot duplicate claims, reset scores or bypass one-ranked-identity policy.

## Epic R — ranking, periods, corrections and pricing

### R-01 Canonical ranking_view_id
### R-02 Period registry
### R-03 Server-anchored event interval
### R-04 Score fact/delta model
### R-05 Snapshot generation
### R-06 SQL rank semantics
### R-07 First-reached semantics
### R-08 Keyset pagination
### R-09 Evidence/environment filters
### R-10 Pricing interpretation records
### R-11 Immutable alias resolution
### R-12 Unpriced/local-compute UX data

Acceptance: environment class changes filtering/eligibility but never mutates accepted raw token totals.

## Epic G — profiles and social graph

### G-01 Handle assignment ledger
### G-02 Profile privacy matrix
### G-03 Block state machine
### G-04 Friend-request state machine
### G-05 Friendship edge model
### G-06 Rival state machine
### G-07 Board aggregate root
### G-08 Membership/role state machine
### G-09 Board invitation state machine
### G-10 Board policy versions
### G-11 Organization/community/hacker-house specialization

Board policy supports minimum evidence and environment exclusions without changing global eligibility.

## Epic L — presence, movement and notifications

### L-01 Qualifying activity signal
### L-02 Presence lease transaction
### L-03 Audience/privacy projection
### L-04 Multi-device merge
### L-05 Overtake event
### L-06 Rank movement event
### L-07 Typed notification schema
### L-08 Preferences and quiet hours
### L-09 Deduplication/hysteresis/grouping
### L-10 Retraction/correction
### L-11 Mandatory-update/security notifications

No notification may expose source/project content.

## Epic M — moderation, appeals and lifecycle

### M-01 Moderation case aggregate
### M-02 Progressive actions
### M-03 Automated authority limits
### M-04 Reviewer authorization/audit
### M-05 Appeal state machine
### M-06 Reversal record
### M-07 Ranking rebuild after reversal
### M-08 Export workflow
### M-09 Server deletion workflow
### M-10 Local deletion workflow

## Epic U — web and native UX

### U-01 Native onboarding/permissions
### U-02 Account login/device pairing
### U-03 Daemon/collector/sync health
### U-04 Adapter discovery/support ceilings
### U-05 Exact outbound privacy inspection
### U-06 Global leaderboard/period/filter views
### U-07 Friends leaderboard/social home
### U-08 Board/org/community/hacker-house leaderboards
### U-09 Public profile/evidence disclosure
### U-10 Personal activity/model/agent views
### U-11 Estimated Cash Burn/provenance
### U-12 Friends/rivals/overtakes/movement
### U-13 Presence controls/privacy
### U-14 Notifications/preferences
### U-15 Board administration
### U-16 Devices/identities/sessions
### U-17 Moderation/restriction/appeal
### U-18 Export/deletion
### U-19 Exceptional-state matrix
### U-20 Accessibility/performance
### U-21 Exact platform-profile status
### U-22 Update channel/deadline/rollback UX
### U-23 Privileged-mode consent/status/downgrade UX

No Android, iOS, iPadOS or ChromeOS native UX unit exists.

## Epic O — packaging, updater and operations

### O-01 macOS Apple-silicon packaging
Signed/notarized arm64 app, daemon and menu-bar release lane.

### O-02 macOS Intel packaging
Signed/notarized x86_64 lane and Universal 2 compatibility where possible.

### O-03 Windows x64 packaging
Native signed installer/service/tray lane.

### O-04 Windows ARM64 packaging
Native signed installer/service/tray lane; no emulation-only claim.

### O-05 Linux deb ecosystem
Debian/Ubuntu-family signed repository and service integration.

### O-06 Linux rpm ecosystems
Fedora/RHEL/Rocky/Alma and openSUSE/SLES signed profiles.

### O-07 Linux Arch/Alpine/Nix/portable
Arch, musl/Alpine, Nix and signed glibc/musl tarball profiles.

### O-08 Linux init/service integrations
systemd-user/linger, OpenRC, runit, s6, dinit and weaker desktop fallback classification.

### O-09 WSL packaging
Independent guest installation, update and uninstall.

### O-10 Container images
Non-root signed multi-architecture images and immutable replacement.

### O-11 CI tool/action packaging
Pinned signed artifacts and expiry compatibility.

### O-12 Signed installer/uninstall verification
All native/package profiles.

### O-13 TUF trust root and role policy
### O-14 Release-set manifest/compatibility graph
### O-15 Automatic update policy engine
Security, compatibility and routine deadlines with bounded deferral.

### O-16 Atomic update/interrupted recovery
### O-17 Rollback/freeze/compromised-version handling
### O-18 Blocked-version safe mode
Diagnostics, update, export and uninstall retained where safe.

### O-19 Privileged supervisor packaging
Separate least-privilege Mac/Windows/Linux artifacts.

### O-20 SBOM/provenance generation
### O-21 Signature transparency/consumer verification
### O-22 Environment/secrets/migration promotion
### O-23 Observability allowlist/canary blocking
### O-24 Backup/restore/disaster recovery
### O-25 SLOs/alerts/incidents/key-compromise playbooks
### O-26 Restore product CI/security/dependency/evaluation/release gates
### O-27 Independent security/privacy review
### O-28 Open-source history/secret/license/trademark review
### O-29 Reproducible public release and launch gate
### O-30 Out-of-scope platform guard
Fail packaging/release if Android, iOS, iPadOS or ChromeOS native artifacts are introduced without a superseding decision.

## Adversarial beta campaigns

Separate campaigns are required for:

- canonicalization/parser/signature/key confusion;
- replay/fork/race storms;
- device clone/restore/migration;
- modified adapters and fake source events;
- clock/suspend/runtime reset/disk failure;
- retry/cancellation/cache/reasoning/nested accounting;
- long offline and extreme legitimate local volume;
- identity/collusion/shared-network false positives;
- social/board authorization abuse;
- notification/privacy leakage;
- moderation reversal/rebuild;
- update/signing/freeze/rollback compromise;
- privileged supervisor cross-user and substitution attacks;
- Windows/WSL duplicate capture;
- container replica/volume clone duplication;
- CI retry/cache/matrix duplication;
- privacy canaries across all processes, logs and server surfaces.

## Post-launch tracks

### PL-01 Country leaderboard research
No launch dependency.

### PL-02 SLM detector bakeoff
Synthetic/consented data, deterministic/classical baselines and separate approval.

## PR acceptance contract

Every PR names:

- unit ID and dependencies;
- decisions, ADRs, contracts and schemas;
- privacy/security impact and threat cases;
- exact platform profiles;
- database/API/wire compatibility and migrations;
- rollback or disable path;
- tests, benchmarks, fixtures and generated artifacts;
- support/evidence ceilings;
- unresolved risks.

Placeholder-only PRs, skipped tests, mocks, empty certifications and planning/prototype validators do not close implementation work.