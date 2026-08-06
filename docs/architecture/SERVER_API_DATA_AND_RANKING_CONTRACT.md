# Server API, Data, and Ranking Contract

Status: normative planning contract
Version: 1

## Service shape

Begin as one modular Go deployment plus independently scalable workers:

- HTTP API and OAuth callbacks;
- claim ingestion and verification module;
- aggregation/outbox worker;
- presence/notification worker;
- administrative migration and recovery CLI.

Modules share versioned internal interfaces and PostgreSQL. Split services only for measured scaling or security isolation.

## Public API

Base path `/v1`. JSON is used for browser/ecosystem APIs; signed claims remain CBOR. All responses include `request_id`. Errors use `{code,message,retryable,details?}` with safe details only.

Core endpoints:

- `/auth/github/start|callback`, `/auth/x/start|callback`, `/auth/device/start|poll|exchange`;
- `/sessions`, `/sessions/{id}/revoke`;
- `/identities`, `/identities/link|unlink`;
- `/devices`, `/devices/enroll|rotate|revoke`;
- `/claim-challenges`, `/claims`, `/claim-batches`, `/claims/{id}`;
- `/leaderboards`, `/leaderboards/{scope}/{period}`, `/rank/me`;
- `/profiles/{handle}`, `/me`;
- `/friends`, `/friend-requests`, `/blocks`, `/rivals`;
- `/boards`, `/organizations`, `/communities`, `/countries`;
- `/presence`, `/notifications`;
- `/moderation/cases`, `/appeals`;
- `/exports`, `/deletion-requests`;
- `/pricing-datasets`, `/compatibility`.

Every state-changing endpoint defines idempotency semantics. Client-supplied idempotency keys are required for claim batches, device enrollment, board creation, invitations, exports, and deletion requests.

## Limits

- JSON request body: 1 MiB unless endpoint-specific lower limit.
- Claim batch: 1 MiB encoded, 500 claims.
- Pagination: cursor-based, default 50, max 200.
- Rate limits are per account, device, IP risk bucket, and endpoint class; responses include standard limit headers without revealing abuse thresholds.
- OAuth callbacks, login attempts, device polling, social requests, and expensive ranking filters have stricter adaptive limits.

## PostgreSQL logical schema

### Identity

`accounts`, `account_handles`, `linked_identities`, `web_sessions`, `recovery_codes`, `optional_authenticators`, `devices`, `device_keys`, `device_enrollment_grants`, `oauth_transactions`.

### Integrity

`claim_challenges`, `claims`, `claim_payloads`, `claim_rejections`, `device_sequences`, `claim_corrections`, `quarantines`, `evidence_assessments`, `moderation_cases`, `appeals`.

### Ranking

`seasons`, `periods`, `minute_scores`, `period_scores`, `ranking_views`, `ranking_projection_generations`, `ranking_entries`, `score_snapshots`, `score_contributions`, `ranking_corrections`, `ranking_movement_events`, `pricing_datasets`, `pricing_entries`, `cost_interpretations`.

### Erasure

`erasure_keys`, `erasure_domains`, `erasure_domain_links`, `erasure_records`, `erasure_restore_receipts`, `deletion_tombstones`.

### Social

`profiles`, `friend_edges`, `friend_requests`, `blocks`, `rival_edges`, `boards`, `board_memberships`, `board_invites`, `organizations`, `communities`, `presence_leases`, `notifications`, `notification_preferences`. There is no country table: country leaderboards remain post-launch under D-052 and the planning DDL is checked for their absence.

### Operations

`outbox_events`, `worker_checkpoints`, `audit_events`, `exports`, `deletion_jobs`, `schema_migrations`, `feature_flags`.

Primary identifiers are UUIDv7. External OAuth subjects use `(provider, provider_subject)` unique constraints. Usernames are case-folded and unique while preserving display case.

`minute_scores` is partitioned by minute, and `notifications` and `audit_events` by creation month. Those three are the retention-driven time series: each is append-only per key, none is the target of a foreign key, and each has a retention window in `packages/schemas/data-disposition-v1.json` that a partition drop enforces in constant time.

**`claims` is not partitioned, and the earlier statement that it was partitioned by receipt month was not executable.** PostgreSQL requires every unique constraint on a partitioned table to include the partition key. `claims` carries three uniqueness invariants the claim-acceptance transaction depends on — `claim_id`, `(device_id, device_sequence)` and `(device_id, payload_hash)` — and none of them can absorb a receipt timestamp without ceasing to be global, which is precisely the guarantee that makes a duplicate race increase a standing at most once. Six tables also carry a foreign key to `claim_id`, and a foreign key must reference a unique constraint. Partitioning by receipt month therefore costs either the replay invariant or six referential integrity constraints. At the recorded scale target neither purchase is worth making, and the honest statement is that claims are one table with the indexes below. `outbox_events` and `social_integrity_events` are unpartitioned for the same reason, in their case `unique (aggregate_id, aggregate_revision)`.

