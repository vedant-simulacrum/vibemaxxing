# PR-Sized Implementation Work Breakdown

Status: canonical planning decomposition; inactive until P-1140F closes and P-1104 is explicitly authorized
Updated: 2026-08-05

This file decomposes `IMPLEMENTATION_HANDOFF.md`. It does not authorize product code. Units prefixed `PF-` are planning repairs permitted in the current phase. All other units are future implementation work and remain blocked.

This file has two parts, and they are not the same kind of object:

1. **Active plan** — units specified to the standard below. These can be picked up and produced as a mergeable change without further design work.
2. **Frozen backlog** — the remaining epic headings. These are a *scope inventory*, retained so the launch scope in `docs/planning/PRODUCT_SCOPE_FREEZE.md` is not silently narrowed. **They are not executable units** and must be promoted into the active plan, with the four required fields, before being worked.

Nothing in the frozen backlog has been removed from scope. Promotion is the only path from backlog to work.

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

### Required unit fields

Every unit in the **active plan** must carry these four lines verbatim, in this order, immediately under its heading. They exist so plan quality is machine-checkable rather than aspirational.

- `Files:` — the exact paths the change touches. Not a component name, not a directory. If the paths are unknown, the unit is not yet specified.
- `Acceptance:` — one runnable assertion. A command, a query, or a grep whose result decides done. Prose descriptions of intent are not acceptance criteria.
- `Depends:` — unit IDs only, comma-separated, or `none`. Prose dependencies ("implemented product paths") are not resolvable and are not permitted.
- `Est:` — hours, as an integer or a range. A unit estimated above 16 hours must be split.

A unit missing any of the four is not ready to start, regardless of how well its prose reads.

`scripts/repository/generate_issue_plan.py` currently validates key format and uniqueness only; it neither reads nor requires these fields, so a file of empty records passes CI today. Extending it to parse the four fields and fail on any active-plan unit missing them is tracked as `PF-037`, and until that lands this standard is enforced by review rather than by tooling.

### Why the active plan is short

The 195-unit decomposition below records scope faithfully but is not executable: 159 units are a heading plus a dependency line, and no unit anywhere names a file path, schema, table, or endpoint — the first item this document's own Global rules require. Expanding all 195 to the standard above before any of them is exercised would repeat the failure this repository is currently repairing. The active plan is therefore sized to what can be specified against artifacts that actually exist, and grows by promotion as each vertical slice teaches what the next one needs.

## Active plan

Units below are specified to the required-fields standard and are ordered by execution sequence. `PF-` units are planning repairs permitted in the current phase. Units marked **gated** are fully specified but must not start until P-1104 is authorized.

Ordering principle: each specification is paired with the artifact or code that consumes it, rather than batched into a specification phase. A contract with no consumer cannot be validated, and validating contracts against each other is what produced the current finding set.

| Unit | Work | Depends | Est (h) |
|---|---|---|---|
| `PF-037` | Enforce required unit fields in the issue plan generator | none | 4-6 |
| `PF-038` | Reconcile state vocabularies across API, SQL and registry | none | 12-16 |
| `PF-039` | Decide and specify the session authentication scheme | none | 6-8 |
| `PF-040` | Specify accounting arithmetic | PF-038 | 8-12 |
| `PF-041` | Specify the OpenTelemetry accounting profile | PF-040 | 8-12 |
| `PF-042` | Author the source receipt contract | PF-041 | 6-8 |
| `PF-043` | Author the appraisal result and policy contracts | PF-038 | 8-10 |
| `PF-044` | Add pagination to unpaginated list operations | none | 3-4 |
| `PF-045` | Specify the error response matrix | PF-038 | 8-10 |
| `PF-046` | Represent evidence class in the public API | PF-043 | 4-6 |
| `PF-047` | Expand profile and rank entry schemas to the rendered product | PF-046 | 6-8 |
| `PF-048` | Author the indexing and partitioning plan | PF-038 | 8-12 |
| `PF-049` | Repair the idempotency contract | PF-038 | 4-6 |
| `PF-050` | Populate retention and disposition policy | PF-038 | 6-8 |
| `PF-051` | Specify multi-observer deduplication | PF-042 | 6-8 |
| `PF-052` | Author ranking generation, entry and snapshot contracts | PF-038, PF-048 | 10-14 |
| `PF-053` | Decide provider-attested evidence for organizations | none | 4-6 |
| `PF-054` | Author the negative CBOR corpus | none | 4-6 |
| `PF-055` | Repair the P-1140F authority validator | none | 3-4 |
| `PF-056` | Restore executable evaluation gates | PF-055 | 4-6 |
| `PF-057` | Specify the P-1104 gate transition | PF-055 | 4-6 |
| `PF-058` | Author the system narrative in PROJECT.md | none | 6-8 |
| `PF-059` | Merge duplicated UI and design documentation | none | 6-8 |
| `PF-060` | Collapse single-purpose documentation directories | PF-059 | 4-6 |
| `PF-061` | Archive spent planning specifications | none | 4-6 |
| `PF-062` | Make the decision register and task catalog machine-readable | PF-053, PF-055 | 12-16 |
| `PF-063` | Complete decision traceability coverage | PF-062 | 4-6 |
| `PF-064` | Remove stale dates from living document filenames | PF-057 | 2-3 |
| `PF-065` | Correct the OpenAPI file extension | PF-038 | 2-3 |
| `PF-066` | Repair unreachable states and false terminal states | none | 6-8 |
| `PF-067` | Make state-vocabulary binding coverage self-checking | none | 4-6 |

Full specifications for these units are in **Current planning program** below, in unit-number order after `PF-036`.

## Current planning program

### PF-001 — Quarantine the shadow VibeProof protocol
Files: `crates/vibeproof-core/README.md`, `crates/vibeproof-core/Cargo.toml`, `apps/api/cmd/api/protocol_fixtures.go`, `conformance/p1140f/artifact-authority-v1.json`, `evals/suites/suites.yaml`
Acceptance: `grep -rn 'VibeProof v1' crates/vibeproof-core apps/api/cmd/api` returns no line that omits the word `prototype`; `artifact-authority-v1.json` records `authority_class: prototype` for both artifacts; `python3 scripts/repository/validate_p1140f_authority.py` exits 0.
Depends: none
Est: 6-8
Status: not-started

`Depends: none` replaces the prose dependency `PR #42 consolidation`, which merged and can no longer be ordered against. The consolidation is a historical fact, not a pending unit.

- classify `crates/vibeproof-core` and Go fixture codec as exploratory prototype;
- remove VibeProof v1 naming from incompatible 11-field fixtures or remove them;
- prohibit product imports from the shadow model;
- mark affected evaluations blocked or prototype-only.

Exit: one VibeProof v1 wire authority remains.

### PF-002 — Align normative protocol and conformance ownership
Files: `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `docs/architecture/VIBEPROOF_V1_CANONICAL_PROFILE.md`, `packages/schemas/vibeproof-claim-v1.cddl`, `conformance/vibeproof/v1/exact-byte-vectors.json`, `conformance/vibeproof/v1/malformed-resource-corpus.json`
Acceptance: `python3 scripts/repository/generate_vibeproof_vectors.py --check` exits 0, and every CDDL rule name in `vibeproof-claim-v1.cddl` appears in exactly one of the two vector files; a second occurrence in a third file fails the check.
Depends: PF-001
Est: 8-12
Status: not-started

- inventory CDDL labels, COSE headers, external AAD, exact vectors, malformed/resource corpus;
- define generation boundaries for Rust/Go types;
- define exact independent implementation evidence expected after P-1104.

### PF-003 — Artifact/evidence maturity registry
Files: `conformance/p1140f/artifact-authority-v1.json`, `evals/suites/suites.yaml`, `scripts/ci/run_evals.py`, `docs/verification/EVAL_SYSTEM.md`
Acceptance: `python3 scripts/ci/run_evals.py --validate-registry` exits 0 and fails when a suite declares an `evidence_ceiling` its fixtures cannot support; every suite in `suites.yaml` carries an `authority_class` drawn from the registry vocabulary.
Depends: PF-001
Est: 8-10
Status: not-started

- classify every executable suite and fixture as structural, semantic, prototype, runtime evidence, or certification;
- rename overclaiming suites;
- reject empty or mislabeled evidence in planning validators.

### PF-004 — Mutable aggregate ownership inventory
Files: `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/planning-schema.sql`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `scripts/repository/validate_state_vocabularies.py`
Acceptance: `python3 scripts/repository/validate_state_vocabularies.py` exits 0 with every registry machine naming a `persistence_owner` that resolves to a `create table` in `planning-schema.sql`, and fails when one does not.
Depends: none
Est: 12-16
Status: not-started

`Depends: none` replaces the prose dependency `PR #42 consolidation`. D-195 has since landed the persistence-owner half of this unit; what remains is the revision model, transaction boundary and outbox behaviour per aggregate.

- enumerate every aggregate named in API, SQL, Protobuf/CDDL, state registry, policy, reasons, and prose;
- require one persistence owner, lifecycle, revision model, transaction boundary, and event/outbox behavior;
- record missing and duplicate owners.

### PF-005 — OAuth provider configuration authority
Files: `packages/schemas/oauth-provider-registry-v1.json` (new), `packages/schemas/oauth-provider-registry-v1.schema.json` (new), `conformance/auth/provider-mixup-vectors-v1.json` (new), `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: the registry validates against its schema; every provider row carries issuer, authorization and token endpoints, client identifier, exact redirect URI, PKCE method, RFC 9207 `iss` capability, scope set, device-flow capability, revision and expiry; the mix-up fixture contains at least one rejected case per provider.
Depends: PF-004
Est: 8-12
Status: not-started

- issuer, endpoints, client, exact redirect, PKCE, RFC 9207 capability, scopes, device-flow capability, revision and expiry;
- provider-specific positive and mix-up/redirect-confusion fixtures.

### PF-006 — Canonical OAuth transaction
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: the `oauth_transactions` table and the `oauth-transaction` registry machine share one vocabulary under `validate_state_vocabularies.py`; `grep -n 'authorization_code' packages/schemas/openapi-v1.yaml` returns no operation that mutates identity without a transaction reference.
Depends: PF-005
Est: 10-14
Status: not-started

- bind action, account/session, recent-auth grant, provider revision, redirect, state, PKCE, expiry and result;
- remove standalone authorization-code identity mutation semantics;
- define single consumption and ambiguous callback behavior.

### PF-007 — Linked identity and recovery lifecycle
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/openapi-v1.yaml`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: the `linked-identity` machine declares all eight states, every one is reachable and no terminal state has an outgoing transition under `validate_state_vocabularies.py`; `linked_identities` carries a durable provider-subject column with a uniqueness constraint.
Depends: PF-006
Est: 10-14
Status: not-started

