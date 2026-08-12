# Authoritative State, API, Persistence, Platform, and Release Contract

Status: normative P-1140D planning contract; no implementation or launch evidence
Version: 2
Updated: 2026-08-06

## Single ownership rule

`packages/schemas/state-machine-registry-v1.json` is the machine-readable index of every mutable product concept. Its schema is `state-machine-registry-v1.schema.json`. Each machine declares one semantic owner, exact persistence tables, aggregate key, states, terminal states, transitions, actor/authentication/recent-auth requirements, idempotency scope, audit event, reversal semantics and transaction boundary.

Prose may explain a state machine but cannot create a second state vocabulary. OpenAPI operations, SQL checks, workers, local IPC and UI states must reference the registry IDs. An unregistered mutation is forbidden.

## State vocabulary rules

These rules are executable. `scripts/repository/validate_state_vocabularies.py` holds the binding table below as data, refuses to run if this document and the schemas disagree, and exits non-zero on any mismatch.

### Naming convention

Every state value, in every owner, is **lowercase kebab-case** matching `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. This applies to registry `states`, `initial_state`, `terminal_states`, `from` and `to`; to every SQL `check (column in (...))` literal for a state column; and to every OpenAPI state enum value. `snake_case` state values are prohibited.

The rule follows the registry rather than SQL convention because `state-machine-registry-v1.schema.json` already constrains every identifier to `^[a-z0-9]+(?:[.-][a-z0-9]+)*$`, which cannot express `_`. Making SQL and the API kebab-case therefore produces one literal vocabulary spelled identically in all three files, whereas making the registry `snake_case` would require a second, mechanical `-`/`_` transform at every boundary — which is the defect this section exists to remove. The rule governs *state* values only; event types, scopes, roles and other enums are out of scope for this contract.

### Three-way agreement

For every aggregate:

- the registry machine's `states` set is the canonical vocabulary;
- the SQL `check` set on the aggregate's state column is **identical** to it — persistence must be able to hold every state a worker can reach;
- the OpenAPI enum is identical to it **minus the declared internal states** in the table below.

An internal state is one a client must never be shown. Every omission from an API enum must appear in the `Internal-only` column; there is no other way to omit a state. Where an aggregate has no registry machine, no SQL column or no API enum, the table records `—` and the reason appears in the recorded-absence table below.

That rule previously said the reason was "given under Open items", and nothing compared the two. Thirty-nine cells recorded `—`; Open items explained four. The reasons therefore live in a table the validator parses and compares entry for entry against its own `RECORDED_ABSENCES`, so a `—` without a reason fails, and a reason for a binding that is in fact populated fails too. The second half matters as much as the first: five `local-*` aggregates carried an explicit empty `sql=()` while `local-store-v1.sql` already defined the tables they name, so a justification can outlive the gap it was written for.

### Binding table

| Aggregate | Registry machine | SQL state columns | API state enums | Internal-only states |
|---|---|---|---|---|
| `oauth-transaction` | `oauth-transaction` | `oauth_transactions.state` | — | — |
| `web-session-family` | `web-session-family` | `session_families.state` | — | — |
| `native-session-family` | `native-session-family` | `session_families.state` | — | — |
| `session-member` | — | `native_sessions.state`, `web_sessions.state` | `Session.state` | — |
| `ranked-identity-eligibility` | `ranked-identity-eligibility` | `ranked_identities.state` | `AccountProfile.ranked_state`, `PublicProfile.ranked_state` | `appealed`, `consolidating`, `investigating`, `reversed` |
| `idempotency-ledger` | `idempotency-ledger` | `idempotency_records.state` | — | — |
| `ranking-projection` | `ranking-projection` | `ranking_projection_generations.state` | — | — |
| `period` | `period` | `periods.state` | — | `corrected` |
| `model-alias-resolution` | `model-alias-resolution` | `cost_interpretations.state`, `pricing_datasets.state` | `PricingDataset.state` | — |
| `friendship` | `friendship` | `friend_requests.state` | — | — |
| `rivalry` | `rivalry` | `rival_edges.state` | — | — |
| `board-membership` | `board-membership` | `board_memberships.state` | — | — |
| `board-invitation` | `board-invitation` | `board_invites.state` | — | — |
| `board-container` | — | `boards.state`, `communities.state`, `organizations.state` | `Board.state`, `Community.state`, `Organization.state` | — |
| `invite-code` | `invite-code` | `invite_codes.state` | — | — |
| `presence-lease` | `presence-lease` | `presence_leases.state` | — | — |
| `notification-delivery` | `notification-delivery` | `notification_events.state`, `notifications.state` | `Notification.state` | `created`, `grouped`, `ready`, `suppressed` |
| `moderation-case` | `moderation-case` | `moderation_cases.state` | `ModerationCase.state` | — |
| `appeal` | `appeal` | `appeals.state` | `Appeal.state` | `screening` |
| `export-job` | `export-job` | `exports.state` | `ExportJob.state` | — |
| `server-deletion` | `server-deletion` | `deletion_jobs.state` | `DeletionJob.state` | `rebuilding-projections` |
| `local-deletion-command` | `local-deletion-command` | `local_deletion_commands.state` | — | — |
| `daemon-lifecycle` | `daemon-lifecycle` | `service_instances.state` | — | — |
| `privileged-supervisor` | `privileged-supervisor` | `privileged_supervisor_instances.state` | — | — |
| `interactive-shell` | `interactive-shell` | `shell_sessions.state` | — | — |
| `local-collection` | `local-collection` | `local_collection_state.state` | — | — |
| `local-sync` | `local-sync` | `local_sync_state.state` | — | — |
| `local-auth` | `local-auth` | `local_auth_state.state` | — | — |
| `local-permission` | `local-permission` | `local_permission_state.state` | — | — |
| `local-connectivity` | `local-connectivity` | `local_connectivity_state.state` | — | — |
| `update-lifecycle` | `update-lifecycle` | `update_installations.state` | — | — |
| `release-trust` | `release-trust` | `release_sets.state` | — | — |
| `platform-certification` | `platform-certification` | `platform_profiles.validation_state` | `CompatibilityProfile.validation_state` | — |
| `account-lifecycle` | `account-lifecycle` | `accounts.state` | — | — |
| `device-enrollment` | `device-enrollment` | `devices.state` | `Device.state` | — |
| `device-authorization-grant` | — | `device_enrollment_grants.state` | `DeviceAuthorizationStatus.state` | — |
| `linked-identity` | `linked-identity` | `linked_identities.state` | `Identity.state` | `candidate`, `superseded` |
| `claim-record` | — | — | `ClaimRecord.state` | — |
| `recovery-case` | `recovery-case` | `recovery_cases.state` | — | — |
| `identity-investigation` | `identity-investigation` | `identity_investigations.state` | — | — |
| `account-consolidation` | `account-consolidation` | `consolidation_cases.state` | — | — |
| `lineage-fork-case` | `lineage-fork-case` | `lineage_fork_cases.state` | — | — |
| `source-certification` | `source-certification` | `source_certifications.state` | — | — |

### Why each state is internal

- `ranked-identity-eligibility.investigating`, `.consolidating`, `.appealed`, `.reversed` are `integrity-private`. Exposing them would tell an adversary whether an anti-abuse investigation is open, which is itself an anti-cheat signal. The public vocabulary is `unverified`, `eligible`, `restricted`, `retired`; `restricted` covers every non-eligible outcome without disclosing its cause. The previous API values `unranked` and `suspended` were synonyms for `unverified` and `restricted` and are removed.
- `notification-delivery.created`, `.grouped`, `.ready` and `.suppressed` are the four states before the item reaches the inbox. D-420 states the rule they follow from: the server inbox is the notification authority, so a notification exists for its recipient exactly when it has been written there, and every earlier state is worker state. `created` is an appended source event that has not been deduplicated. `grouped` and `ready` sit between the dedup/hysteresis worker and the delivery worker. `suppressed` is the state of an event the recipient's preferences, a block, a withdrawn authorization or the D-088 overtake hysteresis stopped; publishing it would hand back the flip-flop the hysteresis exists to remove, and would tell a participant they were overtaken by someone who has blocked them. An earlier revision of this row listed only `grouped` and `ready`, which left `created` and `suppressed` on the API with no display rule any client could write.
- `retracted` is API-visible and required: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` requires corrections, moderation reversals and rebuilds to retract or replace prior notifications, and neither the API nor SQL could previously express it. A retracted item stays in the inbox rather than disappearing from it, because a participant who read the original needs to learn that it was withdrawn. It is not a D-070 path; D-070 is duplicate-account consolidation.
- `appeal.screening` is the automated pre-review pass. It is not a decision and gives the appellant no actionable information; `submitted` is what they see until a human is assigned.
- `server-deletion.rebuilding-projections` is a ranking-worker implementation detail inside the deletion job.

