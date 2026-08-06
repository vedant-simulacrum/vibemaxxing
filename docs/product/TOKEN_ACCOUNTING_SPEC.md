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

## Arithmetic

`packages/schemas/accounting-arithmetic-v1.json` is the machine owner of everything below, and `conformance/accounting/arithmetic-vectors-v1.json` is its executable form. `scripts/repository/validate_planning_artifacts.py` recomputes every vector from the arithmetic record and the accounting profile rather than reading the recorded answer back, so a vector whose expectation is wrong fails the suite.

### Domain and overflow

Every quantity is an unsigned 64-bit integer carried as a decimal string, matching the `uint64` the claim encodes. D-193 forbids floats, so nothing in this path is inexact. Addition and subtraction are checked: a result outside `0 .. 18446744073709551615` rejects. It does not saturate and it does not wrap, because both return a plausible-looking number for an impossible one and neither is distinguishable downstream from a real total.

### Order of operations

An accounting profile declares its source fields, its containment edges, and — through `component_map` — which canonical component each source field resolves to. Evaluation runs in this order and stops at the first rejection:

1. **Placement.** Every source field the reading carries must be one the profile declares. A field the profile does not declare rejects; dropping it would produce a total that looks complete and is not.
2. **Containment.** Each container is reduced by its members with a checked subtraction, containers before members. A member larger than its container rejects: the source asserted a containment its own numbers deny. A member with two containers rejects, because subtracting it once means choosing a container and that choice is a hidden semantic mapping. A containment cycle rejects.
3. **Projection.** Each reduced source field is added into its canonical component.
4. **Summation.** The seven canonical components are summed in the fixed order `input_uncached`, `output_visible`, `cache_read`, `cache_write`, `reasoning`, `multimodal_input`, `multimodal_output`. Addition over a bounded checked domain is not associative with respect to failure — a different order overflows at a different step — so the order is fixed rather than left to an implementation.

A component the profile does not enable is written `0` and read as *the profile declares this unavailable*. That is a different fact from a category the source did not report, which is absent and never encoded as zero.

### Profile digest

`accounting_profile_sha256` is a signed claim field. Under D-241 its preimage is the profile object with `content_sha256` omitted, encoded as RFC 8949 core deterministic CBOR — the same profile the signed claim uses — and hashed with SHA-256. The preimage admits integers, text strings, arrays, maps and `null`; it refuses floats under D-193 and refuses booleans, so a two-valued field is a named enum and stays legible inside the digest.

### Estimated Cash Burn

Unit prices are integers in pricing-currency nano-units per token. `units × unit_price_nano` is an exact integer product. The exact products are summed first and the sum is divided by 1000 once, round-half-even, to reach a pricing-currency micro-unit estimate. Rounding once at the end is what makes the estimate reproducible; rounding each component before summing makes the total depend on how the categories were grouped. An unknown price produces `unpriced` and never zero.

### Retries, cancellation and nested execution

`retry_policy`, `cancellation_policy` and `nested_execution_policy` in `packages/schemas/accounting-profile.schema.json` are enums whose behaviour D-242 defines in the arithmetic record. Each retry value names which attempts count, whether a distinct model execution is required, what identifies an attempt, and which control prevents the double count. Each cancellation value names the counted quantity and the treatment of an unknown remainder, which is absent and never zero. Each nested-execution value names child attribution, whether a parent total contains its children, and which control deduplicates.

### Corrections

An accepted total is immutable. A correction is an append-only contribution with a direction of `add` or `retract` and an unsigned magnitude, because the domain is unsigned and a negative integer has no encoding in it. The composed value is the checked sum of additions minus the checked sum of retractions. Retractions summing past the additions they correct reject rather than clamping to zero, which would produce a total no sequence of contributions explains. A correction rebuilds a period into a new generation that supersedes the previous one; it never edits a published one.

## Retries and failures

- Count each provider operation that reports billable usage.
- A client retry that never reaches a provider and reports no usage counts zero.
- A failed provider operation counts only the authoritative billable usage reported.
- Streaming partials are one operation unless the provider bills them as separate operations.

## Compaction and context reuse

Context compaction is not itself a token event. The resulting model operation counts according to provider usage. Cache reads and writes retain their categories for Cash Burn but do not increase Token Burn beyond the provider-reported total.

## Subagents, nested agents, and multiple observers

Every provider operation may count, including subagents, but one provider operation counts once. `packages/schemas/observer-equivalence-v1.json` is the machine owner of when two observations are observations of one execution, and `conformance/accounting/dedup-vectors-v1.json` is its executable form.

The server decides. Under D-249 the client contributes facts and no verdict: it does not choose the commitment preimage, the equivalence scope, the equivalence class, the survivor, or the disposition.

### The preimage carries source-derived facts only

`duplicate_domain_commitment` is a keyed commitment the collector computes, and the rule fixes what goes into it. Every observer-derived input — collector artifact digest, collector instance, adapter instance, process identifier, device-local random, receive time, installation nonce — is forbidden. Including any one of them guarantees that two observers of a single execution produce different commitments, and a commitment that never collides is a client deciding for itself that its observation is not a duplicate. The key is scoped to the device lineage rather than to an installation, for the same reason.

### Three equivalence classes

- **Strong.** The source names the execution and the observer reads that name. Any two observers that can read it produce the same commitment whatever mode they are in, so a direct observation and a local gateway observation of one request collide and one of them counts.
- **Source-cursor.** The source exposes no execution name but does expose an ordered cursor that belongs to it rather than to the observer — an attribute-set key with a counter start time and an export ordinal, for instance. Two observers in one mode watching one source runtime read the same cursor and collide.
- **Weak.** No source-derived identity of any kind is available. Nothing distinguishes a duplicate from a distinct execution, so the observation is private analytics and never competes. A session file the source rewrites after the fact is this class, because the ordinal an observer read can change under it.

### Exclusivity

The exclusivity unit is one device lineage, one source runtime, one runtime generation. Where two capture channels cover one unit and their modes rank differently, the stronger mode survives and the weaker record is discarded rather than retained alongside; the two are never summed. Where two collector instances share a mode, precedence decides nothing, and the resolution is the honest one: if their commitment sets are identical they observed the same executions and collision deduplicates them to a single counted event, and if the sets differ the unit quarantines. A wrong quarantine is recoverable through appeal; a double count is a scoring defect.

Subagent and parent executions carry different source-assigned identities, so their commitments differ and both count. Distinct commitments mean distinct executions when the observers agree on everything else, and the exclusivity rule is what makes that inference safe.

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
