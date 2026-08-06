# Leaderboard Storage and Ranking

Status: normative planning contract
Decisions: D-018, D-082, D-211, D-212, D-215, D-218

`docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` owns the API and data model. This file owns the physical access paths: which query each index serves, what is partitioned and what is not, and how an index reaches production without locking a table.

## Write path

1. Validate schema and size.
2. Verify signature and device state.
3. Enforce sequence, challenge, replay, and idempotency rules.
4. Insert accepted claim into append-only ledger.
5. Insert outbox event in the same PostgreSQL transaction.
6. Commit once.

## Aggregate path

An idempotent worker consumes outbox rows and applies deltas to:

- `minute_scores`
- `period_scores`
- `score_contributions`
- `ranking_movement_events`

Worker checkpoints and aggregate mutations occur transactionally. Reprocessing the same event produces no additional burn.

## Ranking semantics

Every ranking query specifies scope, period, metric, deterministic tie rule and stable pagination order.

Ordering:

1. `credited_token_burn` descending. This is the credited figure, not the raw one. D-082 and ADR-020 make the confidence weight the difference between them, and D-144 keeps the raw figure off public surfaces so the weight cannot be recovered by division.
2. `first_reached_at` ascending, then `erasure_domain_id` ascending. Both order the display and neither orders the rank.

`rank()` is used rather than `dense_rank()`: equal credited figures share a rank and the following ranks have gaps. That is competition rank and it is a product decision under D-018, not an incidental SQL choice.

An erased entry is omitted from the rendered page and keeps its position in the sealed generation, so a page can be shorter than the limit while more entries remain.

## Materialized views

Materialized views may serve historical analytics and slow-changing summaries. They are not the primary mechanism for minute-fresh active rankings, because PostgreSQL core refreshes the whole view rather than maintaining an arbitrary view incrementally. Sealed generations serve that need instead: a generation is written once and read many times, which is the same benefit without the refresh.

## Access paths and the index each needs

Every index in `packages/schemas/planning-schema.sql` is either the referencing side of a foreign key or one of the paths below. PostgreSQL indexes the referenced side of a foreign key and never the referencing side, so an unindexed referencing column turns a delete on the parent into a sequential scan of the child while holding a lock. Ninety-eight tables carried four indexes before this contract, and thirty-one of them reference `accounts`, which the erasure path deletes from.

| Query | Access path | Index |
|---|---|---|
| Leaderboard page, any scope and period | Range scan on a sealed generation from a position anchor | `ranking_entries` primary key `(ranking_view_id, generation, position)` — no separate index exists or is needed, and that is exactly why the cursor anchors on position |
| Suppression of an erased entry | Join to the domain, then to the key, testing `destroyed_at is null` | `erasure_domains` primary key, `erasure_keys_live_idx` |
| `/rank/me` | Account to domain by keyed digest, then domain to entry | `erasure_domains.subject_lookup_digest` unique, `ranking_entries` unique `(ranking_view_id, generation, erasure_domain_id)` |
| A participant's own explanation of a period figure | Contributions for one domain in one period | `score_contributions_period_domain_idx` |
| Friends board membership, both directions | Canonical pair plus its reverse | `friend_edges` primary key `(account_id_a, account_id_b)` and `friend_edges_reverse_idx` |
| Directional block check at display | Blocker to blocked and blocked to blocker | `blocks` primary key and `blocks_reverse_idx` |
| Board leaderboard membership | Board to member, and member to board | `board_memberships` primary key and `board_memberships_account_idx` |
| Notification inbox | Newest first for one account | `notifications_account_created_idx` |
| Outbox drain | Unprocessed rows oldest first | `outbox_events_unprocessed_idx`, partial on `processed_at is null` so the index holds only the backlog |
| Claim history for one account | Newest first | `claims_account_received_idx` |
| Replay and continuity checks | Exact sequence and exact fingerprint | `claims` unique `(device_id, device_sequence)` and `(device_id, payload_hash)` |
| Expiry sweeps | One index per `expires_at`, partial where a consumed row is dead | `claim_challenges_expiry_idx`, `presence_leases_expiry_idx`, `idempotency_records_expiry_idx`, `board_invites_expiry_idx`, `exports_expiry_idx`, `oauth_transactions_expiry_idx`, `device_enrollment_grants_expiry_idx`, `local_deletion_commands_expiry_idx` |
| Erasure enumeration across consolidated identities | Both directions of the domain link | `erasure_domain_links` primary key and `erasure_domain_links_absorbed_idx` |
| Season and period boundary lookup | Window containment | `seasons_window_idx`, `periods_type_window_idx` |

Every table with an `expires_at` column names the actor that acts on it in `packages/schemas/data-disposition-v1.json`. An expiry with no actor is a comment.

## Partitioning

Partitioned, by range, with a default partition and a monthly rotation:

- `minute_scores` on `minute_start`;
- `notifications` on `created_at`;
- `audit_events` on `created_at`.

All three qualify on the same three grounds: the retention window in the disposition registry is enforced by dropping a partition rather than by deleting rows, no foreign key points at them, and their only uniqueness is their own identity, so the partition key can join the primary key without weakening an invariant.

**Not partitioned, and the reason is a constraint rather than a preference.**

- **`claims`.** PostgreSQL requires every unique constraint on a partitioned table to include the partition key. `claims` holds three global uniqueness invariants — `claim_id`, `(device_id, device_sequence)` and `(device_id, payload_hash)` — and the acceptance transaction depends on all three being global; partitioning by receipt month would make each of them per-month, which is not the guarantee. Six tables also carry a foreign key to `claim_id`, and a foreign key must reference a unique constraint. An earlier revision of the server contract asserted partitioning by receipt month; it was not executable and has been corrected rather than worked around.
- **`outbox_events` and `social_integrity_events`.** `unique (aggregate_id, aggregate_revision)` is what makes processing exactly-once. A partition key cannot join it without weakening that.
- **`period_scores`.** Its size is participants times periods times views, not time times participants, so a monthly partition would produce many small partitions and buy nothing.

## Online index creation

Every index is created `CONCURRENTLY`, outside a transaction, in the migration that introduces it. `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block, which is why D-097 required a migration tool with a no-transaction directive and is one of the reasons `goose` was chosen over the alternatives.

A concurrent build can fail and leave an invalid index behind. The migration that creates one also states the drop-and-retry it needs, and a deployment check that finds an invalid index treats it as a failed migration rather than as a slow query.

Adding a range partition to a table that already has a default partition scans the default to prove no row belongs in the new bound, and takes a lock while it does. Partitions are therefore created ahead of the window they cover, not at the moment rows start arriving in it.

## Required benchmarks

- Top 100 global.
- Current-user rank outside top 100.
- Friends and private-board ranks.
- Tie-heavy data.
- Period rollover.
- Concurrent ingestion and reads.
- Correction and recomputation.
- Pagination across a generation containing erased entries, holding one cursor from first page to last.
- Erasure of a participant appearing in many sealed generations, measuring the cost of the key destruction and of the live-row deletes across every table referencing `accounts`.
- 10x forecast launch traffic.

None of these has been run. No index has been built against data, no plan has been read, and no latency figure in this repository is measured.