### Shared, derived, projected and transient vocabularies

- `session_families.state` is shared by the `web-session-family` and `native-session-family` machines. Its `check` set is exactly the union of the two, and each machine's states must be a subset of it. `device-revoked` is native-only.
- `web_sessions.state`, `native_sessions.state` and `Session.state` describe an individual member row of a token family, not the family. They have no machine of their own and share one vocabulary.
- `account-lifecycle` and `device-enrollment` each carry a restoration transition because `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md:87` requires every restriction, quarantine and revocation to have restoration semantics, review authority and deterministic correction of derived ranks. `account-restore` and `device-requalify` are the transitions that satisfy it; both need recent moderator authentication, matching the account-level restriction rule under Ranked identity. `device-requalify` is named for the `requalify` lineage event in `device-lineage.schema.json`, and `device-quarantine` covers the fork and clone detections AC-A-010 and AC-A-011.
- `device-revoke` cascades: revoking a device drives its `native-session-family` to `device-revoked` in the same `device-and-token-family` transaction. Revocation is not terminal — `device-delete` follows it — but re-enrolling produces a new `device_id`, never a revoked row returning to `active`.
- `model_alias_facts` derives its state from `effective_at`/`superseded_at` and has no state column.
- Claims are append-only facts. `ClaimRecord.state` is derived from `claims`, `claim_corrections` and `quarantines`; adding a mutable state column to `claims` would contradict "accepted claims never mutate".
- `PresenceLease.availability` is a declared coarsening of `presence-lease`: `absent`, `expired` and `revoked` all render as `offline`, `active` renders as `online`, `idle` renders as `idle`. The validator requires the mapping to cover every machine state. `PresenceRenewalRequest.availability` was declared alongside it and is gone under PF-026: a projection coarsens a server-derived state on the way out and cannot run inbound, so declaring the request body as one meant the client named the state that AGENTS.md says the server derives. The request carries a device, a lease generation and a qualifying boolean.
- `ClaimBatchResult.state` and `OAuthCompletion.state` report the outcome of one request rather than a stored aggregate. `OAuthCompletion.state` now carries the machine's terminal value `consumed` rather than the synonym `completed`.
- `board_memberships.role` is now one-to-one with the machine's `active-*` states, enforced by a table `check`. `active-viewer` was added to the machine because `BoardInvitationRequest.role` already offered `viewer` and no membership state could hold it. The `board_one_active_owner` unique index keys on `state = 'active-owner'`; there is still no board owner column. It enforces at most one owner and cannot enforce at least one, so the other half is the `board-create-owner` transaction and the paired transfer, both planned in `conformance/p1140e/sql-race-plans-v1.json`.
- `board-membership` and `board-invitation` no longer carry a block-caused terminal state. PF-025 removed `blocked` and `invalidated-by-block` for the reason D-585 removed the friendship one: a directional block between two accounts was terminally ending a membership and an invitation that a third party — the board owner — had granted, and unblocking could not restore either. A board still refuses a person through `removed`, which is the board's own reversible act under recent authentication.
- Sub-entity vocabularies that are not aggregate lifecycles are declared in `SQL_LOCAL_VOCABULARIES` in the validator: `device_keys.state`, `quarantines.state`, `deletion_effects.state`, `platform_certifications.state`, `appeal_decisions.decision`, `notification_deliveries.state`, `local_deletion_commands.disposition`, `local_deletion_receipts.outcome`, the assessed `provenance_state`/`continuity_state`/`integrity_state` triple on `evidence_assessments`, `evidence_assessments.public_state`, `verifier_appraisals.certification_state` and `verifier_appraisals.public_state`, and the lineage `continuity_state` on `device_lineages`, which is its sole owner under PF-009: it previously sat on `device_sequences` as well, with nothing stating which of the two won. The same triple sat on `verifier_appraisals` until PF-072 and was removed rather than redeclared: the appraisal aggregate is described by `verifier-appraisal-v1` and `appraisal-result-v1.schema.json`, neither of which contains those three states, and the table now carries the seven dimensions both of them do. `verifier_appraisals` is that aggregate's sole persistence owner; `evidence_assessments` is the older, coarser record of the same claim and decides nothing the appraisal decides.
- `notification_deliveries.state` is one transport attempt and not the notification. The aggregate is the notification; an attempt is queued against an inbox item that already exists, and losing one loses a hint. Three table constraints carry the authority rule rather than leaving it to a worker: a `server-inbox` attempt has the single outcome `accepted`, because it is written in the same transaction as the inbox row; a `push` or `email` attempt cannot exist without the opt-in timestamp that authorized it, which is why none is writable at launch under D-086; and the table has no read column, so `accepted` and `acknowledged` can never become a read. `notifications.read_at` is the only read there is.
- `local_deletion_commands.disposition` is a declared coarsening of the `local-deletion-command` machine by two facts the machine cannot carry, and it is checked equal to that coarsening in the DDL rather than maintained beside it. `unreachable` is `expired` with no acknowledgement — a device that never heard the request — and `waived` is the participant's act rather than the device's. `LocalDeletionOutcome.disposition` mirrors it, under the same rule that publishes `appeal_decisions.decision` as `Appeal.decision`.
- `local_deletion_receipts.outcome` repeats, deliberately and exactly, the vocabulary the device-side receipt in `packages/schemas/local-store-v1.sql` already declares. The server row is the transported form of the device row. A second spelling for the same fact is the duplication SR-009 exists to remove.
- `appeal_decisions.decision` records the outcome only — `upheld`, `partially-upheld`, `reversed`. Its previous values `needs_information` and `expired` were appeal *workflow* states and now live in `appeals.state`, which is where the `appeal` machine puts them. Because the outcome is not a state, moving it out of `Appeal.state` would otherwise have removed the appellant's only way to tell `upheld` from `partially-upheld` from `reversed`. `Appeal.decision` publishes it instead: an optional enum, present exactly when `appeals.state` is `approved`, and required by the validator to equal the `appeal_decisions.decision` vocabulary. A `denied` appeal has no decision row and no `decision` field.
- `server-deletion` has a `cancelled` state and a `deletion-cancel` transition from `cooling-off`, and `cancelDeletion` is its only route. Two open items above said this was missing, and `docs/privacy/DATA_MAP.md` states the seven-day window as cancellable inside the Article 30 record, so the gap was the record describing a reversal no owner could perform. The actor is the participant under recent authentication rather than a worker: an erasure a worker can call off is not a right. `deletion_jobs` refuses a cancellation whose time is not before `effective_after`, so lateness is refused where the value is written rather than where it is read.
- `deletion_effects` is keyed on `data_domain` rather than on a free-text `subsystem`, and its vocabulary no longer contains `not-applicable`. The column had no CHECK at all, so two workers could spell one subsystem two ways and both rows were accepted; and `not-applicable` was a member meaning "we did not look", which let a plan cover every domain by declining to answer for any. `packages/schemas/consolidation-plan-v1.schema.json` refuses the same value in the same position for the same reason. A domain that held nothing reaches `complete` with an affected row count of zero.
- `export-manifest-v1.schema.json` no longer carries a fourth spelling of the deletion vocabulary. `deletion_state_at_generation` held `cooling_off`, `executing` and `completed`, none of which is a state of any machine, table or API enum, so a manifest and the deletion job it described could not be compared at all. It now carries the `server-deletion` states plus `none`, and the planning validator compares the two sets.
- `platform_certifications.state` records one certification run against one release set. It is not the profile lifecycle; that is `platform_profiles.validation_state`, bound to the `platform-certification` machine.

