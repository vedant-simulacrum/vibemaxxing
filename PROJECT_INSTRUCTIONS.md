# VibeMaxxing Project Instructions

## Authority

Use this precedence when materials disagree:

1. User's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. This file.
4. `CURRENT_STATUS.md`.
5. `MODEL_OPERATING_MANUAL.md`.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. Nearest `AGENTS.md`.
9. Accepted ADRs and current specifications.
10. Historical research documents.

Never silently choose between contradictory sources. Record and resolve contradictions through the planning audit and decision register.

## Current phase

The project is in planning and decision-closing mode. Do not implement the product, deploy infrastructure, build production adapters, or generate placeholder scaffolding until the user explicitly opens implementation.

Allowed work includes audits, research, ADRs, specifications, schemas, APIs, state machines, threat/control mappings, benchmark plans, fixtures, test plans, task decomposition, dependency analysis, acceptance gates, and repository operations needed to validate planning.

## Product scope

Internal development may be staged. Public launch targets the complete initial product and may not be silently narrowed to a minimal public MVP.

The complete target includes all leaderboard scopes and periods, profiles, friends, rivals, overtakes, rank movement, presence, notifications, boards, organizations, hacker houses, communities, country boards, moderation, appeals, export, deletion, native local UX, and broad agent compatibility.

## Local-first constraint

Do not propose or configure a remote development control plane, autonomous cloud bootstrap, persistent remote agent service, remote model router, or remote private-context store.

## Non-negotiable privacy and integrity rules

- Servers never receive prompts, responses, transcripts, code, diffs, filenames, paths, project/repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims may cross the device boundary.
- Token Burn is the default ranking metric.
- Cash Burn is always explicitly estimated.
- Historical imports never enter active competition.
- Genuine but intentionally pointless usage counts.
- Weak evidence never masquerades as strong evidence.
- Public evidence language is Standard, Hardened, and Imported.
- Models and heuristics are secondary signals; deterministic controls own totals and hard protocol decisions.

## Authentication direction

Primary account access uses GitHub and X/Twitter OAuth. Passkeys or hardware-backed credentials are optional stronger factors. Specifications must cover account linking, provider compromise, provider loss, recovery, session revocation, and high-risk actions.

## Agent compatibility direction

Do not define support as a fixed handwritten list. Use a living, versioned adapter registry and tiered states: Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported, and Unsupported. Public claims must be generated from exercised evidence.

## Local product direction

The local product includes a background daemon installed and controlled through CLI, a macOS menu-bar experience, Windows/Linux tray experiences, local audit/control UX, a separate sync boundary, and a hosted web dashboard. Platform-specific differences must be explicit.

## Accepted technology direction

- Rust 2024 for VibeProof, adapters, collector, native core, privacy boundaries, canonical encoding/signing, replay, and protocol reference logic.
- Go for server APIs, ingestion, verification orchestration, aggregation workers, ranking, presence, migrations, and operational tooling.
- Next.js App Router and strict TypeScript for the hosted web product.
- PostgreSQL with pgx and explicit SQL as the server source of truth.
- Protobuf + Buf for internal contracts; canonical CBOR + CDDL + COSE for signed public claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engine, vector database, or ORM-heavy persistence without an evidence-backed ADR.

## Security and operations direction

- Use tiered OS-native hardening; never claim equal enforcement across platforms.
- Use append-only accepted claims, transactional outbox, idempotent aggregation, and deterministic rebuild.
- Freeze canonical encoding and require cross-language, malformed-vector, fuzz, resource, and differential tests.
- Require consumer-side release verification and TUF conformance before updater acceptance.
- Use telemetry allowlists and seeded canaries; content-bearing GenAI telemetry fields are forbidden.
- Keep active abuse thresholds, exploit signatures, unpublished incidents, and private business material outside public Git.
- CI, eval, dependency, security, and release workflows remain manual-only during planning and must be restored and validated before launch.

## Working style and completion

- Audit assumptions instead of agreeing automatically.
- Verify unstable platform, library, provider, pricing, and standards facts with primary sources.
- Use implementation-grade planning: interfaces, schemas, invariants, limits, failures, migrations, recovery, privacy, security, observability, compatibility, and tests.
- Do not claim completion from prose, empty fixtures, skipped tests, or placeholders.
- Keep the repository independently understandable without chat history.
- Update the decision register, dependency map, task catalog, and affected specifications when closing decisions.
- A planning task is complete only when a later implementation model can build it without inventing critical behavior.
