# T20 Certification and Selection Specification

Status: normative planning contract
Updated: 2026-07-19
Scope: P-1130A through P-1130D

This specification completes the planning semantics required by the T20 golden-path contract. It defines what is certified, how evidence is trusted, how the rolling cohort is selected, and how accounting sources are reconciled. It does not identify the production T20 cohort or claim implementation evidence.

## P-1130A — Certification tuple and coverage matrix

A certification applies only to this immutable tuple:

`model family × provider model ID × exact model version × agent/runtime × agent/runtime version × API mode × capture path × platform × architecture × accounting profile version × conformance-suite version`

No certification may be inherited across a changed tuple component without an explicit compatibility rule backed by fixtures. Marketing family names, aliases, floating endpoints, preview labels, and provider routing names are discovery metadata—not certification identities.

Each T20 family has a coverage matrix containing every materially used tuple. Every entry must be one of:

- `hardened`: exact passing certification and passing optimization evidence;
- `competitive-certified`: exact passing certification without the complete T20 optimization guarantee;
- `community-certified`: externally maintained evidence accepted under published governance;
- `generic-live`: working generic capture with explicitly weaker evidence;
- `pending`: selected but not yet certified;
- `unsupported`: known gap displayed honestly.

Material usage coverage is calculated as the eligible competitive usage represented by `hardened` entries divided by all eligible usage for that family. A T20 slot requires at least 0.90 family-level material usage coverage unless an approved exception identifies the excluded tuple, usage share, user impact, owner, and expiry. A single optimized path cannot conceal materially used unsupported paths.

Certification expiry is the earliest of:

1. 90 days after testing;
2. a material provider accounting/API change;
3. a material runtime/capture-path change;
4. retirement or silent mutation of the tested model version;
5. fixture or conformance-suite invalidation.

## P-1130B — Evidence classes, binding and downgrade

Evidence strength is ordered:

1. `E1-provider-signed`: cryptographically provider-bound receipt or signed usage record;
2. `E2-server-observed-provider-response`: trusted server directly observes authenticated provider usage fields;
3. `E3-trusted-local-structured-event`: authenticated local runtime emits structured usage with process/device binding;
4. `E4-gateway-proxy-observation`: trusted gateway observes request/response usage but lacks direct provider signature;
5. `E5-deterministic-derivation`: totals derived deterministically from authoritative public rules;
6. `E6-untrusted-import`: user-supplied or retrospective data, private analytics only.

Every certification records source binding: provider/account identity where privacy permits, device or process identity, request/batch correlation, challenge or nonce binding, capture timestamp, sequence continuity, and duplicate domain.

Replay controls must include stable event identity, bounded freshness, sequence or monotonic continuity, idempotent ingestion, and duplicate-domain reconciliation. Evidence is downgraded when source binding, freshness, continuity, exact version detection, or authoritative usage categories are absent.

Rules:

- E6 can never enter active competition.
- E5 cannot be Hardened when authoritative provider-reported usage exists but is unavailable to the capture path.
- E4 cannot outrank a matching E1–E3 record for the same duplicate domain.
- Conflicting stronger sources fail closed for public competition until reconciled.
- Unknown model revisions, unrecognized aliases, or missing accounting fields downgrade to `pending`, `generic-live`, or private-only behavior; they never silently inherit Hardened status.

## P-1130C — Reproducible T20 selection

The selection window is the most recent complete 30-day UTC period. A selection run is immutable, versioned, reproducible, and records its datasets, algorithm, reviewer, privacy thresholds, sample-size threshold, exclusions, and confidence method.

### Eligible population

Include genuine, non-duplicated active competitive usage attributable to a canonical model family. Exclude imported history, test fixtures, internally generated conformance traffic, rejected abuse, unverifiable unknown-model traffic, and events below privacy/cohort thresholds.

### Dataset precedence

1. privacy-safe VibeMaxxing eligible usage is the primary usage dataset;
2. provider/runtime aggregate data may correct known capture blind spots when provenance and overlap are documented;
3. external public datasets may inform candidate discovery and relevance scores but may not fabricate VibeMaxxing usage share.

### Deduplication and normalization

Deduplicate by the declared duplicate domain using the strongest evidence record and stable request/batch identity. Normalize provider aliases to canonical families only through versioned alias rules. Unresolved aliases remain unknown and do not receive a family score.

### Score

Each candidate receives a 0–100 score:

`0.40 × usage + 0.30 × agent/coding relevance + 0.20 × capability relevance + 0.10 × deployment diversity`

Each component and its input provenance is retained. Missing usage is zero, never imputed from popularity. Missing non-usage inputs use a documented conservative floor and reduce confidence.

### Constraints and ties

- normally no provider occupies more than five slots;
- at least four slots represent qualifying open-weight or self-hostable families;
- a concentration override requires measured usage above 35% plus written approval;
- ties resolve by higher usage, then higher agent/coding relevance, then higher confidence, then lexicographic `family_id`;
- minimum approved sample size and privacy threshold must pass before a run can become `approved`;
- bootstrap or equivalent resampling produces confidence for rank stability; low-confidence boundary candidates are reviewed and recorded, not silently reordered.

The selected cohort is refreshed monthly and before each release candidate. Changes are prospective. Newly selected families are `t20-pending` until certification; departing families retain honest historical labels but do not satisfy current T20 coverage.

## P-1130D — Accounting profiles and precedence

Accounting profiles are versioned by provider, API surface, and effective behavior. Each profile defines:

- authoritative token/usage categories and units;
- inclusion or exclusion of system, reasoning, cached, speculative, multimodal, tool, batch, and provider-overhead usage;
- streaming finalization and partial-response behavior;
- retry, cancellation, background-job, compaction, and subagent attribution;
- missing-usage behavior;
- pricing dataset reference and effective interval;
- alias/version applicability and retirement conditions.

Source precedence within one duplicate domain is:

1. valid E1 provider-signed totals;
2. matching E2 provider-response totals;
3. matching E3 trusted runtime totals;
4. matching E4 gateway totals;
5. E5 derivation only where the profile explicitly permits it;
6. E6 import, private only.

The selected source supplies authoritative totals. Lower-priority matching observations are reconciliation evidence and must not be added again. Category-level enrichment from a weaker source is forbidden unless the accounting profile proves categories are non-overlapping and the merge rule has dedicated fixtures.

When sources disagree beyond the profile tolerance, the event is quarantined or downgraded; totals are not averaged. Missing required authoritative categories follow the profile’s declared behavior: reject, downgrade, labelled estimate, or private-import-only.

Estimated Cash Burn uses immutable pricing data selected by provider model ID, category, region/mode where applicable, currency, and effective timestamp. Missing or ambiguous pricing produces an unavailable or explicitly estimated value, never fabricated actual spend.

## P-1130E completion evidence

Planning completion requires:

- schema-valid canonical registry in honest `prelaunch-pending` state;
- a valid quantitative optimization-evidence fixture;
- an invalid fixture that cannot claim `pass` while mandatory gates fail;
- validator checks for this specification, the golden-path contract, schemas, registry invariants, and fixtures;
- task and decision registers that distinguish completed planning from future implementation evidence.

Passing these checks proves planning consistency only. It does not certify any real model, provider, runtime, platform, or capture path.
