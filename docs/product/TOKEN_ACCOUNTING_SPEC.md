# VibeProof Token Accounting Specification v1

Status: Normative draft. Must be implemented with cross-provider golden fixtures before competitive beta.

## Goals

- Deterministic counting.
- No overlapping-category double counting.
- Honest distinction between authoritative and estimated usage.
- Reproducible Cash Burn estimates.
- Stable semantics across adapters.

## Canonical fields

Every normalized operation may contain:

- `operation_id`
- `provider`
- `agent`
- `model`
- `started_at_bucket`
- `ended_at_bucket`
- `input_tokens_total`
- `output_tokens_total`
- `cache_read_input_tokens`
- `cache_write_input_tokens`
- `reasoning_output_tokens`
- `tool_tokens`
- `other_billable_tokens`
- `billable_tokens_total`
- `count_source`
- `count_confidence`
- `category_relationships`
- `provider_usage_schema_version`
- `adapter_version`

No content fields are permitted.

## Source precedence

1. Provider/API authoritative billable usage attached to the operation.
2. Agent-produced structured usage derived directly from provider response.
3. Trusted local proxy measurement.
4. Offline tokenizer estimate.
5. Unknown.

Lower-precedence sources must never override a higher-precedence source for the same operation.

## Total calculation

`billable_tokens_total` is used when the provider supplies an authoritative non-overlapping total.

Otherwise, compute from non-overlapping leaf categories only. Category metadata must state whether a category is:

- `exclusive`
- `included_in_input`
- `included_in_output`
- `included_in_total`
- `informational_only`

Cached input is normally included in total input. Reasoning/thought output is normally included in total output when the provider reports it that way. The normalizer must not add them again.

## Retries and failures

- Count each provider operation that reports billable usage.
- A client retry that never reaches a provider and reports no usage counts zero.
- A failed provider operation counts only the authoritative billable usage reported.
- Streaming partials are one operation unless the provider bills them as separate operations.

## Compaction and context reuse

Context compaction is not itself a token event. The resulting model operation counts according to provider usage. Cache reads and writes retain their categories for Cash Burn but do not increase Token Burn beyond the provider-reported total.

## Subagents and nested agents

Every provider operation may count, including subagents, but the same provider operation must have one canonical observation identity. Multiple adapters observing the same operation must deduplicate through source identifiers, commitments, timing, device, model, and operation metadata. If safe deterministic deduplication is impossible, the weaker duplicate observation is quarantined rather than counted twice.

## Tool usage

Tool calls, file operations, and shell commands are event counts, not tokens. `tool_tokens` counts only when the provider exposes a distinct billable tool-token category. Tool arguments and outputs are forbidden from claims.

## Multimodal usage

Provider-reported token-equivalent units may be included when the provider reports them as billable tokens. Non-token units such as images, seconds, searches, or storage must remain separate pricing units and do not inflate Token Burn unless the provider explicitly maps them to tokens.

## Local models

Locally generated model tokens may count toward Token Burn only when measured through a reproducible tokenizer/model pair and labeled estimated or local-measured. Cash Burn is unavailable by default or displayed as an explicitly hypothetical selected API equivalent.

## Subscription usage

Token Burn may use authoritative counts from subscription-backed agents. Cash Burn remains API-equivalent and never claims actual payment.

## Evidence classes

- `authoritative`: provider or cryptographically source-bound usage.
- `structured`: agent-produced stable structured usage.
- `observed`: live local observation with deterministic normalization.
- `estimated`: tokenizer or heuristic estimate.
- `imported`: retrospective private analytics only.

## Versioning

Any semantic change increments `accounting_spec_version`. Claims retain the version used. Cross-version rankings require a documented compatibility decision and migration evidence.