Every foreign key has an index on its referencing side. PostgreSQL indexes only the referenced side, so an unindexed referencing column turns a delete on the parent into a sequential scan of the child while holding a lock — which matters most on exactly the path this contract added, since an erasure deletes from `accounts` and thirty-one tables reference it. `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md` states the access path each index serves.

## Claim acceptance transaction

One serializable or explicitly locked transaction:

1. Lock device sequence row.
2. Validate account/device/key/challenge status.
3. Parse and verify canonical claim/signature.
4. Check challenge expiry/use, expected sequence, previous hash, claim ID, event fingerprint, lateness, adapter eligibility, accounting invariants, and privacy policy.
5. If exact previously accepted claim, return idempotent success.
6. Insert immutable claim and payload hash.
7. Update sequence/hash head and consume challenge.
8. Insert outbox event.
9. Commit.

Uniqueness constraints protect claim ID, `(device_id,sequence)`, challenge use, and scoped dedup fingerprint. A duplicate race can increase a standing at most once. Those three constraints are global and unpartitioned, which is the reason `claims` is one table.

Rejected claims are stored only with privacy-safe metadata, payload hash, reason code, and bounded diagnostics. Invalid raw payloads are not retained by default.

## Outbox and aggregation

Workers claim rows with `FOR UPDATE SKIP LOCKED`, process idempotently, and record deterministic output version. Aggregation applies additive deltas to the minute and period projections using unique source claim references, and records each delta in `score_contributions` so a period figure can be explained claim by claim. Corrections insert inverse and forward deltas; accepted claims are never mutated.

Rebuild truncates derived tables for a target scope/version and deterministically replays accepted claims plus corrections. Rebuild output is hash-compared before promotion. Worker crash at any point is safe to retry.

## Ranking

### The two quantities

Two figures, never merged, never both public. ADR-020 owns the function and D-082, D-144 and D-218 own the consequences.

- **Token Burn**, `token_burn_total`, is the accepted, immutable, unnormalized accounting quantity. D-004 and D-037 are untouched: it is still the raw ranking metric of record and it is still what every accounting rule is written against.
- **Credited Token Burn**, `credited_token_burn`, is `floor(token_burn_total × confidence_weight_hundredths / 100)`. It is the quantity `rank()` orders and the only burn figure a public surface publishes.

`score` is not a field name anywhere. `minute_scores.token_burn_total`, `period_scores.token_burn_total` and `period_scores.credited_token_burn` are the repaired columns; the three table names still contain the word, because `packages/schemas/state-machine-registry-v1.json` names them as persistence owners of the `ranking-projection` machine and that registry is owned by another track. On the wire the split is already expressed: `RankEntry` carries `credited_token_burn` and `SelfRankEntry` is the only shape carrying `token_burn_total`, `confidence_weight_hundredths` and both factors, under D-227.

### Generations

A ranking generation is built, validated, sealed, and then never modified. Sealing writes `content_hash`, `sealed_entry_count` and `sealed_total_credited_token_burn` and mints one `score_snapshots` row, which is the durable client-visible name for the generation.

`content_hash` is SHA-256 over the deterministic CBOR encoding of the entry rows in position order. It covers no handle, no account identifier and no appraisal detail, so a rename, a block, a visibility change and an erasure all leave it intact. A trust-state change under ADR-020 does not mutate a sealed generation; it builds a new one, marks the old `superseded`, and retains both.

The sealed aggregates are frozen and never recomputed. Republishing a recomputed count or total for one generation would let an observer difference two publications of the same thing and recover the exact figure of a participant who has since been erased.

### Entries

An entry names an `erasure_domain_id` — an opaque pseudonym, one per ranked-identity lineage — rather than an account. That is the change that makes an Article 17 erasure expressible without deleting a row or moving a position. The handle is resolved per entry at read time.

Each entry persists every ADR-020 input beside the result: `token_burn_total`, the awarded `evidence_profile_id` and `evidence_class`, `trust_state_at_projection`, `evidence_weight_hundredths`, `trust_weight_hundredths`, `confidence_weight_hundredths` and `credited_token_burn`. An entry is therefore recomputable from its own row, which is what the `validating` step checks and what makes an appeal about an arithmetic.

### Ordering

Canonical query partitions by scope, period, eligibility, evidence filter, and optional agent/model filter. Default ordering:

`rank() over (order by credited_token_burn desc)` with presentation tie-breakers `first_reached_at asc, erasure_domain_id asc`.

Equal credited figures share a rank and leave gaps. The tie-breakers order the display and never the rank.

### Cursors

A cursor anchors on `(ranking_view_id, generation, position)` and carries no subject identifier. It is the deterministic CBOR encoding of that triple plus the page size and an issue time, MAC'd under a server key. It does not contain an account identifier, a handle or a figure; the previous form did, which put personal data into a token the client keeps indefinitely.

D-222 already makes the cursor opaque, server-issued, and bound to the `snapshot_id` and principal it was issued against. This states what is inside it. A snapshot names exactly one sealed generation, so binding to a snapshot and anchoring on a generation are the same binding said twice.

