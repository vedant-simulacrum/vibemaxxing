# T20 Model Hardening Contract

Status: normative planning contract
Updated: 2026-07-19

## Requirement

VibeMaxxing must provide bespoke Hardened coverage for a rolling cohort of the 20 most materially relevant model families before public launch. Generic agent, proxy, OpenTelemetry, ACP, wrapper, gateway, or import support does not satisfy the T20 requirement.

The cohort is called **T20**. A T20 slot represents a model family plus exact provider/version records. A family may contain multiple aliases or endpoints, but Hardened status is awarded only to exact exercised versions and modes.

## Coverage hierarchy

T20 is the product's **golden path** and receives the highest engineering, correctness, performance, compatibility, maintenance, and UX priority.

Models outside T20 may still be supported through Competitive-certified, Community-certified, Generic live, Imported, or Unsupported states. Their existence never reduces the T20 obligation and they do not need to meet the full T20 optimization bar unless promoted into the cohort.

The intended hierarchy is:

1. **T20 optimized Hardened** — bespoke, exhaustively exercised and continuously maintained.
2. **Other Hardened or Competitive-certified models** — strong exact support where available, without the full T20 optimization guarantee.
3. **Community-certified and Generic live** — useful lower-assurance coverage.
4. **Imported or Unsupported** — private retrospective analytics or an honestly visible gap.

## T20 optimization standard

“Fully optimized” means the T20 path is not merely functionally compatible. For each active T20 slot, VibeMaxxing must optimize and prove:

- the most authoritative available capture path, with weaker fallbacks used only when explicitly labelled;
- exact accounting semantics for every provider-reported category, including reasoning, cache, multimodal, tool, batch and retry behavior;
- deterministic normalization with no avoidable lossy mapping;
- minimum practical collection and synchronization overhead, measured on supported platforms;
- bounded CPU, memory, disk, network and startup impact with published budgets;
- the lowest practical claim latency and fastest safe presence/ranking propagation;
- exact model and version detection, including cloud aliases, dated snapshots, preview channels and regional endpoints;
- first-class UX: automatic detection, zero manual mapping in the normal path, clear state, precise errors and guided recovery;
- comprehensive duplicate prevention across native events, agents, proxies, SDKs and provider receipts;
- provider-specific pricing and token-category handling rather than generic estimation when authoritative data exists;
- complete positive, negative, malformed, replay, retry, cancellation, cache, reasoning, tool, multimodal, subagent and privacy fixtures;
- platform-specific hardening on every materially used supported environment;
- signed release provenance, emergency disable, rollback and rapid re-certification;
- monitoring for upstream accounting or API changes and a defined owner for each T20 family.

A T20 integration may not be described as fully optimized while it knowingly uses a generic parser, generic alias mapping, avoidable polling, incomplete token categories, unresolved duplicate domains, manual setup in the normal case, or an unmeasured high-overhead path when a better supported mechanism exists.

## Optimization evidence gates

In addition to Hardened conformance, every T20 slot must have versioned evidence for:

1. **Accounting fidelity** — agreement with authoritative provider totals and category semantics across the full fixture corpus.
2. **Performance** — measured collection overhead, memory, CPU, disk, network, startup and end-to-end claim latency within approved budgets.
3. **Reliability** — soak, crash, restart, offline, upgrade, rollback and provider-change tests.
4. **Coverage depth** — all materially used agents, SDKs, API modes, cloud aliases and platforms for that model are either optimized or explicitly shown as unsupported.
5. **User experience** — automatic detection and normal operation require no model-specific manual configuration.
6. **Maintenance freshness** — upstream changes are detected, triaged and re-certified within the defined service window.

The exact numerical budgets are implementation evidence and must be recorded in the registry alongside each certification. A slot cannot pass the T20 launch gate using only qualitative claims.

## Selection method

T20 is refreshed at least monthly and before each release candidate. Selection uses a documented score with four inputs:

