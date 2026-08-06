# Accounting, Pricing, and Time Contract

Status: normative planning contract
Version: 3
Updated: 2026-08-06
Decisions: D-235

## Token Burn

Token Burn is the checked sum of the mutually exclusive outputs declared by the exact immutable accounting profile. The canonical output family is `input_uncached`, `output_visible`, `cache_read`, `cache_write`, `reasoning`, `multimodal_input`, and `multimodal_output`, but a profile enables only the components it can produce without overlap.

Source totals and provider categories are observations, not universal addends. The profile containment graph determines whether cache is contained in input, reasoning is contained in output, modality units are separate, or parent totals contain child execution. A contained category is subtracted from its container before both appear as canonical outputs. Unknown categories are absent, never encoded as zero. Contradictory or overflowing containment rejects, quarantines, or becomes private analytics under the profile's fixed policy.

The machine contract is `packages/schemas/accounting-profile.schema.json`; registered planning profiles and representative no-double-count fixtures live under `conformance/accounting/`. A profile states which fields exist, how they contain one another, and through `component_map` which canonical component each field resolves to. It does not state the arithmetic those declarations are evaluated under: `packages/schemas/accounting-arithmetic-v1.json` owns that, and `docs/product/TOKEN_ACCOUNTING_SPEC.md` is its prose owner. The two together are what two independent implementations need in order to reach the same total.

Under D-261 a profile's `content_sha256`, which the signed claim carries as `accounting_profile_sha256`, is SHA-256 over the profile's RFC 8949 core deterministic CBOR encoding with that field omitted.

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
- Host/guest, IDE/CLI, proxy/provider, and orchestrator/subagent duplication is resolved by `packages/schemas/observer-equivalence-v1.json`, which fixes the commitment preimage to source-derived facts, forbids every observer-derived input, and gives the server the scope, the survivor order and the disposition. Equivalent observations are never summed.

## Producer bindings

A telemetry producer pins its schema surface, instrumentation scope, metric or message shape, attribute disposition and accounting profile in `packages/schemas/producer-accounting-binding-v1.schema.json` before its numbers are read as accounting input. Registered bindings live in `conformance/accounting/producer-bindings-v1.json`.

The binding separates two ceilings that reading a registry casually would merge. `capability_ceiling` is the strongest public profile the mechanism could reach if it were certified, and is a property of the mechanism. `effective_ceiling` is what it reaches today, and the schema holds it at `private-analytics` for every certification state other than `active`. Generic OpenTelemetry, generic ACP, proxy, wrapper and unknown-version integrations are therefore private analytics by construction rather than by convention. No binding in the registry is `active`.

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

- Claims bind a bounded event interval and uncertainty, monotonic clock domain/generation/duration, challenge, previous checkpoint, and server receipt time.
- Maximum delayed-sync age is owned by the exact source/accounting/platform policy profile; no universal 24-hour window exists.
- Reboot, suspend, restore, rollback, or clock-domain reset starts or records a new monotonic generation.
- Claims outside the applicable profile bound remain private analytics unless a named checkpoint/continuity policy explicitly admits them.
- Period results remain provisional through the lateness window, then finalize.
- Appeals and verified server corrections can modify finalized results through explicit correction records and audit events.

### Clock synchronization and skew bounds

The monotonic clock domain is a first-class claim field, clock rollback is a catalogued attack (AC-A-008), and backdating into a prior period is another (AC-A-007). Until this section existed, no tolerance window, time-source requirement or skew bound was stated anywhere except a single 300-second authentication figure in ADR-015, so the controls those attack entries name had no threshold to enforce.

**The server's clock is the authority.** Canonical event time is server-receipt time plus bounded source metadata, and every bound below is measured against the server's clock rather than negotiated with the client.

| Bound | Value | What it constrains |
|---|---:|---|
| Request signing freshness | 300 seconds | ADR-015 already sets it: a native client whose clock is further than this from the server cannot authenticate |
| Future event tolerance | 300 seconds | a claim whose declared source interval ends more than this far ahead of server receipt time is rejected |
| Past event tolerance | `standard_claim_lateness_seconds`, currently 86,400 | already owned by the policy registry and by the lateness window above |
| Declared time uncertainty ceiling | 300 seconds | a claim declaring `time_uncertainty_ms` above this is admitted as private analytics and is not competitively eligible |
| Server clock offset, review | 250 ms | the server compares its own clock against a second source and reports a `daily-digest` alert beyond this |
| Server clock offset, refuse | 2,000 ms | beyond this the server stops finalizing claims and stops assigning periods, because a period boundary decided by a wrong clock cannot be corrected without rebuilding |

