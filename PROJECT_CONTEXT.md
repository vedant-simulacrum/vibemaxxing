# VibeMaxxing — authoritative project context

## Identity

- Canonical name: **VibeMaxxing**; lowercase wordmark: `vibemaxxing`; domain: `vibemaxxing.dev`.
- Greenfield rebuild inspired by WhoBurnedMore; no migration of old accounts, rankings, or scores.
- Product thesis: **Codex restraint × Steam social competition**.
- Visual thesis: **The Competitive Ledger**.
- The repository is private during planning and becomes public open source before public launch.

## Current phase

Technical planning and implementation contracts are complete. Product implementation has not begun and requires explicit user approval. Development is local-first; do not introduce a remote coding control plane or remote private-context source of truth.

## Complete public-launch target

Public launch is not a narrow MVP. It includes:

- global, friends, private-board, organization, hacker-house, community, and country leaderboards;
- daily, weekly, monthly, seasonal, yearly, and lifetime periods;
- profiles, friends, rivals, overtakes, rank movement, presence, notifications, boards, organizations, communities, moderation, appeals, export, and deletion;
- a background daemon installed and controlled through a CLI;
- macOS menu-bar and Windows/Linux tray experiences;
- local controls plus a hosted web dashboard;
- broad agent compatibility through a tiered adapter system.

Staged internal milestones are required, but staging must not silently reduce public-launch scope.

## Metrics and privacy

- **Token Burn** is the default raw usage-volume metric.
- **Estimated Cash Burn** is always explicitly an estimate, never actual spend.
- Genuine but intentionally pointless usage counts.
- Historical imports are private analytics only, labelled **Imported**, and never affect active rankings, streaks, overtakes, rivals, or presence.
- The server never receives prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims cross the network boundary. Transcript-capable processes have no network; networked sync cannot inspect transcript content.

## Integrity

- Deterministic code owns counting, normalization, signatures, sequences, replay protection, duplicate handling, eligibility, and claim construction.
- Public evidence labels are **Standard**, **Hardened**, and **Imported**.
- An SLM/model is conditional residual-risk detection only and may not rewrite totals or permanently ban a user.
- Do not claim mathematical cheat-proofing on a user-controlled machine.

## Agent compatibility

Support is a living compatibility system covering CLI, IDE, desktop, hosted, open-source, local-model, gateway, orchestration, ACP, OpenTelemetry, CI/remote, and unknown tools.

Tiers: Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported, and honestly Unsupported. Public support claims come only from an exercised version/mode/platform registry.

## Authentication

GitHub uses a GitHub App with web and device authorization. X uses OAuth 2.0 Authorization Code with PKCE. Passkeys/hardware credentials are optional stronger factors. Account linking, sessions, recovery, provider compromise/loss, native enrollment, authorization and deletion follow ADR-006 and the authentication contract.

## Local product topology

Separate collector, sync, daemon, CLI, menu-bar/tray shell, local privacy/audit UI, hosted web product, and updater responsibilities. Closing the shell does not stop collection. Platform capability and hardening differences are explicit.

## VibeProof

VibeProof requires deterministic normalized events, fixed-schema signed claims, deterministic CBOR/CDDL, COSE_Sign1 with Ed25519 initially, monotonic sequences, challenge/replay protection, previous-claim chaining, revocable device keys, isolated collection/sync, encrypted local state, inspectable outbound ledger, explicit compatibility, and export/deletion.

## Accepted implementation direction

- Rust 2024: VibeProof, adapters, collector, daemon/native core, privacy boundaries, canonical accounting/encoding/signing.
- Go: OAuth/API, verification, ingestion, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router with strict TypeScript: hosted web product.
- PostgreSQL with `pgx` and explicit SQL: server source of truth.
- Protobuf + Buf: internal contracts.
- Deterministic CBOR + CDDL + COSE: signed public claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engine, vector database, or ORM-heavy persistence without an evidence-backed ADR.

## Design

The leaderboard is dominant. Launch direction is a light, premium, technically precise Competitive Ledger: spacious typography, tabular numerals, hairlines, restrained motion, accessibility, keyboard navigation, mobile recomposition, and no generic analytics-card, crypto, cyberpunk, flame, coin, gauge, or esports aesthetic.

## Normative planning authority

Start implementation from `docs/implementation/IMPLEMENTATION_HANDOFF.md`. It links the frozen accounting, adapters, protocol, native, identity, data, social, integrity, UX, operations and launch contracts. Material behavioral changes require the decision register and an ADR.

## Implementation-time selections

The following are deliberately selected during implementation within frozen contracts rather than left behaviorally undefined:

- exact Rust CBOR/COSE crates after conformance bakeoff;
- exact cloud provider and primary regions using the portable deployment contract;
- exact detector/SLM model only if measured lift passes the shipping gate;
- final dependency/legal confirmation of Apache-2.0, CC BY 4.0 and DCO policy;
- exact platform signing/notarization accounts and release-key custody implementation;
- whether VibeProof later separates into its own repository.

These choices may not alter privacy, accounting, evidence, identity, compatibility, data lifecycle, social, authorization or launch semantics without an ADR.