1. **Observed usage share — 40%**: privacy-safe aggregate usage across VibeMaxxing, public routing/usage datasets, and supported provider telemetry.
2. **Agent and coding relevance — 30%**: material use in coding agents, IDEs, orchestration systems, and autonomous workflows.
3. **Capability relevance — 20%**: current frontier or widely deployed capability for coding, reasoning, multimodal, tool-use, or long-context workloads.
4. **Provider and deployment diversity — 10%**: avoid a cohort dominated by one provider; include major hosted and local/open-weight ecosystems.

No provider may occupy more than five slots unless its measured usage share exceeds 35%. At least four T20 slots must cover open-weight or self-hostable model families when such families meet the relevance threshold.

The exact cohort and score inputs are versioned in `conformance/models/t20-model-registry-v1.json`. Selection changes are prospective and require a decision-register entry when they alter launch coverage.

## Bespoke Hardened profile

Every T20 family requires a provider- and version-specific profile covering:

- canonical model family and exact provider model IDs;
- aliases, dated versions, preview/stable channels, regional or cloud-hosted aliases, and retirement dates;
- tokenizer or provider-reported accounting authority;
- input, output, cache-read, cache-write, reasoning, image, audio, video, and tool-use accounting semantics;
- whether totals include or exclude hidden reasoning, cached tokens, system tokens, speculative tokens, or provider overhead;
- streaming, retries, partial failures, cancellations, batch APIs, background jobs, compaction, subagents, and parent/child attribution;
- pricing dataset provenance, currency, effective dates, batch discounts, cache pricing, and missing-price behavior;
- exact supported agents, SDKs, API modes, proxies, local runtimes, and platforms;
- source precedence and duplicate-accounting rules when several capture paths observe the same request;
- privacy-negative tests and forbidden-field canaries;
- version probes, signed fixture provenance, emergency downgrade, sunset, and re-certification rules.

## Hardened evidence gate

A T20 entry is Hardened only when all of the following pass for an exact version, mode, platform, and capture path:

1. authenticated provider receipt or equally strong source-bound evidence;
2. deterministic normalization and accounting vectors;
3. independent verifier agreement;
4. replay, duplicate, retry, cancellation, cache, reasoning, tool, multimodal, and batch tests applicable to that model;
5. privacy-negative and content-exfiltration tests;
6. alias/version detection and fail-closed behavior for unknown revisions;
7. pricing provenance validation where Estimated Cash Burn is displayed;
8. signed certification record with suite version, fixture commit, maintainer, tested date, and expiry.

Certification expires after 90 days, immediately upon a material provider accounting change, or when an exact model version is retired or altered without a stable version identifier.

## Launch gate

Public launch is blocked unless:

- the T20 registry contains exactly 20 active cohort slots;
- every slot has at least one non-expired T20 optimized Hardened certification for a materially used capture mode;
- every slot passes the optimization evidence gates, not only functional conformance;
- the combined cohort represents at least 80% of measured eligible competitive usage in the most recent 30-day selection window, or a documented exception is approved because the product has insufficient pre-launch usage;
- no T20 slot relies solely on generic fallback;
- unsupported modes and weaker evidence paths are explicitly labelled;
- the compatibility UI is generated from the registry rather than a handwritten marketing list.

After launch, a newly selected T20 model receives a 45-day certification window. Until certification passes, it is labelled `T20-pending` and cannot be presented as Hardened or fully optimized. A departing model retains its last honest certification label but no longer satisfies current T20 launch coverage.

## Initial planning candidates

The initial candidate pool must include the leading families from OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen, Mistral, Meta/Llama, Kimi/Moonshot, and major self-hosted inference ecosystems. The exact twenty must not be hardcoded in prose because availability, usage, and model naming change rapidly.

## Evidence boundary

This contract defines required coverage and optimization. It does not claim that any T20 model is currently certified or optimized. Certifications, performance budgets, compatibility matrices and maintenance evidence are implementation evidence and remain empty until exercised against real versions and capture paths.