### Recorded absences

Every `—` in the binding table above appears here exactly once, with the reason that cell is empty. `scripts/repository/validate_state_vocabularies.py` compares this table to its `RECORDED_ABSENCES` in both directions and on the reason text, so this document and the validator cannot disagree about what is unchecked.

An absence is not a defect. Not stating one is: an aggregate whose binding was never populated is otherwise indistinguishable from an aggregate that legitimately has no such owner, and the aggregate count rises either way.

| Aggregate | Absent binding | Reason |
|---|---|---|
| `account-consolidation` | `api` | D-070 consolidation under D-382. getConsolidationPlan publishes the plan and no lifecycle value; a state like `applying` is an operational fact. |
| `account-lifecycle` | `api` | Exposed through the account's own surface as capability, not as a lifecycle enum. |
| `board-container` | `machine` | A two-value archive flag; its mutable concepts have machines of their own. |
| `board-invitation` | `api` | An invitee sees the invitation or does not; intermediate states are server-side. |
| `board-membership` | `api` | Membership is exposed as presence in a board's member list, not as a state value. |
| `claim-record` | `machine` | Claims are immutable facts; the registry indexes mutable concepts. |
| `claim-record` | `sql` | Append-only; the state is derived from later records, never stored. |
| `daemon-lifecycle` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `device-authorization-grant` | `machine` | Open: mutable, but the OAuth flow owns its transitions and they are unspecified. |
| `friendship` | `api` | The API exposes the edge, not the machine; the viewer's own side is derived. |
| `idempotency-ledger` | `api` | Replay is observed through the replayed response, never as a state value. |
| `identity-investigation` | `api` | Integrity-private under D-381; a public state value would publish the sanction. |
| `interactive-shell` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `invite-code` | `api` | Private-beta admission under D-180. The invitee is told whether it worked, not its state. |
| `lineage-fork-case` | `api` | D-072 fork and clone resolution under D-383; quarantine is read through evidence class. |
| `local-auth` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `local-collection` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `local-connectivity` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `local-deletion-command` | `api` | The API publishes LocalDeletionOutcome.disposition, the declared coarsening, rather than the machine state; see OUTCOME_MIRRORS. |
| `local-permission` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `local-sync` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `native-session-family` | `api` | Families are server-internal; a client sees only its own session member. |
| `oauth-transaction` | `api` | OAuthCompletion.state echoes the terminal value only; see TRANSIENT_API_ENUMS. |
| `presence-lease` | `api` | PresenceLease.availability is a declared coarser projection; see PROJECTIONS. |
| `privileged-supervisor` | `api` | Local-only; never persisted server-side and never exposed by the API. |
| `period` | `api` | A client reads a period's standing, never its lifecycle; the finalization boundary is server-side and no operation exposes it. |
| `ranking-projection` | `api` | Generation build state is operational; a client sees a sealed generation or none. |
| `recovery-case` | `api` | Account recovery under D-380. No operation exposes the case. |
| `release-trust` | `api` | Local-only; trust in a release is evaluated on the device against TUF metadata. |
| `rivalry` | `api` | The API exposes the edge, not the machine; the viewer's own side is derived. |
| `session-member` | `machine` | Member rows of a token family; the family machines own the transitions. |
| `source-certification` | `api` | D-387. Certification is server-assigned; exposing it would let a client select it. |
| `update-lifecycle` | `api` | The lifecycle state is a device-local fact; the server records the installed release set and publishes no state enum for it. |
| `web-session-family` | `api` | Families are server-internal; a client sees only its own session member. |

