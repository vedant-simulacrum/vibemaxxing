# Adapter and VibeProof Implementation Contract

Status: normative planning contract; P-1140B data boundaries frozen, P-1140C wire protocol pending
Version: 2
Updated: 2026-07-24

## Authority split

Adapters observe source facts. The collector applies a digest-addressed accounting profile, produces mutually exclusive canonical token components, applies deterministic local rules and runs the privacy gate. A device signs facts and commitments only. The server verifier alone creates a `VerifierAppraisal`, awards a public evidence profile, determines ranking eligibility, interprets pricing and authorizes corrections.

A client field can never select Standard, Hardened, Imported, estimated price, eligibility, correction, or moderation outcome.

## Typed local stages

### SourceObservation

`packages/schemas/source-observation.schema.json` owns adapter-to-collector input. It is L0, ephemeral, local-only and never network serializable. Each observation binds the exact adapter artifact and manifest digests, registered source/version/platform/mode, source cursor and runtime generation, a non-content source-local reference, bounded wall-time observation, monotonic clock domain/generation, a typed token-observation variant, outcome/retry facts and an explicit L0 sensitivity marker.

An adapter may inspect raw source data only inside the non-networked source process. Raw data is discarded after normalization or the shortest configured diagnostic window. No raw alias, provider request ID, prompt, output, path, repository name, tool content or content-derived hash may enter the next stage.

### NormalizedAccountingEvent

`packages/schemas/normalized-event.schema.json` owns the collector-local durable L1 fact. Event and session IDs are collector-generated UUIDv7 values. The event binds exact adapter/certification/accounting-profile digests; registered source/provider/model IDs; monotonic and bounded wall-time observations; mutually exclusive canonical components; source-observed categories with containment labels; count authority; retry/outcome semantics; duplicate-domain scope; keyed local fingerprint; deterministic rule result and privacy policy result.

The event is not directly network serializable. `network_eligible=false` is a schema invariant. Unknown values are absent or explicitly enumerated; zero never means unknown.

### LocalDetectorResult

`packages/schemas/local-detector-result.schema.json` owns the optional L1 advisory result. It contains only bundle/runtime digests, feature version, input mode, fixed anomaly enums, confidence bucket, execution status, bounded resource buckets and deterministic precheck ID. It contains no prose, embedding, explanation, network address or authority over counts/evidence. Only its digest may be committed in a claim.

### IPC direction and retention

| Stage | Producer → consumer | Storage | Default retention | Network access |
|---|---|---|---|---|
| SourceObservation | adapter → collector | ephemeral adapter/collector memory | until normalization; never backup | forbidden |
| NormalizedAccountingEvent | collector → claim builder | encrypted local event store | user-configurable; excluded from sync store | forbidden as an object |
| LocalDetectorResult | detector sandbox → collector | encrypted local advisory store | aligned to contributing event | forbidden |
| EvidenceClaim | claim builder → sync/verifier | encrypted claim queue and outbound audit ledger | policy-bound | exact allowlist only |

`packages/schemas/local-control-v1.proto` is the sole local IPC envelope. It uses typed bodies for observation, acknowledgement, claim construction, queue/receipt summaries and local export/deletion. Opaque JSON, opaque serialized domain bytes and arbitrary metadata are prohibited. Peer role, ACL, connection nonce, monotonic message sequence, body limit, rate and deadline are checked before body materialization.

## Adapter artifact and capability contract

`packages/schemas/adapter-manifest.schema.json` binds:

- adapter artifact, manifest payload, source commit, build provenance and SBOM digests;
- exact source product/version, platform, capture mode and permissions;
- observed source categories and applicable accounting profiles;
- certification bundle, suite, source version and platform profile;
- a capability-derived maximum public profile;
- duplicate domains, lifecycle and emergency disable state.

The manifest digest covers the canonical manifest payload with the digest field omitted. Marketing or registry presence never raises the exercised ceiling. Unknown source versions, expired certification, artifact mismatch or missing profile fail closed to the highest lower explicitly allowed state.

