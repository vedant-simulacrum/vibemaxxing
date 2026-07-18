# VibeMaxxing — authoritative project context

## Identity

- Canonical name: **VibeMaxxing**; lowercase wordmark: `vibemaxxing`; domain: `vibemaxxing.dev`.
- Greenfield rebuild inspired by WhoBurnedMore; no migration of old accounts, rankings, or scores.
- Product thesis: **Codex restraint × Steam social competition**.
- Visual thesis: **The Competitive Ledger**.
- The repository is private during planning and must become public open source before public launch.

## Current phase

The project is in planning and decision-closing mode. Internal work may be staged, but product implementation starts only after the planning exit gate and an explicit user phase change. Development is local-first; do not introduce a remote coding control plane or remote private-context source of truth.

## Complete public-launch target

Public launch is not a narrow MVP. It includes:

- global, friends, private-board, organization, hacker-house, community, and country leaderboards;
- daily, weekly, monthly, seasonal, yearly, and lifetime periods;
- profiles, friends, rivals, overtakes, rank movement, presence, notifications, boards, organizations, communities, moderation, appeals, export, and deletion;
- a background daemon installed and controlled through a CLI;
- macOS menu-bar and Windows/Linux tray experiences;
- local controls plus a hosted web dashboard;
- broad agent compatibility through a tiered adapter system.

Staged internal milestones are required, but staging must not silently reduce the public-launch scope.

## Metrics

- **Token Burn** is the default ranking metric.
- **Estimated Cash Burn** is always explicitly an estimate, never actual spend.
- Genuine but intentionally pointless usage counts.
- Historical imports are private analytics only, labelled **Imported**, and never affect active rankings, streaks, overtakes, rivals, or presence.

## Privacy boundary

The server must never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project or repository names, credentials, embeddings, summaries, classifications, or personal insights.

Only fixed-schema safe claims may cross the network boundary. A process that can inspect transcript content must have no network access; a networked sync process must be unable to inspect transcript content.

## Integrity

- Deterministic code owns counting, normalization, signatures, sequence validation, replay protection, duplicate handling, and claim construction.
- Public evidence labels are **Standard**, **Hardened**, and **Imported**.
- An SLM or other model is only a residual-risk signal. It may not rewrite totals or permanently ban a user by itself.
- Do not claim mathematical cheat-proofing on a user-controlled machine.

## Agent compatibility

Support is a living compatibility system, not a fixed list. It must cover CLI, IDE, desktop, hosted, open-source, local-model, gateway, orchestration, ACP, OpenTelemetry, and unknown-tool categories.

Support tiers:

1. Hardened-certified.
2. Competitive-certified.
3. Community-certified.
4. Generic live.
5. Imported.
6. Unsupported, stated honestly.

Public support claims must be generated from an exercised, versioned adapter registry.

## Authentication

Primary sign-in is OAuth-based through GitHub and X/Twitter. Passkeys or hardware-backed credentials are optional stronger-authentication factors, not mandatory for normal users. Account linking, provider compromise, recovery, session revocation, and provider loss require explicit state machines.

## Local product topology

The intended local system contains separate responsibilities for collection, synchronization, daemon control, CLI installation/control, menu-bar or tray UX, local audit UX, and updating. Closing the tray must not silently corrupt or lose collection state. Platform-specific capability and hardening differences must be explicit.

## VibeProof

VibeProof is the local-first accounting and integrity protocol. It requires deterministic normalization, fixed-schema claims, canonical CBOR/CDDL, COSE signatures, monotonic sequences, challenge and replay protection, commitments, revocable device keys, isolated collection/sync processes, encrypted local state, an inspectable outbound ledger, and export/deletion controls.

## Accepted implementation direction

- Rust 2024: VibeProof, adapters, collector, local privacy boundaries, canonical encoding/signing, and native core.
- Go: ingestion APIs, verification orchestration, aggregation, ranking, presence, workers, migrations, and operational tooling.
- Next.js App Router with strict TypeScript: hosted web product.
- PostgreSQL with `pgx` and explicit SQL: server source of truth.
- Protobuf + Buf: internal contracts.
- Canonical CBOR + CDDL + COSE: signed public claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engine, vector database, or ORM-heavy persistence without an evidence-backed ADR.

## Design

The leaderboard is the dominant object. The launch direction is a light, premium, technically precise Competitive Ledger: spacious typography, tabular numerals, hairlines, restrained motion, strong accessibility, keyboard navigation, mobile recomposition, and no generic analytics-card, crypto, cyberpunk, flame, coin, gauge, or esports aesthetic.

## Repository and launch rules

- Keep product source independently buildable and understandable without chat history.
- Keep secrets, unpublished incidents, active abuse thresholds, exploit signatures, and private business material outside public Git.
- Automated CI, eval, dependency, security, and release workflows remain manual-only during planning.
- Before public launch, restore and validate the required automated checks, release signing, consumer verification, operations, legal/privacy readiness, and open-source governance.

## Open decisions

Do not silently invent final licenses, cloud providers/regions, RPO/RTO, budgets, exact detector models, country-verification method, privacy defaults, pricing update operations, release notarization details, or whether VibeProof later becomes a separate repository.