The three 300-second figures are deliberately the same number. A client that can authenticate can submit, and a client that cannot authenticate cannot submit anything at all; giving event admission a wider window than authentication would create a band in which a claim is admissible from a client that cannot present it. One number also means one thing for a participant to understand: **your machine's clock must be within five minutes of real time.**

Five minutes is chosen against the period model rather than against cryptographic practice. The shortest competitive period boundary that matters is the UTC calendar day, and daily, weekly, monthly and yearly boundaries are all at least a day apart. A five-minute tolerance is 0.35% of a day, so the number of claims a maximally skewed honest clock can land on the wrong side of a boundary is negligible, while a tolerance an order of magnitude wider would start to matter at the minute-aggregate level.

The 2,000-millisecond refusal threshold is set an order of magnitude above the 250-millisecond review threshold, which is roughly what an unsynchronized virtual machine drifts in an hour. Refusing at two seconds means a server whose time source has failed stops making irreversible period assignments within about an hour of the failure rather than continuing indefinitely.

**Time source.** The server's host clock is disciplined by a network time protocol client with at least four independent sources. On managed compute the platform owns that discipline and the provider's published statement of it is a selection input under ADR-017; the service does not assume it. The service independently measures its own offset against a second source and applies the two thresholds above, because a platform assurance that the service cannot verify is a platform assurance the service is not entitled to rely on for an irreversible decision.

**Client clocks are never trusted and never need to be.** A skewed client clock does not corrupt accounting, because the monotonic domain carries duration and the server carries the wall-clock anchor. What a skewed client clock does is fail authentication, which ADR-015 already describes as a visible failure rather than a silent downgrade. Reboot, suspend, restore, rollback or clock-domain reset starts a new monotonic generation, as stated above, and a generation change is the signal that wall-clock continuity was broken — a claim spanning a generation boundary carries the break explicitly rather than averaging across it.

**Leap seconds.** The service makes no assumption about how the platform handles one. All internal arithmetic is on monotonic durations and on integer counts, no interval is computed by subtracting two wall-clock timestamps, and period boundaries are UTC calendar boundaries evaluated from the platform's own calendar rather than from an elapsed-seconds count. A smeared or repeated second therefore changes no accepted total.

### Ties, ranks, streaks

- Competition uses SQL `rank()` semantics: equal score shares rank and leaves gaps.
- Stable secondary ordering is `score DESC, first_reached_score_at ASC, user_id ASC`; it affects display order, not rank.
- An overtake requires strictly greater score, not display-order movement within a tie.
- Rank movement compares finalized snapshots at the same scope/period/filter.
- Streaks require at least one accepted competitive claim per UTC day.
- Deleted or disqualified scores trigger deterministic recomputation.

## Accounting event invariants

Every `NormalizedAccountingEvent` binds collector-generated IDs; adapter artifact/manifest and certification digests; registered source/provider/model IDs; accounting-profile ID/digest; monotonic domain/generation and bounded wall-time uncertainty; mutually exclusive canonical components; separately retained source observations with containment labels; count/reconstruction authority; retry/outcome and duplicate-domain semantics; deterministic rule result; and privacy policy result. It is local-only and has `network_eligible=false`.

All integer additions use checked arithmetic. Negative, overflowed, internally inconsistent, or duplicate usage is rejected or quarantined with a stable reason code. `packages/schemas/accounting-arithmetic-v1.json` states the domain, the evaluation order and the rejection conditions; `conformance/accounting/arithmetic-vectors-v1.json` is the executable form and the planning validator recomputes every vector rather than reading its answer back.

Each accepted event has exactly one `packages/schemas/source-receipt-v1.schema.json` receipt, which is device-local, records every observation that saw the execution and which single one counted, and asserts no provider attestation under D-100. `packages/schemas/evidence-bundle-v1.cddl` binds the signed claim bytes, that receipt, the profile and arithmetic digests, the provenance chain, the privacy decision and the equivalence record into one at-rest record that never crosses the device boundary.

Corrections do not rewrite accepted totals. Under D-263 they are append-only contributions with a direction and an unsigned magnitude, composed as the checked sum of additions minus the checked sum of retractions, rejecting rather than clamping when retractions exceed what they correct.

## Required tests

Golden fixtures cover every category, unknown fields, nested agents, retries, failed/aborted streams, cache semantics, multimodal usage, totals that include children, conflicting sources, late events, season boundaries, pricing changes, unpriced models, and correction rebuilds.