- exact linked-identity ID and durable provider subject;
- candidate, linked, unlink-pending, lost, compromised, recovery-pending, unlinked, superseded;
- last-authentication-method invariant;
- token/session/device notification and cooling-off effects.

### PF-008 — Ranked identity and consolidation authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`, `packages/schemas/consolidation-plan-v1.schema.json` (new)
Acceptance: `ranked_identities` is a separate table from `accounts` with a survivor reference; the consolidation-plan schema validates a fixture covering identities, devices, claims, social state, boards, moderation, exports and deletions; no path in the API sums two accounts' scores.
Depends: PF-007
Est: 12-16
Status: not-started

- separate account and ranked identity;
- canonical survivor, retired duplicates, private investigation evidence, restrictions, appeal and reversal;
- immutable consolidation plan for identities, devices, claims, social state, boards, moderation, exports/deletions;
- historical score recomputation from valid non-overlapping claim contributions, never aggregate summation.

### PF-009 — Canonical challenge and lineage continuity
Files: `packages/schemas/device-lineage.schema.json`, `packages/schemas/vibeproof-claim-v1.cddl`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`
Acceptance: one identifier spelling for a challenge and one for a lineage resolves across CDDL, OpenAPI and SQL; `python3 scripts/repository/validate_cross_references.py` exits 0 and `claim_challenges`, `device_sequences` and `device_lineages` all key on the lineage rather than the device row.
Depends: PF-004
Est: 10-14
Status: not-started

- one identifier/type model across CDDL, OpenAPI and SQL;
- expected lineage revision, sequence, commitment head, checkpoint, batch commitment, policy, issue/expiry;
- lineage-scoped rather than device-row-scoped continuity.

### PF-010 — Rotation, lost-key recovery, fork and requalification
Files: `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/planning-schema.sql`, `conformance/vibeproof/v1/fork-and-rotation-vectors.json` (new), `docs/security/INTEGRITY_MODEL.md`
Acceptance: the fork fixture contains a lineage that branches, and a decoder run over it quarantines every post-fork branch while accepting every pre-fork claim; `device_key_events` records both authorizations for an ordinary rotation.
Depends: PF-009
Est: 12-16
Status: not-started

- dual authorization for ordinary rotation;
- lost-key recovery authority;
- quarantine all post-fork branches;
- preserve pre-fork accepted claims;
- select/recover one survivor and resume in a new lineage generation;
- appeal, reversal, downgrade and notification.

### PF-011 — Native process and trust-domain model
Files: `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `packages/schemas/local-trust-domains-v1.json` (new)
Acceptance: every one of the eight named roles appears exactly once in the trust-domain file with an executable identity, an OS peer identity, a user/session boundary and an explicit capability and data-class list; a role absent from the file fails `validate_planning_coverage.py`.
Depends: PF-004
Est: 10-14
Status: not-started

- daemon, collector, sync, shell, CLI, dashboard, updater, privileged supervisor;
- executable identity, OS peer identity, user/session boundary, artifact/release identity;
- allowed capabilities and data classes per role.

### PF-012 — Local channel protocol
Files: `packages/schemas/local-control-v1.proto`, `conformance/sandbox/local-channel-vectors-v1.json` (new), `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`
Acceptance: `local-control-v1.proto` declares one request and one response message per role rather than a universal union; the vector file contains a same-user impersonation case and a stale-process case, each with the expected rejection reason drawn from `packages/schemas/reason-codes-v1.json`.
Depends: PF-011
Est: 10-14
Status: not-started

- handshake, daemon-assigned role, generation, nonce, sequence window, capability grant, deadline, revocation;
- typed request/response per role rather than one universal message union;
- same-user impersonation and stale-process fixtures.

### PF-013 — Shell and subsystem state separation
Files: `packages/schemas/state-machine-registry-v1.json`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
Acceptance: `interactive-shell` declares only process and connection states, and daemon, collection, sync, auth, permission, update and connectivity are separate machines; `validate_state_vocabularies.py` reports every state of all seven reachable.
Depends: PF-011
Est: 8-12
Status: not-started

- shell owns process/connection state only;
- daemon, collection, sync, auth, permission, update and connectivity are independent projections;
- pre-auth startup and restart after crash;
- UI exit, pause collection, pause sync, stop daemon, logout, uninstall are distinct.

### PF-014 — Local persistence and migration contract
Files: `packages/schemas/local-schema.sql` (new), `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `conformance/privacy/p1140b-boundary-canaries-v1.json`
Acceptance: `local-schema.sql` parses under `sqlite3 -init` with no errors, declares an encryption key reference per table holding claim material, and the canary fixture proves no log, backup, diagnostic or corruption-report column can hold a forbidden content class.
Depends: PF-011
Est: 12-16
Status: not-started

- local DDL ownership, encryption, key references, schema generation, crash consistency, queues, commitments, receipts, migrations and recovery;
- forbidden-content boundaries for logs, backups, diagnostics and corruption reports.

### PF-015 — Atomic compatibility tuple
Files: `packages/schemas/compatibility-tuple-v1.schema.json` (new), `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.schema.json`
Acceptance: the tuple schema requires all nine components and a canonical digest; two independently ordered serialisations of the same tuple produce the same digest in a fixture that records both inputs and the expected digest.
Depends: PF-004
Est: 8-12
Status: not-started

- product/source, exact version/artifact, platform profile, mode, adapter/collector artifacts, protocol/telemetry profile, accounting profile, privacy profile and evidence ceiling;
- canonical digest construction.

### PF-016 — Certification lifecycle and revocation
Files: `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/certification-result-v1.schema.json` (new), `docs/integrations/ADAPTER_CERTIFICATION_POLICY.md`
Acceptance: the `certification` machine declares all eight states with one vocabulary across registry, SQL and API under `validate_state_vocabularies.py`; the result schema requires suite and case digests, a validity interval and a signer reference, and rejects a bundle missing any of them.
Depends: PF-015
Est: 10-14
Status: not-started

- candidate, testing, active, degraded, suspended, expired, superseded, retired;
- signed result bundle, suite/case digests, validity interval, signer/verifier policy;
- narrow per-tuple emergency downgrade and reinstatement.

### PF-017 — Source observation and operation identity
Files: `packages/schemas/source-observation.schema.json`, `packages/schemas/normalized-event.schema.json`, `docs/product/TOKEN_ACCOUNTING_SPEC.md`
Acceptance: every example under `packages/schemas/examples/` and `conformance/adapters/claude-code-otel/` validates, and a normalized event that names no operation identity, observer identity or cumulative/incremental flag is rejected by the schema.
Depends: PF-015
Est: 10-14
Status: not-started

- authenticated tuple selection before normalization;
- provider/model/source facts;
- operation, parent/child, retry generation, observer identity, cumulative/incremental semantics;
- direct/proxy/ACP/OTel equivalence.

### PF-018 — Accounting reconciliation and bounds
Files: `packages/schemas/accounting-profile.schema.json`, `conformance/accounting/reconciliation-vectors-v1.json` (new), `docs/product/TOKEN_ACCOUNTING_SPEC.md`
Acceptance: every reconciliation vector produces the same result under two array orderings; a vector with two equal-authority contradicting sources produces the recorded deterministic outcome; an event exceeding the declared period bound is rejected rather than saturating.
Depends: PF-017
Est: 12-16
Status: not-started

- per-operation grouping;
- source authority, containment, cache/reasoning/modality semantics;
- equal-authority contradiction handling;
- deterministic tie-breaking independent of array order;
- checked arithmetic and practical event/period bounds.

### PF-019 — Idempotency authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`
Acceptance: `idempotency_records` keys on `(principal_type, principal_id, operation_id, idempotency_key)`; the `idempotency-ledger` machine declares `executing`, `committed`, `replayable-failure`, `conflict`, `expired` and `abandoned`, and all six are reachable under `validate_state_vocabularies.py`.
Depends: PF-004
Est: 8-12
Status: not-started

- typed principal, operation/API version, key and request fingerprint;
- exact stored status, content type, safe headers, bytes and result references;
- executing, committed, replayable-failure, conflict, expired and abandoned semantics;
- retention: at least 30 days for high-impact mutations; claim-batch responses until later acknowledged checkpoint supersession.

