# Accounting, Pricing, and Time Contract

Status: normative planning contract
Version: 1
Updated: 2026-07-19

## Token Burn

`token_burn_total = input + output + cache_read + cache_write + reasoning + multimodal_input + multimodal_output`.

Each category is stored independently as a non-negative integer. Unknown categories are `null`, never zero. Totals are accepted only when the accounting profile identifies whether a source total already includes subcategories; reconciliation prevents double addition.

Tool calls are not a separate token category. Tokens consumed by tool definitions, arguments, results, context, compaction, summaries, retries and subagents are counted in the provider-reported categories that incurred them.

### Rules

- Count genuine provider/local-model inference even when intentionally wasteful.
- Count successful and failed requests when the model actually consumed tokens.
- Locally estimated tokens enter global competition only when the exact adapter/accounting profile permits estimates, marks `count_quality=estimated` and the active ranking policy admits that quality.
- Provider-reported usage outranks deterministic tokenizer reconstruction; tokenizer reconstruction outranks byte/character estimates. This is accounting authority, not proof of provider origin.
- A retry is a distinct request when it caused a distinct model execution.
- Provider-internal retries count only once unless separately billed/reported.
- Streaming counts the final authoritative usage report. If absent, an adapter may reconstruct only under a lower accounting authority and evidence profile.
- Aborted requests count known consumed tokens; unknown remainder remains null.
- Cache read/write categories count when explicitly reported and remain visible separately.
- Reasoning tokens count when reported; hidden reasoning is never inferred from transcript content.
- Images, audio and video use provider-reported token-equivalent units and retain modality fields.
- Subagent usage is attributed to the initiating user and source device, with parent/child IDs. Parent totals that already include child usage are not added to child totals.
- Compaction and summarization calls count as normal model calls.

## Versioned accounting profiles

Every competitive normalized event references an exact accounting profile version. A profile binds:

- provider and API surface;
- exact model/version or documented alias scope;
- source field names and category meanings;
- whether totals include cache, reasoning, modalities, children or provider overhead;
- streaming finalization and missing-final-usage behavior;
- retry, cancellation, batch and partial-failure semantics;
- parent/child inclusion rules;
- count-quality and evidence ceilings;
- pricing dataset compatibility;
- unknown or changed provider-field behavior.

Unknown API revisions or category semantics fail closed for Hardened and downgrade only to an exercised Standard profile. OpenTelemetry or generic telemetry is an ingestion transport, not a canonical accounting authority; its semantic-convention version and provider mapping are recorded.

## Deterministic request identity and reconciliation

Each observation has a `duplicate_domain`, authority class and one or more identity components. Reconciliation uses this order:

1. provider-issued request/execution ID only when issuer, namespace, stability and reuse semantics are established by the accounting profile;
2. official runtime execution ID under an exercised source-version contract;
3. versioned keyed local fingerprint over allowlisted non-content structural fields;
4. no merge when identity confidence is insufficient.

A fingerprint profile specifies exact fields, canonical encoding, keyed hash algorithm, key scope, temporal/session window and collision behavior. It never contains prompt, response, code, path, repository, filename or tool-body content.

Observations are merged only when they belong to the same duplicate domain and compatible identity profile. Cross-domain relationships—host/guest, IDE/CLI, proxy/provider and orchestrator/subagent—use explicit edges rather than global fuzzy matching.

If compatible observations disagree:

- a higher accounting authority may supersede the contributing interpretation through an explicit reconciliation record;
- equal-authority conflicts quarantine;
- lower-authority records never add on top of an inclusive higher-authority total;
- a collision or ambiguous identity never silently merges two executions;
- immutable source observations remain stored; competitive aggregates consume the current accepted interpretation only.

Late higher-authority evidence creates a correction event with old interpretation ID, new interpretation ID, reason, effective periods and deterministic aggregate rebuild. It does not mutate the original event.

## Nested agents and retries

Every execution is represented as a node with optional parent edge and an inclusion policy:

