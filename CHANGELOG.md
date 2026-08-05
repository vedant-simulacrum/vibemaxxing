# Changelog

All notable changes will be documented here. Releases follow Semantic Versioning where the public protocol and application compatibility permit it.

## Unreleased

- Restructured `PR_SIZED_WORK_BREAKDOWN.md` into an active plan and a frozen backlog, and added 21 specified planning units (`PF-037`..`PF-057`) carrying required `Files`, `Acceptance`, `Depends`, and `Est` fields.
- Corrected the review scope and P-1104 criteria to include `SR-017`; three sites previously read "SR-005 through SR-016", leaving an open P1 outside the gate.
- Consolidated the repository: archived nine superseded point-in-time reports to `docs/history/`, removed the now-empty `docs/reviews/` directory, and extended `docs/project/DOCUMENTATION.md` from 29 mapped documents to full coverage of every file under `docs/`, with known duplication clusters recorded rather than left implicit.
- Added a root `LICENSE` (Apache-2.0), so the license is machine-detectable rather than described only in prose.
- Added a `Makefile` entrypoint, `.editorconfig`, and a `CLAUDE.md` symlink to `AGENTS.md`.
- Enabled GitHub private vulnerability reporting and corrected `SECURITY.md` and `CONTRIBUTING.md`, which both stated the repository was private after it had become public.
- Rewrote `README.md` around the privacy boundary, an honest status, and a working quick start.
- Establish production engineering, evaluation, security and release baseline.

## Local-First v5

- Added Wave 3 research on protocol libraries, WebAuthn, local IPC, device keys, packaging, pricing provenance, abuse resistance, and country privacy.
- Accepted maintained `go-webauthn` over deprecated Duo Labs package.
- Added platform-specific IPC identity requirements and device-key lifecycle.
- Added immutable versioned Cash Burn pricing ledger design.
- Added privacy-preserving country-board and progressive anti-abuse policy.
- Added corresponding eval-suite placeholders that cannot falsely pass before implementation.
## Local-First v6 — Decision-closing research wave

- Added Wave 4 viability audit and ADR-005.
- Added agent integration research matrix.
- Added metadata-only local agent capability probe.
- Added telemetry canary leakage scanner and test canaries.
- Added PostgreSQL ranking benchmark seed schema.
- Added adversarial case registry.
- Added six evidence-gated eval suites for adapters, protocol libraries, ranking, updater, telemetry, and beta go/no-go.