### PF-020 — Transaction and ambiguous-commit model
Files: `conformance/p1140e/sql-race-plans-v1.json`, `packages/schemas/planning-schema.sql`, `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
Acceptance: `sql-race-plans-v1.json` contains a plan for each of crash-before-commit, crash-after-commit, dropped response, takeover and expiry, each naming the exact rows a correct implementation leaves behind; `python3 scripts/repository/validate_p1140e_contracts.py` exits 0.
Depends: PF-019
Est: 10-14
Status: not-started

- idempotency, business effect, audit, outbox and exact response commit together;
- crash before commit, crash after commit, dropped response, takeover and expiry cases;
- expired high-impact keys reject reuse rather than becoming fresh mutations.

### PF-021 — Ranking definition and audience authorization
Files: `packages/schemas/ranking-view-v1.schema.json`, `packages/schemas/openapi-v1.yaml`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
Acceptance: `ranking-view-v1.schema.json` separates the ranking definition from the audience; only the global scope carries `security: []` in the OpenAPI document and every other scope requires a viewer; `grep -n 'security: \[\]' packages/schemas/openapi-v1.yaml` returns exactly one leaderboard operation.
Depends: PF-004
Est: 12-16
Status: not-started

- stable ranking definition separate from viewer/board audience;
- metric/version, period, evidence/source/agent/provider/model filters, tie and projection policy;
- viewer, friend/rival cohort, block/privacy, board membership/visibility revisions;
- only global public by default.

### PF-022 — Ranking generations, entries, snapshots and cursors
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
Acceptance: `ranking_projection_generations` carries exactly one active pointer enforced by a partial unique index; every entry key in `score_snapshots` includes the generation; a cursor fixture records the viewer, the authorization revision and the expiry, and a cursor replayed by another viewer is rejected.
Depends: PF-021
Est: 12-16
Status: not-started

- generation included in entry keys;
- isolated build/validation/promotion and one active pointer;
- immutable retained entries;
- viewer-bound signed cursor with authorization revision and expiry;
- score-only `rank()` peer groups and separate deterministic display key.

### PF-023 — Periods, seasons, contributions and corrections
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
Acceptance: the `period` machine declares `open`, `frozen`, `closed`, `corrected` and `archived` with all five reachable; `minute_scores` and `period_scores` are append-only by constraint; a rebuild from `ranking_corrections` reproduces the recorded totals in a fixture.
Depends: PF-022
Est: 12-16
Status: not-started

- exact calendar/timezone, open/frozen/closed/corrected/archived states;
- late-claim and correction windows;
- immutable contribution ledger;
- inverse/replacement corrections and rebuild equivalence;
- movement, overtake, streak and season event/retraction references.

### PF-024 — Social relationship authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: `friend_edges` stores one canonical ordered pair with a check constraint, `blocks` is directional with no symmetry constraint, and `rival_edges` references neither; a fixture proves a block does not remove a friendship row and a friendship does not clear a block.
Depends: PF-004
Est: 10-14
Status: not-started

- canonical friendship pair and directional request lifecycle;
- directional blocks separate from friendship;
- rivals separate from blocks/friendship;
- decline, cancel, expiry, unblock, generation and current authorization.

### PF-025 — Board ownership and role authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: `boards` and `board_memberships` are written in one transaction in the recorded SQL plan; a partial unique index enforces exactly one owner per board; `board_invites` cannot grant an admin or owner role, which a rejected fixture case proves.
Depends: PF-024
Est: 10-14
Status: not-started

- atomic board creation plus initial owner;
- invitations grant only non-privileged membership;
- separate recent-authenticated revision-checked admin promotion;
- paired ownership transfer preserving exactly one owner;
- role/action authorization matrix and recovery.

### PF-026 — Presence evidence and projection
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: `presence_leases` records a device-bound lease generation; the `presence` machine transitions to `idle` at 90 seconds and `offline` at 300 seconds with those exact numbers in `packages/schemas/policy-defaults-v1.json`; a two-device merge fixture yields the same result under both device orderings.
Depends: PF-011, PF-024
Est: 10-14
Status: not-started

- device-bound qualifying pulse every 30 seconds;
- active, idle at 90 seconds, offline at 300 seconds;
- lease generations and sleep/resume;
- deterministic multi-device merge;
- private/block/relationship/board visibility as separate viewer projection.

### PF-027 — Notification source, inbox and channel model
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`
Acceptance: `notification_events` is append-only and `notifications` carries the recipient projection with an authorization revision; the `notification` machine can express `retracted`; a delivery attempt row records `queued`, `deferred`, `accepted`, `acknowledged`, `failed` or `expired` and never maps `accepted` to a read.
Depends: PF-024, PF-026
Est: 12-16
Status: not-started

- immutable source event and revision;
- recipient inbox item, grouping, authorization revision, read/dismiss/expiry/retraction;
- per-channel queued/deferred/accepted/acknowledged/failed/expired attempts;
- preferences, quiet hours, security-critical policy and subscription lifecycle;
- push provider acceptance is not user read or guaranteed delivery.

### PF-028 — Export authority
Files: `packages/schemas/export-manifest-v1.schema.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`
Acceptance: the manifest schema requires version, included and excluded domains, per-domain counts, checksums and an encryption reference, and rejects a manifest missing any; `exports` and `export_artifacts` carry a snapshot cutoff and a revocable grant with an expiry.
Depends: PF-004, PF-019
Est: 10-14
Status: not-started

- durable status resource and cancellation/purge;
- frozen recent-auth grant and coherent snapshot cutoff;
- versioned package, manifest, included/excluded domains, counts, checksums, encryption and short-lived revocable grants;
- rights-of-others filtering and download audit.

### PF-029 — Deletion plan, per-effect outcomes and tombstones
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: `deletion_jobs`, `deletion_effects`, `local_deletion_commands` and `local_deletion_receipts` cover every domain named in `docs/privacy/DATA_MAP.md`, with a per-device outcome of `complete`, `pending`, `expired`, `unreachable` or `waived`; `grep -in 'forensic' docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` returns no claim of erasure.
Depends: PF-023, PF-024, PF-027, PF-028
Est: 12-16
Status: not-started

- hosted and local device deletion separated;
- immutable domain/effect plan;
- account mutation restrictions during execution;
- public profile/social/ranking/notification corrections;
- per-device command/result: complete, pending, expired, unreachable, waived;
- execution receipt does not claim forensic erasure;
- legal holds, retention and backup tombstone reapplication.

### PF-030 — Release authorization and component manifest
Files: `packages/schemas/release-set-v1.schema.json`, `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
Acceptance: the release-set schema requires a TUF role reference, a target path, an architecture, a hash, a provenance reference, a native signature reference, a compatibility tuple and an update class per component, and rejects a manifest that is not itself an authenticated target.
Depends: PF-015
Est: 8-12
Status: not-started

- TUF root/delegated roles own authorization;
- release manifest is an authenticated target;
- component IDs, target paths, architecture, hashes, provenance, native signing, compatibility and update class.

### PF-031 — Migration, health and rollback policy
Files: `packages/schemas/planning-schema.sql`, `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
Acceptance: `update_policies` and `update_installations` express an ordered migration chain and a compatibility window; a fixture records one reversible and one irreversible migration, and the irreversible case has no rollback edge in the `update-lifecycle` machine.
Depends: PF-014, PF-030
Est: 10-14
Status: not-started

- ordered migration chain and compatibility window;
- pre/post health checks;
- binary rollback only while prior version remains read/write compatible;
- irreversible migration recovery by roll-forward or verified pre-migration snapshot.

### PF-032 — Platform supervision and installer truth table
Files: `packages/schemas/platform-profile-registry-v1.json`, `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `docs/security/PLATFORM_ISOLATION.md`
Acceptance: `platform-profile-registry-v1.json` validates against its schema with a row for macOS, Windows, Linux, WSL, container and CI, each naming its supervision mechanism, its session and restart limitation, and its competitive eligibility separately from its installability.
Depends: PF-011, PF-030
Est: 10-14
Status: not-started

- exact macOS, Windows, Linux, WSL, container and CI mechanisms;
- disclose session and restart limitations honestly;
- separate installation capability from competitive eligibility;
- install, upgrade, reboot, repair, uninstall and orphan cleanup states.

### PF-033 — Privacy projection and invalidation matrix
Files: `packages/schemas/privacy-projection-v1.json` (new), `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/DATA_MAP.md`
Acceptance: every viewer-visible field in the OpenAPI document appears exactly once in the projection file with the authorization revision that gates it; a fixture proves a block, a board removal and a deletion each invalidate the cursors, grants and caches the file names.
Depends: PF-021, PF-024, PF-026, PF-027, PF-028, PF-029
Est: 12-16
Status: not-started

- immutable historical facts versus current authorization;
- block, privacy, board removal, moderation reversal, identity consolidation and deletion invalidation;
- cursor/grant/cache invalidation and append-only retraction.

### PF-034 — Schema/interface inventory repair
Files: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `scripts/repository/validate_planning_coverage.py`
Acceptance: `python3 scripts/repository/validate_planning_coverage.py` exits 0 with every file under `packages/schemas/` and `conformance/` present in the inventory and every inventory row resolving to a file; `grep -in 'closed-world\|complete' docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` returns no maturity claim.
Depends: PF-005, PF-006, PF-007, PF-008, PF-009, PF-010, PF-011, PF-012, PF-013, PF-014, PF-015, PF-016, PF-017, PF-018, PF-019, PF-020, PF-021, PF-022, PF-023, PF-024, PF-025, PF-026, PF-027, PF-028, PF-029, PF-030, PF-031, PF-032, PF-033
Est: 12-16
Status: not-started

The prose range `PF-005 through PF-033` is expanded to the full enumeration because `Depends:` admits unit IDs only, and a range cannot be resolved by the cross-reference validator.

- update every interface maturity and owner;
- remove stale “closed-world/complete” claims;
- register all new schemas, tables, messages, policies and fixtures;
- validate cross-file enum and identifier mappings.

### PF-035 — P-1140E validator repair
Files: `scripts/repository/validate_p1140e_contracts.py`, `conformance/p1140e/validation-matrix-v1.json`, `tests/ci/test_p1140e_contracts.py` (new)
Acceptance: `python3 scripts/repository/validate_p1140e_contracts.py` exits non-zero on each of six injected defects — missing owner, unreachable lifecycle, SQL/state/API vocabulary mismatch, missing generation key, missing authority revision, and a content digest that does not match — and 0 on the clean tree; the summary line names the check as structural.
Depends: PF-034
Est: 10-14
Status: not-started

- verify owner existence and reachable lifecycle;
- detect SQL/state/API vocabulary mismatch;
- detect missing generation keys and authority revisions;
- verify content digests and tuple/certification references;
- remain structural and never claim runtime proof.

### PF-036 — P-1140F exact-head review
Files: `conformance/p1140f/review-target-v1.json`, `conformance/p1140f/semantic-findings-v1.json`, `conformance/p1140f/REPAIR_HEAD_REVIEW.md`
Acceptance: mechanical part: `review-target-v1.json` pins a commit that `git cat-file -e` resolves, every one of SR-005..SR-017 carries a closure verdict, and `python3 scripts/repository/validate_p1140f_authority.py` exits 0 with zero open P0 or P1. The review judgement itself is not mechanizable and must not be presented as though the validator produced it.
Depends: PF-001, PF-002, PF-003, PF-004, PF-005, PF-006, PF-007, PF-008, PF-009, PF-010, PF-011, PF-012, PF-013, PF-014, PF-015, PF-016, PF-017, PF-018, PF-019, PF-020, PF-021, PF-022, PF-023, PF-024, PF-025, PF-026, PF-027, PF-028, PF-029, PF-030, PF-031, PF-032, PF-033, PF-034, PF-035
Est: 12-16
Status: not-started

- pin exact commit;
- independent manual review of SR-005 through SR-017;
- record any P0/P1 with exact normative owner;
- require zero open P0/P1 before considering P-1104.

### PF-037 — Enforce required unit fields in the issue plan generator
Files: `scripts/repository/generate_issue_plan.py`, `docs/implementation/ISSUE_GENERATION.md`, `tests/ci/test_generate_issue_plan.py` (new)
Acceptance: `python3 scripts/repository/generate_issue_plan.py` exits non-zero when any unit under `## Active plan` lacks `Files:`, `Acceptance:`, `Depends:`, or `Est:`; exits 0 on the current file; emitted records carry all four fields.
Depends: none
Est: 4-6

