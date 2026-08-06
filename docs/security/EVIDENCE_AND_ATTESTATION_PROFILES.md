# Evidence and Attestation Profiles

Status: normative planning contract; P-1140B appraisal policy frozen, P-1140C wire binding pending.
Updated: 2026-08-06

## Purpose

VibeProof establishes that a registered device key signed a canonical evidence claim and that the server verifier accepted or rejected it under defined accounting, privacy, compatibility, continuity and policy rules.

It does not by itself prove:

- that a provider issued a usage record;
- that the local source was uncompromised;
- that a user-controlled machine was not cloned;
- that an OAuth account maps to one unique human.

Consumer-facing states remain Standard, Hardened and Imported. The server verifier awards Standard or Hardened through a named, versioned profile. The client submits facts and cannot select its final state.

## Machine-readable appraisal policy

`packages/schemas/evidence-profile-policy-v1.json` is the planning authority for the independent dimension enums, named profile minimums, fatal conditions and downgrade order. The client does not serialize a desired public state. The server stores an immutable `VerifierAppraisal` that references the exact policy and implementation digests; changing policy creates a new appraisal or explicit re-evaluation record rather than mutating a claim.

Evaluation is dimensional: a stronger key cannot compensate for contradictory accounting, and strong source authority cannot bypass privacy, continuity or artifact failures. Fatal conditions reject or quarantine. Failure to satisfy Hardened evaluates Standard; failure to satisfy Standard becomes private analytics. E5 remains Imported/private only.

`packages/schemas/appraisal-policy-v1.json` is the exact policy an appraisal is produced under. It binds the file above by path and content digest rather than copying its enums, so there is one dimension authority and a change there changes the bundle's identity. What it adds is what evaluating a claim needs and that file does not carry: the wire ordinals, the validity interval, the verifier implementation digest, the supersession chain, the persistence binding for the appraisal aggregate, and the D-078 limb refinement.

The `source` enum in the owning file carries a single `E1` value. The bundle's `dimension_refinements` splits it into E1-S and E1-R with their availability, whether each binds an individual claim, whether each alters raw score, and whether each reaches Hardened — none of which they do. The base enum is untouched; the refinement is what the appraisal record and the wire use. The split is therefore machine-readable rather than prose-only, and the planning validator fails when the refined vocabulary and the appraisal schema's enum disagree.

## Independent dimensions

Every verifier appraisal records independently:

1. source authority;
2. capture binding;
3. accounting authority;
4. device-key protection;
5. continuity strength;
6. environment assurance;
7. freshness/time uncertainty;
8. exact compatibility and certification evidence;
9. deterministic integrity-rule result;
10. anomaly disposition, when applicable.

The first seven are the classification dimensions and carry an enumerated value each. The last three are the evidence those values were read from and are recorded beside them rather than composed into them.

No stronger value in one dimension silently upgrades a failed mandatory requirement in another.

## The appraisal record

`packages/schemas/appraisal-result-v1.schema.json` is the one appraisal record. Before it, three authorities described this aggregate three ways and SR-017 cited the disagreement: `verifier-appraisal-v1` in `packages/schemas/vibeproof-claim-v1.cddl` carried the seven dimensions as unnamed integers, the evidence policy enumerated the same seven as names with no ordinals, and `packages/schemas/planning-schema.sql` stored three states that appear in neither.

The record carries the seven dimensions by name, the evaluated certification bundle, deterministic rule bundle, accounting profile, observer-equivalence rule and anomaly disposition beside them, and four things no previous authority held: the digest of the exact signed claim bytes that were assessed, the digest of the device-local evidence bundle that explains them, a validity interval, and a supersession chain with the trigger that produced it. `appraisal-policy-v1.json` binds each dimension name to the integer the CDDL declares for it, and the planning validator fails when an ordinal leaves the CDDL range, when the ordinals are not dense from zero, or when the JSON enum and the policy vocabulary diverge. The CBOR appraisal and the JSON appraisal are one record rather than two that happen to share a field count.

The SQL half of SR-017 is not closed by this. `appraisal-policy-v1.json` names the three columns no other authority uses as `dropped_columns` and each field the table cannot hold as `unbound_fields`, and both lists are checked against the DDL: the validator fails if a dropped column disappears or an unbound field lands, so the remaining distance is machine-visible and closing it requires moving an entry rather than editing prose.

The appraisal assesses the quality of a self-report. Under D-100 it never records that a provider confirmed a figure, because no provider offers an individual-account path by which one could, and ADR-020's confidence weight rather than source attestation is what carries the integrity load downstream.

