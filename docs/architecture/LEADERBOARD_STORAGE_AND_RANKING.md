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

## The definition and the audience are two things

A ranking view is a pair. `ranking_definitions` holds what is ranked — the metric and its version, the period, the five filter dimensions, the tie rule, the display order and the digests of every input that decides an ordering. `ranking_views` holds who may read it — the scope, the board, and the visibility default — and points at one definition. `ranking_view_id` is the digest over `ranking_definition_id` and `audience_id` and over nothing else, so two audiences of one ranking share a definition identifier, differ in view identifier, and cannot land in one sealed generation. `packages/schemas/ranking-view-v1.schema.json` is the machine form and `validate_ranking_view_separation` recomputes all three digests.

Two consequences are constraints rather than conventions.

`check ((scope = 'global') = (default_visibility = 'universally-public'))` on `ranking_views` puts AGENTS.md's rule that only the global leaderboard is universally public where the row is written. It had lived only where a page is rendered, and the write path admitted a friends view that called itself public. `GET /leaderboards/{scope}/{period}` was the same defect on the API: it carried `security: []` while its `scope` segment admitted `global`, `friends`, `rivals` and `board`, so an unauthenticated caller reached a cohort or private-board standing by naming it in the path, and the `board` value named no board at all. The global board now has its own unauthenticated path, the cohort scopes require a session, and a board standing is addressed by board.

The viewer is not in either table. A viewer belongs to a request, and the authorization inputs a request is evaluated under are `packages/schemas/projection-authorization-v1.json`, re-read at every display rather than replayed from what was sealed.

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

Every index in `packages/schemas/planning-schema.sql` is either the referencing side of a foreign key or one of the paths below. PostgreSQL indexes the referenced side of a foreign key and never the referencing side, so an unindexed referencing column turns a delete on the parent into a sequential scan of the child while holding a lock. Thirty-one tables reference `accounts`, which the erasure path deletes from.

| Query | Access path | Index |
|---|---|---|
| Leaderboard page, any scope and period | Range scan on a sealed generation from a position anchor | `ranking_entries` primary key `(ranking_view_id, generation, position)` — no separate index exists or is needed, and that is exactly why the cursor anchors on position |
| Suppression of an erased entry | Join to the domain, then to the key, testing `destroyed_at is null` | `erasure_domains` primary key, `erasure_keys_live_idx` |
| `/rank/me` | Account to domain by keyed digest, then domain to entry | `erasure_domains.subject_lookup_digest` unique, `ranking_entries` unique `(ranking_view_id, generation, erasure_domain_id)` |
| A participant's own explanation of a period figure | Contributions for one domain in one period | `score_contributions_period_domain_idx` |
| Erasure of a participant's contributions | Every contribution for one domain, across every period | `score_contributions_domain_idx`. The period-leading index above cannot serve it, and this is the path that runs while the erasure key is being destroyed |
| Friends board membership, both directions | Canonical pair plus its reverse | `friend_edges` primary key `(account_id_a, account_id_b)` and `friend_edges_reverse_idx` |
| Directional block check at display | Blocker to blocked and blocked to blocker | `blocks` primary key and `blocks_reverse_idx` |
| Board leaderboard membership | Board to member, and member to board | `board_memberships` primary key and `board_memberships_account_idx` |
| Notification inbox | Newest first for one account | `notifications_account_created_idx` |
| Outbox drain | Unprocessed rows oldest first | `outbox_events_unprocessed_idx`, partial on `processed_at is null` so the index holds only the backlog |
| Claim history for one account | Newest first | `claims_account_received_idx` |
| Replay and continuity checks | Exact sequence and exact fingerprint, both scoped to the lineage rather than the device row | `claims` unique `(lineage_id, device_sequence)` and `(lineage_id, payload_hash)`. D-592 and PF-010 moved both off `device_id`; this row named the old columns until PF-048 |
| Expiry sweeps | One index per `expires_at`, partial where a consumed or settled row is dead | `claim_challenges_expiry_idx`, `presence_leases_expiry_idx`, `idempotency_records_expiry_idx`, `board_invites_expiry_idx`, `exports_expiry_idx`, `oauth_transactions_expiry_idx`, `device_enrollment_grants_expiry_idx`, `local_deletion_commands_expiry_idx`, `invite_codes_expiry_idx`, `recovery_cases_expiry_idx`, `identity_investigations_expiry_idx`, `consolidation_cases_expiry_idx` |
| Idempotency row retention, which is a second sweep on a later date | Rows past `retain_until`, whose response bytes went at `expires_at` days earlier | `idempotency_records_retention_idx`. The two dates bound different things and one index over `expires_at` could drive only the first |
| Erasure enumeration across consolidated identities | Both directions of the domain link | `erasure_domain_links` primary key and `erasure_domain_links_absorbed_idx` |
| Season and period boundary lookup | Window containment | `seasons_window_idx`, `periods_type_window_idx` |
| Latest sealed generation for a view | Descending scan on the generation | `score_snapshots_view_generation_idx` on `(ranking_view_id, generation desc)`. The `unique (ranking_view_id, generation)` constraint indexes the same columns ascending, and a backward scan of it orders both columns descending, which is not this order |
| The one active generation of a view | Equality on the view, over live rows only | `ranking_projection_generations_active_idx`, unique and partial on `state = 'active'`. It is the promotion invariant rather than a lookup: the machine calls its transition `atomic-promote` and, until this index existed, two workers could each promote and leave two rows in `active` |
| Which sealed generation produced a live period figure | The view and the generation the projection names | `period_scores_generation_idx`. The primary key leads with `ranking_view_id` and continues with `period_id`, so it cannot serve this; the column pointed at nothing at all until PF-022 gave it a foreign key |
| One participant's moderation and appeal history | Account to case, account to appeal | `moderation_cases_account_idx`, `appeals_account_idx`. Neither column is a foreign key: both records survive the account's erasure unlinked |
| One participant's deletion job | Account to job | `deletion_jobs_account_idx`. Not a foreign key either — the job is the proof the deletion happened and cannot reference what it deleted |
| Per-device deletion fan-out and acknowledgement | Job to commands is the unique pair; device to commands and device to receipts are the reverse | `local_deletion_commands_device_idx`, `local_deletion_receipts_device_idx` |
| Boards and spaces one account owns | Owner to organization, owner to community | `organizations_owner_idx`, `communities_owner_idx`. Both outlive the owner's erasure and neither is a foreign key |
| Codes one account issued | Issuer to code | `invite_codes_issuer_idx`. An issued code outlives the issuer's erasure |
| Session revocation across a token family | Family to its sessions | `web_sessions_family_idx` |
| Social integrity events attributed to one actor | Actor to event | `social_integrity_events_actor_idx`. The event outlives the actor, so the column carries no foreign key |
| Applying or reversing one correction across views | Correction to its per-view rows | `ranking_corrections_correction_idx` |
| Rebuilding one participant's period figure from its corrections | The view, then the period, then the participant | `ranking_corrections_view_idx`. This is the path the rebuild equivalence in `conformance/planning/ranking-correction-vectors-v1.json` reads. It did not exist and could not have: until PF-023 the table named no period and no participant, so the row above was the only path and it answers "which views did correction C touch" rather than "what happened to this person in this period" |
| The active certification for a tuple shape | Exact tuple, live rows only | `source_certifications_active_idx`, unique and partial on `state = 'active'`, so two rows can never make "the exact certified tuple" ambiguous |
| The live provider binding for a subject | Provider and subject, live states only | `linked_identities_live_subject_idx`, unique and partial, which is the one-live-binding rule rather than a lookup |