Also corrects three defects in the generator: `labels` hardcodes `blocked` and `phase_gate` hardcodes `P-1104-explicit-implementation-approval` with no gate-state input, so every generated record is mislabeled the moment the gate moves; `POST_LAUNCH_HEADING` and the `PL-` branch are dead code matching a heading that does not exist; and `ISSUE_GENERATION.md` documented stable keys in a two-digit form that the generator's own `\d{3}` key pattern rejects, since corrected to the three-digit headings the breakdown actually carries.

### PF-038 — Reconcile state vocabularies across API, SQL and registry
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: a script asserts that for every aggregate with a `state` column, an API enum, and a registry machine, the three value sets are identical; zero mismatches reported.
Depends: none
Est: 12-16

Nine aggregates currently disagree. `Appeal` shares exactly one state name between API and registry. `ranking-projection` is `building/published/superseded/failed` in SQL against `building/validating/active/superseded/failed` in the registry, so the projection worker has no valid target state. `Notification` cannot express `retracted`, which is the D-070 correction path. `idempotency_records` is `reserved/committed/failed` in SQL against `reserved/committed/conflict/expired` in the registry — neither is a superset. Export, deletion, certification, update-lifecycle, and web-session-family also diverge; certification has four vocabularies across three files plus the inventory.

This unit also fixes the absence of a naming-convention rule: SQL uses `snake_case`, the registry uses `kebab-case`, and no document specifies which wins. Highest-leverage unit in the plan — every code generator, migration, and worker depends on its output.

### PF-039 — Decide and specify the session authentication scheme
Files: `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md` (new), `packages/schemas/openapi-v1.yaml`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: `openapi-v1.yaml` declares a `securitySchemes` entry matching the ADR; a refresh operation exists if the ADR requires one; `grep -c "bearerAuth" openapi-v1.yaml` no longer returns a global-only result.
Depends: none
Est: 6-8

`AUTHENTICATION_AND_RECOVERY.md:63-66` specifies HTTP-only same-site cookies with refresh-token rotation. `openapi-v1.yaml:13-16,1710-1715` declares a single global opaque `bearerAuth` with no cookie scheme, no OAuth2 flows, no scopes, and no refresh endpoint among its 39 paths. These are two different architectures and the first authenticated request cannot be implemented until one is chosen. The `web-session-family` machine has a `replay-detected` state that neither SQL nor the API can persist.

### PF-040 — Specify accounting arithmetic
Files: `packages/schemas/accounting-profile.schema.json`, `docs/product/TOKEN_ACCOUNTING_SPEC.md`, `conformance/accounting/arithmetic-vectors-v1.json` (new)
Acceptance: two independent implementations reproduce every vector in the new fixture byte-for-byte, including the profile digest.
Depends: PF-038
Est: 8-12

`accounting-profile.schema.json` defines no rounding, overflow, precision, or unit-conversion rules, and no canonical digest algorithm — yet `accounting_profile_sha256` is a signed claim field. `retry_policy`, `cancellation_policy`, and `nested_execution_policy` at `:209-228` are enum labels with no defined behavior. Two implementations cannot currently agree on a token total, which makes cross-language parity meaningless.

### PF-041 — Specify the OpenTelemetry accounting profile
Files: `packages/schemas/accounting-profile-otel-v1.json` (new), `docs/integrations/AGENT_INTEGRATION_RESEARCH_MATRIX.md`, `conformance/accounting/otel-capture-vectors-v1.json` (new)
Acceptance: the profile maps a captured OTLP payload to a `NormalizedAccountingEvent` deterministically; fixture includes at least one real capture per supported metric.
Depends: PF-040
Est: 8-12

Empirically verified capture surface, 2026-08-05: Claude Code emits `claude_code.token.usage` as a counter with attributes `model`, `query_source` (`main`/`subagent`/`auxiliary`), and `type` (`input`/`output`/`cacheRead`/`cacheCreation`). Gemini CLI emits `gemini_cli.token.usage`; Codex emits `codex.turn.token_usage`. Prompt and response content appears only on the logs channel and is redacted unless explicitly enabled, so metrics-only capture keeps the collector out of L0 entirely.

Three hazards this profile must encode: every Claude Code metric carries `organization.id`, `user.account_uuid`, `user.account_id`, `user.email`, and `user.id`, which must be dropped at ingest rather than trusted for identity; Gemini CLI's `logPrompts` defaults to **true**; and Codex's `metrics_exporter` defaults to `statsig`, not `none`.

### PF-042 — Author the source receipt contract
Files: `packages/schemas/source-receipt-v1.schema.json` (new), `packages/schemas/source-observation.schema.json`, `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
Acceptance: every `NormalizedAccountingEvent` fixture resolves to exactly one source receipt; schema validates the full existing observation corpus.
Depends: PF-041
Est: 6-8

Inventory line `:35`. Provenance for every claim, and the first of the 33 `planned-missing` contracts that blocks real work. Note the inventory maps this to `PF-021/PF-022`, which are ranking units; the accounting owners are `PF-017`/`PF-018`.

### PF-043 — Author the appraisal result and policy contracts
Files: `packages/schemas/appraisal-result-v1.schema.json` (new), `packages/schemas/appraisal-policy-v1.schema.json` (new), `packages/schemas/openapi-v1.yaml`
Acceptance: `ClaimRecord.appraisal_id` resolves to a defined schema and a retrievable operation; no dangling reference remains.
Depends: PF-038
Est: 8-10

Inventory lines `:37-38`. `ClaimRecord.appraisal_id` already references an appraisal today and there is no `/appraisals/{id}` path and no schema behind it.

### PF-044 — Add pagination to unpaginated list operations
Files: `packages/schemas/openapi-v1.yaml`
Acceptance: every operation returning a collection declares `cursor` and `limit` parameters with the contract's default 50 and maximum 200; zero collection operations without both.
Depends: none
Est: 3-4

Twelve operations lack both: `listSessions:279`, `listIdentities:339`, `listDevices:446`, `listFriends:868`, `listFriendRequests:894`, `listBlocks:959`, `listRivals:1024`, `listBoards:1089`, `listOrganizations:1198`, `listCommunities:1263`, `listModerationCases:1427`, `listAppeals:1492`. `SERVER_API_DATA_AND_RANKING_CONTRACT.md:44` already specifies the contract they violate.

### PF-045 — Specify the error response matrix
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
Acceptance: every operation declares its 4xx responses; every reason code maps to exactly one HTTP status and one registered state machine.
Depends: PF-038
Est: 8-10

No operation currently declares 401, 403, 404, 409, or 422 — only 200, 429, and default. `reason-codes-v1.json` has 20 codes for a 39-path API and 24 state machines, and all 20 reference `state_machine: "vibeproof-v1"`, which is not one of the registered machines. Every code dangles.

### PF-046 — Represent evidence class in the public API
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/evidence-disclosure-v1.schema.json` (new), `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`
Acceptance: `grep -c evidence_class packages/schemas/openapi-v1.yaml` returns non-zero; the disclosure projection defines exactly what a viewer may see.
Depends: PF-043
Est: 4-6

The string `evidence_class` does not appear in 3,780 lines of OpenAPI. The product's central differentiator is currently unrepresentable in its own API. Four vocabularies exist for this concept — `packages/ui` uses `Hardened|Standard|Imported`, `crates/vibeproof-core` uses `Authoritative|Structured|Observed|Estimated|Imported`, `evidence-profile-policy-v1.json` uses `authoritative-profile`, and the API has none. Reconcile to one.

### PF-047 — Expand profile and rank entry schemas to the rendered product
Files: `packages/schemas/openapi-v1.yaml`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: every field rendered by `packages/ui/src/concepts/product-storyboards.tsx` and `packages/ui/src/patterns/product-system.tsx` resolves to an API field; no storyboard depends on a value the API cannot return.
Depends: PF-046
Est: 6-8

`PublicProfile` has 4 fields and `RankEntry` has 7, both `additionalProperties: false`. The finished 2,900-LOC design system renders avatars, evidence badges, rank movement, sparklines, and board standings that no operation can supply. This unit also removes the banned copy at `product-storyboards.tsx:56,105,111` ("Verified competitor", "All sources verified", "Rankings are based on verified Token Burn"), which `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md:134-138` and `docs/product/PRODUCT_SPEC.md:109` prohibit.

### PF-048 — Author the indexing and partitioning plan
Files: `packages/schemas/planning-schema.sql`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
Acceptance: every foreign key and every documented query path has a supporting index; claims are partitioned as the contract states; `grep -c "CREATE INDEX" planning-schema.sql` is greater than 3.
Depends: PF-038
Est: 8-12