## Accounting authority

`packages/schemas/accounting-profile.schema.json` and `conformance/accounting/accounting-profiles-v1.json` define immutable profile identity, source fields/units/authority, containment graph, mutually exclusive outputs, source-total authority, cache/reasoning/modality semantics, retry/cancellation/nested-execution policy, exact reconstruction and evidence ceiling.

Token Burn is the checked sum of a profile's mutually exclusive outputs. A source total or parent total that contains a subcategory is never added to that subcategory. Contradictions reject, quarantine or become private analytics exactly as the profile declares. Representative cloud-inclusive, cloud-exclusive, retry, cancellation and exact local-runtime cases live in `conformance/accounting/p1140b-accounting-cases-v1.json`.

## Time and delayed synchronization

Every event records a monotonic clock domain UUID, generation, start/end counters, bounded wall-time observation and uncertainty. Suspend, restore, reboot or rollback that invalidates monotonic continuity starts a new generation and is represented explicitly.

The server anchors accepted intervals to challenge, receipt and prior checkpoint state. Maximum delayed-sync age is a versioned policy of the exact source/accounting/platform profile; there is no universal 24-hour rule. Activity beyond the applicable bound is private analytics unless a named policy and continuity class explicitly admit it. Client wall time alone never selects a ranking period.

## Device lineage and source trust

`packages/schemas/device-lineage.schema.json` defines enrollment, dual-authorized rotation, lost-key recovery, restore/clone detection, retirement and requalification. Concurrent successors quarantine the lineage. A restored state older than the accepted checkpoint cannot silently continue. Lost-key recovery resets continuity; a new or recovered lineage does not inherit Hardened.

Every support/evidence claim binds exact artifact, provenance, certification and platform-profile digests. `packages/schemas/evidence-profile-policy-v1.json` keeps source, capture, accounting, key, continuity, environment and freshness dimensions independent and applies an explicit downgrade order.

## Pricing authority

Claims contain token facts and registered model IDs only. They never contain a pricing dataset, price, currency, cost estimate or correction authority.

`packages/schemas/pricing-interpretation.schema.json` owns the immutable server-side event-time alias resolution, pricing dataset/rule digest, typed category line items, quantity/unit/denominator, region/tier/mode conditions, rounding, canonical currency/scale and priced/unpriced result. Every value remains explicitly Estimated in product presentation.

## Privacy egress contract

`packages/schemas/egress-allowlist-v1.schema.json` validates the registry at `packages/schemas/egress-allowlist-v1.json`. A field absent from that registry is denied. The registry records type, encoded-size ceiling, semantic owner, L2 classification, source process, destination, retention policy and positive/negative fixture identifiers.

The privacy gate runs after normalization and optional detector work, immediately before canonical claim serialization and signing. `conformance/privacy/p1140b-boundary-canaries-v1.json` covers adapter, IPC, local store, detector, claim, HTTP, telemetry, notification, moderation and export boundaries. Forbidden content or an unregistered field rejects before egress.

## Evidence appraisal

The server evaluates the independent dimensions and named minimums in `packages/schemas/evidence-profile-policy-v1.json`. Any fatal privacy, artifact, accounting or continuity contradiction rejects or quarantines. Failure to meet Hardened evaluates Standard; failure to meet Standard becomes private analytics. E5 remains Imported/private only.

The signed claim carries facts and commitments. P-1140C will freeze its deterministic CBOR/COSE representation, checkpoint, replay, batch, rotation, gap and correction records. Until then, `packages/schemas/vibeproof-claim-v1.cddl` remains blocked and must not generate codecs.

## P-1140C boundary

P-1140C must not change the P-1140B authority split or reintroduce client-owned evidence/pricing, raw aliases, request IDs, arbitrary extensions, opaque IPC payloads, overlapping token totals or universal lateness. It owns only the mutually complete wire/state representation and exact protocol vectors.
