# VibeProof Token Accounting Specification v1

Status: Normative draft. Must be implemented with cross-provider golden fixtures before competitive beta.

## Goals

- Deterministic counting.
- No overlapping-category double counting.
- Honest distinction between authoritative and estimated usage.
- Reproducible Cash Burn estimates.
- Stable semantics across adapters.

## Canonical fields

`packages/schemas/normalized-event.schema.json` is the machine owner of the normalized record and `packages/schemas/source-observation.schema.json` is the machine owner of what an adapter hands it. This section is their prose, not a second vocabulary.

Until PF-017 it was a second vocabulary. It listed eighteen field names — `operation_id`, `provider`, `agent`, `model`, `started_at_bucket`, `ended_at_bucket`, `input_tokens_total`, `output_tokens_total`, `cache_read_input_tokens`, `cache_write_input_tokens`, `reasoning_output_tokens`, `tool_tokens`, `other_billable_tokens`, `billable_tokens_total`, `count_source`, `count_confidence`, `category_relationships`, `provider_usage_schema_version` and `adapter_version` — and **not one of them existed in any schema in this repository**. The two documents answered the same question and only one of them was executable, which is how `operation_id` came to be a field the specification named, the schemas had never had, and reconciliation needed.

The record binds five groups of facts.

- **Identity of the record.** `event_id` and `session_id`, both collector-minted, and `parent_event_id` for this collector's own event graph. None of the three survives being observed by a second collector.
- **Identity of the execution.** `operation.identity_source`, `operation.operation_ref` and `operation.parent_operation_ref`. The discriminator comes first because it says how the identity was obtained: `source-assigned` when the source named the execution, `source-cursor-derived` when it exposed only an ordered cursor that belongs to it, `absent` when there is no source-derived identity at all. The schema refuses `absent` beside a populated reference and refuses a populated discriminator beside a null one, so a collector cannot supply an identity it did not read, and it pins an `absent` event to private analytics because that is the weak class of `packages/schemas/observer-equivalence-v1.json` and the weak class never competes.
- **Identity of the observer.** `observer.collector_instance_id` and `observer.adapter_instance_id`, with `certification.capture_mode`. Mode and collector instance are the exclusivity channel identity the equivalence rule names, and the rule's tied-channel case — two collector instances in one mode over one source runtime — could not be evaluated at all while the event carried neither. Both observer fields are listed in that rule's forbidden commitment preimage inputs, and they are forbidden there for the same reason they are required here: an observer-derived commitment never collides, and a commitment that never collides is a client deciding for itself that its observation is not a duplicate.
- **What was read.** `reading.accumulation`, `reading.reset_detection` and `reading.series_generation`, then `canonical_tokens`, `source_observed_categories`, `count_authority` and `reconstruction_method`. `accumulation` is the flag that separates a running total from an increment; an OTLP counter is cumulative by default, and a receiver that adds two cumulative readings has counted everything before the second one twice. A cumulative reading is not an accounting input until it has been differenced, and `packages/schemas/accounting-arithmetic-v1.json#reconciliation` rejects one that has not been.
- **What was decided.** `certification`, `outcome`, `retry`, `duplicate_domain`, `local_fingerprint`, `rule_result`, `privacy_scan`, `local_detector_commitment` and `network_eligible`, which is always false.

No content fields are permitted, and `additionalProperties` is false on both records, so the prohibition is a refusal rather than an instruction.

### Outcome

The observation vocabulary and the event vocabulary shared three values and each held two the other did not. An observation could report `aborted-unknown` and `unknown`; an event could record `aborted-known` and `quarantined-unknown`; no mapping was declared anywhere, so `aborted-unknown` had to be written as `aborted-known`, which inverts the fact the source reported.