73 tables carry 3 indexes total at `:651-653` and zero `PARTITION BY`, while `SERVER_API_DATA_AND_RANKING_CONTRACT.md:70` states claims are partitioned by receipt month. `friend_edges:275` and `rival_edges:289` have no reverse-direction index, so bidirectional queries sequential-scan. The 300 ms leaderboard SLO is unreachable as written.

### PF-049 — Repair the idempotency contract
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`
Acceptance: a replayed request returns the original response body byte-for-byte; the ledger expresses `conflict` and `expired`.
Depends: PF-038
Est: 4-6

`planning-schema.sql:420-430` stores a nullable `response_digest` with no response-body column, so exact replay cannot return the original response. The primary key at `:426` is `(actor_account_id, idempotency_key)` with no global uniqueness, and the principal is account-only.

### PF-050 — Populate retention and disposition policy
Files: `packages/schemas/policy-defaults-v1.json`, `packages/schemas/data-disposition-v1.json` (new), `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: every one of the 73 tables has a declared retention class; no `expires_at` column exists without a documented enforcement owner.
Depends: PF-038
Est: 6-8

Inventory `:106-107` assigns retention to `policy-defaults-v1.json`, which currently contains 16 knobs and zero retention windows. `expires_at` is stored in several tables and enforced nowhere.

### PF-051 — Specify multi-observer deduplication
Files: `packages/schemas/normalized-event.schema.json`, `docs/product/TOKEN_ACCOUNTING_SPEC.md`, `conformance/accounting/dedup-vectors-v1.json` (new)
Acceptance: two collectors observing one session produce a single counted event; fixture covers the colliding and non-colliding commitment cases.
Depends: PF-042
Est: 6-8

Inventory `:74`. `TOKEN_ACCOUNTING_SPEC.md:74-76` currently relies on the collector's own `duplicate_domain_commitment`, so two collectors on one real session can choose non-colliding commitments and double-count. Double counting is a scoring defect, not a data-quality defect.

### PF-052 — Author ranking generation, entry and snapshot contracts
Files: `packages/schemas/ranking-generation-v1.schema.json` (new), `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`
Acceptance: `LeaderboardPage.snapshot_id` and `revision` and `RankEntry.ranking_view_id` all resolve; a generation can be pinned, superseded, and read back.
Depends: PF-038, PF-048
Est: 10-14

Inventory `:88`. Three fields dangle in the API today. This is also where `getLeaderboard` gains a viewer parameter and loses its unauthenticated `security: []` while the `Scope` enum at `:1775` still admits `friends|rivals|board`.

### PF-053 — Decide provider-attested evidence for organizations
Files: `docs/decisions/ADR-016-PROVIDER_ATTESTED_ORG_EVIDENCE.md` (new), `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/planning/DECISION_REGISTER.md`
Acceptance: the ADR states whether org boards use provider admin APIs, and `EVIDENCE_AND_ATTESTATION_PROFILES.md` reflects the resulting E1 availability.
Depends: none
Est: 4-6

Research on 2026-08-05 established that Anthropic's Admin API (`/v1/organizations/usage_report/messages` plus the Claude Code analytics endpoint), OpenAI's `/v1/organization/usage/completions`, and Cursor's team usage API all return provider-attested counts that a user cannot fabricate — but all three require org-admin credentials, and no provider offers an OAuth scope permitting an individual to authorize third-party read of their own consumption. Anthropic's documentation states the Admin API is unavailable for individual accounts.

Consequence: E1 evidence is reachable **today for organizations and unreachable for individuals**. This bears directly on the ranking-integrity limits recorded in `docs/security/THREAT_MODEL.md` and determines whether a credible evidence tier exists at all. It affects the identity and board data model, so it is decided before ranking contracts are frozen rather than after.

### PF-054 — Author the negative CBOR corpus
Files: `conformance/vibeproof/v1/negative-vectors.json` (new), `docs/architecture/VIBEPROOF_V1_CANONICAL_PROFILE.md`
Acceptance: a decoder rejects every vector for the stated reason; duplicate keys, non-minimal integers, indefinite-length containers, and trailing bytes are each covered.
Depends: none
Est: 4-6

`vibeproof-claim-v1.cddl` is the strongest artifact in the repository — all nine types resolve, COSE alg −8 and tag 18 are pinned, byte-exact positive vectors exist. Its gap is that only positive vectors exist, and canonicalization, nesting depth, and allocation ceilings live in prose rather than in testable form. Batch, rotation, gap, and correction vectors are also absent.

### PF-055 — Repair the P-1140F authority validator
Files: `scripts/repository/validate_p1140f_authority.py`, `tests/ci/test_validate_p1140f_authority.py` (new)
Acceptance: closing a finding in `conformance/p1140f/semantic-findings-v1.json` leaves the validator green; the validator fails when the open count increases.
Depends: none
Est: 3-4

`:53` raises unless exactly 13 P1 findings are open; `:139` raises unless zero are open for a review to pass. The two conditions cannot both hold, so closing a finding correctly turns CI red and the only routes to green are inaction or editing the validator. Replace the exact-count check with monotonic non-regression.

### PF-056 — Restore executable evaluation gates
Files: `.github/workflows/planning-checks.yml`, `evals/suites/suites.yaml`, `scripts/ci/run_evals.py`
Acceptance: `run_evals.py --validate-registry`, `verify_repository.py`, and `python -m unittest discover -s tests` all run in CI and exit 0.
Depends: PF-055
Est: 4-6

Four validators fail at HEAD and no workflow invokes them, so nothing detected the failure. Commit `31a6539` added `authority_class` and `evidence_ceiling` to satisfy `validate_p1140f_authority.py:124`, while `run_evals.py` rejected any key outside its allowlist — one validator required exactly what another forbade.

**Partially repaired 2026-08-06.** The allowlist now admits both keys, which resolves the first contradiction. A second one remains and needs a decision rather than a patch: `shadow-codec-parity` carries `reason: "…not normative VibeProof conformance"`, which is a **scope disclaimer**, while `run_evals.py:156` treats `reason` purely as a not-applicable excuse and requires it blank on `ready` suites. One key is serving two purposes. Either split the disclaimer into a distinct field such as `scope_note` — which `validate_p1140f_authority.py` must then read for the evidence-ceiling justification — or relax the blank-reason rule when `authority_class` is present. Choose deliberately; both validators depend on the answer.

Until that is settled, `run_evals.py --validate-registry`, `generate_gate_ledger.py`, `verify_repository.py`, and one test in `tests/ci/test_run_evals.py` still fail. 1,255 of 3,206 Python lines never execute in automation, including the fixture-digest binding, argv shell-injection refusal, path-traversal containment, and evidence-freshness checks. This unit also removes the `paths:` filters that currently exempt `apps/`, `crates/`, `Cargo.toml`, and `.github/workflows/ci.yml` from every check.

### PF-057 — Specify the P-1104 gate transition
Files: `scripts/repository/doctor.py`, `docs/project/STATUS.md`, `docs/planning/TASK_CATALOG.md`, `docs/implementation/IMPLEMENTATION_HANDOFF.md`
Acceptance: `doctor.py` derives phase state from `conformance/p1140f/*.json` rather than from prose substrings; opening or closing the gate requires no edit to `doctor.py`.
Depends: PF-055
Est: 4-6

The gate is currently enforced by prose substring assertions in four files: `doctor.py:90` requires `STATUS.md` to contain the literal string "implementation remains unauthorized", `:95` requires "blocked-approval" in `TASK_CATALOG.md`, `:105` requires "P-1104: blocked", and `:110` requires "inactive" and "blocked" in the handoff. Moving the gate therefore requires editing the validator that enforces it, which is the same defect as PF-055 in a different place. The machine-readable state already exists in `conformance/p1140f/`; the validator should read it.

### PF-058 — Author the system narrative in PROJECT.md
Files: `docs/project/PROJECT.md`, `docs/project/DOCUMENTATION.md`
Acceptance: a reader who has read only `PROJECT.md` can state the full path a token takes from an agent process to a public rank, and name the component that owns each step.
Depends: none
Est: 6-8

No document explains how the system works end to end. Understanding it currently requires reading eight files in a prescribed order, which is why `AGENTS.md:12` has to prescribe that order. `PROJECT.md` should carry one narrative — install, adapter observes, collector normalizes, sync signs, verifier appraises, ledger records, projection ranks — with a diagram, and every other document should read as detail hanging off it.

This is the single highest-value change for anyone, human or agent, encountering the repository for the first time. It does not replace any normative contract; it gives them a spine.

### PF-059 — Merge duplicated UI and design documentation
Files: `docs/style-guide/COMPONENT_INVENTORY.md`, `docs/style-guide/COMPONENT_STANDARD.md`, `docs/style-guide/README.md`, `docs/style-guide/UI_ARCHITECTURE.md`, `docs/style-guide/UI_FOUNDATIONS.md`, `docs/style-guide/BRAND.md`, `docs/project/DOCUMENTATION.md`
Acceptance: one owner per concept; no two files in `docs/style-guide/` describe the same component surface; `DOCUMENTATION.md` names the surviving owner for each.
Depends: none
Est: 6-8

Three files described components (`COMPONENTS.md`, `COMPONENT_INVENTORY.md`, `COMPONENT_STANDARD.md`) and three described design foundations (`design/design.md`, `design/UI_FOUNDATIONS.md`, `style-guide/README.md`); the first and fourth of those have since been merged into their surviving owners. `docs/architecture/ARCHITECTURE.md` and the former `docs/style-guide/ARCHITECTURE.md` shared a filename while describing unrelated scopes, which made every reference to "ARCHITECTURE.md" ambiguous until the latter was renamed to `docs/style-guide/UI_ARCHITECTURE.md`.

Merge unique content into one owner per concept, repair references, and delete or clearly mark the duplicates, per the rule already stated in `DOCUMENTATION.md`.

