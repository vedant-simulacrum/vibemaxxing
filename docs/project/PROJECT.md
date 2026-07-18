# VibeMaxxing Project Authority

Status: planning-hardening. Product implementation is not authorized.

## Identity and product

VibeMaxxing (`vibemaxxing`, `vibemaxxing.dev`) is a greenfield, privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It is inspired by WhoBurnedMore but does not migrate old accounts, rankings or scores.

Product thesis: **Codex restraint × Steam social competition**.
Visual thesis: **The Competitive Ledger**.

Public launch includes all intended leaderboard periods and scopes, profiles, friends, rivals, overtakes, movement, presence, notifications, private boards, organizations, hacker houses, communities, countries, moderation, appeals, export, deletion, native local UX, hosted web and broad agent compatibility. Internal implementation may be staged but must not redefine launch scope.

## Non-negotiable privacy and integrity

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project or repository names, credentials, embeddings, summaries, classifications or personal insights.
- Only fixed-schema safe claims cross the device boundary.
- Transcript-capable processes have no network access; networked sync cannot inspect transcript content.
- Token Burn is the default raw ranking metric.
- Estimated Cash Burn is always explicitly an estimate.
- Historical imports remain private analytics and never enter active competition.
- Authentic intentionally pointless usage counts.
- Deterministic controls own accounting, signatures, sequences, replay, duplicates and hard eligibility.
- Public evidence states are Standard, Hardened and Imported.
- Models and statistical detectors are secondary signals and cannot independently rewrite totals or permanently ban users.

## Product topology

The local product contains separate collector, sync, daemon, CLI, menu-bar/tray shell, local privacy/audit UI and updater responsibilities. Closing the shell does not stop collection. Platform capabilities and hardening differences are explicit.

Primary identity uses a GitHub App with web/device authorization and X OAuth 2.0 Authorization Code with PKCE. Passkeys or hardware credentials are optional stronger factors.

Agent compatibility is a versioned conformance registry with Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported and Unsupported states.

## Accepted stack

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundaries, accounting, canonical encoding and signing.
- Go: OAuth, APIs, verification, ingestion, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router with strict TypeScript: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal contracts.
- Deterministic CBOR/CDDL/COSE: signed public claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases or ORM-heavy persistence without an evidence-backed ADR.

## Planning and evidence boundary

Major behavioral contracts are substantially specified. Planning is not complete until P-1120 through P-1128 pass: draft schemas and registries validate, protocol edge semantics and policy ownership are closed, governance is coherent, canonical references resolve and the repository doctor passes from a clean checkout.

Planning artifacts are not implementation evidence. Working code, generated bindings, cryptographic vectors, certified adapters, passing tests, benchmarks, packages, deployment, security review and launch evidence require a later explicitly authorized implementation phase.

The repository remains private during planning and must become public open source before public launch.

## Authority

When sources disagree:

1. the user's latest explicit instruction;
2. this file;
3. `docs/project/STATUS.md`;
4. `docs/planning/DECISION_REGISTER.md`;
5. accepted ADRs and normative contracts/schemas;
6. the future implementation handoff;
7. historical research.

Never resolve a material contradiction silently. Update decisions and affected contracts; use an ADR for material architectural or behavioral changes.
