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

The five values this section previously listed conflated two different things: where a certification is in its life, and how strong the evidence it produces may be. `experimental` and `suspended` are lifecycle; `standard`, `hardened` and `imported` are evidence classes owned by D-008 and D-143. They are separated here under D-328, and the separation is what makes it possible to say that a suspended adapter still has an evidence ceiling.

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

## Signed result bundle

`packages/schemas/certification-result-v1.schema.json` is the record of one run, and `certification_results` is its persistence owner. It is append-only: a later run is a new row and never an edit, because the appraisal of a claim accepted under an earlier result has to stay reproducible.

A result binds the suite manifest by digest under D-242, so it cannot claim a pass against a suite whose cases moved afterwards. It counts negative cases separately from total cases, and a passing result with zero negative cases is unrepresentable — a suite that has never failed carries no information about the thing it passed. The signature is COSE_Sign1 with algorithm -19 Ed25519 under D-190.

Revocation is `revoked_at` with a reason code, and the row is retained rather than deleted, because a claim accepted under a revoked certification still names its tuple digest and has to stay explainable.

## The tuple being certified

`packages/schemas/compatibility-tuple-v1.schema.json` is what a certification is about, and D-327 records why each dimension is inside it. The manifest list above describes what an adapter declares; the tuple is what the product advertises against, and the two are not the same document. A declaration is a claim by the adapter author. A tuple is an identity, addressed by digest under D-058, that a signed result attaches to.

## Fail-safe degradation

An adapter must stop competitive submission or downgrade explicitly when its parser, telemetry contract, version, or evidence surface changes. It must never continue with zeroed categories, guessed totals, or inflated evidence labels.