### PF-060 — Collapse single-purpose documentation directories
Files: `docs/protocol/`, `docs/qa/`, `docs/evals/`, `docs/design/`, `docs/project/DOCUMENTATION.md`, `README.md`, `AGENTS.md`
Acceptance: no directory under `docs/` holds fewer than four files without a recorded reason; every moved path resolves; `doctor.py` passes.
Depends: PF-059
Est: 4-6

Eighteen directories hold 82 files, and seven of them hold one to three: `protocol/` (1), `qa/` (1), `evals/` (2), `privacy/` (2), `design/` (3), `engineering/` (3), `project/` (3). Fold `protocol/` into `architecture/`, combine `qa/` and `evals/` into one verification directory, and fold `design/` into `style-guide/`. Keep `privacy/` and `project/` where they are — both are small but load-bearing, and `privacy/` deliberately isolates the invariant everything else serves.

Every move must repair inbound references. `AGENTS.md` and `doctor.py`'s REQUIRED list both name paths.

### PF-061 — Archive spent planning specifications
Files: `docs/history/MACHINE_CONTRACT_REPAIR_SPEC.md`, `docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md`, `docs/history/`, `docs/project/DOCUMENTATION.md`, `AGENTS.md`, `README.md`
Acceptance: both files are in `docs/history/` with unique content merged into a living owner; no inbound reference is broken; `doctor.py` passes.
Depends: none
Est: 4-6

`MACHINE_CONTRACT_REPAIR_SPEC.md` (521 lines) declares itself a "normative P-1140B–E planning input"; P-1140E is closed, so it is spent. `REPOSITORY_ALIGNMENT_2026-07-23.md` (366 lines) restates decisions owned by `DECISION_REGISTER.md` and is cited in the `AGENTS.md` initialization order and in `DOCUMENTATION.md`, so both must be updated when it moves. Roughly 890 lines leave the active planning surface.

Unlike the nine files archived on 2026-08-05, these two have live inbound references. Merge before moving; do not orphan a reference.

### PF-062 — Make the decision register and task catalog machine-readable
Files: `conformance/planning/decisions-v1.json` (new), `conformance/planning/decisions-v1.schema.json` (new), `conformance/planning/tasks-v1.json` (new), `conformance/planning/tasks-v1.schema.json` (new), `scripts/repository/generate_planning_docs.py` (new), `docs/planning/DECISION_REGISTER.md`, `docs/planning/TASK_CATALOG.md`
Acceptance: the Markdown register and catalog are generated from JSON and byte-identical to the committed files; a validator fails on drift between source and generated output.
Depends: PF-053, PF-055
Est: 12-16

`conformance/p1140f/*.json` is the pattern that works in this repository: validators read structure. But 77 decisions and every planning gate live in Markdown tables, and validators reach them by substring matching — `validate_p1140f_authority.py:131` greps prose for a count, and `doctor.py` asserts that literal strings appear somewhere in a document. That is why the phase gate could only be moved by editing its own validator.

Make JSON the source and generate the Markdown, so prose can no longer drift from state and validators can assert on structure. This unit is what lets PF-063 assert on the whole register.

### PF-063 — Complete decision traceability coverage
Files: `scripts/repository/validate_p1140e_contracts.py`, `docs/planning/decision-traceability/`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: every accepted implementation-bearing decision has a traceability row with an implementation owner, machine or state ownership, platform scope, and executable evidence requirement; the traceability validator covers the whole register rather than a frozen prefix of it.
Depends: PF-062
Est: 4-6

Reference resolution itself is closed. `scripts/repository/validate_cross_references.py` resolves every decision, finding, ADR, program, work-unit, path, `$ref`, and `operationId` citation in the repository and exits non-zero on any that dangles; `tests/ci/test_cross_references.py` proves it fires per class. The 128 dangling work-unit citations that motivated this unit — a superseded two-digit numbering across 72 identifiers, including the `I-`, `PL-` and `U-` prefixes that never existed in the breakdown, and `D-01` through `D-10` used as work-unit identifiers in the same files where `D-001` onward are decisions — were deleted rather than remapped, because no unit they named survives.

What remains is coverage, not resolution. Decisions D-070 onward have no traceability rows at all, because `validate_p1140e_contracts.py:52-59` freezes its matrix at `range(1, 70)` and delegates the remainder to a validator that never references a `D-` identifier.

### PF-064 — Remove stale dates from living document filenames
Files: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`, `scripts/repository/doctor.py`, `AGENTS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/TASK_CATALOG.md`
Acceptance: no file that is still being updated carries a date in its filename; every inbound reference resolves; `doctor.py` passes.
Depends: PF-057
Est: 2-3

`P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md` is live and was last updated 2026-08-04, but its filename says July 24. A date in a filename should mean the document is a point-in-time record; using it for a living document teaches readers to distrust the convention. It has nine inbound references including `doctor.py`'s REQUIRED list.

Archived point-in-time reports in `docs/history/` keep their dates. That is what the convention is for.

### PF-065 — Correct the OpenAPI file extension
Files: `packages/schemas/openapi-v1.yaml`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_planning_coverage.py`, `scripts/repository/validate_p1140e_contracts.py`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: the file's extension matches its contents; every reader resolves it; all planning validators pass.
Depends: PF-038
Est: 2-3

`openapi-v1.yaml` contains JSON. YAML is a superset of JSON so parsers accept it, but the first tool that selects a parser by extension, or any human opening it expecting YAML, will be wrong. Either rename to `.json` or convert the contents to YAML — decide deliberately and record which, since several validators reference the path by name.

### PF-066 — Repair unreachable states and false terminal states
Files: `packages/schemas/state-machine-registry-v1.json`, `tests/ci/test_state_vocabularies.py`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: every state in every registry machine is reachable from its initial state, and no state listed in `terminal_states` has an outgoing transition. A test asserts both across all 26 machines, not only those bound to SQL or an API enum.
Depends: none
Est: 6-8

Two defect classes found by a reachability sweep during the PF-038 follow-up. Both are invisible to `validate_state_vocabularies.py`, which compares vocabularies across three sources and does not examine transitions.

**Unreachable states.** `daemon-lifecycle` cannot reach `degraded`, `offline`, `stopped`, or `stopping`. `privileged-supervisor` cannot reach `degraded`. `interactive-shell` cannot reach **10 of its 15 states**. These machines bind to neither a SQL column nor an API enum, so the existing three-way check never looks at them. A declared state no transition can produce is a specification that cannot be implemented.

One instance of this class was already fixed: `Notification.state` exposed `read` with no transition reaching it — all three sources agreed on a state no worker could produce. The `notification-read` transition closed it, and a scoped reachability guard now covers bound machines. This unit extends that guard to all 26.

**False terminal states.** Four machines declare a state terminal while giving it an outgoing transition: `idempotency-ledger.committed → expired`, `moderation-case.reversed → closed`, `update-lifecycle.failed → rolled-back`, `release-trust.superseded → expired`. A worker that trusts `terminal_states` will refuse a legal transition, and one that trusts the transition list will violate the terminal declaration. Decide which is authoritative per machine and make the registry say it once.

### PF-067 — Make state-vocabulary binding coverage self-checking
Files: `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_state_vocabularies.py`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: the validator fails when a declared aggregate has an unpopulated `sql=` or `api=` binding that could have been populated, and reports its true three-way coverage rather than an aggregate count.
Depends: none
Est: 4-6

`validate_state_vocabularies.py` is a genuine check — its drift-injection tests prove it catches renames, deletions, and dropped enum values. But its guarantee is narrower than its name implies. Of 31 declared aggregates, only **7** receive a real three-way registry + SQL + API comparison. 19 are two-way, usually legitimately because there is no API surface, and 5 are format-only.

Coverage is driven by a hardcoded `BINDINGS` table, so an aggregate whose `sql=` or `api=` field was simply never populated silently escapes the identity checks while still counting toward the reported total. The validator does fail closed on newly orphaned columns and enums, which is what prevents regression — the gap is that a binding omitted at authoring time is indistinguishable from one that is legitimately absent.

Make omission explicit: require every aggregate to declare either a binding or a recorded reason for having none, and have the summary line state three-way, two-way, and format-only counts separately so a green run cannot be read as more than it is.