Every table with an `expires_at` column names the actor that acts on it in `packages/schemas/data-disposition-v1.json`. An expiry with no actor is a comment.

Two rules govern this table and they are checked, by `validate_index_coverage` in `scripts/repository/validate_planning_artifacts.py`, in both directions. Every foreign key in `packages/schemas/planning-schema.sql` has a *total* index, primary key or unique constraint whose leading columns are its referencing columns — partial indexes do not count, because PostgreSQL's referential check on a parent delete has to see the rows the predicate excludes. And every index that supports no foreign key appears above, naming the query it serves; an index named by no query cannot be shown to be wrong and cannot be dropped by anyone who did not write it.

Eighteen foreign keys had no index when that rule was first written down here, including all five on `oauth_transactions` and `score_contributions.erasure_domain_id`, which is on the erasure path this section exists for. What made them invisible is that the only stated figure was a count — and a count rises when a redundant index is added and falls when a wrong one is removed. There was a redundant one too: a second index over `(aggregate_id, aggregate_revision)` on `social_integrity_events` duplicated that table's own unique constraint column for column, and removing it lowered the count while improving the schema.

## Partitioning

Partitioned, by range, with a default partition and a monthly rotation:

- `minute_scores` on `minute_start`;
- `notifications` on `created_at`;
- `audit_events` on `created_at`.

All three qualify on the same three grounds: the retention window in the disposition registry is enforced by dropping a partition rather than by deleting rows, no foreign key points at them, and their only uniqueness is their own identity, so the partition key can join the primary key without weakening an invariant.

**Not partitioned, and the reason is a constraint rather than a preference.**

- **`claims`.** PostgreSQL requires every unique constraint on a partitioned table to include the partition key. `claims` holds three global uniqueness invariants — `claim_id`, `(lineage_id, device_sequence)` and `(lineage_id, payload_hash)` — and the acceptance transaction depends on all three being global; partitioning by receipt month would make each of them per-month, which is not the guarantee. Six tables also carry a foreign key to `claim_id`, and a foreign key must reference a unique constraint. An earlier revision of the server contract asserted partitioning by receipt month; it was not executable and has been corrected rather than worked around.
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
