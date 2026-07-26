# ADR-003: Platform Isolation, Authentication, Ranking, and Release Verification

- Status: Accepted, amended 2026-07-19
- Date: 2026-07-19

## Context

VibeMaxxing needs a privacy-enforcing local collector, low-friction social account access, optional stronger authentication, minute-fresh rankings, and verifiable native releases. These concerns have different platform constraints and cannot be solved honestly by one generic abstraction.

## Decision

1. Use a tiered, OS-native process-isolation model with a portable two-process baseline and stronger platform-specific enforcement.
2. Use GitHub and X/Twitter OAuth as primary account access. Passkeys or hardware-backed credentials are optional stronger factors for sensitive actions, privileged roles, and users who choose them.
3. Keep social account identity separate from activity-integrity evidence. OAuth proves control of an external account, not authenticity of usage, person uniqueness, or device integrity.
4. Support multiple linked identity providers, explicit account linking/merge, provider-compromise/loss handling, bounded sessions, session revocation, recovery codes, cooling-off, and human appeal.
5. Maintain active leaderboard aggregates incrementally through transactional outbox processing and idempotent delta tables; do not depend on frequent full materialized-view refreshes.
6. Use canonical CBOR/CDDL/COSE for signed claims with frozen canonicalization rules and differential golden-vector testing.
7. Require both producer-side release signing/attestation and consumer-side verification tests.
8. Apply telemetry allowlists and privacy-negative tests to all observability output.

## Phase 1 implementation boundary

The initial Rust reference freezes only the CDDL fixed schema and a bounded canonical
CBOR subset. It deliberately does not claim COSE verification, key management, or a
selected COSE library. Those remain pending `protocol-library-bakeoff` evidence.
Pricing manifests are immutable test fixtures but unsigned; authority and signing-key
selection remain open. Rollback quarantines an affected protocol/accounting version
and requires deterministic fixture-bound replay rather than reinterpretation.

## Consequences

- The collector has platform-specific modules and evidence tiers.
- Authentication requires provider-specific threat modeling, minimal scopes, native authorization binding, account-linking conflict handling, and recovery design.
- Optional passkeys improve protection but cannot be a universal adoption prerequisite.
- Ranking storage includes explicit aggregate and worker-checkpoint tables.
- Release pipelines must build and verify artifacts on each target platform.
- Observability instrumentation cannot be enabled blindly.

## Rejected alternatives

- Claiming equivalent sandbox strength across operating systems.
- Treating OAuth identity as anti-cheat evidence.
- Mandatory passkeys for all ordinary users.
- Password-only or unprotected email reset as the primary design.
- Refreshing full materialized views for active rankings.
- Signing without verification.
- Logging arbitrary request, claim, or GenAI payloads.

## Validation required

- GitHub App versus OAuth App decision using current official permissions and lifecycle evidence.
- X/Twitter sign-in protocol and operational constraints.
- Native CLI/daemon device authorization and browser-binding tests.
- Account-link, merge, provider-loss, takeover, recovery, and session-replay simulations.
- Optional WebAuthn interoperability testing before stronger-factor release.