### PF-068 — Author the Ed25519 divergence-case conformance corpus
Files: `conformance/vibeproof/v1/ed25519-divergence-corpus.json` (new), `conformance/vibeproof/v1/README.md` (new), `scripts/repository/generate_vibeproof_vectors.py`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`
Acceptance: the corpus contains at least one case for each of non-canonical `A`, non-canonical `R`, small-order `A`, and `S >= l`; every case records its expected ZIP-215 verdict; and a generator reproduces the corpus byte-identically from recorded inputs, so no verdict is asserted by hand.
Depends: PF-005
Est: 8-12

VibeProof v1 pins Ed25519 verification to ZIP-215 because RFC 8032 does not pin it: SS5.1.7 permits both the cofactored and cofactorless group equations, and FIPS 186-5 SS7.7 repeats that permission verbatim. A cofactored verifier accepts a strictly larger set of signatures than a cofactorless one, and the implication runs one way only, so a Rust signer and a Go verifier that both conform to RFC 8032 can disagree without any round-trip test noticing.

RFC 8032's own test vectors cannot detect this. They are well-formed signatures that pass under every implementation, which is exactly why they prove nothing about the axes that diverge. Only adversarial inputs separate the criteria sets.

The corpus is a precondition of any cross-language conformance claim, and it cannot be authored by asserting verdicts from the specification text alone - each expected outcome has to be confirmed against a ZIP-215 reference implementation, or the corpus repeats the original defect at one remove. Go's `crypto/ed25519` is cofactorless and will fail these cases by design; selecting a ZIP-215-capable Go implementation is part of the D-012 bakeoff.

## Frozen backlog — scope inventory, not executable units

Everything below is retained to hold the launch scope in `docs/planning/PRODUCT_SCOPE_FREEZE.md`. **These are headings, not units.** None carries `Files:`, `Acceptance:`, `Depends:` in resolvable form, or `Est:`, and none names a file path, schema, table, or endpoint. They must be promoted into the active plan against the required-fields standard before being worked, and they are all blocked until P-1104 regardless.

Known defects in this section, recorded rather than silently carried:

- **Six units declare prose dependencies that do not resolve**: `PF-001`, `PF-004`, `O-005`, `X-001`, `X-009`, `X-010` depend on phrases such as "implemented product paths" and "all launch paths". Prose dependencies cannot be ordered.
- **Eleven units are orphans** that nothing depends on: `F-008`, `L-014`, `N-018`, `N-019`, `P-010`, `S-001`, `S-004`, `S-015`, `W-001`, `W-010`, `X-011`. `S-001` is the Go service foundation, and `S-002` through `S-015` do not depend on it.
- **`X-011` does not gate launch.** P-1105 readiness transitively depends on 162 of 194 units, excluding all ten Epic W units — the entire hosted web product — plus `O-012`, `R-012`, `M-011`, `S-015`, `N-018`, `N-019`, `P-010`, and `F-008`. Launch readiness is currently declarable with no web application.
- **52 of the 73 tables in `packages/schemas/planning-schema.sql` are named nowhere in this file or in `IMPLEMENTATION_HANDOFF.md`.** Organizations and communities have four OpenAPI operations and two tables, and the words "organization" and "community" do not appear in this document at all. Passkeys, recovery codes, `model_alias_facts`, `minute_scores`, `social_integrity_events`, `audit_events`, and `adapter_installations` have no owning unit.
- **Thirteen categories have no unit anywhere**: local development environment, product CI/CD, logging and metrics and tracing, error taxonomy, API versioning and deprecation, rate limiting, data migration and backfill, load testing, runbooks and on-call, staging environment, cost modeling, feature-flag mechanics, and product analytics.

Promotion of any unit below must resolve the defects that apply to it.

### Future implementation epics — blocked until P-1104

## Epic F — Reproducible foundation

### F-001 Toolchain and lockfile pins
Files: `rust-toolchain.toml`, `.node-version`, `Cargo.toml`, `apps/api/go.mod`, `apps/web/package.json`, `scripts/ci/check_toolchain_pins.py` (new)
Acceptance: `python3 scripts/ci/check_toolchain_pins.py` exits 0 on the pinned tree and non-zero when any manifest names a range, a caret or `latest`; the installed `cargo`, `go` and `node` versions equal the pinned strings byte-for-byte.
Depends: PF-036
Est: 4-6
Status: not-started

### F-002 Workspace initialization and package boundaries
Files: `Cargo.toml`, `crates/vibeproof-core/Cargo.toml`, `crates/vibeproof-adapters/Cargo.toml` (new), `crates/vibeproof-collector/Cargo.toml` (new), `crates/vibeproof-sync/Cargo.toml` (new), `crates/vibemaxxing-daemon/Cargo.toml` (new), `crates/vibemaxxing-cli/Cargo.toml` (new)
Acceptance: `cargo metadata --locked --no-deps` lists exactly the workspace members declared in `Cargo.toml`; `cargo tree --invert vibeproof-collector` shows no path from a network-capable crate into the collector, which is the D-006 boundary expressed as a dependency edge.
Depends: F-001
Est: 8-12
Status: not-started

### F-003 Authoritative generated bindings
Files: `packages/protocol/rust/src/lib.rs` (new), `packages/protocol/go/protocol.go` (new), `packages/protocol/typescript/index.ts` (new), `scripts/ci/generate_bindings.py` (new), `packages/schemas/openapi-v1.yaml`
Acceptance: `python3 scripts/ci/generate_bindings.py --check` exits 0, and exits non-zero after one byte of any source schema changes without regeneration; `git diff --exit-code packages/protocol` after a fresh regeneration proves no generated file is hand-maintained.
Depends: F-001
Est: 12-16
Status: not-started

### F-004 Byte-identical regeneration and drift detection
Files: `scripts/ci/generate_bindings.py` (new), `tests/ci/test_generated_bindings.py` (new), `.github/workflows/ci.yml`
Acceptance: two consecutive regenerations produce identical bytes under `sha256sum`, and CI fails when a committed generated file differs from a fresh regeneration; `python3 -m unittest tests.ci.test_generated_bindings` exits 0.
Depends: F-003
Est: 6-8
Status: not-started

### F-005 Checked numeric/time/digest/identifier primitives
Files: `crates/vibemaxxing-primitives/Cargo.toml` (new), `crates/vibemaxxing-primitives/src/lib.rs` (new), `crates/vibemaxxing-primitives/tests/overflow.rs` (new)
Acceptance: `cargo test -p vibemaxxing-primitives` exits 0 with one case per operation proving addition, multiplication and unit conversion return an error at the boundary rather than wrapping or saturating; `cargo clippy -p vibemaxxing-primitives -- -D clippy::arithmetic_side_effects` exits 0.
Depends: F-002
Est: 8-12
Status: not-started

### F-006 Privacy canary library and fixtures
Files: `crates/vibemaxxing-canary/Cargo.toml` (new), `crates/vibemaxxing-canary/src/lib.rs` (new), `conformance/privacy/p1140b-boundary-canaries-v1.json`, `conformance/telemetry/canaries.json`
Acceptance: `cargo test -p vibemaxxing-canary` exits 0 and fails when any canary string from either fixture reaches an outbound buffer; the suite covers every forbidden content class named in `docs/privacy/PRIVACY_CONTRACT.md`, and a class present in the contract but absent from the suite fails the test.
Depends: F-002
Est: 8-12
Status: not-started

### F-007 Feature disable and emergency-revoke framework
Files: `crates/vibemaxxing-kill-switch/Cargo.toml` (new), `crates/vibemaxxing-kill-switch/src/lib.rs` (new), `apps/api/internal/killswitch/killswitch.go` (new), `packages/schemas/policy-defaults-v1.json`
Acceptance: `cargo test -p vibemaxxing-kill-switch` and `go test ./internal/killswitch/...` both exit 0, with a case proving a revoked capability is refused within the propagation deadline recorded in `packages/schemas/policy-defaults-v1.json` and that the revocation survives a process restart.
Depends: F-002
Est: 8-12
Status: not-started

### F-008 Narrow format/lint/unit automation restoration
Files: `.github/workflows/ci.yml`, `scripts/ci/verify_repository.py`
Acceptance: `cargo fmt --check`, `cargo clippy -- -D warnings`, `gofmt -l`, `go vet ./...`, `npm run lint` and `npm test` each run in CI and exit 0; `grep -n 'paths:' .github/workflows/ci.yml` returns no filter exempting `apps/`, `crates/` or `Cargo.toml`.
Depends: F-001, F-002, F-003, F-004, F-005, F-006, F-007
Est: 6-8
Status: not-started

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

### F-009 Local development environment
Files: `docs/engineering/LOCAL_DEVELOPMENT.md` (new), `scripts/dev/bootstrap.sh` (new), `compose.dev.yaml` (new), `Makefile`
Acceptance: `make dev-up` brings up PostgreSQL and the API from a clean checkout with no manual step, `make dev-check` exits 0, and `bash scripts/dev/bootstrap.sh --verify` exits non-zero when a toolchain version pinned by `F-001` is missing or wrong.
Depends: F-001, F-002
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. The database engine and migration tool are fixed by ADR-018 and are not re-decided here.

### F-010 Product CI/CD pipeline
Files: `scripts/ci/check_required_checks.py` (new), `docs/engineering/CI_AND_DELIVERY.md` (new), `.github/workflows/ci.yml`, `docs/engineering/ENGINEERING_SYSTEM.md`
Acceptance: `python3 scripts/ci/check_required_checks.py` exits 0 only when every quality layer listed under `## Required quality layers` in `docs/engineering/ENGINEERING_SYSTEM.md` has a matching job in the workflow set and appears in the branch-protection required-checks list, and exits non-zero when a layer has no job.
Depends: F-008
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. Deployment is deliberately excluded here and stays in `X-001`; this unit ends at a verified artifact, not at a running environment. Activating product CI is outside the current authorization for the reason recorded under `F-008`.

### F-011 Feature-flag mechanics
Files: `packages/schemas/feature-flag-v1.schema.json` (new), `apps/api/internal/flags/flags.go` (new), `packages/schemas/planning-schema.sql`, `packages/schemas/policy-defaults-v1.json`
Acceptance: `go test ./internal/flags/...` exits 0 with cases proving evaluation is deterministic for a given `(flag, principal, revision)` triple, that an unknown flag resolves to its recorded default rather than erroring, and that no flag name or evaluation result appears in any egress buffer under the `F-006` canary suite.
Depends: F-007, S-002
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

## Epic P — Normative VibeProof

### P-001 Rust canonical normative model
Files: `crates/vibeproof-core/src/model.rs` (new), `crates/vibeproof-core/tests/model.rs` (new), `packages/schemas/vibeproof-claim-v1.cddl`
Acceptance: `cargo test -p vibeproof-core --test model` exits 0, and a name cross-check in that test fails when any CDDL rule in `packages/schemas/vibeproof-claim-v1.cddl` has zero or more than one corresponding Rust type.
Depends: F-003
Est: 12-16
Status: not-started

### P-002 Rust deterministic CBOR encoder/decoder
Files: `crates/vibeproof-core/src/cbor.rs` (new), `crates/vibeproof-core/tests/canonical_cbor.rs` (new), `conformance/vibeproof/v1/negative-vectors.json` (new)
Acceptance: `cargo test -p vibeproof-core --test canonical_cbor` exits 0; encoder output matches every vector in `conformance/vibeproof/v1/exact-byte-vectors.json` byte-for-byte; the decoder rejects every negative vector with its recorded reason; a fixture encoded with the RFC 8949 Section 4.2.3 length-first ordering fails, which is what pins D-191.
Depends: P-001
Est: 12-16
Status: not-started

### P-003 Rust COSE_Sign1 and Ed25519 profile
Files: `crates/vibeproof-core/src/cose.rs` (new), `crates/vibeproof-core/tests/cose.rs` (new), `conformance/vibeproof/v1/exact-byte-vectors.json`
Acceptance: `cargo test -p vibeproof-core --test cose` exits 0; the protected header encodes algorithm -19 and not -8, which a byte assertion on the header proves per D-190; every case in the ZIP-215 divergence corpus authored by `PF-068` yields its recorded verdict.
Depends: P-002, PF-068
Est: 12-16
Status: not-started