- `exclusive`: parent total excludes child execution;
- `inclusive`: parent total includes all identified child execution;
- `unknown`: contribution is quarantined or downgraded until the profile defines treatment.

Retry ordinals are local to one logical operation but each actual model execution retains its own execution identity. A client retry, provider retry and stream reconnection are distinct concepts and are handled only by an exact profile.

## Comparability

Raw tokens are the default competitive unit. The system does not claim equal computational value across models. Every leaderboard supports model, provider, agent, evidence-tier and local/hosted filters. UI states that raw tokens are a usage-volume comparison, not a capability-normalized benchmark.

No hidden normalization multiplier changes competitive totals. Future normalized views require a new versioned metric and never rewrite Token Burn.

## Estimated Cash Burn

Estimated Cash Burn is computed from immutable usage facts and a versioned pricing dataset:

`estimated_cost = sum(category_units * effective_unit_price)`.

Rules:

- Label every value `Estimated`.
- Store pricing dataset ID, effective date, currency, provider, model alias, region and category prices.
- Use the price effective at event time; later price changes do not rewrite historical estimates.
- Corrections create a new interpretation record and visible correction reason.
- Subscription plans, free tiers, credits, negotiated enterprise rates and bundled usage do not alter the API-equivalent estimate.
- Batch, cache, priority, regional and modality pricing are represented when known.
- Unknown model/price produces `unpriced`, never zero.
- Local models show token usage and `Local compute`; dollar estimates remain absent until an approved local-compute methodology exists.
- FX conversion is display-only, timestamped and does not alter the canonical pricing-currency estimate.
- Taxes and user-specific billing adjustments are excluded.

## Time and ranking periods

Canonical event time is server-receipt time plus bounded source-time metadata. The server owns period assignment.

- Daily: UTC calendar day.
- Weekly: Monday 00:00 UTC through next Monday.
- Monthly: UTC calendar month.
- Yearly: UTC calendar year.
- Lifetime: all accepted competitive claims.
- Seasons: explicit immutable UTC start/end timestamps and versioned rules.

Local-time views may be offered as private analytics but do not change global competitive periods.

### Late and offline events

- Claims include source event time, monotonic counters, local commitment time/reference when applicable, challenge context and receipt time.
- Standard claims may arrive up to 24 hours late; a Hardened profile may set a stricter platform/adapter limit.
- A server challenge establishes submission freshness, not original event occurrence.
- Claims outside the accepted lateness window remain private analytics and are excluded from active rankings.
- Period results remain provisional through the lateness window, then finalize.
- Appeals and server corrections modify finalized results through explicit correction records and audit events.

### Ties, ranks, streaks

- Competition uses SQL `rank()` semantics: equal score shares rank and leaves gaps.
- Stable secondary ordering is `score DESC, first_reached_score_at ASC, user_id ASC`; it affects display order, not rank.
- An overtake requires strictly greater score, not display-order movement within a tie.
- Rank movement compares finalized snapshots at the same scope/period/filter.
- Streaks require at least one accepted competitive claim per UTC day.
- Deleted or disqualified scores trigger deterministic recomputation.

## Accounting event invariants

Every normalized request includes adapter ID/version, source version, event ID, session ID, optional parent event ID, model/provider identifiers, start/end times, token categories, total quality, source evidence class, accounting profile, duplicate domain, identity profile, inclusion policy, evidence inputs and privacy classification.

All integer additions use checked arithmetic. Negative, overflowed, internally inconsistent, ambiguous-inclusive or duplicate usage is rejected or quarantined with a stable reason code.

## Required tests

Golden fixtures cover every category, unknown fields, nested agents, retries, provider-internal retries, failed/aborted streams, cache semantics, multimodal usage, totals that include children, conflicting sources, fingerprint collisions, provider-ID reuse, cross-domain duplicates, late higher-authority correction, late events, season boundaries, pricing changes, unpriced models and correction rebuilds.
