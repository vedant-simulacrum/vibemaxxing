# Authoritative State, API, Persistence, Platform, and Release Contract

Status: normative P-1140D planning contract; no implementation or launch evidence
Version: 1
Updated: 2026-07-24

## Single ownership rule

`packages/schemas/state-machine-registry-v1.json` is the machine-readable index of every mutable product concept. Its schema is `state-machine-registry-v1.schema.json`. Each machine declares one semantic owner, exact persistence tables, aggregate key, states, terminal states, transitions, actor/authentication/recent-auth requirements, idempotency scope, audit event, reversal semantics and transaction boundary.

Prose may explain a state machine but cannot create a second state vocabulary. OpenAPI operations, SQL checks, workers, local IPC and UI states must reference the registry IDs. An unregistered mutation is forbidden.

## Authentication and sessions

### OAuth transactions

An OAuth transaction binds transaction UUID, provider/issuer, client configuration, exact redirect URI, state-verifier hash, encrypted PKCE verifier, intended action, initiating web session or native instance, optional enrollment public-key commitment, creation/expiry/consumption and a one-time browser-handoff secret hash.

The callback verifies issuer, exact redirect, state, PKCE, transaction lifetime and one-time use before creating/linking provider identity or a session. Mutable usernames never identify the provider subject. Transaction consumption and session/provider binding are one database transaction.

### Session families

Web and native token families are separate. Each refresh token row binds family, parent, token hash, issue/expiry/consumption, authentication strength, recent-auth instant and native device/instance when applicable. Rotation consumes the parent and creates exactly one child. Parent reuse revokes the whole family and emits a replay audit event.

Web access uses secure same-site HTTP-only cookies. Native families bind server-side to device installation, lineage and active key. Sensitive native calls include device-key proof over request method, route, nonce and body digest.

Launch does not claim standards-compliant DPoP. Adding DPoP requires a separate accepted ADR and exercised client/server vectors; no ad-hoc `jkt` or proof header is exposed meanwhile.

Per-session and revoke-all controls are transactional. Provider loss cannot bypass ranked-identity restriction, recent-auth requirements or recovery review.

## Ranked identity

The registry machine `ranked-identity-eligibility` enforces one active ranked identity per resolved person without claiming mathematical proof of humanity. Investigation, restriction, consolidation, anti-reenrollment signals, appeal and reversal persist independently from the public profile.

Permanent account-level restriction or cross-account consolidation requires human authorization and recent moderator authentication. Effects are append-only, bind exact claims/periods/ranking views and reverse through inverse ranking events and projection rebuild. New devices/providers do not clear account-level state.

## API and idempotency

`packages/schemas/openapi-v1.yaml` contains endpoint-specific closed schemas. Generic Resource, untyped Collection, arbitrary error details and base64 claim bodies are prohibited.

Every mutating operation declares:

- authentication and authorization owner;
- whether recent authentication is required;
- idempotency scope `principal + route + key`;
- typed conflict behavior;
- `429`, `Retry-After` and safe rate metadata;
- stable typed error details;
- concurrency/precondition semantics where state can race.

The idempotency record is created/locked inside the business transaction and stores request SHA-256, status, exact response status/content-type/bytes and expiry. Byte-identical retry returns stored bytes. Same key with different bytes is `409`.

Claim batches are binary `application/vibemaxxing-claim-batch+cbor` and follow the atomic P-1140C transaction. There is no partial success.

Collections bind cursor to endpoint identity, filter digest, immutable snapshot/revision and maximum page size. Poll objects expose minimum interval, expiry and per-principal outstanding limits. Load shedding refuses expensive work before durable mutation and never weakens authorization or consistency.

## Persistence and transactions

`packages/schemas/planning-schema.sql` is the repaired planning migration contract. It separates append-only facts/events from mutable workflow/projection rows.

Required guarantees include:

- active provider subject, handle, token-family member and key uniqueness;
- canonical friendship pair ordering;
- one active board owner membership and no board owner column;
- exact claim/appraisal/receipt/correction and ranking-view foreign keys;
- principal/route/key idempotency uniqueness and exact response bytes;
- single-use challenges and monotonic device checkpoint constraints;
- checked non-negative u64-compatible values;
- append-only protection for accepted protocol, appraisal, receipt, pricing, moderation, ranking and audit facts;
- typed social/notification/outbox rows rather than arbitrary payload JSON;
- projection build/validate/promote state and rebuild provenance;
- deletion tombstones reapplied after restore.

One accepted batch locks authenticated account/lineage, idempotency and challenge/checkpoint rows; inserts claims/appraisals/receipts/outbox; consumes the challenge; advances checkpoint; persists exact response; then commits.

## Ranking and pricing

A `ranking_view_id` is the SHA-256 identity of canonical scope type/ID, metric/version, period, evidence filter, agent/provider/model filters, board policy, ranking policy and projection schema. Scores, snapshots, cursors, movement, overtakes, moderation effects and rebuilds bind it.

A generation builds in isolation, validates totals/order/invariants, then atomically becomes active. Cursors carry view, generation and snapshot IDs. Corrections append ranking events; accepted claims never mutate.

Pricing interpretations are immutable server facts using the P-1140B schema. Event-time registered model alias resolution, dataset/rule digests, typed line items and unpriced reasons are persisted. The product always labels results Estimated.

