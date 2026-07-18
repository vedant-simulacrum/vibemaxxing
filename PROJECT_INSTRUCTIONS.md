# VibeMaxxing Project Instructions

## Authority

1. User's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. This file.
4. `CURRENT_STATUS.md`.
5. `MODEL_OPERATING_MANUAL.md`.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. Nearest `AGENTS.md`.
9. Accepted ADRs and current normative specifications.
10. Historical research.

Never silently choose between contradictory sources. Record material changes in the decision register and ADRs.

## Current phase

Technical planning is complete. Do not implement the product, deploy, enable production automation, or claim executable evidence until the user explicitly approves entry into implementation. Once approved, start from `docs/implementation/IMPLEMENTATION_HANDOFF.md`.

## Non-negotiable product and privacy rules

- Servers never receive prompts, responses, transcripts, code, diffs, filenames, paths, project/repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims cross the device boundary.
- Token Burn is the default raw ranking metric; Cash Burn is always explicitly estimated.
- Historical imports never enter active competition.
- Weak evidence never masquerades as strong evidence; public states are Standard, Hardened and Imported.
- Public launch is comprehensive; staging does not reduce scope.
- GitHub App and X PKCE are primary identity paths; passkeys are optional stronger factors.
- Agent support is tiered and generated from exercised conformance evidence.
- Local product includes collector, sync, daemon, CLI, menu-bar/tray, local audit UX and hosted web.

## Accepted technology direction

- Rust 2024 for VibeProof, adapters, native collection/runtime, privacy boundaries, canonical accounting/encoding/signing.
- Go for OAuth, APIs, ingestion, verification, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router and strict TypeScript for web.
- PostgreSQL/pgx and explicit SQL as server source of truth.
- Protobuf/Buf internally; deterministic CBOR/CDDL/COSE for signed claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engine, vector database or ORM-heavy persistence without evidence-backed ADR.

## Implementation rules after approval

- Follow the normative contract set and build sequence in the implementation handoff.
- Select libraries only within frozen behavior; material semantic changes require ADRs.
- Define/generated schemas before business logic.
- Preserve transcript/network process separation.
- Treat database constraints, migrations, rollback, deletion and rebuild as correctness.
- Every PR identifies task/decision IDs, contract sections, privacy/security impact, compatibility, tests, benchmarks and rollback.
- Do not claim completion from mocks, placeholders, skipped tests or unexecuted fixtures.

## Evidence boundary

Planning contracts are complete. CI, conformance, attacks, benchmarks, accessibility, packaging, security review, recovery drills and launch readiness remain executable evidence that must be produced during implementation.