### P-004 Independent Go normative model and decoder
Files: `apps/api/internal/vibeproof/model.go` (new), `apps/api/internal/vibeproof/decode.go` (new), `apps/api/internal/vibeproof/decode_test.go` (new)
Acceptance: `go test ./internal/vibeproof/...` exits 0 against the same exact-byte and negative corpora as `P-002`; `go list -deps ./internal/vibeproof` names no artifact produced by the Rust crate, so the two implementations share only the CDDL source.
Depends: F-003
Est: 12-16
Status: not-started

### P-005 Go COSE verification and authorization binding
Files: `apps/api/internal/vibeproof/cose.go` (new), `apps/api/internal/vibeproof/cose_test.go` (new)
Acceptance: `go test ./internal/vibeproof/ -run COSE` exits 0 with every ZIP-215 divergence case producing its recorded verdict; substituting the standard-library `crypto/ed25519` makes the suite fail, which is the check that D-192 is actually enforced rather than merely cited.
Depends: P-004
Est: 12-16
Status: not-started

### P-006 Exact claim/appraisal/receipt/challenge/batch vectors
Files: `conformance/vibeproof/v1/exact-byte-vectors.json`, `scripts/repository/generate_vibeproof_vectors.py`
Acceptance: `python3 scripts/repository/generate_vibeproof_vectors.py --check` exits 0; the file carries at least one vector for each of claim, appraisal, receipt, challenge and batch; both implementations reproduce every byte, and hand-editing any vector makes the check fail, which is what D-194 requires.
Depends: P-003, P-005
Est: 8-12
Status: not-started

### P-007 Rotation/gap/correction/fork vectors
Files: `conformance/vibeproof/v1/fork-and-rotation-vectors.json` (new), `scripts/repository/generate_vibeproof_vectors.py`
Acceptance: the generator's `--check` mode exits 0; the file covers rotation, sequence gap, correction and fork, each carrying an expected accept-or-quarantine verdict; Rust and Go agree on every verdict.
Depends: P-006
Est: 8-12
Status: not-started

### P-008 Malformed, mutation and resource corpus
Files: `conformance/vibeproof/v1/malformed-resource-corpus.json`, `conformance/vibeproof/v1/negative-vectors.json` (new)
Acceptance: both decoders reject every case with its recorded reason; a bounded-allocator test fails when either exceeds the declared allocation ceiling or nesting depth; a single-bit mutation of any accepted vector is rejected rather than decoded.
Depends: P-003, P-005
Est: 10-14
Status: not-started

### P-009 Cross-language differential and byte-exact suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_protocol_differential.py` (new), `scripts/ci/run_evals.py`
Acceptance: `python3 scripts/ci/run_evals.py --suite protocol-conformance` exits 0 and reports a status that is not `not_applicable`; the suite runs both implementations over every vector and fails on any disagreement, so a suite that skips one implementation cannot report a pass.
Depends: P-006, P-007, P-008
Est: 10-14
Status: not-started

### P-010 Fuzz/property harness activation
Files: `crates/vibeproof-core/fuzz/fuzz_targets/decode.rs` (new), `crates/vibeproof-core/fuzz/Cargo.toml` (new), `.github/workflows/fuzz.yml` (new), `docs/verification/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md`
Acceptance: `cargo fuzz run decode -- -runs=100000` exits 0 with no crash and no timeout, and a deliberately reintroduced non-minimal-integer acceptance is found inside that budget — a green fuzz run with no capability check is not evidence.
Depends: P-009
Est: 10-14
Status: not-started

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

## Epic A — Accounting and deterministic integrity

### A-001 Immutable accounting-profile loader and digest verification
Files: `crates/vibeproof-core/src/accounting/profile.rs` (new), `packages/schemas/accounting-profile.schema.json`, `conformance/accounting/accounting-profiles-v1.json`
Acceptance: `cargo test -p vibeproof-core --test accounting_profile` exits 0; the loader refuses a profile whose recomputed `accounting_profile_sha256` differs by one byte, and the digest it computes equals the value recorded in the fixture.
Depends: F-003, F-005
Est: 8-12
Status: not-started

### A-002 Operation/observer identity model
Files: `crates/vibeproof-core/src/accounting/identity.rs` (new), `packages/schemas/normalized-event.schema.json`, `conformance/accounting/accounting-v1-fixtures.json`
Acceptance: two observations of one operation from different observers resolve to a single operation identity and a retry generation resolves to a distinct one, each asserted by a fixture case; an event with no observer identity is rejected rather than defaulted.
Depends: A-001
Est: 8-12
Status: not-started

### A-003 Category containment and source authority
Files: `crates/vibeproof-core/src/accounting/containment.rs` (new), `conformance/accounting/p1140b-accounting-cases-v1.json`
Acceptance: a case whose cache-read count exceeds its containing input count is rejected rather than clamped; when two sources disagree, the higher-authority source wins by the recorded ordering and the losing value is retained in the result rather than dropped.
Depends: A-002
Est: 8-12
Status: not-started

### A-004 Cache/reasoning/modality/total reconciliation
Files: `crates/vibeproof-core/src/accounting/reconcile.rs` (new), `conformance/accounting/reconciliation-vectors-v1.json` (new)
Acceptance: every vector reconciles to its recorded total; a vector whose parts cannot sum to its stated total yields a contradiction verdict rather than a silent adjustment, and the test fails if any adjustment is applied.
Depends: A-003
Est: 10-14
Status: not-started

### A-005 Retry/cancellation/nested-agent reconciliation
Files: `crates/vibeproof-core/src/accounting/lifecycle.rs` (new), `conformance/accounting/reconciliation-vectors-v1.json` (new)
Acceptance: each value of `retry_policy`, `cancellation_policy` and `nested_execution_policy` is exercised by at least one vector, which a coverage assertion in the test enforces; a cancelled operation contributes exactly the recorded amount and a nested subagent turn is counted exactly once.
Depends: A-003
Est: 10-14
Status: not-started

### A-006 Duplicate-domain engine
Files: `crates/vibeproof-core/src/accounting/dedup.rs` (new), `conformance/accounting/dedup-vectors-v1.json` (new)
Acceptance: two collectors over one session produce one counted event in every vector, including the case where the two choose non-colliding duplicate-domain commitments; each vector is run under both input orderings and must produce the same result.
Depends: A-002
Est: 10-14
Status: not-started

### A-007 Checked arithmetic and bounds
Files: `crates/vibeproof-core/src/accounting/bounds.rs` (new), `crates/vibemaxxing-primitives/src/lib.rs` (new)
Acceptance: `cargo test -p vibeproof-core --test accounting_bounds` exits 0; every arithmetic path returns an error at the boundary rather than wrapping, and an event above the recorded per-period ceiling is rejected with a reason code that resolves in `packages/schemas/reason-codes-v1.json`.
Depends: F-005
Est: 6-8
Status: not-started

### A-008 Deterministic contradiction/quarantine results
Files: `crates/vibeproof-core/src/accounting/verdict.rs` (new), `packages/schemas/reason-codes-v1.json`
Acceptance: every contradiction produces exactly one verdict drawn from the reason registry; running the whole fixture corpus twice with shuffled input order produces byte-identical verdict output, which is the order-independence D-018 assumes.
Depends: A-003, A-004, A-005, A-006, A-007
Est: 8-12
Status: not-started

### A-009 Server pricing interpretation model
Files: `apps/api/internal/pricing/pricing.go` (new), `packages/schemas/pricing-interpretation.schema.json`, `conformance/pricing/pricing-v1.json`, `conformance/pricing/pricing-v1-manifest.json`
Acceptance: `go test ./internal/pricing/...` exits 0; an unpriced model yields no cash figure rather than zero; every emitted figure carries the estimated label, which a response-schema assertion enforces so the label cannot be dropped by a caller.
Depends: A-001
Est: 8-12
Status: not-started

Persistence owner for `pricing_datasets`, `pricing_entries`, `cost_interpretations` and `model_alias_facts`. All four had no owning unit before this one; `model_alias_facts` in particular is what lets an unrecognised model alias resolve to a priced model without guessing.

### A-010 Accounting differential and order-invariance evidence
Files: `evals/suites/suites.yaml`, `evals/fixtures/token-accounting-conformance.json`, `tests/conformance/test_accounting_differential.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite ranking-accounting` exits 0 with a status that is not `not_applicable`; the Rust and Go implementations produce identical totals for every fixture under both input orderings, and a one-token divergence fails the suite.
Depends: A-008
Est: 10-14
Status: not-started

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

The currently-unstarted active-plan units are `PF-001`, `PF-037`, `PF-039` through `PF-052`, `PF-053`, `PF-054`, and `PF-062` through `PF-067`. (Checked against `git log --oneline origin/main`: PF-055 and PF-056 have landed; none of PF-001, PF-037, PF-053, PF-054 appear in recent commits, confirming they remain unstarted.)

All `F-` through `X-` units remain blocked until P-1104.

An earlier revision of this section stated "PF-001 only", and a companion claim placed `PF-002`/`PF-003` immediately after `PF-001` on the critical path. Both were wrong by this file's own dependency lines: `PF-002` and `PF-003` are leaves that nothing depends on, and the longest `PF-` chain begins at `PF-004`, which does not depend on `PF-001`. The corrected chain to `PF-036` is `PF-004 → PF-021 → PF-022 → PF-023 → PF-029 → PF-033 → PF-034 → PF-035 → PF-036`, a depth of nine.

For reference, the longest chains in the frozen backlog, measured in units rather than time: 19 to `S-010` (first claim accepted server-side), 26 to `V-004` (first working adapter), 28 to `W-003` (leaderboard visible in a browser), 36 to `X-011`, and 37 to `W-010`. A 26-unit serial chain before one real token reaches a board is the specific reason the active plan is sequenced by vertical slice rather than by layer.