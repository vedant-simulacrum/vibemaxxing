# VibeMaxxing Staged Delivery and Launch Roadmap

Updated: 2026-07-19
Status: planning roadmap; implementation not authorized

## Governing rule

Internal milestones are deliberately narrow and evidence-driven. Public launch is not a narrow MVP: it requires the complete initial product and launch gates defined by the planning catalog.

## Stage 0 — Repository truth and planning exit

Close authority contradictions, generated metadata, glossary, launch matrix, user journeys, decisions, schemas, state machines, negative cases, research ownership, and implementation handoff.

Exit requires P-1101 through P-1104. Until then, no product implementation.

## Stage 1 — Synthetic secure spine

First implementation milestone after approval:

synthetic live source → deterministic accounting → fixed-schema signed claim → isolated sync boundary → server verification → replay/duplicate rejection → append-only persistence → deterministic aggregate → leaderboard API → polished row.

This stage proves architecture only. It is not a public product or adapter-support claim.

## Stage 2 — Native local foundation

Deliver daemon, collector, sync, CLI, local storage, device identity, IPC, local privacy audit, platform lifecycle, crash/offline recovery, and initial menu-bar/tray shells.

Exit requires platform-specific attack tests and resource budgets. Baseline operation must not require elevated privileges; optional hardening is tiered.

## Stage 3 — VibeProof interoperability

Deliver frozen claim schema, canonical CBOR/CDDL profile, COSE signing profile, cross-language verifier, error registry, sequences/challenges, batching, compatibility, golden/malformed vectors, fuzzing, resource limits, and differential tests.

## Stage 4 — Universal adapter framework

Deliver machine-readable agent census, adapter manifest, normalized events, source reconciliation, support tiers, certification, community governance, emergency disable, and generated compatibility claims.

Begin with a few representative adapters across different families for framework validation, then expand continuously. Public launch requires coverage of all major agent families and credible generic paths; it does not falsely claim Hardened certification for every private or future tool.

## Stage 5 — Server, accounting, and ranking core

Deliver OAuth account foundation, device authorization, ingestion, PostgreSQL schema, claim transaction, outbox, aggregation, periods, ties, late/offline behavior, corrections, rebuilds, pagination, current-user rank, evidence filters, and capacity/failure benchmarks.

## Stage 6 — Competitive Ledger product

Deliver complete route/state architecture for leaderboards, profiles, periods, scopes, Estimated Cash Burn, movement, evidence explanations, privacy verification, responsive/accessibility behavior, and native-to-hosted continuity.

## Stage 7 — Full social and group system

Deliver friendships, blocks, rivals, overtakes, streaks, seasons, presence, notifications, private boards, organizations, hacker houses, communities, country boards, ownership/administration, privacy, and lifecycle behavior.

## Stage 8 — Authentication, recovery, moderation, and appeals

Deliver GitHub and X/Twitter OAuth, linked providers, optional stronger factors, sessions, provider loss/compromise, account merge, native authorization, permission matrix, abuse controls, quarantine, moderator audit, appeals, restoration, export, and deletion.

## Stage 9 — Anti-cheat validation

Execute the attack catalog, deterministic control tests, replay/clone/rollback/downgrade/Sybil/collusion campaigns, statistical baselines, detector bakeoff, optional SLM feasibility decision, calibration budgets, red-team tournaments, and independent review.

No model-based detector may replace deterministic accounting or permanently ban by itself.

## Stage 10 — Packaging and production operations

Deliver signed native packages, notarization, TUF updater, rollback/freeze defense, consumer verification, SBOM/provenance, deployment, observability allowlists/canaries, SLOs, backup/restore, disaster recovery, incidents, key compromise, moderation operations, and legal/privacy operations.

## Stage 11 — Open-source release candidate

Finalize license, DCO/CLA decision, trademark policy, contributor/maintainer governance, community adapter policy, security advisories, release authority, signing-key custody, public documentation, clean checkout, reproducible build evidence, and restored automated checks.

The repository becomes public before public launch after a secrets, incident, private-threshold, and exploit-enabling-material review.

## Stage 12 — Comprehensive public-launch gate

Public launch requires:

- complete intended product scope;
- major agent-family coverage and honest support tiers;
- privacy and threat/control traceability;
- successful adversarial integrity evidence;
- accessibility, browser, native-platform, performance, and reliability evidence;
- production operations and moderation readiness;
- verified packaging/update/recovery;
- public open-source governance;
- zero unresolved P0 contradictions or launch-blocking accepted risks;
- explicit user launch approval.

## Current next tasks

Remain in planning. Follow `docs/planning/TASK_CATALOG.md`, beginning with repository metadata/provenance and complete launch/product contracts. Do not run implementation spikes until P-1104 explicitly opens implementation.
