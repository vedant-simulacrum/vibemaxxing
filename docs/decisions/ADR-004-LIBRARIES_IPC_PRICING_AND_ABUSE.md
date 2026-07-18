# ADR-004: Protocol Libraries, Local IPC, Pricing Provenance, and Abuse Controls

Status: Accepted
Date: 2026-07

## Decision

1. Use `github.com/go-webauthn/webauthn` behind an internal adapter for WebAuthn ceremonies. Do not use the deprecated Duo Labs package.
2. Evaluate `coset` as the initial Rust COSE structure library, but enforce VibeProof's canonical CBOR profile independently and require differential tests before final adoption.
3. Authenticate collector/sync IPC with platform peer credentials plus a fresh application-level handshake and strict endpoint ACLs.
4. Bind devices to revocable public keys and rotate keys through explicit server challenges; lost keys create new device identities.
5. Represent Cash Burn using immutable, versioned, source-backed pricing datasets. Store usage facts independently of estimates.
6. Use coarse, privacy-controlled country assertions and progressive anti-abuse controls. Do not require government identity for ordinary use.
7. Treat native signing, notarization, timestamping, provenance, and clean consumer verification as release blockers once native artifacts ship.

## Consequences

- More conformance and adversarial fixtures are required before protocol libraries are accepted.
- Authentication-library upgrades become high-risk reviewed changes.
- Cross-platform IPC needs platform-specific code and test runners.
- Pricing changes become auditable and reproducible.
- Country and anti-abuse features trade some ranking precision for privacy and accessibility.
