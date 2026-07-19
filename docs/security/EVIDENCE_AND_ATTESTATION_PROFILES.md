# Evidence and Attestation Profiles

Status: normative planning contract
Updated: 2026-07-19

## Purpose

VibeProof proves that a registered device key signed a canonical claim and that the server accepted it under defined sequence, challenge, accounting, privacy and compatibility rules. It does not, by itself, prove that a provider issued the usage record, that the local source was uncompromised, or that a user-controlled machine was not cloned.

Consumer-facing states remain `Standard`, `Hardened`, and `Imported`. `Hardened` is not a generic adjective: it is awarded only through a named, versioned profile whose complete requirements pass for the exact certification tuple.

## Independent evidence dimensions

Every competitive claim records these dimensions independently:

1. **Source authority** — who produced or observed the usage fact.
2. **Capture binding** — how the observation is bound to the source execution.
3. **Accounting authority** — how token categories and totals were obtained.
4. **Device-key protection** — how export, cloning and unauthorized signing are resisted.
5. **Continuity strength** — sequence, prior-hash, local commitment and rollback properties.
6. **Environment assurance** — signed build, process identity, OS or hardware attestation.
7. **Freshness** — source event time, local commitment time, challenge time and receipt time.
8. **Compatibility evidence** — exact runtime, version, mode, platform and conformance result.

No stronger value in one dimension silently upgrades a weaker value in another.

## Source evidence classes

### E1 — Provider-signed or provider-verifiable

An independently verifiable artifact is cryptographically signed by the provider or can be verified through a provider-operated verification interface. The verified statement must bind the provider request or execution identifier, exact model/version, usage categories, outcome, issuance time and anti-replay identifier.

Authenticated TLS transport, ordinary JSON usage metadata, request IDs, invoices, screenshots, local logs and bearer-token possession do not qualify by themselves.

### E2 — VibeMaxxing-server-observed provider response

A VibeMaxxing-controlled service observes an authenticated provider response in the request path and binds it to a server-side request record. This is not portable provider-signed evidence and must never be labelled E1. It is permitted only when the product flow explicitly routes the model call through that service and the privacy contract remains satisfied.

### E3 — Trusted local structured event

An official source hook, SDK callback, local API or structured event is observed by an exercised adapter. The event is bound to an exact source version and capture path. Trust remains bounded by the user-controlled device and the source's own integrity.

### E4 — Gateway or proxy observation

A local or user-controlled gateway observes request/response metadata. The evidence ceiling depends on process identity, endpoint binding, duplicate-domain controls and whether encrypted traffic is terminated by the gateway. It never qualifies as provider-signed merely because upstream TLS authenticated the provider during transport.

### E5 — Deterministic derivation

Counts are reconstructed from non-content structural facts or an approved tokenizer/accounting algorithm. The exact algorithm and source version are recorded. Estimates are explicitly labelled and cannot satisfy a profile that requires provider-reported accounting.

### E6 — Untrusted import

Historical or caller-supplied records from mutable storage. E6 is private analytics only and never enters active competitive rankings.

## Device-key protection classes

- **K1 hardware non-exportable** — key generated and used in hardware-backed secure storage; export is prohibited by the platform API and the key is bound to an attested device or security module.
- **K2 OS-bound non-exportable** — key is non-exportable through documented OS APIs but lacks a qualifying hardware attestation.
- **K3 OS credential protected** — export may be possible through account backup, migration, administrator access or credential-store APIs; encryption and ACLs protect ordinary access.
- **K4 application encrypted** — application-managed encrypted key material with explicit passphrase or OS wrapping.
- **K5 insecure fallback** — plaintext, weakly protected or operationally clonable storage. K5 cannot produce competitive Hardened evidence.
- **KU unknown** — protection has not been established; fail closed for Hardened.

Key protection class is determined by exercised platform behavior, not product naming. Backup, sync, migration and restore behavior are part of certification.

