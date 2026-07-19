# T20 Model Hardening Contract

Status: normative planning contract
Updated: 2026-07-19

## Requirement

VibeMaxxing must provide bespoke Hardened coverage for a rolling cohort of the 20 most materially relevant model families before public launch. Generic agent, proxy, OpenTelemetry, ACP, wrapper, gateway, or import support does not satisfy the T20 requirement.

T20 is an engineering-priority cohort, not a claim that a model family is universally supported. A slot identifies a model family and its exact model endpoints. Hardened certification is granted only to an exercised certification tuple.

## Certification tuple

A certification tuple is:

`model endpoint × agent/runtime × capture path × API mode × platform/architecture × accounting-profile version × evidence class`

Each dimension is independently versioned. A passing tuple does not imply support for another agent, runtime, platform, endpoint alias, API mode, or evidence path in the same family.

The registry must distinguish:

- model family, provider, exact provider model ID, endpoint or dated snapshot;
- agent, IDE, SDK, proxy, gateway or local runtime and exact tested version;
- capture path and duplicate domain;
- API mode, including streaming, batch, background, tool, multimodal and agent/subagent modes;
- operating system, architecture and packaging context;
- accounting authority and accounting-profile version;
- evidence class and verification method;
- certification suite, fixtures, result, expiry and maintainer.

## Coverage hierarchy

T20 is the product's golden path and receives the highest engineering, correctness, performance, compatibility, maintenance and UX priority.

1. **T20 optimized Hardened** — an exact certification tuple has passed all applicable gates and required coverage thresholds.
2. **Other Hardened or Competitive-certified** — strong exact support without the full T20 optimization commitment.
3. **Community-certified and Generic live** — useful lower-assurance coverage.
4. **Imported or Unsupported** — private retrospective analytics or an honestly visible gap.

No family-level label may conceal unsupported or weaker tuples.

## Evidence classes

Evidence is classified before accounting or anti-replay decisions:

1. **E1 provider-signed** — independently verifiable provider-signed evidence with a documented trust root, canonical payload, freshness and request binding.
2. **E2 server-observed provider response** — usage metadata observed by a VibeMaxxing-controlled server during an authenticated provider exchange, bound to request identity and ingestion state but not independently provider-signed.
3. **E3 trusted local structured event** — structured data from an exercised agent, SDK, runtime or OS integration with source identity and local continuity controls.
4. **E4 gateway or proxy observation** — structured observation at an exercised gateway or proxy, with explicit duplicate-domain and retry semantics.
5. **E5 deterministic derivation** — tokenizer, log or file-derived accounting that is reproducible but estimated or incomplete.
6. **E6 untrusted import** — retrospective data that is private analytics only and cannot enter active competition.

OpenTelemetry is an ingestion transport and normalization input. It is not proof by itself. A semantic-convention field becomes usable only through a versioned adapter and accounting profile with fixtures and source classification.

“Authenticated provider receipt” must not be used as a generic synonym for ordinary API response metadata. Only E1 evidence may be described as independently verifiable provider-signed evidence.

## Source binding and replay controls

Every competitive tuple must define:

- stable event or request identity and canonical duplicate key;
- provider, agent/runtime, device and account binding available to that path;
- challenge, nonce, timestamp, sequence or continuity controls available to that evidence class;
- retry, cancellation, partial response, streaming and batch semantics;
- maximum freshness and acceptance windows;
- cross-path duplicate precedence when the same activity is observed more than once;
- clone, snapshot rollback, copied-state and concurrent-device behavior;
- downgrade behavior when source identity, continuity or version detection fails.

E2 through E5 evidence must never inherit E1 trust language. Device-key continuity can prove continuity of a device identity, not uniqueness of physical hardware. Cloned device state, VM snapshots and copied local databases must be treated as explicit attack cases and controlled through server challenges, sequence/hash continuity, duplicate domains, concurrency checks and progressive risk handling.

## Accounting profiles

Accounting semantics are provider/API/version specific. Each tuple references an immutable accounting profile defining:

- authoritative fields and their precedence;
- input, output, cached, cache-write, reasoning, multimodal, tool and provider-overhead categories;
- whether totals include hidden, cached, system, speculative or retry tokens;
- streaming finalization, cancellation, retry, batch and background-job behavior;
- parent, child and subagent attribution;
- missing, contradictory and revised usage behavior;
- pricing provenance and effective dates for Estimated Cash Burn;
- deterministic test vectors and reconciliation tolerances.

