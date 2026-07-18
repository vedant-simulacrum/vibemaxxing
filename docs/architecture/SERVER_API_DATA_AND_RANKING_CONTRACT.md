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

`periods`, `minute_scores`, `period_scores`, `score_snapshots`, `ranking_corrections`, `pricing_datasets`, `pricing_entries`, `cost_interpretations`.

### Social

`profiles`, `friend_edges`, `friend_requests`, `blocks`, `rival_edges`, `boards`, `board_memberships`, `board_invites`, `organizations`, `communities`, `country_assertions`, `presence_leases`, `notifications`, `notification_preferences`.

### Operations

`outbox_events`, `worker_checkpoints`, `audit_events`, `exports`, `deletion_jobs`, `schema_migrations`, `feature_flags`.

Primary identifiers are UUIDv7. External OAuth subjects use `(provider, provider_subject)` unique constraints. Usernames are case-folded and unique while preserving display case. Claims are partitioned by receipt month; period scores by period type/start where volume justifies it.

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

Uniqueness constraints protect claim ID, `(device_id,sequence)`, challenge use, and scoped dedup fingerprint. A duplicate race can increase score at most once.

Rejected claims are stored only with privacy-safe metadata, payload hash, reason code, and bounded diagnostics. Invalid raw payloads are not retained by default.

## Outbox and aggregation

Workers claim rows with `FOR UPDATE SKIP LOCKED`, process idempotently, and record deterministic output version. Aggregation applies additive deltas to minute and period score tables using unique source claim references. Corrections insert inverse/forward deltas; accepted claims are never mutated.

Rebuild truncates derived tables for a target scope/version and deterministically replays accepted claims plus corrections. Rebuild output is hash-compared before promotion. Worker crash at any point is safe to retry.

## Ranking

Canonical query partitions by scope, period, eligibility, evidence filter, and optional agent/model filter. Score is `sum(token_burn_total)` or a separately selected estimated-cost interpretation. Default ordering:

`rank() over (order by score desc)` with presentation tie-breakers `first_reached_score_at asc, account_id asc`.

Cursor contains filter/version, score, first-reached timestamp, account ID, and snapshot generation. A cursor is invalid after incompatible filter or snapshot change and returns a restart code.

Current-user rank is fetched from the same snapshot/version as the visible page. Quarantined or private accounts are omitted according to policy; their removal causes deterministic recomputation. Evidence badges never alter raw score unless the selected leaderboard explicitly filters eligibility.

## Cache

PostgreSQL is authoritative. Redis-compatible storage may cache leaderboard pages, presence leases, and rate-limit state. Cache keys include complete filter and generation. Outbox events invalidate affected scopes. Stale-while-revalidate may serve up to 60 seconds with a visible update timestamp; correctness-sensitive personal actions bypass cache.

## Presence

Presence is a signed/authorized renewable lease, not a permanent state. The daemon sends safe activity state at most every 30 seconds. Lease expires after 90 seconds without renewal. Server stores account/device, coarse agent enum, evidence state, start bucket, and privacy status—never project or transcript details.

## Deletion and retention

Account deletion creates a durable job, immediately hides public surfaces and revokes sessions/devices. After cooling-off, personal identity/social records and claims are deleted or irreversibly anonymized according to legal requirements. Public aggregate removal triggers rebuild. Security audit records retain only minimal pseudonymous data for a documented bounded period.

## Migrations

Expand/contract migrations, backward-compatible deployments, version gates, online index creation, tested rollback, and preproduction restore drills are mandatory. Destructive migrations require a verified backup and explicit data-lifecycle approval.

## Observability

Allowlisted dimensions only: route template, status class, latency, bytes, reason code, worker type, queue age, database operation class, adapter ID/version, and evidence state. No payloads, handles, OAuth tokens, claim bytes, model free text, paths, or transcript-derived fields.

## Required tests

Contract tests, authorization matrix, property tests, SQL constraint/race tests, duplicate storms, outbox crash points, rebuild equivalence, period rollover, late claims, corrections, pagination stability, cache invalidation, OAuth replay, deletion rebuild, backup/restore, load/soak, and privacy canaries.
