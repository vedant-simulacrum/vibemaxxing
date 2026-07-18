# VibeMaxxing Project Authority

Status: planning mode. Technical planning and implementation contracts are complete. Product implementation is not authorized.

## Identity and product

VibeMaxxing (`vibemaxxing`, `vibemaxxing.dev`) is a greenfield, privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It is inspired by WhoBurnedMore but does not migrate old accounts, rankings, or scores.

Product thesis: **Codex restraint × Steam social competition**.
Visual thesis: **The Competitive Ledger**.

Public launch includes all intended leaderboard periods and scopes, profiles, friends, rivals, overtakes, movement, presence, notifications, private boards, organizations, hacker houses, communities, countries, moderation, appeals, export, deletion, native local UX, hosted web, and broad agent compatibility. Internal implementation may be staged but must not redefine launch scope.

## Non-negotiable privacy and integrity

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project or repository names, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims cross the device boundary.
- Transcript-capable processes have no network access; networked sync cannot inspect transcript content.
- Token Burn is the default raw ranking metric.
- Estimated Cash Burn is always explicitly an estimate, never actual spend.
- Historical imports remain private analytics and never enter active competition.
- Authentic intentionally pointless usage counts.
- Deterministic controls own accounting, signatures, sequences, replay, duplicate handling, and hard eligibility.
- Public evidence states are Standard, Hardened, and Imported.
- Models and statistical detectors are secondary risk signals and cannot rewrite totals or permanently ban users independently.

## Product topology

The local product contains separate collector, sync, daemon, CLI, menu-bar/tray shell, local privacy/audit UI, and updater responsibilities. Closing the shell does not stop collection. Platform capabilities and hardening differences must be explicit.

Primary identity uses a GitHub App with web/device authorization and X OAuth 2.0 Authorization Code with PKCE. Passkeys or hardware credentials are optional stronger factors.

Agent compatibility is a living, versioned, conformance-backed registry with Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported, and Unsupported states.

## Accepted stack

- Rust 2024: VibeProof, adapters, collector, daemon/native core, privacy boundaries, deterministic accounting, canonical encoding, and signing.
- Go: OAuth, APIs, verification, ingestion, aggregation, ranking, presence, notifications, migrations, and operations.
- Next.js App Router with strict TypeScript: hosted web product.
- PostgreSQL with pgx and explicit SQL: server source of truth.
- Protobuf and Buf: internal contracts.
- Deterministic CBOR, CDDL, and COSE: signed public claims.

Do not add Kubernetes, Kafka, GraphQL, a service mesh, workflow engine, vector database, or ORM-heavy persistence without an evidence-backed ADR.

## Phase and evidence boundary

Planning is complete at contract level. Planning completion is not implementation evidence. Working code, valid generated schemas, cryptographic vectors, certified adapters, passing tests, benchmarks, packaging, deployment, security review, and launch evidence must be produced only after an explicit implementation phase change.

The repository remains private during planning and must become public open source before public launch.

## Authority

When sources disagree, use this order:

1. The user's latest explicit instruction.
2. This file.
3. `docs/project/STATUS.md`.
4. `docs/planning/DECISION_REGISTER.md`.
5. Accepted ADRs and normative subsystem contracts.
6. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and its linked work breakdown.
7. Historical research.

Never resolve a material contradiction silently. Update the decision register and affected contracts; use an ADR for material architectural or behavioral change.
