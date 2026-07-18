# ADR-003: Platform Isolation, Authentication, Ranking, and Release Verification

- Status: Accepted direction; implementation validation required
- Date: 2026-07-19

## Context

VibeMaxxing needs a privacy-enforcing local collector, phishing-resistant account access, minute-fresh rankings, and verifiable native releases. These concerns have different platform constraints and cannot be solved honestly by one generic abstraction.

## Decision

1. Use a tiered, OS-native process-isolation model with a portable two-process baseline and stronger platform-specific enforcement.
2. Use WebAuthn/passkeys as the preferred authentication path, with multiple credentials and a deliberately hardened recovery flow.
3. Maintain active leaderboard aggregates incrementally through transactional outbox processing and idempotent delta tables; do not depend on frequent full materialized-view refreshes.
4. Use canonical CBOR/CDDL/COSE for signed claims with frozen canonicalization rules and differential golden-vector testing.
5. Require both producer-side release signing/attestation and consumer-side verification tests.
6. Apply telemetry allowlists and automated privacy tests to all observability output.

## Consequences

- The collector will have platform-specific crates/modules and evidence tiers.
- Recovery UX is more involved than a simple email reset.
- Ranking storage includes explicit aggregate and worker-checkpoint tables.
- Release pipelines must build and verify artifacts on each target platform.
- Observability instrumentation cannot be enabled blindly.

## Rejected alternatives

- Claiming equivalent sandbox strength across operating systems.
- Password or email-only recovery as the primary design.
- Refreshing full materialized views for active rankings.
- Signing without verification.
- Logging arbitrary request or claim payloads.