## Continuity classes

- **C0 none** — no competitive continuity.
- **C1 server sequence** — server-enforced device sequence and idempotency.
- **C2 hash continuity** — C1 plus previous accepted-claim hash and fork quarantine.
- **C3 pre-challenge local commitment** — C2 plus append-only local commitments created before future server challenges are known.
- **C4 rollback-resistant commitment** — C3 plus platform-backed monotonic or rollback-resistant state with exercised restore/clone tests.

A fresh server challenge proves submission freshness only. It does not prove that an offline event existed before the challenge. Claims must expose their continuity class.

## Environment classes

- **A0 unmeasured** — no verified official-build or process evidence.
- **A1 signed release** — official release signature and version verified.
- **A2 process bound** — exercised process identity, executable identity and IPC peer controls.
- **A3 device attested** — current device or OS attestation verified with nonce, freshness, trust chain and policy.
- **A4 controlled confidential environment** — approved controlled execution with remotely verifiable isolation and measurement.

Attestation is an input, not a blanket truth claim. The verifier records issuer, format, nonce binding, measurement, policy version, verification time, expiry and revocation status.

## Named public profiles

### Standard Live v1

Minimum requirements:

- E3, E4 or E5 source evidence from an exercised adapter;
- K3 or stronger, unless a documented platform limitation forces K4 and the UI discloses the ceiling;
- C2 continuity;
- A1 signed release;
- exact runtime/version/mode/platform certification is non-expired;
- deterministic privacy scan and fixed-schema claim;
- duplicate-domain and accounting-profile rules pass.

### Hardened Source-Bound v1

Minimum requirements:

- E1, E2 or an explicitly approved E3 source whose official structured hook and process binding have passed hostile-source tests;
- provider-reported accounting where the source exposes it; estimates cannot satisfy this profile;
- K1 or K2;
- C3 or C4;
- A2 or stronger;
- source version and model endpoint fail closed when unknown;
- exact certification tuple and all relevant replay, clone, rollback, retry, cancellation, duplicate, privacy and malformed fixtures pass;
- no unresolved observation gap during the claimed continuity interval.

### Imported v1

- E6 only;
- private analytics;
- never active competition.

Additional Hardened profiles may be added only by a decision-register entry and machine-readable policy. A claim displays the simple consumer state and exposes its profile ID and dimensional breakdown for inspection.

## Replay and source binding

Every competitive claim binds:

- account and device key;
- exact certification tuple;
- event ID generated at first live observation;
- source execution identifier when safely available;
- duplicate domain and local keyed fingerprint;
- source event interval and monotonic counters;
- local commitment reference and commitment time when C3/C4 applies;
- single-use account/device-bound server challenge;
- device sequence and previous accepted-claim hash;
- accounting profile and evidence class.

Exact replay is idempotent. Conflicting reuse of an event, request, commitment, challenge, sequence or duplicate-domain identifier rejects or quarantines. Cross-account reuse is never accepted as a new competitive event.

## Device cloning and rollback outcomes

- Concurrent valid successors from one sequence create a fork and quarantine the device.
- Restored state older than the server checkpoint cannot silently resume; it requires recovery and receives a new device chain.
- A cloned K3/K4 key cannot retain a Hardened profile after clone or migration uncertainty.
- Device transfer is explicit key rotation or new enrollment, never file copying.
- VM snapshots, home-directory restores, credential migration and OS backup/restore are mandatory platform fixtures.
- Failure to prove rollback resistance lowers the continuity and public evidence profile; it does not fabricate an unsupported guarantee.

## SLM boundary

An SLM is not an evidence source, accounting authority or attestation verifier. It may consume only approved privacy-safe structured features after deterministic validation. It may produce a bounded risk signal, never alter totals, award a stronger profile, or permanently ban a user. Initial launch does not depend on an SLM unless a measured bakeoff demonstrates incremental value over deterministic and classical baselines.