### Open items

- **No registry machine for board or claim, by design.** `claim-record` does not need one: claims are immutable facts, and the registry indexes mutable concepts. `board-container` does not need one: it is a two-value archive flag whose mutable concepts (`board-membership`, `board-invitation`) already have machines. `device-authorization-grant` remains open: it is genuinely mutable, but its transitions are owned by the RFC 8628 device flow and are not yet specified to the level the registry requires. `identity-link` no longer appears here at all. PF-007 gave it the eight-state `linked-identity` machine the provider-loss section of `docs/security/AUTHENTICATION_AND_RECOVERY.md` already described in prose, and renamed the aggregate to the spelling its table and its machine use, because an aggregate with one name in the binding table, another in the DDL and none in the registry is the drift the one-spelling rule exists to stop.
- **Cancelling a deletion requested from `restricted` returns the account to `active`.** `account-lifecycle` allows `account-request-deletion` from both `active` and `restricted`, because a restricted account keeps its deletion rights, but one state column cannot hold "pending deletion" and "restricted" at once. `account-cancel-deletion` therefore targets `active`, and the restriction must be re-applied from the append-only moderation effects. Modelling restriction as a flag independent of lifecycle would remove this.
- **`ranked-identity-eligibility` now has persistence.** The machine names `ranked-identities`, `identity-investigations` and `identity-events`, and all three are defined in `planning-schema.sql`. This was one of nineteen machines naming a table the DDL did not define; `validate_state_vocabularies.py` now fails when any declared persistence owner does not resolve, so the class of defect cannot return. The registry stores owners in kebab-case and the DDL declares them in snake_case, which is why a naive comparison had found nothing wrong.
- **`certification_state` in the platform profile registry.** `platform-profile-registry-v1.schema.json` pins it to the constant `planned-validation-required`, which is the machine's `planned` state under an older spelling. `platform_profiles.validation_state` and `CompatibilityProfile.validation_state` now use `planned`; the frozen constant, its 34 uses in `platform-profile-registry-v1.json` and its uses in `conformance/p1140e/platform-validation-plan-v1.json` remain to be renamed.
- **`evidence_assessments.public_state` has no API representation.** Its vocabulary is taken from `evidence-profile-policy-v1.json`; exposing evidence class in the public API is `PF-046`.

