# Leaderboard Storage and Ranking

## Write path

1. Validate schema and size.
2. Verify signature and device state.
3. Enforce sequence, challenge, replay, and idempotency rules.
4. Insert accepted claim into append-only ledger.
5. Insert outbox event in the same PostgreSQL transaction.
6. Commit once.

## Aggregate path

An idempotent worker consumes outbox rows and applies deltas to:

- `usage_minute_user`
- `usage_period_user`
- `leaderboard_score_current`
- `rank_event`

Worker checkpoints and aggregate mutations occur transactionally. Reprocessing the same event must produce no additional score.

## Ranking semantics

Every ranking query must specify:

- Scope.
- Period.
- Metric.
- Deterministic tie rule.
- Stable pagination order.

Recommended ordering:

1. Score descending.
2. Time reaching score ascending only if product explicitly chooses first-to-score tie breaking; otherwise peers share rank.
3. Stable user identifier as pagination-only final ordering, never as hidden competitive advantage.

Use `rank()` or `dense_rank()` deliberately and test peer behavior. Do not let incidental SQL ordering define product semantics.

## Materialized views

Materialized views may serve historical analytics and slow-changing summaries. They are not the primary mechanism for minute-fresh active rankings because PostgreSQL core refreshes the view rather than maintaining arbitrary views incrementally.

## Required benchmarks

- Top 100 global.
- Current-user rank outside top 100.
- Friends and private-board ranks.
- Tie-heavy data.
- Period rollover.
- Concurrent ingestion and reads.
- Correction/recomputation.
- 10x forecast launch traffic.
