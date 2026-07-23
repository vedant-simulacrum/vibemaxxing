# T20 Model Hardening Candidate Contract

Status: provisional planning candidate under D-046
Updated: 2026-07-23

## Authority and scope

D-046 is provisional. T20 is a candidate rolling golden-path engineering cohort for prioritizing exact model/runtime integration work; it is not a public-launch dependency and it does not override capability-based universal adapter rollout.

This contract preserves a rigorous candidate selection and certification design so it can be evaluated later using real usage and implementation evidence. It does not require exactly twenty model families at launch, does not authorize implementation, and does not claim that any current family is certified.

## Exact certification tuple

A certification applies only to:

`model family × provider model ID × exact model version × agent/runtime × runtime version × API mode × capture path × platform × architecture × accounting-profile version × conformance-suite version × evidence class`

No result inherits across a changed tuple component without an explicit compatibility rule and fixtures.

## Candidate support hierarchy

1. **T20-optimized Hardened candidate** — exact tuple passes all applicable certification and optimization evidence.
2. **Other Hardened or competitive-certified** — exact strong support without the T20 optimization commitment.
3. **Community-certified or generic-live** — useful lower-assurance coverage.
4. **Imported or unsupported** — private retrospective analytics or an honest gap.

No family-level label may conceal weaker or unsupported tuples.

## Evidence classes

- `E1-provider-signed`: independently verifiable provider-signed usage evidence.
- `E2-server-observed-provider-response`: authenticated provider fields observed by a VibeMaxxing-controlled server, but not independently provider-signed.
- `E3-trusted-local-structured-event`: structured local source data with exercised process/device binding.
- `E4-gateway-proxy-observation`: exercised gateway observation with explicit duplicate semantics.
- `E5-deterministic-derivation`: reproducible derivation with an explicit estimate or incompleteness ceiling.
- `E6-untrusted-import`: private analytics only; never active competition.

OpenTelemetry is transport and normalization input, not proof by itself. Ordinary API response metadata is not called a provider-signed receipt.

## Source binding and deterministic controls

Every competitive tuple defines:

- stable source event or request identity;
- source, account, runtime, device and environment binding available to the path;
- challenge, nonce, timestamp, sequence and continuity controls;
- retry, cancellation, streaming, batch and partial-response behavior;
- duplicate domain and cross-path precedence;
- clone, snapshot, copied-state and concurrent-device behavior;
- fail-closed or downgrade behavior for unknown versions and missing authority.

Device-key continuity proves continuity of a device identity, not physical-device uniqueness. Clone resistance requires server challenges, sequence/hash continuity, duplicate-domain reconciliation, concurrency checks, explicit lineage transitions and progressive review.

## Accounting profiles

Each tuple references an immutable accounting profile covering:

- authoritative fields and precedence;
- mutually exclusive input, output, cached, cache-write, reasoning, multimodal, tool and overhead categories;
- whether source totals include hidden, speculative, retry or child usage;
- streaming finalization, cancellation, retries, batch and background jobs;
- parent, child and subagent attribution;
- missing usage, unknown aliases and version mutation;
- pricing provenance and effective-time interpretation.

Matching observations are reconciled; they are not blindly summed or averaged.

## Provisional candidate selection

A future selection run may use the most recent complete 30-day UTC period and must record datasets, exclusions, privacy thresholds, missing-data treatment, deduplication, algorithm, confidence, ties, reviewer and policy version.

Candidate score:

`0.40 × usage + 0.30 × agent/coding relevance + 0.20 × capability relevance + 0.10 × deployment diversity`

Missing usage is zero, never inferred from popularity. External data may nominate candidates but cannot fabricate VibeMaxxing usage share. Provider concentration and open-weight diversity constraints remain candidate policy, not launch authority.

Until representative usage and implementation exist, the registry remains `prelaunch-pending` with no slots, selection runs, accounting profiles or certifications.

## Optimization evidence

A candidate slot cannot pass using qualitative claims. Versioned optimization evidence must cover:

- exact accounting vectors;
- collector CPU, memory, disk, network and latency budgets;
- crash, offline, upgrade, rollback and upstream-change reliability;
- materially used agent/runtime/mode/platform coverage;
- automatic detection and zero manual mapping in normal operation;
- duplicate prevention across every observable path;
- privacy-negative canaries;
- maintenance owner, expiry, emergency disable and recertification.

Numerical results are implementation evidence and remain absent during planning.

## Promotion gate

T20 becomes an accepted product or launch requirement only after:

1. P-1140B and P-1140E reconcile it with capability-based rollout;
2. real usage shows material value over ordinary exact-tuple certification;
3. the maintenance and launch cost is measured;
4. an explicit decision supersedes provisional D-046.

Until then, no validator, task, UI or launch checklist may require twenty active slots.

## Evidence boundary

This is a provisional planning candidate. It proves no real model, provider, runtime, adapter, platform, accounting profile, performance target or launch readiness.