## Source receipt and evidence bundle

`packages/schemas/source-receipt-v1.schema.json` is the provenance record for one accounting event: every observation that saw the execution, which single one counted and why the others did not, the profile, arithmetic and equivalence rule it was evaluated under, the certification state of the capture path, and the source evidence class. It is device-local and never crosses the device boundary. It records `attestation` as `none` with a basis of `self-reported-at-source`, so no receipt can be read as a provider-verified figure.

`packages/schemas/evidence-bundle-v1.cddl` binds the signed claim bytes by digest, that receipt by identity and digest, the accounting profile and arithmetic by identity and digest, the provenance chain, the privacy decision and the observer-equivalence record into one at-rest record. It is not a wire format: it adds no field to `packages/schemas/egress-allowlist-v1.json` and carries no COSE envelope. The only thing that crosses the boundary is the fixed-schema aggregate claim that already does. The bundle is what makes an accepted claim explainable later without making it transmissible, which is what an appeal and an export need and what the privacy boundary forbids sending.

## Source evidence classes

### E1 — provider-signed or provider-verifiable

Usage authority originates with the provider rather than with the measured party, either as an artifact the provider signed or through an interface the provider operates. Ordinary JSON usage metadata, request IDs, invoices, screenshots, bearer-token possession, local logs and authenticated TLS do not qualify by themselves.

Under ADR-016 and D-078 the class splits into two limbs of different availability. E1 alone is not a sufficient designation; an appraisal records which limb applies.

- **E1-S provider-signed claim receipt** — an independently verifiable artifact cryptographically signed by the provider, binding exact model/version, usage categories, outcome, issuance time and anti-replay identity. Reserved and unavailable; no provider currently issues a qualifying artifact.
- **E1-R provider-retrieved organization aggregate** — the server retrieves aggregate consumption from a provider-operated administrative usage interface, authenticated by a provider-issued credential supplied by the enrolled organization's administrator. Available today at organization scope only.

E1-R authority comes from the retrieval channel and the credential, not from the artifact: the measured party cannot write what the interface returns. Anthropic, OpenAI and Cursor expose administrative usage endpoints. No provider exposes an authorization scope by which an individual permits third-party read of their own consumption, so E1-R is unreachable for individual accounts and individual evidence remains bounded by the user-controlled device.

E1-R is not a receipt. It is unsigned, carries no per-request outcome and no anti-replay identity, is retrieved rather than issued, and may be restated by the provider on re-query. It binds at board scope for a stated interval, never to an individual EvidenceClaim, and it does not alter raw score.

E1-R coverage is partial by construction. The administrative endpoints report API-key traffic, while subscription-backed agent usage is largely unexposed, so an enrolled organization may hold substantial genuine activity that no retrieval corroborates. Partial retrieval is never presented as whole-board corroboration, and normal disagreement between retrieved and claimed totals within a stated reconciliation window is not an integrity signal.

### E2 — trusted local structured source event

An official source hook, SDK callback, local API or runtime-native structured event is observed by an exercised adapter. The event binds an exact source version, capture path and artifact certification tuple.

This remains bounded by the user-controlled device and source integrity.

### E3 — local gateway or protocol observation

A local gateway/wrapper observes approved structural request/response metadata. Its ceiling depends on process identity, endpoint binding, duplicate-domain controls and encrypted-traffic handling.

It never becomes provider-signed evidence merely because upstream TLS authenticated a provider.

### E4 — deterministic derivation

Counts are reconstructed using approved non-content structural facts, emitted token IDs or an exact tokenizer/accounting algorithm. The algorithm, model/tokenizer identity and source version are recorded.

Exact certified derivation may compete at a named profile. Approximate estimates remain private analytics.

### E5 — untrusted import

Historical or caller-supplied records from mutable storage. Private analytics only; never active competition.

## Explicitly excluded launch source class

The launch architecture does not route user model traffic through a VibeMaxxing-controlled inference service merely to observe provider responses. Any future hosted inference product is a separate explicit mode and cannot silently redefine the default privacy contract or become required for competition.

## Device-key protection classes

- **K1 hardware non-exportable** — generated and used in qualifying hardware-backed storage; platform API prohibits export and certification covers restore/migration behavior.
- **K2 OS-bound non-exportable** — documented OS non-exportability without qualifying hardware attestation.
- **K3 OS credential protected** — protected by OS encryption/ACLs but potentially migratable or recoverable by administrators/accounts.
- **K4 application encrypted** — application-managed encrypted key material with explicit OS wrapping or passphrase.
- **K5 insecure fallback** — plaintext, weak or operationally clonable; cannot produce Hardened.
- **KU unknown** — protection not established; fail closed for Hardened.

