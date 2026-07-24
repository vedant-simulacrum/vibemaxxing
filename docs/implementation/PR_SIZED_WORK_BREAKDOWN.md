# PR-Sized Implementation Work Breakdown

Status: consolidated planning draft; inactive until P-1140F closes and the user explicitly authorizes P-1104
Updated: 2026-07-24

Each unit must remain independently reviewable, testable, migration-aware and reversible where possible. This file is subordinate to `IMPLEMENTATION_HANDOFF.md`, accepted decisions, ADRs and repaired contracts.

Country leaderboards and the SLM detector are not launch implementation units. Android, iOS, iPadOS and ChromeOS have no native implementation units.

## Entrance constraints

Before any unit starts:

- P-1140F must be complete with zero open semantic P0/P1 findings;
- SR-001 through SR-004 must be repaired in the normative contracts;
- generated types must come only from repaired schemas;
- product CI/security/release automation remains disabled until separately authorized;
- no planning fixture or prototype is implementation evidence.

## Dependency order

1. semantic contract repairs and generated workspaces;
2. deterministic protocol/accounting core;
3. synthetic secure spine;
4. local daemon, collector, sync, interactive shell and device boundary;
5. one local and one cloud source;
6. provider-capability-aware authentication and ranked identity;
7. ranking, pricing and social state;
8. packaging, update and release trust;
9. broad adapter/platform certification and launch evidence.

## Epic F — contract workspaces

### F-01 Toolchain pins

Pin Rust, Go, Node/package manager, Buf/Protobuf, CDDL, OpenAPI, JSON Schema, PostgreSQL migration and cross-compilation tooling.

### F-02 Authoritative schema workspaces

Create generated Rust, Go and TypeScript bindings from repaired schemas, including provider capability, interactive-shell state and immutable source-evidence records.

### F-03 Deterministic regeneration

Clean regeneration must be byte-identical and drift must fail clearly.

### F-04 Checked primitives

Cross-language token, sequence, timestamp, duration, money, digest and identifier primitives.

### F-05 Privacy-canary framework

Seed forbidden values across source, IPC, storage, logs, network, notifications, review, privileged supervisor and crash facilities.

### F-06 Structural and semantic gate checks

Keep P-1140E structural validation distinct from the P-1140F manual semantic gate. Neither may claim runtime or security proof.

## Epic P — VibeProof core

### P-01 Rust canonical model and encoder
### P-02 Go independent decoder/verifier
### P-03 deterministic CBOR and COSE profile
### P-04 exact claim/appraisal/receipt/rotation/correction/gap vectors
### P-05 malformed and resource corpus
### P-06 atomic batch and exact replay
### P-07 continuity, gap, fork, rollback and recovery
### P-08 cross-language interoperability suite

Acceptance: independent implementations agree byte-for-byte and malformed input fails without excess allocation or partial acceptance.

## Epic A — accounting and deterministic integrity

### A-01 immutable accounting-profile registry
### A-02 mutually exclusive token categories and containment
### A-03 cache, reasoning, modality and source-total reconciliation
### A-04 retry, cancellation and nested-agent accounting
### A-05 local tokenizer/runtime-native profiles
### A-06 monotonic clock/generation rules
### A-07 duplicate-domain engine
### A-08 deterministic fatal/quarantine/diagnostic rules
### A-09 server-owned pricing interpretation
### A-10 throughput-envelope registry

Acceptance: representative cloud, local, WSL, container and CI cases reconcile without double counting or client-controlled pricing/evidence.

## Epic N — native runtime

### N-01 typed SourceObservation IPC
### N-02 non-networked collector process
### N-03 source-blind networked sync process
### N-04 OS-supervised daemon/control process
### N-05 authenticated local IPC and peer identity
### N-06 encrypted local database and migrations
### N-07 append-only commitment and receipt store
### N-08 crash consistency and bounded queues
### N-09 sleep/resume, offline, disk-full, permission-loss and corruption recovery
### N-10 CLI parity
### N-11 interactive menu-bar/tray shell

The shell has its own generated state machine and process identity. It covers absent/headless, starting, connected, daemon-unavailable, stale, paused, offline, degraded, auth-required, update-required, update-blocked, permission-repair and exiting states.

### N-12 shell/daemon action separation

UI exit, collection pause, sync pause, daemon stop, logout and uninstall are distinct. Closing or crashing the shell never stops the daemon.

### N-13 platform shell mappings

- macOS menu-bar app plus approved login-item/LaunchAgent integration;
- Windows notification-area shell plus supervised background process;
- Linux desktop shell plus systemd-user and explicit headless mode.

### N-14 optional privileged supervisor
### N-15 mandatory-update coordinator
### N-16 environment identity and diagnostics

Acceptance: daemon, collector, sync, shell and CLI fail independently; no privileged boundary can read source content.

## Epic D — device identity and cloning controls

### D-01 installation, key and lineage schema
### D-02 enrollment and server challenge binding
### D-03 macOS key backend
### D-04 Windows CNG/TPM and fallback backend
### D-05 Linux TPM/keyring/Secret Service and fallback backend
### D-06 rotation and lost-key recovery
### D-07 restore, clone, VM/WSL/container snapshot handling
### D-08 requalification and evidence downgrade
### D-09 optional issuer-specific attestation adapters
### D-10 CI ephemeral and container workload identity