Positions inside a sealed generation are immutable, which gives every case an answer:

- **The anchor entry was erased.** The next page starts immediately after that position, the erased entry is absent, and every surviving entry sits at the position it always had. No restart, no renumbering, no error. The anchor is a number and the number is still there.
- **The generation was superseded while the cursor was held.** The cursor reads the generation it names, which is retained. The response reports the generation served and the current active generation. It does not silently jump, because a jump would show one page composed of two rank orders.
- **The ranking view was retired and its generations purged.** Restart outcome. This is the only case that produces one.
- **The filter or scope changed.** `ranking_view_id` is a digest over the full rule set, so a different filter is a different view and its cursors are not interchangeable. Restart outcome.
- **Viewer authorization changed.** The page is re-projected under current authorization on every request, so entries can disappear from a friends or board page between two requests holding one cursor. Positions still do not move.

`snapshot_id` is unaffected by an erasure. A client that pinned one keeps reading the same generation, the same content hash and the same positions, with one fewer rendered item.

### Suppression and current authorization

An entry renders only while its domain's key is alive. An erased entry contributes no item, no handle, no figure and no placeholder, because a retained figure at a retained position joins trivially against a third party's archived copy of the board, and a visible "erased" marker publishes the fact of the erasure against a position that archive already names.

A page can therefore return fewer items than requested while more remain, and pagination continues from the position anchor rather than from an item count. `LeaderboardPage` needs a position-range field to let a client tell a short page from the end of the board; `packages/schemas/openapi-v1.yaml` is owned by another work unit and does not carry it, so the API under-describes this projection today.

Quarantined and private accounts are omitted by the same read-time projection rather than by recomputation. Current-user rank is read from the same generation as the visible page. Evidence profiles never alter Token Burn, and they determine the confidence weight applied to Credited Token Burn at projection — which is a ranking effect that occurs without any board filtering eligibility.

`docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` is the normative owner of the erasure mechanism, its key material, its proof of destruction, its backup and restore behaviour, and its stated limits.

## Cache

PostgreSQL is authoritative. Redis-compatible storage may cache leaderboard pages, presence leases, and rate-limit state. Cache keys include complete filter and generation. Outbox events invalidate affected scopes. Stale-while-revalidate may serve up to 60 seconds with a visible update timestamp; correctness-sensitive personal actions bypass cache.

## Presence

Presence is a signed/authorized renewable lease, not a permanent state. The daemon sends safe activity state at most every 30 seconds. Lease expires after 90 seconds without renewal. Server stores account/device, coarse agent enum, evidence state, start bucket, and privacy status—never project or transcript details.

## Deletion and retention

Account deletion creates a durable job, immediately hides public surfaces and revokes sessions and devices. After the cooling-off window, live personal records — identity, session, device, social, presence, notification, claim and live projection rows — are deleted outright.

**Public aggregate removal does not trigger a rebuild.** A sealed generation is retained unchanged and its entry becomes unattributable when the erasure destroys the domain key. `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` states the mechanism and `packages/schemas/data-disposition-v1.json` states, for every one of the persistence owners in `packages/schemas/planning-schema.sql`, its classification, its retention window, what an erasure does to it, whether it is inside the backup set, and which worker enforces the window. Every table carrying an `expires_at` column names the actor that acts when the timestamp passes.

A generation carrying an erasure is no longer rebuildable from source claims, because the erasure deleted them. A rebuild spanning it carries the erased entries forward verbatim from the sealed rows, so the hash comparison still covers the full row set and determinism survives while derivability does not.

Security audit records retain minimal pseudonymous data for the window in the disposition registry.

## Migrations

Expand/contract migrations, backward-compatible deployments, version gates, online index creation, tested rollback, and preproduction restore drills are mandatory. Destructive migrations require a verified backup and explicit data-lifecycle approval.

Every index in `packages/schemas/planning-schema.sql` is created `CONCURRENTLY` in the migration that introduces it, outside a transaction. That is one of the reasons D-097 selected `goose`: its no-transaction directive is what makes online index creation expressible in a migration file at all. The planning contract states the target shape; the migration text is a separate artifact.

A restore is not complete when the cluster is up. It is complete when the erasure journal has been replayed and an `erasure_restore_receipts` row records it, and the receipt cannot record traffic admitted before the replay finished. **No restore drill has been run and nothing is provisioned.**

## Observability

Allowlisted dimensions only: route template, status class, latency, bytes, reason code, worker type, queue age, database operation class, adapter ID/version, and evidence state. No payloads, handles, OAuth tokens, claim bytes, model free text, paths, or transcript-derived fields.

## Required tests

Contract tests, authorization matrix, property tests, SQL constraint/race tests, duplicate storms, outbox crash points, rebuild equivalence, period rollover, late claims, corrections, pagination stability, cache invalidation, OAuth replay, deletion rebuild, backup/restore, load/soak, and privacy canaries.