Protection is established by exercised behavior, not product naming. Backup, sync, migration and restore are certification fixtures.

## Continuity classes

- **C0 none** — no competitive continuity.
- **C1 server sequence** — server-enforced sequence and idempotency.
- **C2 local hash continuity** — C1 plus append-only local commitment and fork quarantine.
- **C3 checkpoint-anchored continuity** — C2 plus a previous/following signed server checkpoint receipt that anchors the local head.
- **C4 rollback-resistant continuity** — C3 plus platform-backed rollback-resistant state and exercised clone/restore tests.

A fresh upload challenge proves submission freshness only. It does not prove an offline event existed before the challenge.

The repaired protocol must distinguish previous local commitment, previous server checkpoint and current challenge.

## Environment classes

- **A0 unmeasured** — no official-build/process evidence.
- **A1 signed release** — official artifact signature and digest verified.
- **A2 process bound** — executable identity, IPC peer and privilege controls exercised.
- **A3 platform/device attested** — current attestation verified with nonce, trust chain, policy, expiry and revocation.
- **A4 controlled confidential environment** — approved remotely verifiable isolation and measurement.

Attestation is an input, not a blanket truth claim. It does not independently prove token accounting.

## Named public profiles

### Standard Competitive v1

Minimum direction:

- E2, E3 or certified E4;
- K3 or stronger, or K4 with an explicit platform ceiling;
- C2 or stronger;
- A1 official digest-addressed release;
- non-expired exact certification tuple;
- deterministic accounting, privacy, duplicate and compatibility rules pass;
- no fatal contradiction.

Delayed offline activity may qualify when its local continuity is internally consistent. Lack of checkpoint anchoring may cap it at Standard.

### Hardened Source-Bound v1

Minimum direction:

- qualifying E1-S, hostile-tested E2 or specially approved exact E4 local-runtime path;
- deterministic authoritative accounting for the source;
- K1 or K2 unless another named profile explicitly proves an equivalent protection path;
- C3 or C4;
- A2 or stronger;
- exact source, runtime, model/tokenizer, mode, platform, adapter and collector artifact certification;
- replay, duplicate, clone, rollback, retry, cancellation, privacy and malformed fixtures pass;
- no unresolved observation gap for the claimed interval.

Hardened must not depend exclusively on cloud-provider receipts or hardware attestation. Certified local models can qualify under a named local-source profile.

E1-R does not satisfy this minimum. An organization-level aggregate supplies no per-member runtime, model/tokenizer, mode, platform, adapter or collector certification and cannot close an observation gap, so no account or board reaches Hardened by way of E1-R.

### Imported v1

- E5 only;
- private analytics;
- never active competition.

Additional profiles require an accepted decision, machine-readable policy and conformance evidence.

## Replay, source and provenance binding

Every competitive EvidenceClaim must eventually bind:

- account pseudonym and device lineage/key;
- exact collector and adapter artifact digests;
- exact source/runtime/model/tokenizer/mode/platform certification tuple;
- event identity created at first live observation;
- safe source execution identity when available;
- duplicate domain and keyed non-content fingerprint;
- source interval, monotonic clock domain/generation and duration;
- previous/current local commitment;
- previous server checkpoint receipt;
- single-use account/device challenge;
- local claim sequence;
- accounting profile and evidence facts;
- deterministic rule bundle and privacy policy version.

Exact replay is idempotent. Conflicting reuse of claim, event, sequence, challenge, commitment, checkpoint or duplicate-domain identity rejects or quarantines. Cross-account reuse never creates a new competitive event.

## Device cloning and recovery

- concurrent valid successors create a fork and quarantine the lineage;
- restored state older than a checkpoint cannot silently resume;
- uncertain clone/migration lowers trust and requires requalification;
- device transfer uses explicit rotation/recovery, never file copying;
- new lineages do not inherit Hardened automatically;
- account-level restrictions and appeals persist across device replacement.

## Detector boundary

Deterministic rules and verifier policy are authoritative.

Server anomaly detectors use privacy-safe aggregate features and begin in shadow mode.

The SLM is post-launch research only. It is not an evidence source, accounting authority or attestation verifier. It may produce a bounded advisory risk signal but cannot alter totals, award a profile or permanently ban.