## Authentication and sessions

### OAuth transactions

An OAuth transaction binds transaction UUID, one preconfigured provider-capability record, immutable issuer, authorization endpoint, token endpoint, client identifier, exact redirect URI, state-verifier hash, encrypted PKCE verifier, intended action, initiating web session or native instance, optional enrollment public-key commitment, creation/expiry/consumption and a one-time browser-handoff secret hash. Callback-controlled values never select provider configuration, issuer, client configuration, redirect URI, or token endpoint.

For a provider whose capability record advertises RFC 9207 support, the callback requires `iss` equal to that stored immutable issuer. For a provider without RFC 9207 support, the stored transaction provider and unique provider-specific redirect path bind the callback instead. Every callback verifies the stored exact redirect, state, PKCE, transaction lifetime and one-time use before creating/linking provider identity or a session. Mutable usernames never identify the provider subject. Transaction consumption and session/provider binding are one database transaction.

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
- projection `building`/`validating`/`active` state and rebuild provenance;
- deletion tombstones reapplied after restore.

One accepted batch locks authenticated account/lineage, idempotency and challenge/checkpoint rows; inserts claims/appraisals/receipts/outbox; consumes the challenge; advances checkpoint; persists exact response; then commits.

## Ranking and pricing

A `ranking_view_id` is the SHA-256 identity of canonical scope type/ID, metric/version, period, evidence filter, agent/provider/model filters, board policy, ranking policy and projection schema. Scores, snapshots, cursors, movement, overtakes, moderation effects and rebuilds bind it.

