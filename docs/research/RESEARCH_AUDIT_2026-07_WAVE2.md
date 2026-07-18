# Research Audit — Wave 2 (July 2026)

This document records the second research pass. It is advisory until reflected in ADRs and implementation.

## 1. Cross-platform process isolation

No single portable primitive can enforce the privacy boundary identically on every operating system.

Accepted strategy:

- Portable baseline: two separate executables, least-privilege OS accounts where practical, explicit IPC schema, no inherited file descriptors, deny-by-default path allowlists, and negative tests proving forbidden reads and network calls fail.
- macOS: App Sandbox for distributable GUI/helper components where compatible; app-group containers for controlled shared state; security-scoped access only for user-selected paths. Some collector behaviors may require a separately signed helper because App Sandbox forbids arbitrary process and filesystem access.
- Linux: Landlock for unprivileged filesystem restriction, seccomp for syscall filtering, namespaces where available, and cgroup limits. Landlock is additive defense, not a complete replacement for process and network policy.
- Windows: AppContainer/less-privileged process isolation with explicit filesystem and network capabilities. New composable sandbox APIs remain experimental and must not become the only supported path until stable.

The product must expose an evidence tier that reflects the actual enforcement available on that device. Baseline portability must not be falsely labeled Hardened.

## 2. Canonical signed claims

The signed VibeProof format remains canonical CBOR + CDDL + COSE.

Implementation rules:

- Treat RFC 8949 deterministic encoding requirements as protocol behavior, not a library default assumption.
- Freeze a canonicalization profile in the protocol specification.
- Maintain cross-language golden vectors for valid, invalid, non-canonical, duplicate-map-key, integer-boundary, and malformed inputs.
- Verify the exact bytes that were signed; never decode and re-encode before signature verification unless the protocol explicitly requires canonical rejection first.
- Reject duplicate map keys, unsupported tags, indefinite-length forms if excluded by the profile, and non-minimal integer encodings.
- Pin crypto algorithms and prohibit algorithm negotiation from untrusted claims.
- Keep library selection provisional until differential tests compare at least two independent implementations.

## 3. Authentication and recovery

Passkeys/WebAuthn should be the default authentication path because credentials are origin-bound public-key credentials and phishing resistant.

Recovery is the highest-risk part of passwordless authentication.

Accepted direction:

- Support multiple passkeys per account from launch.
- Encourage a second device or hardware security key during onboarding.
- Require recent strong authentication for adding or removing credentials, changing recovery methods, exporting sensitive data, or deleting an account.
- Recovery must not silently downgrade to weak email-only account takeover.
- If recovery codes are offered, store only salted verifier material and display codes once.
- Notify all registered channels and existing sessions after credential or recovery changes.
- Add cooling-off periods and session revocation for high-risk recovery.
- Maintain an auditable credential event log that contains no biometric data or authenticator secrets.
- Do not require attestation unless a specific high-assurance policy justifies its privacy and compatibility cost.

## 4. PostgreSQL leaderboard design

PostgreSQL window functions correctly express rank and peer behavior, but running rank calculations over the entire raw claim ledger on every request will not scale.

PostgreSQL core does not currently provide built-in incremental materialized-view maintenance. A plain materialized view requires refresh and should not be used as the primary minute-fresh ranking mechanism.

Accepted design:

- Append accepted claims transactionally.
- Write a transactional outbox row in the same transaction.
- Aggregate deltas into minute/user/scope/period tables with idempotent worker checkpoints.
- Maintain compact current-period score tables keyed by scope, period, and user.
- Compute visible rank using deterministic SQL ordering and explicit tie policy.
- Use materialized views only for slower analytical or historical surfaces where refresh semantics are acceptable.
- Partition raw claims by time only after measured data volume warrants it.
- Keep corrections append-only and recompute affected aggregates deterministically.
- Benchmark rank reads, current-user rank, top-N, pagination, ties, and period rollover.

## 5. Native packaging and software supply chain

Generating signatures, SBOMs, or attestations is insufficient unless release consumers and CI verify them.

Accepted release chain:

- Reproducible or independently repeatable builds where practical.
- Platform-native signing and notarization for macOS and Windows.
- Sigstore/Cosign bundle for release blobs and container images.
- GitHub build provenance and SBOM attestations.
- TUF metadata for update-channel compromise, rollback, and freeze resistance.
- Bootstrap installers pin an exact version, checksum, signature identity, and trusted TUF root.
- CI downloads the published release through the same public path and verifies it as a consumer would.
- Release keys and identities have documented rotation and compromise procedures.

## 6. Observability without privacy leakage

OpenTelemetry semantic conventions should be used for services, but generic auto-instrumentation can capture dangerous attributes.

Rules:

- Maintain a telemetry allowlist, not only a denylist.
- Never record claims, prompts, transcript-derived data, filenames, paths, repository names, user-entered text, authorization headers, cookies, or secret-bearing query strings.
- Use pseudonymous stable identifiers only where operationally necessary and document retention.
- Separate product analytics from security/audit telemetry.
- Add automated telemetry payload tests that fail if forbidden field names or high-entropy secret patterns appear.
- Rust OpenTelemetry support remains beta; isolate the instrumentation adapter so it can be replaced without touching protocol code.
- Sampling must preserve error and security-event visibility without retaining sensitive payloads.

## 7. Adversarial integrity testing

The integrity suite must include active attacks, not only happy-path fixtures.

Required campaigns:

- Claim byte mutation after signing.
- Alternate canonical encodings of the same semantic object.
- Duplicate map keys and parser differentials.
- Sequence rollback and gap attacks.
- Cross-device replay.
- Clock rollback and period-boundary manipulation.
- Concurrent duplicate submission races.
- Worker crash between ledger insert and aggregate update.
- Snapshot/state-cloning replay.
- Adapter source spoofing.
- Oversized and decompression-bomb inputs.
- Malformed Unicode and normalization edge cases.
- Resource exhaustion against verification and ranking endpoints.
- Compromised update metadata and rollback attempts.

Property-based, fuzz, differential, and state-machine testing are all required before public competitive rankings are considered trustworthy.

## 8. Explicitly rejected shortcuts

- One universal sandbox abstraction claimed to be equally strong everywhere.
- Email-only recovery as the default passkey fallback.
- Full materialized-view refresh every minute for active global rankings.
- Signing release artifacts without publishing and testing verification instructions.
- Unbounded OpenTelemetry auto-capture.
- Treating a single CBOR/COSE implementation as proof of protocol correctness.
