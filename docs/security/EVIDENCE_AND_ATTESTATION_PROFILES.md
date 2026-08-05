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

The policy file carries a single `E1` value in its `source` enum and no marker distinguishing the E1-S and E1-R limbs introduced by D-078, so the availability split below is currently expressed only in prose. Reconciling the machine-readable policy with it is a required follow-up owned by that file.

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

No stronger value in one dimension silently upgrades a failed mandatory requirement in another.

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