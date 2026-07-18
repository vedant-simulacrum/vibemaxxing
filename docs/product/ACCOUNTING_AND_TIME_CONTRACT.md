# Accounting, Pricing, and Time Contract

Status: normative planning contract
Version: 1

## Token Burn

`token_burn_total = input + output + cache_read + cache_write + reasoning + multimodal_input + multimodal_output`.

Each category is stored independently as a non-negative integer. Unknown categories are `null`, never zero. Totals are accepted only when the adapter identifies whether a source total already includes subcategories; reconciliation prevents double addition.

Tool calls are not a separate token category. Tokens consumed by tool definitions, arguments, results, context, compaction, summaries, retries, and subagents are counted in the provider-reported categories that incurred them.

### Rules

- Count genuine provider/local-model inference even when intentionally wasteful.
- Count successful and failed requests when the model actually consumed tokens.
- Do not count locally estimated tokens in global competition unless the adapter tier permits estimates and marks `count_quality=estimated`.
- Provider-reported usage outranks tokenizer reconstruction; tokenizer reconstruction outranks byte/character estimates.
- A retry is a distinct request when it caused a distinct model execution.
- Provider-internal retries count only once unless separately billed/reported.
- Streaming counts the final authoritative usage report. If absent, the adapter may reconstruct from emitted content only at a lower evidence tier.
- Aborted requests count known consumed tokens; unknown remainder remains null.
- Cache read/write categories count when explicitly reported. They remain part of Token Burn because they represent model-context processing, while UI breakdowns expose them separately.
- Reasoning tokens count when reported; hidden reasoning is never inferred from transcript content.
- Images, audio, and video use provider-reported token-equivalent units and retain modality fields.
- Subagent usage is attributed to the initiating user and source device, with parent/child IDs. Parent totals that already include child usage must not be added to child totals.
- Compaction and summarization calls count as normal model calls.
- Host/guest, IDE/CLI, proxy/provider, and orchestrator/subagent duplication is resolved through source-authority rules and stable request fingerprints.

## Comparability

Raw tokens are the default competitive unit. The system does not claim equal computational value across models. Every leaderboard supports model, provider, agent, evidence-tier, and local/hosted filters. UI states that raw tokens are a usage-volume comparison, not a capability-normalized benchmark.

No hidden normalization multiplier may change competitive totals. Future normalized views require a new versioned metric and never rewrite Token Burn.

## Estimated Cash Burn

Estimated Cash Burn is computed from immutable usage facts and a versioned pricing dataset:

`estimated_cost = sum(category_units * effective_unit_price)`.

Rules:

- Label every value `Estimated`.
- Store pricing dataset ID, effective date, currency, provider, model alias, region, and category prices.
- Use the price effective at event time; later price changes do not rewrite historical estimates.
- Corrections create a new interpretation record and visible correction reason.
- Subscription plans, free tiers, credits, negotiated enterprise rates, and bundled usage do not alter the API-equivalent estimate.
- Batch, cache, priority, regional, and modality pricing are represented when known.
- Unknown model/price produces `unpriced`, never zero.
- Local models show token usage and `Local compute`; dollar estimates remain absent until an approved local-compute methodology exists.
- FX conversion is display-only, timestamped, and does not alter the canonical pricing-currency estimate.
- Taxes and user-specific billing adjustments are excluded.

## Time and ranking periods

Canonical event time is server-receipt time plus bounded source time metadata. The server owns period assignment.

- Daily: UTC calendar day.
- Weekly: Monday 00:00 UTC through next Monday.
- Monthly: UTC calendar month.
- Yearly: UTC calendar year.
- Lifetime: all accepted competitive claims.
- Seasons: explicit immutable UTC start/end timestamps and versioned rules.

Local-time views may be offered as private analytics but do not change global competitive periods.

### Late and offline events

- Claims must include source event time, local monotonic sequence, challenge context, and receipt time.
- Standard claims may arrive up to 24 hours late; Hardened continuity may use a stricter adapter/platform limit.
- Claims outside the accepted lateness window remain private analytics and are excluded from active rankings.
- Period results remain provisional through the lateness window, then finalize.
- Appeals and verified server corrections can modify finalized results through explicit correction records and audit events.

### Ties, ranks, streaks

- Competition uses SQL `rank()` semantics: equal score shares rank and leaves gaps.
- Stable secondary ordering is `score DESC, first_reached_score_at ASC, user_id ASC`; it affects display order, not rank.
- An overtake requires strictly greater score, not display-order movement within a tie.
- Rank movement compares finalized snapshots at the same scope/period/filter.
- Streaks require at least one accepted competitive claim per UTC day.
- Deleted or disqualified scores trigger deterministic recomputation.

## Accounting event invariants

Every normalized request includes: adapter ID/version, source version, event ID, session ID, optional parent event ID, model/provider identifiers, start/end times, token categories, total quality, source authority, evidence inputs, and privacy classification.

All integer additions use checked arithmetic. Negative, overflowed, internally inconsistent, or duplicate usage is rejected or quarantined with a stable reason code.

## Required tests

Golden fixtures cover every category, unknown fields, nested agents, retries, failed/aborted streams, cache semantics, multimodal usage, totals that include children, conflicting sources, late events, season boundaries, pricing changes, unpriced models, and correction rebuilds.