Acceptance: clone, export/import, runner retry and architecture migration cannot silently duplicate score or preserve stronger trust.

## Epic S — server secure spine

### S-01 Go modular service skeleton
### S-02 ordered PostgreSQL migrations, roles and recovery
### S-03 provider capability and OAuth transaction persistence
### S-04 device/key/environment persistence
### S-05 challenge and idempotency ledgers
### S-06 atomic claim acceptance and exact replay
### S-07 conflict/fork quarantine
### S-08 immutable claim/appraisal/checkpoint/correction facts
### S-09 transactional outbox and worker checkpoints
### S-10 ranking projection and rebuild equivalence
### S-11 compatibility/update policy service
### S-12 environment eligibility and board minimums

Acceptance: exact retry cannot add score; conflicting reuse is deterministic and auditable; expired tools receive signed actionable outcomes.

## Epic O — authentication, sessions and ranked identity

### O-01 provider-capability registry

Bind immutable issuer, authorization endpoint, token endpoint, client identifier, redirect URI, PKCE requirements and RFC 9207 issuer-response support.

### O-02 desktop browser authorization

macOS, Windows and desktop Linux use the system browser with Authorization Code plus PKCE and exact stored redirect/provider binding.

### O-03 provider-specific callback verification

Require callback `iss` only where supported; otherwise use fixed provider configuration and unique redirect paths. Never select provider or token endpoint from callback-controlled values.

### O-04 limited-input/headless device authorization

Implement only for explicitly registered interactive profiles and providers supporting RFC 8628. It is not the ordinary desktop path and is forbidden for unattended CI.

### O-05 web/native token families and replay revocation
### O-06 linked identity and recovery
### O-07 ranked eligibility, investigation and anti-reenrollment
### O-08 restriction, consolidation, appeal and reversal
### O-09 OAuth mix-up, redirect-confusion and race fixtures

Acceptance: provider/session/recovery operations cannot duplicate claims, reset scores, choose attacker-controlled endpoints or bypass ranked-identity policy.

## Epic V — first sources and universal support

### V-01 local runtime selection spike
### V-02 cloud structured-usage selection spike
### V-03 local adapter and accounting profile
### V-04 cloud adapter and accounting profile
### V-05 certification runner
### V-06 immutable support registry publication
### V-07 emergency disable and sunset
### V-08 upgrade-break fixtures
### V-09 WSL host/guest reconciliation
### V-10 container replica reconciliation
### V-11 CI retry/matrix reconciliation

Acceptance: support is advertised only from non-expired certification bound to artifact digest, source version, exact platform tuple, mode and accounting profile.

## Epic R — ranking and pricing

### R-01 canonical ranking_view_id
### R-02 period registry and server-anchored event interval
### R-03 immutable score facts and corrections
### R-04 isolated generation, validation and promotion
### R-05 snapshots, keyset cursors and movement
### R-06 evidence/environment filters
### R-07 immutable pricing aliases and line items
### R-08 rebuild equivalence

Acceptance: filtering never mutates accepted raw token totals and corrections remain append-only.

## Epic G — social, presence and moderation

### G-01 profiles and privacy matrix
### G-02 block, friend, rival and canonical relationship state
### G-03 boards, membership, invitation, role and ownership transfer
### G-04 viewer-specific collector-derived presence
### G-05 typed notification preferences, dedup, quiet hours and retraction
### G-06 moderation cases, effects, appeals and reversals
### G-07 typed export and distinct server/local deletion

Acceptance: block and privacy changes invalidate visibility immediately; notifications recheck authorization; moderation and deletion effects are reversible/auditable as specified.

## Epic L — packaging, platform and release trust

### L-01 immutable source-evidence schema

Every platform source binds source ID, immutable version/release/commit, retrieval timestamp, content SHA-256, canonical URI and supported fields.

### L-02 exact platform-profile certification runner
### L-03 macOS installer, daemon and shell registration
### L-04 Windows installer, background process and tray registration
### L-05 Linux packages, systemd-user and headless mode
### L-06 WSL, container and CI lifecycle lanes
### L-07 TUF repository, thresholds and expiry
### L-08 signed release-set manifest and provenance
### L-09 mandatory update deadlines, rollback and compromise recovery
### L-10 uninstall, export and diagnostics

Acceptance: no platform is advertised before exact certification; all artifacts and source evidence are immutable and digest-bound; rollback/freeze/mix-and-match defenses are exercised.

## Epic W — hosted web and product UI

### W-01 generated API clients
### W-02 authentication and recovery UX
### W-03 leaderboards, profiles, rivals, boards and social UX
### W-04 evidence/privacy disclosure and outbound preview
### W-05 device, platform, update and shell-status surfaces
### W-06 moderation, appeals, export and deletion UX
### W-07 accessibility, responsive and exceptional-state coverage

The existing hosted-web/Storybook code remains a fixture-backed runnable prototype until integrated with implemented contracts.

## Release gates

A work unit is not complete because code compiles. Applicable gates include unit/integration/property/concurrency/privacy tests, migration and rollback evidence, cross-language vectors, platform execution, security review, operational drills, reproducible artifacts and documentation updates.

P-1105 public-launch review remains blocked until every advertised source and platform has executable, non-expired evidence.
