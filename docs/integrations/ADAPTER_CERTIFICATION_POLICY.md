# Adapter Certification Policy

An adapter is not publicly supported until every mandatory artifact exists.

## Required manifest

- adapter ID and display name
- agent vendor and product
- exact tested versions and modes
- supported operating systems and architectures
- observation surface
- token source and source precedence
- evidence class
- privacy field allowlist
- explicit forbidden-field list
- deduplication identity strategy
- upgrade detection strategy
- failure/degradation behavior
- last conformance timestamp
- maintainer and review owner

## Required executable evidence

- installation/version probe
- synthetic qualifying session
- authoritative/structured token reconciliation
- cache/reasoning/retry fixtures where supported
- no-content negative tests
- duplicate observation test
- crash and restart test
- unsupported-version behavior
- upgrade fixture from at least one prior version
- performance overhead result

## Certification states

The five values this section previously listed conflated two different things: where a certification is in its life, and how strong the evidence it produces may be. `experimental` and `suspended` are lifecycle; `standard`, `hardened` and `imported` are evidence classes owned by D-008 and D-143. They are separated here under D-388, and the separation is what makes it possible to say that a suspended adapter still has an evidence ceiling.

**Lifecycle** is the `source-certification` machine in `packages/schemas/state-machine-registry-v1.json`, persisted by `source_certifications`:

| State | Meaning |
|---|---|
| `candidate` | a tuple has been submitted and nothing has been run |
| `testing` | the conformance suite is running against the exact tuple |
| `active` | a signed passing result exists and the tuple is advertised |
| `degraded` | the source surface changed and the tuple no longer produces its full evidence |
| `suspended` | withdrawn by the release authority pending a new result |
| `expired` | the validity interval ended |
| `superseded` | a newer exact tuple replaced it |
| `retired` | terminal; the tuple is never advertised again |

**Evidence ceiling** is the strongest class a claim under the tuple may reach: `hardened`, `standard` or `private-analytics`. `imported` is not a ceiling — a historical import is excluded from competition by D-007 and D-087 regardless of any certification, so it is a property of the record rather than of the tuple.

Only `active` may exceed `private-analytics`. That is a check constraint on `source_certifications` and a schema constraint in `packages/schemas/certification-result-v1.schema.json`, not a rule somebody applies at query time, because a registry that advertised a planned, expired or suspended certification is exactly the overclaim the binding rules forbid.

### Nothing here is certified

Every tuple this repository can reach is `candidate`. No conformance suite has been run against any exact tuple, no result bundle has been signed, and no row in `source_certifications` has ever left the initial state. This section specifies a lifecycle; it is not evidence that anything has moved through it, and `PF-016` closed the specification without asserting otherwise.

### What an uncertified capture looks like

A capture taken under no certified tuple is the ordinary case today, not an error, and every layer now says so in the same way. `packages/schemas/normalized-event.schema.json` admits a null `certification.bundle_sha256` and pins such an event to a `private-analytics` disposition; `packages/schemas/evidence-bundle-v1.cddl` already called the same field "nil while uncertified"; `producer-accounting-binding-v1.schema.json`, `appraisal-result-v1.schema.json` and `openapi-v1.yaml` already admitted the null.

The event schema was the one out of step, and the cost was concrete: it required a 64-hexadecimal digest with no null admitted while every producer binding in this repository carries null, so no `NormalizedAccountingEvent` could be constructed from any OTLP capture this repository can actually take, and the only fixture that filled the field used sixty-four `f` characters. `packages/schemas/accounting-profile-otel-v1.json` recorded that as a computed contradiction and blocked the field's derivation behind it; both are now resolved rather than described, and `validate_otel_accounting_profile` reads the admissibility out of the schema so neither the gap nor the declaration of it can outlive the other.

Admitting the null is a representation, never a permission. The `private-analytics` pin is in the schema rather than in a collector, because a collector that forgets to set the disposition is indistinguishable from one that decided to.

### Where the lifecycle is published

The eight states are one vocabulary in three places: the `source-certification` machine, the `source_certifications.state` check constraint, and `evaluated.certification_state` on `AppraisalSummary` in `packages/schemas/openapi-v1.yaml`. The API third did not exist — the document published which certification a claim was appraised under, by digest, and nothing about whether that certification was still active when it was read. Those are different facts and an appeal argues from both: a claim capped at private analytics because its tuple had expired is entitled to be told that rather than to infer it from a ceiling.

The published enumeration is the machine's eight states plus `uncertified`, which is not a state of the machine. A capture bound to no certification has no aggregate to be in a state, and admitting the value is what lets the absence be stated instead of read out of a null.

## Signed result bundle

`packages/schemas/certification-result-v1.schema.json` is the record of one run, and `certification_results` is its persistence owner. It is append-only: a later run is a new row and never an edit, because the appraisal of a claim accepted under an earlier result has to stay reproducible.

A result binds the suite manifest by digest under D-242, so it cannot claim a pass against a suite whose cases moved afterwards. It counts negative cases separately from total cases, and a passing result with zero negative cases is unrepresentable — a suite that has never failed carries no information about the thing it passed. The signature is COSE_Sign1 with algorithm -19 Ed25519 under D-190.

Each case is bound by digest too, not only by identifier. The manifest digest binds the *set* of cases; a case's own `case_sha256` binds that case's identifier, fixture bytes and declared expectation. The two answer different questions, and only the second notices a fixture rewritten under an unchanged manifest — a result that recorded the manifest digest alone would report a pass against cases that are no longer the ones it ran. D-058 makes trust digest-addressed for this reason: an identifier is a name.

The three counts are derived from the case list rather than believed. `cases` is required and non-empty, and `validate_certification_contracts` recomputes `case_count`, `negative_case_count` and `failed_case_count` from it and refuses a result whose declared numbers differ. Unbound, the way to turn a failing suite into a passing one was to delete the entry that failed: `failed_case_count` was whatever the runner wrote, and `negative_case_count` — the number the `certification_results` check constraint reads to refuse an untested pass — improved as cases were removed from the thing it counts.

Revocation is `revoked_at` with a reason code, and the row is retained rather than deleted, because a claim accepted under a revoked certification still names its tuple digest and has to stay explainable.

## The tuple being certified

`packages/schemas/compatibility-tuple-v1.schema.json` is what a certification is about, and D-387 records why each dimension is inside it. The manifest list above describes what an adapter declares; the tuple is what the product advertises against, and the two are not the same document. A declaration is a claim by the adapter author. A tuple is an identity, addressed by digest under D-058, that a signed result attaches to.

## Fail-safe degradation

An adapter must stop competitive submission or downgrade explicitly when its parser, telemetry contract, version, or evidence surface changes. It must never continue with zeroed categories, guessed totals, or inflated evidence labels.
