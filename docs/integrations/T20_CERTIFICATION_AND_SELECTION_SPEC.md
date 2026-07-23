# T20 Certification and Selection Candidate Specification

Status: provisional candidate specification under D-046
Updated: 2026-07-23
Scope: candidate semantics only; not a launch requirement

This provisional candidate specification defines how a future T20 cohort could be selected and certified without inventing current support. It does not identify a production cohort, require twenty launch slots, or claim implementation evidence.

## Certification tuple and coverage matrix

A certification applies only to:

`model family × provider model ID × exact model version × agent/runtime × agent/runtime version × API mode × capture path × platform × architecture × accounting profile version × conformance-suite version`

No certification inherits across a changed tuple component without an explicit compatibility rule and fixtures. Marketing aliases, floating endpoints and provider routing names are discovery metadata, not certification identities.

A coverage entry is one of:

- `hardened` — exact passing certification and optimization evidence;
- `competitive-certified` — exact passing competitive support without the complete T20 optimization commitment;
- `community-certified` — externally maintained evidence accepted under published governance;
- `generic-live` — working generic capture with a weaker disclosed ceiling;
- `pending` — candidate tuple not yet certified;
- `unsupported` — known visible gap.

A single optimized path cannot conceal materially used unsupported paths. Candidate certifications expire after 90 days or immediately after a material source, accounting, runtime, alias or conformance change.

## Evidence classes, source binding and downgrade

Evidence strength is ordered:

1. `E1-provider-signed` — independently verifiable provider-signed usage evidence;
2. `E2-server-observed-provider-response` — authenticated provider fields observed by VibeMaxxing but not independently signed;
3. `E3-trusted-local-structured-event` — exercised structured local source with process/device binding;
4. `E4-gateway-proxy-observation` — exercised gateway observation with duplicate semantics;
5. `E5-deterministic-derivation` — reproducible derivation with an explicit ceiling;
6. `E6-untrusted-import` — private analytics only.

E6 can never enter active competition.

Every tuple records source binding, device or process identity, environment class, request/batch correlation, challenge or nonce where available, capture time, sequence continuity and duplicate domain. Evidence downgrades when source identity, freshness, continuity, exact version detection or authoritative usage categories are absent.

Device continuity does not prove physical-device uniqueness. Clone, snapshot, copied-state, concurrent-device and restored-runner behavior require explicit fixtures and server reconciliation.

## Provisional selection method

A future selection run uses the most recent complete 30-day UTC period and records datasets, algorithm, reviewer, privacy thresholds, sample-size thresholds, exclusions, confidence and deterministic tie-breaking.

Eligible population includes genuine non-duplicated competitive usage attributable to a canonical family. It excludes imports, fixtures, conformance traffic, rejected abuse and unresolved unknown-model traffic.

Dataset precedence:

1. privacy-safe eligible VibeMaxxing usage;
2. provider/runtime aggregates that document provenance and overlap;
3. external public datasets for candidate discovery only.

Deduplicate through the declared duplicate domain and strongest valid evidence. Unresolved aliases remain unknown.

Candidate score:

`0.40 × usage + 0.30 × agent/coding relevance + 0.20 × capability relevance + 0.10 × deployment diversity`

Missing usage is zero, never imputed from popularity. Missing non-usage inputs use a conservative documented floor and reduce confidence.

Provider concentration, open-weight diversity and confidence-boundary review remain candidate policies. They have no launch force while D-046 is provisional.

## Accounting profiles and precedence

Profiles are immutable by provider, API surface, runtime mode and effective behavior. They define authoritative token categories, inclusion rules, streaming finalization, retry/cancellation behavior, background jobs, compaction, parent/child attribution, missing usage, pricing provenance and alias applicability.

Source precedence within one duplicate domain is:

1. valid E1 provider-signed totals;
2. matching E2 provider-response totals;
3. matching E3 trusted-runtime totals;
4. matching E4 gateway totals;
5. E5 derivation where the profile permits;
6. E6 import, private only.

The selected source supplies totals. Matching lower-priority observations are reconciliation evidence and are not added again. Category enrichment from a weaker source is forbidden unless a profile proves non-overlap with dedicated fixtures. When sources disagree beyond tolerance, quarantine or downgrade; totals are not averaged.

Estimated Cash Burn uses immutable event-time pricing provenance. Missing or ambiguous pricing is unavailable or explicitly estimated, never fabricated actual spend.

## Candidate optimization evidence

A passing candidate record must include accounting, performance, reliability, coverage depth, user experience, maintenance and final result sections. It cannot claim pass when mandatory gates fail.

The registry remains `prelaunch-pending` with no slots, selection runs, accounting profiles or certifications until real implementation evidence exists and D-046 is promoted by a later decision.

## Evidence boundary

Passing these checks proves planning consistency only. It does not certify any real model, provider, runtime, platform, source, adapter, accounting profile or launch readiness.