`packages/schemas/accounting-arithmetic-v1.json#outcome_normalization` now declares the whole map. `aborted-unknown` is carried through unchanged, `unknown` becomes `quarantined-unknown` because quarantining is the normalizer's decision rather than the source's report, and `aborted-known` is declared as normalizer-assigned: it is reached only from an `aborted-unknown` observation plus a `count-reported-consumption` cancellation policy, and no source can hand it over. The validator checks the map is total over the observation enum, lands inside the event enum, and that every event value the map does not reach carries a reason — so a missing case and a stale excuse both fail.

## Source precedence

The precedence list here was five prose levels — provider, agent-produced, trusted local proxy, offline tokenizer, unknown — and it resolved to nothing. `count_authority` has four values, `packages/schemas/observer-equivalence-v1.json` ranks nine observation modes, and there was no mapping between any two of the three. It has been replaced with the two orders that are executable, in the sequence reconciliation applies them.

**Count authority** ranks who is being trusted, and is the declaration order of `count_authority` in `packages/schemas/normalized-event.schema.json`:

1. `provider-reported`
2. `runtime-reported`
3. `source-reported`
4. `exact-reconstruction`

This is not an order of precision. An exact tokenizer reconstruction is the most precise of the four and ranks last because it is the only one the participant's own machine produces; ranking it above a provider figure would make the strongest evidence class the one with no external witness. `packages/schemas/accounting-profile.schema.json` spelled the fourth value `reconstructed` while nine other artifacts spelled it `exact-reconstruction`, two spellings with no overlap, so a profile's declared authority could not be ranked at all; the profile now uses the one spelling and the validator compares the two vocabularies by set equality.

**Observation mode** ranks the channel, and is `precedence_rank` in `packages/schemas/observer-equivalence-v1.json`: native-event, official-hook, extension-api, local-runtime, ACP, OTel, proxy, wrapper, live-log. The same nine values are the `execution_mode` of an observation, the `capture_mode` of an event and both mode vocabularies of `packages/schemas/source-receipt-v1.schema.json`. `acp` was missing from the observation schema while `generic-acp-v1` was a registered producer binding, so an ACP observation was unrepresentable in the schema every ACP adapter has to write; `capture_mode` on the event was an unconstrained slug, so an event could name a mode with no precedence rank and the survivor rule would have had nothing to order it by.

Lower-precedence sources never override a higher-precedence source for the same operation, and are never added to it. See **Reconciliation** below for what happens when the precedence does not separate them.

## Total calculation

Token Burn is the checked sum of the mutually exclusive canonical components the profile enables. A source total is an observation rather than a universal addend: `source_total_authority` on the profile states whether it is authoritative and exclusive, authoritative and containing, diagnostic-only, or absent, and `containment_edges` state which categories are contained in which. A contained category is subtracted from its container with a checked subtraction before both appear as canonical outputs, and `containment` on each `source_observed_categories` entry records what the source said about it: `exclusive`, `contains-other-categories`, `contained-by-other-category` or `diagnostic-total`.

Cached input is normally included in total input, and reasoning output is normally included in total output when the provider reports it that way. The containment graph is what says so for a given profile, and the normalizer never adds them again.

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

`accounting_profile_sha256` is a signed claim field. Under D-261 its preimage is the profile object with `content_sha256` omitted, encoded as RFC 8949 core deterministic CBOR — the same profile the signed claim uses — and hashed with SHA-256. The preimage admits integers, text strings, arrays, maps and `null`; it refuses floats under D-193 and refuses booleans, so a two-valued field is a named enum and stays legible inside the digest.

### Estimated Cash Burn

Unit prices are integers in pricing-currency nano-units per token. `units × unit_price_nano` is an exact integer product. The exact products are summed first and the sum is divided by 1000 once, round-half-even, to reach a pricing-currency micro-unit estimate. Rounding once at the end is what makes the estimate reproducible; rounding each component before summing makes the total depend on how the categories were grouped. An unknown price produces `unpriced` and never zero.

### Retries, cancellation and nested execution