A generation builds in isolation, validates totals/order/invariants, then atomically becomes active. Cursors carry view, generation and snapshot IDs. Corrections append ranking events; accepted claims never mutate.

Pricing interpretations are immutable server facts using the P-1140B schema. Event-time registered model alias resolution, dataset/rule digests, typed line items and unpriced reasons are persisted. The product always labels results Estimated.

## Social, boards, presence, and notifications

Friendship uses one canonical ordered pair. One pending request exists per pair; crossed requests become active deterministically. Blocking in one transaction removes friendship/rival state, invalidates invitations and pending notifications, revokes presence visibility and appends social events. Unblocking never restores old relationships.

Board ownership is the `board-membership` state `active-owner`, which the `board_one_active_owner` unique index enforces; `board_memberships.role` is constrained to agree with it and there is no competing owner field. Transfer locks the board and both memberships, requires recent auth, promotes the successor and demotes/removes the prior owner in one transaction. The last owner cannot leave. Policy versions apply prospectively unless a rebuild record explicitly targets prior periods. Organization, community and hacker-house metadata are typed specializations.

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

`packages/schemas/platform-profile-registry-v1.json` freezes exact candidate tuples as of 2026-07-24. Every row is `advertised=false` and sits in the `platform-certification` machine's initial state `planned` — still spelled `planned-validation-required` in that registry's frozen `certification_state` constant, as recorded under Open items. A profile becomes public only through the `platform-certification` machine after immutable results pass: `planned` → `candidate` → `exercised` → `certified` → `published`, with `blocked`, `degraded` and `suspended` as the withdrawal paths.