## Social, boards, presence, and notifications

Friendship uses one canonical ordered pair. One pending request exists per pair; crossed requests become active deterministically. Blocking in one transaction removes friendship/rival state, invalidates invitations and pending notifications, revokes presence visibility and appends social events. Unblocking never restores old relationships.

Board ownership is active membership role `owner`; there is no competing owner field. Transfer locks the board and both memberships, requires recent auth, promotes the successor and demotes/removes the prior owner in one transaction. The last owner cannot leave. Policy versions apply prospectively unless a rebuild record explicitly targets prior periods. Organization, community and hacker-house metadata are typed specializations.

Presence renews only from an authorized native session and binds a recent qualifying collector activity/accepted-continuity reference, device and privacy policy. Audience visibility is computed per viewer; block, revocation and privacy changes invalidate immediately. Multi-device merge uses deterministic activity precedence and never exposes project/source details.

Notifications are a closed event union with typed subject/object IDs, ranking view/snapshot where relevant, policy version and visibility revision. Preferences are typed rows by event/channel. Dedup/grouping, hysteresis and quiet hours are versioned. Authorization is rechecked at delivery/render. Invalidated events append a retraction.

## Moderation and appeals

Cases bind subject kind/ID, exact claims, periods and ranking views. Human actions append typed effects; they do not mutate claims. Permanent outcomes require human authorization. User-safe message keys are separate from private reason/evidence references.

Appeal approval records exact restored/excluded effects, appends reversal actions and triggers projection rebuild. Board/org administrators see only the minimum eligibility/restriction projection permitted by policy.

## Export and deletion

Export scope is typed. Sensitive exports require recent auth, coherent snapshot, manifest/checksums, encryption, short-lived revocable download grant, access audit and purge. Other users' private data and abuse thresholds are excluded.

Server deletion and local deletion are distinct:

- server deletion applies hosted hide/delete/anonymize effects, tombstones and projection rebuild;
- a per-device local deletion command is signed/acknowledged/executed by that device and produces a local receipt;
- no server response claims to erase offline devices;
- “everything” is an orchestrated UX over these independent states.

## Native runtime and platform profiles

`packages/schemas/platform-profile-registry-v1.json` freezes exact candidate tuples as of 2026-07-24. Every row is `advertised=false` and `planned-validation-required`; it becomes public only through the `platform-certification` state machine after immutable results pass.

The registry includes macOS 26/15/14 on Apple silicon and compatible Intel; Windows 11 25H2 x64/ARM64; Windows Server 2025 x64; exact maintained Linux distribution/architecture/environment/package/init tuples; WSL2 Ubuntu 26.04; signed immutable OCI x64/arm64; and ephemeral CI x64/arm64. Windows Server ARM64 is not advertised without an applicable first-party release profile. Android, iOS, iPadOS and ChromeOS remain explicitly outside native scope.

Daemon, shell, collector and sync lifecycles are independent. Closing shell never stops the OS-supervised daemon. Pausing collection or sync does not terminate the daemon. Crash loop, permission loss, key denial, disk exhaustion, sleep/reboot/login/logout, offline operation, update/rollback and uninstall are explicit failure cases.

macOS uses per-user launchd with optional separate constrained privileged service. Windows uses per-user service/task and optional constrained Windows Service. Linux uses systemd-user primarily and declared init templates. Privileged supervisors have separate identity/ACL/consent, cannot read ordinary source content or merge users, and can be removed without deleting user state.

WSL has guest lineage and duplicate domain separate from Windows. Containers bind state volume/workload identity, detect replicas and update via image replacement. CI uses short-lived job lineage and server-enforced artifact expiry.

## Mandatory update and release trust

The release registry machines cover TUF trust and installation separately.

TUF bootstraps pinned root keys, threshold roles and root rotation; timestamp/snapshot/targets/delegated platform/channel metadata has bounded expiry and consistent-snapshot hashes. Rollback, freeze, mix-and-match and endless-data defenses fail closed while preserving diagnostics, update, export and uninstall when safe.

A release-set manifest binds daemon, collector, sync, shell, CLI, adapters, schemas and database migration range; min/max protocol/database versions; SBOM, source commit, provenance and transparency references; update class/deadline/deferral; and rollback compatibility.

Installation downloads/verifies/stages, checks disk/migration preconditions, quiesces children, installs atomically, runs bounded health checks, promotes or rolls back, and restores supervision ownership. Interrupted download/install and disk-full states remain recoverable. Containers replace images; CI must use non-expired pinned artifacts. Competitive profiles cannot permanently disable required updates.

## Validation boundary

P-1140D planning validation must prove:

- registry schema validity, unique machine/profile/transition IDs and state closure;
- each required mutable domain and exact persistence owner exists;
- each high-impact transition declares auth, recent-auth, idempotency, audit and reversal;
- OpenAPI has endpoint-specific schemas, typed errors, binary claims, rate and polling contracts;
- SQL loads with ordered constraints/triggers/indexes and contains no board owner column or country scope;
- platform sources/tuples/capabilities/failure matrices are complete;
- no profile is advertised without executable certification;
- social/notification/moderation events remain typed and privacy-safe.

This is planning evidence only. No service, migration, installer, updater, TUF repository or platform package exists yet.
