# Research Audit — Wave 3

Date: 2026-07
Status: Accepted research guidance; implementation remains subject to executable validation.

## Scope

This wave evaluated:

- Rust CBOR/CDDL/COSE libraries and parser strategy
- Go WebAuthn server libraries
- secure cross-platform local IPC
- device registration and key rotation
- native packaging and signing
- Cash Burn pricing provenance
- abuse resistance and country leaderboard privacy

## Conclusions

### 1. Rust CBOR/COSE

Use `coset` only as a COSE data-model and serialization building block. It currently builds on `ciborium`; this does not by itself prove that every accepted byte string satisfies VibeProof's frozen deterministic CBOR profile.

The protocol implementation must therefore include a narrow validation layer that:

- accepts only the exact VibeProof claim schema;
- rejects duplicate keys;
- rejects indefinite-length items;
- rejects non-minimal integers and lengths;
- rejects unsupported tags and floating-point values;
- verifies the exact signed bytes rather than decode/re-encode equivalents;
- pins algorithms and protected-header requirements;
- enforces size, nesting, and collection-count limits before allocation;
- has cross-language golden vectors and parser-differential tests.

Candidate Rust libraries should be benchmarked and adversarially tested rather than selected by popularity. The initial shortlist is `coset` plus `ciborium`, `minicbor`, and any verified or generated parser option that can satisfy the schema and maintenance constraints. A final library decision requires a runnable spike.

### 2. Go WebAuthn

Use `github.com/go-webauthn/webauthn`, not the deprecated `github.com/duo-labs/webauthn` package. Pin a reviewed version and wrap it behind a small internal interface.

Required validation includes:

- registration and authentication ceremonies;
- discoverable credentials and conditional mediation;
- user-verification policy;
- sign-counter behavior without assuming all authenticators provide reliable monotonic counters;
- origin and RP ID validation;
- session/challenge storage and expiry;
- credential deletion and replacement;
- multiple passkeys per account;
- recovery and recent-authentication gates;
- browser interoperability tests.

The library is pre-v1, so upgrades are security-sensitive changes requiring conformance tests and review.

### 3. Local IPC

Filesystem permissions alone are not sufficient. Each platform must combine kernel peer identity, restricted endpoint permissions, protocol versioning, freshness, and an authenticated application handshake.

- Linux: pathname Unix-domain sockets in a private runtime directory; verify `SO_PEERCRED`; optionally use `SO_PASSCRED`; reject unexpected UID/GID/PID; avoid abstract sockets for the primary security boundary because they lack portable filesystem ACLs.
- Windows: explicit named-pipe security descriptors; deny remote clients; scope access to the intended logon SID; avoid permissive default descriptors; use identification-only impersonation unless stronger impersonation is explicitly required.
- macOS: prefer XPC for signed app/helper deployments and validate the connecting process's code identity/audit token where supported; use private Unix-domain sockets only for non-bundled development flows.

All platforms must add a one-time challenge, protocol negotiation, peer role, process-start nonce, and rate/size limits. Peer PID is a signal, not a durable identity.

### 4. Device keys and rotation

Generate a non-exportable hardware-backed key when practical, with a software-backed encrypted fallback clearly labeled. Device registration binds:

- account ID;
- device public key;
- platform and collector build identity;
- evidence capability tier;
- registration epoch;
- server-issued device ID.

Rotation uses an old-key authorization plus a fresh server challenge when the old key is available. Lost-key recovery creates a new device identity and revokes the old one; it must not silently transfer trust. Device revocation and key-compromise events invalidate future claims but preserve append-only historical audit records.

### 5. Packaging and signing

- macOS: Developer ID signing, hardened runtime, notarization, stapling, and Gatekeeper verification on a clean machine.
- Windows: signed MSIX for the primary desktop distribution where feasible; timestamp signatures; enable package-integrity enforcement; use a production signing service or trusted certificate appropriate to publisher eligibility.
- Linux: publish signed packages for selected formats only after update and ownership semantics are defined. Start with signed archives plus checksums, Sigstore provenance, and TUF metadata; add deb/rpm repositories when operationally justified.

Every release must be verified from the consumer side on clean platform runners.

### 6. Cash Burn provenance

Cash Burn is an estimate based on a versioned pricing ledger, never an unversioned live lookup.

Each price record must include:

- provider and canonical model identifier;
- provider-published source URL/reference;
- retrieval timestamp;
- effective start and optional end time;
- currency and unit;
- input, output, cache-read, cache-write, reasoning, batch, and other applicable categories;
- region or tier constraints;
- minimum-charge or rounding rules;
- source-content digest;
- reviewer and approval state;
- pricing-dataset version.

Claims store usage categories, not a mutable cash total. Estimated Cash Burn is computed with an explicitly selected pricing-dataset version. Historical leaderboard values do not silently change; a deliberate reprice view may show an alternative estimate.

Subscription value, credits, negotiated discounts, taxes, and actual invoices are excluded unless the user explicitly provides a separate private analytics source.

### 7. Abuse and country privacy

Do not make country a freely editable competitive field. Use a coarse, change-controlled country assertion with a confidence/source category and user visibility controls. Never retain exact IP addresses for leaderboard display logic beyond the shortest operational need.

Country boards should require minimum cohort sizes and suppress low-population slices. Users need an opt-out and a correction flow. Country evidence must never be framed as proof of nationality or residence.

Sybil resistance should be progressive rather than identity-invasive:

- rate limits and device registration;
- passkey-backed accounts;
- account-age and activity-history signals;
- suspicious-cluster review;
- limits on newly created private boards and friend-request spam;
- optional stronger verification only for prizes or high-impact events;
- appeals and transparent enforcement reasons.

Do not require government identity for ordinary leaderboard participation.

## Rejected shortcuts

- Trusting decode/re-encode equality as signature equivalence
- Using the deprecated Duo Labs WebAuthn package
- Relying only on socket-file permissions
- Treating PID as a cryptographic identity
- Repricing all historical Cash Burn values whenever providers change pricing
- Using exact IP geolocation as a public profile field
- Requiring invasive identity verification for ordinary participation
- Publishing unsigned native binaries while claiming a secure update channel