`retry_policy`, `cancellation_policy` and `nested_execution_policy` in `packages/schemas/accounting-profile.schema.json` are enums whose behaviour D-262 defines in the arithmetic record. Each retry value names which attempts count, whether a distinct model execution is required, what identifies an attempt, and which control prevents the double count. Each cancellation value names the counted quantity and the treatment of an unknown remainder, which is absent and never zero. Each nested-execution value names child attribution, whether a parent total contains its children, and which control deduplicates.

### Reconciliation

Several readings can describe one operation: a provider figure and a proxy measurement, two collectors watching one runtime, an OTLP export and an official hook. Until PF-018 nothing said what to do with them, so the answer was whichever reading an implementation processed last. `packages/schemas/accounting-arithmetic-v1.json#reconciliation` owns the rule and `conformance/accounting/reconciliation-vectors-v1.json` is its executable form.

Reconciliation is **per operation**, grouped on the whole exclusivity unit — device lineage, source runtime, runtime generation — plus the operation reference. The generation is in the key because a source that restarts may reuse an operation identifier, and a key without it would discard the second execution as a duplicate of the first.

Within a group:

1. A reading whose `identity_source` is `absent` is not reconciled with anything, because nothing distinguishes it from a duplicate. It is private analytics. Its tokens are real and the participant keeps them; they do not compete. Every retrospective import has this shape.
2. A cumulative reading rejects. It is not an accounting input until it has been differenced against the previous reading of its series generation.
3. The highest count authority in the group survives. Every lower-authority reading is **superseded**, never averaged with the survivor and never added to it. Two readings of one operation are two descriptions of one consumption.
4. If authority does not separate them and their canonical components agree, one is counted and the rest are superseded. Observation-mode precedence decides which, and the choice does not change the total.
5. If authority does not separate them and their canonical components disagree, the operation takes the disposition its accounting profile declared in advance through `contradiction_policy`: reject, quarantine, or private analytics. **Selecting a survivor between two equally authoritative contradicting sources is forbidden**, because the accepted total would then depend on which reading was seen first.

The result is a function of the readings and never of their order. Ties break on authority rank, then observation-mode precedence rank, then the reading's own canonical bytes; array position, arrival order, receive time and local wall-clock time are named as forbidden inputs and the vector schema refuses to be able to carry any of them, because a field a vector can carry is a field a tie can be broken on. The validator evaluates every vector under **every permutation** of its readings and requires one result.

Nothing in this section asserts that any capture tuple is certified. None is: every producer binding in `conformance/accounting/producer-bindings-v1.json` is `candidate` or `uncertified` and every effective ceiling is private analytics. Reconciliation decides which reading counts; certification decides whether the counted figure may compete, and it is a separate gate that is closed today for every mechanism this repository can capture.

### Bounds

The integer domain says what a `uint64` can hold. Two further bounds say what is plausible, and both refuse rather than report the ceiling.

| Bound | Value | What happens |
|---|---:|---|
| One event's Token Burn | 100,000,000 | the event is rejected |
| A period accumulator | 18,446,744,073,709,551,615 | the event that would exceed it is rejected; the period total is unchanged |

One hundred million tokens in a single model operation is not a measurement. The largest published context window is under ten million and the seven canonical components of one operation cannot together reach ten times that, so a figure above the bound is a misread counter — most often a cumulative reading admitted as an increment, which is exactly the confusion `reading.accumulation` now makes visible. A saturating implementation would report the bound itself, and nothing downstream distinguishes that from a real total.

Neither bound caps what a participant may accumulate. Token Burn is the raw metric of record: accepted, immutable and unnormalized. The per-event bound refuses one impossible event and the period bound refuses one event that would leave the integer domain; clipping an accumulated period figure would be normalization under another name, and `capping` is recorded as forbidden in the arithmetic record for that reason.

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

The server decides. Under D-269 the client contributes facts and no verdict: it does not choose the commitment preimage, the equivalence scope, the equivalence class, the survivor, or the disposition.

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
