# Build Plan

Updated: 2026-07-19
Status: future implementation plan; implementation not yet authorized

This plan begins only after planning task P-1104. Internal stages may be narrow, but public launch must satisfy the complete scope freeze and launch gate.

## Stage 0 — Approved contracts and repository integrity

- Planning exit report approved.
- Toolchains and lockfiles pinned.
- Complete privacy, accounting, adapter, protocol, native, API, database, ranking, identity, social, anti-cheat, operations, and launch contracts frozen.
- Deterministic repository metadata regenerated.
- Required implementation-phase CI restored without placeholder passes.

## Stage 1 — Synthetic secure vertical slice

- Synthetic source and normalized event.
- Deterministic Token Burn accounting.
- Signed fixed-schema VibeProof claim.
- Isolated collector/sync boundary.
- Go verification/ingestion.
- Replay, invalid-signature, and duplicate rejection.
- Append-only PostgreSQL persistence and deterministic aggregation.
- One leaderboard API and polished row.

This is internal architecture evidence only.

## Stage 2 — Native foundation

- Daemon, collector, sync, CLI, local storage, device identity, IPC, local audit UX.
- macOS menu-bar and Windows/Linux tray shells.
- Headless WSL/container/CI operation.
- Crash, offline, sleep/resume, disk-full, corruption, update, rollback, uninstall, export, and deletion behavior.

## Stage 3 — VibeProof conformance

- Frozen CBOR/CDDL/COSE profile.
- Rust reference codec and independent verifier.
- Golden/malformed vectors, fuzzing, resource limits, differential tests.
- Challenge, sequence, replay, duplicate, clock, fork, batching, acknowledgement, and compatibility state machines.

## Stage 4 — Universal adapter framework

- Machine-readable agent census.
- Adapter manifest and normalized event schemas.
- Source reconciliation and double-count prevention.
- Support tiers, certification, community governance, emergency disable, and generated compatibility claims.
- Representative adapters across materially different agent families before broad expansion.

## Stage 5 — Account and server core

- GitHub and X/Twitter OAuth.
- Linked providers, sessions, native authorization, optional stronger factors, recovery, and provider-loss handling.
- Go APIs, PostgreSQL schema, ingestion transaction, outbox, workers, ranking, corrections, rebuild, pagination, and benchmarks.

## Stage 6 — Competitive Ledger web and local continuity

- Complete route/state shell.
- Global and period leaderboards, profiles, evidence explanations, Token Burn, Estimated Cash Burn, movement, privacy verification.
- Local daemon/device/adapter controls connected safely to hosted UX.
- Accessibility, browser, responsive, visual, and performance evidence.

## Stage 7 — Complete social and group product

- Friends, blocks, rivals, overtakes, streaks, seasons.
- Presence and notifications.
- Private boards, organizations, hacker houses, communities, and countries.
- Ownership, administration, permissions, privacy, lifecycle, and abuse behavior.

## Stage 8 — Anti-cheat, moderation, and appeals

- Execute deterministic attack campaigns.
- Populate reason-code and evidence qualification registries.
- Statistical and graph baselines.
- Detector bakeoff; SLM only if measured lift justifies it.
- Quarantine, restrictions, moderator audit, appeals, restoration, and insider controls.

## Stage 9 — Packaging and operations

- Signed/notarized platform packages.
- TUF updater and malicious-metadata tests.
- SBOM, provenance, consumer verification, dependency/security automation.
- Deployment, configuration, secrets, SLOs, observability, backup/restore, DR, incidents, rollback, and key compromise.

## Stage 10 — Open-source release candidate and public launch

- Final license, DCO/CLA, trademark, contributor, maintainer, adapter, security-advisory, and release governance.
- Secret/private-threshold/exploit-material review before repository publication.
- Clean checkout and reproducible release evidence.
- Complete agent-family coverage matrix.
- Full product, privacy, integrity, accessibility, performance, operations, moderation, legal/privacy, and launch review.
- Explicit user approval.

## Prohibited shortcuts

- No public launch with only three adapters or a narrow social subset.
- No mandatory passkey requirement for ordinary users.
- No SLM-owned token accounting or permanent-ban authority.
- No retrospective imported data in competitive rankings.
- No hidden content-bearing telemetry.
- No handwritten support claims without exercised registry evidence.
- No placeholder, skipped, or `not_applicable` evidence used as a launch pass.
