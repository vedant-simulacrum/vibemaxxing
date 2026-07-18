# VibeMaxxing Implementation Roadmap

## Objective

Prove that VibeMaxxing can privately and deterministically measure real usage from major AI agents, resist obvious competitive-integrity attacks, operate unobtrusively on user devices, and get a new user onto a trustworthy leaderboard in under five minutes.

## Phase 0 — Repository truth and build integrity

Exit criteria:

- Clean checkout builds all implemented components.
- CI cannot pass because a required command is missing or skipped.
- Toolchains and lockfiles are pinned.
- Required branch protections and CODEOWNERS are documented.
- Every eval is either a real pass, a real failure, or explicitly `not_applicable` with an owning milestone.

## Phase 1 — Three exercised agent adapters

Initial targets:

1. Gemini CLI
2. Claude Code
3. Codex

For each adapter:

- Machine-readable manifest and version probe.
- Synthetic live-session fixture.
- Authoritative or explicitly estimated token source.
- Input/output/cache/reasoning category reconciliation.
- Execution-mode-specific tests.
- Forbidden-field and telemetry-canary tests.
- Upgrade-breakage test.
- Double-counting prevention.
- Evidence-state classification.

Exit criteria:

- Three adapters pass conformance and privacy-negative tests.
- Public support claims are generated from the tested registry.

## Phase 2 — VibeProof protocol core

Deliverables:

- Frozen canonical CBOR profile.
- CDDL schema.
- COSE signing profile with pinned algorithms.
- Rust reference implementation.
- Independent cross-language verifier.
- Exact-byte golden vectors.
- Duplicate-key, non-minimal integer, indefinite-length, malformed-header, algorithm-confusion, deep-nesting, and oversized-input rejection.
- Fuzzing and differential tests.

Exit criteria:

- Cross-language vectors pass.
- Invalid and altered claims fail deterministically.
- Parser differentials cannot produce acceptance disagreement.

## Phase 3 — Secure local boundary and device identity

Deliverables:

- Separate transcript-reading and network-sync processes.
- Linux Unix-socket peer credential enforcement.
- macOS signed XPC/helper identity path or clearly labeled weaker development path.
- Windows named-pipe DACL and peer identity path.
- Application-level challenge-response, process nonce, sequence, size, and rate limits.
- Device registration, rotation, revocation, and lost-key state machine.

Exit criteria:

- Rogue-process, PID reuse, socket replacement, replay, stale challenge, flood, downgrade, and state-cloning tests pass per platform.

## Phase 4 — Server ingestion and deterministic ranking

Deliverables:

- Go ingestion API.
- PostgreSQL append-only accepted-claim ledger.
- Replay and idempotency state.
- Transactional outbox.
- Idempotent aggregation worker.
- Minute and period score tables.
- Deterministic tie policy and current-user rank.
- Rebuild-from-ledger path.

Exit criteria:

- Invalid signatures, replays, and duplicate races cannot increase scores.
- Aggregates rebuild identically from the ledger.
- Benchmarks meet approved budgets at staged data sizes.

## Phase 5 — Competitive Ledger web slice

Deliverables:

- Leaderboard route with Token Burn default and explicitly estimated Cash Burn.
- Period and scope controls.
- Current-user row and movement.
- Accessible loading, empty, error, offline, and private states.
- Responsive layouts and visual regression.
- Privacy-verification screen showing exactly what leaves the device.

Exit criteria:

- Accessibility, browser, performance, and visual-regression gates pass.
- User testing confirms core ranking and evidence language is understood.

## Phase 6 — Authentication, social, and abuse controls

Deliverables:

- Passkeys with multiple credentials.
- Hardened recovery and session revocation.
- Friends, rivals, overtakes, presence, and private boards.
- Progressive rate limits, quarantine, appeals, moderator audit trail, and device revocation.
- Country privacy controls and cohort thresholds.

Exit criteria:

- WebAuthn interoperability matrix passes.
- Recovery cannot silently bypass credential security.
- Abuse simulations and moderation workflows meet defined thresholds.

## Phase 7 — Packaging, updates, and operations

Deliverables:

- Signed native packages for supported platforms.
- TUF-based updater with root rotation, expiry, rollback/freeze protection, and atomic recovery.
- Checksums, SBOM, provenance, Sigstore evidence, and TUF metadata.
- Clean consumer-side verification test.
- Privacy-safe observability with telemetry canary blocking.
- Backup, restore, migration, rollback, incident, SLO, load, soak, and failure-injection evidence.

Exit criteria:

- A clean consumer verifies and installs every release layer.
- Recovery and restore tests pass.
- Production-readiness review is approved with evidence.

## Immediate next tasks

1. Run the capability probe on a developer machine with target agents installed.
2. Implement the Gemini CLI synthetic adapter spike.
3. Implement Claude Code JSON/stream-JSON adapter spike.
4. Implement Codex mode-by-mode adapter probes.
5. Write the versioned token-accounting semantics specification.
6. Build the Rust CBOR/COSE bakeoff harness.
7. Turn the PostgreSQL seed into a reproducible benchmark runner.
8. Create the first complete signed-claim-to-leaderboard vertical slice.
