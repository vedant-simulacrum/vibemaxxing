# T20 Model Hardening Contract

Status: normative planning contract
Updated: 2026-07-19

## Requirement

VibeMaxxing must provide bespoke Hardened coverage for a rolling cohort of the 20 most materially relevant model families before public launch. Generic agent, proxy, OpenTelemetry, ACP, wrapper, gateway, or import support does not satisfy the T20 requirement.

The cohort is called **T20**. A T20 slot represents a model family plus exact provider/version records. A family may contain multiple aliases or endpoints, but Hardened status is awarded only to exact exercised versions and modes.

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
- every slot has at least one non-expired Hardened certification for a materially used capture mode;
- the combined cohort represents at least 80% of measured eligible competitive usage in the most recent 30-day selection window, or a documented exception is approved because the product has insufficient pre-launch usage;
- no T20 slot relies solely on generic fallback;
- unsupported modes and weaker evidence paths are explicitly labelled;
- the compatibility UI is generated from the registry rather than a handwritten marketing list.

After launch, a newly selected T20 model receives a 45-day certification window. Until certification passes, it is labelled `T20-pending` and cannot be presented as Hardened. A departing model retains its last honest certification label but no longer satisfies current T20 launch coverage.

## Initial planning candidates

The initial candidate pool must include the leading families from OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen, Mistral, Meta/Llama, Kimi/Moonshot, and major self-hosted inference ecosystems. The exact twenty must not be hardcoded in prose because availability, usage, and model naming change rapidly.

## Evidence boundary

This contract defines required coverage. It does not claim that any T20 model is currently certified. Certifications are implementation evidence and remain empty until exercised against real versions and capture paths.