The registry includes macOS 26/15/14 on Apple silicon and compatible Intel; Windows 11 25H2 x64/ARM64; Windows Server 2025 x64; exact maintained Linux distribution/architecture/environment/package/init tuples; WSL2 Ubuntu 26.04; signed immutable OCI x64/arm64; and ephemeral CI x64/arm64. Windows Server ARM64 is not advertised without an applicable first-party release profile. Android, iOS, iPadOS and ChromeOS remain explicitly outside native scope.

Under PF-013 the shell owns process and connection state alone: `absent`, `headless`,
`starting`, `connected`, `daemon-unavailable`, `stale`, `exiting` and `crashed`. It
previously carried fifteen states covering six other subsystems — collection was
`paused`, connectivity was `offline` and `degraded`, authentication was
`auth-required`, updates were `update-required` and `update-blocked`, and permissions
were `permission-repair`. One state variable cannot hold six independent facts, so a
device whose collection was paused *and* whose network was offline had no representable
shell state and the transition table had to pretend one of the two had not happened.

Collection, sync, auth, permission and connectivity are now separate single-row
projections persisting in `packages/schemas/local-store-v1.sql`, not
`planning-schema.sql`: none of them is a fixed-schema aggregate accounting figure or an
integrity claim, and those are the only things `AGENTS.md` permits across the device
boundary. Update state was already its own machine, and so was the daemon.

Daemon, shell, collector and sync lifecycles are independent. `interactive-shell` is the authoritative registry machine for the menu-bar/tray process and its authenticated IPC relationship to the daemon. Closing or crashing shell never stops the OS-supervised daemon. Pausing collection or sync does not terminate the daemon. Crash loop, permission loss, key denial, disk exhaustion, sleep/reboot/login/logout, offline operation, update/rollback and uninstall are explicit failure cases.

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