Provider-reported totals outrank deterministic estimates only for categories and modes covered by the exact profile. Unknown revisions fail closed or downgrade visibly; they do not silently inherit prior semantics.

## Optimization evidence gates

Every active T20 slot must have versioned evidence for:

1. accounting fidelity against the authoritative source for each certified tuple;
2. performance budgets for collection overhead, memory, CPU, disk, network, startup and claim latency;
3. reliability under crash, restart, offline, upgrade, rollback and upstream change;
4. coverage depth across materially used agents, runtimes, API modes, aliases and platforms;
5. automatic detection and normal operation without model-specific manual mapping;
6. duplicate prevention across all certified paths that can observe the same activity;
7. privacy-negative and forbidden-field canary tests;
8. maintenance ownership, freshness window, emergency disable and re-certification.

Numerical budgets and exercised results are implementation evidence and remain empty during planning.

## Reproducible selection method

The cohort is refreshed at least monthly and before each release candidate. Selection is prospective and uses a versioned selection run. Every run records:

- eligible population and excluded activity;
- observation window and dataset provenance;
- privacy threshold and minimum sample size;
- source coverage, known bias and missing-data treatment;
- cross-source deduplication method;
- score normalization and weighting;
- confidence or uncertainty measure;
- tie handling and deterministic ordering;
- provider-concentration and open-weight constraints;
- the exact algorithm and policy versions;
- reviewer and approval record.

The intended score components remain:

- observed eligible competitive usage: 40%;
- agent and coding relevance: 30%;
- capability relevance: 20%;
- provider and deployment diversity: 10%.

These weights do not make a selection run valid without the recorded methodology above. Providers, model publishers and users must not be able to purchase, self-report or synthetically generate inclusion without passing eligibility, deduplication and anti-manipulation controls.

Before representative VibeMaxxing usage exists, the registry must state `prelaunch-pending`. External datasets may nominate candidates but cannot support claims about measured VibeMaxxing coverage. Any pre-launch exception requires an explicit decision entry and must not be described as an 80% measured-usage result.

No provider may occupy more than five slots unless its deduplicated eligible usage share exceeds 35%. At least four slots should cover open-weight or self-hostable families when they pass the same relevance threshold; exceptions require recorded evidence rather than a quota-only override.

## Coverage requirements

A T20 family is launch-covered only when:

- at least one exact endpoint tuple is non-expired and Hardened;
- all materially used capture paths for the family are represented in the coverage matrix as Hardened, lower assurance, pending or unsupported;
- the certified tuples collectively meet the registry's measured coverage threshold for that family;
- no handwritten marketing claim exceeds the generated matrix;
- unsupported agents, runtimes, modes and platforms are visible.

One convenient provider API path is insufficient when material competitive usage occurs through unsupported agents or runtimes.

## Hardened evidence gate

A certification tuple is Hardened only when all applicable gates pass:

1. evidence-class-specific source verification and binding;
2. deterministic normalization and accounting vectors;
3. independent verifier agreement where possible;
4. replay, duplicate, retry, cancellation, cache, reasoning, tool, multimodal, batch and subagent tests;
5. device cloning, copied-state, snapshot rollback and concurrent-submission tests where local state exists;
6. privacy-negative and content-exfiltration tests;
7. exact alias/version detection and fail-closed behavior;
8. pricing provenance validation when Estimated Cash Burn is displayed;
9. signed certification record with suite version, fixture reference, maintainer, tested date and expiry.

Certification expires after 90 days, immediately after a material accounting or source change, or when an exact version is retired or altered without a stable identifier.

## Launch gate

Public launch is blocked unless:

- the registry contains exactly 20 active slots produced by a valid selection run;
- every slot has non-expired Hardened tuple coverage meeting the slot's material-usage threshold;
- the combined certified coverage represents at least 80% of deduplicated eligible competitive usage in the most recent 30-day run;
- any pre-launch exception is explicit, narrow and does not claim measured coverage that does not exist;
- no slot relies solely on generic fallback;
- weaker and unsupported tuples are explicitly labelled;
- compatibility UI and launch claims are generated from the registry.

A newly selected family is `t20-pending` until required tuple coverage passes. A departing family keeps its last honest tuple labels but no longer satisfies the current T20 gate.

## Initial candidate pool

The candidate pool should include leading hosted and self-hosted coding-agent model ecosystems. Exact families must not be hardcoded in prose because availability, naming and usage change rapidly.

## Evidence boundary

This contract defines planning requirements only. It does not claim that any model, endpoint, agent, runtime, capture path, platform or accounting profile is currently certified, optimized or launch-ready.