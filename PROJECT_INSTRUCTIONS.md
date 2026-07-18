# VibeMaxxing Project Instructions

## Authority

Use this precedence when materials disagree:

1. The user's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. This file.
4. `CURRENT_STATUS.md`.
5. `MODEL_OPERATING_MANUAL.md`.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. The nearest `AGENTS.md`.
9. Accepted ADRs and current specifications.
10. Historical research documents.

Never silently choose between contradictory sources. Record and resolve contradictions through the planning audit and decision register.

## Current phase

The project is in **planning and decision-closing mode**. Do not implement the product, execute deployment, build production adapters, or generate placeholder scaffolding unless the user explicitly opens the implementation phase.

Allowed work includes audits, research, ADRs, specifications, schemas, APIs, state machines, threat/control mappings, benchmark plans, fixtures, test plans, task decomposition, dependency analysis, acceptance gates, and repository operations needed to validate planning.

## Local-first constraint

Do not propose, configure, or assume a remote development control plane, autonomous cloud bootstrap, persistent remote agent service, remote model router, or remote private-context store. Previous remote orchestration plans are cancelled.

## Non-negotiable product and privacy rules

- Servers never receive prompts, responses, transcripts, code, diffs, filenames, paths, project or repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims may cross the device boundary.
- Token Burn is the default ranking metric.
- Cash Burn is always explicitly estimated.
- Historical imports never enter active competitive rankings.
- Weak evidence never masquerades as strong evidence.
- Public evidence language is `Standard`, `Hardened`, and `Imported`.

## Working style

- Audit assumptions rather than agreeing automatically.
- Verify unstable platform, library, provider, pricing, and standards facts with primary sources.
- Keep secrets outside prompts, logs, source control, and generated artifacts.
- Use implementation-grade planning: interfaces, schemas, invariants, limits, failures, migrations, recovery, privacy, security, observability, compatibility, and tests.
- Do not claim completion from documentation, empty fixtures, skipped tests, or placeholders.
- Keep the repository independently understandable without chat history.
- Update `docs/planning/DECISION_REGISTER.md`, `DEPENDENCY_MAP.md`, and `TASK_CATALOG.md` when closing decisions.

## Accepted technology direction

Use the stack in ADR-002:

- Rust 2024 for VibeProof, native collection, privacy boundaries, canonical encoding, signing, replay, and protocol reference logic.
- Go for server APIs, ingestion, verification orchestration, aggregation workers, presence, and operational tooling.
- Next.js App Router and strict TypeScript for the web product.
- PostgreSQL with pgx and explicit SQL as the server source of truth.
- Protobuf + Buf for internal contracts; canonical CBOR + CDDL + COSE for signed public claims.

Do not add Kubernetes, Kafka, GraphQL, a service mesh, workflow engine, vector database, or ORM-heavy persistence without an evidence-backed ADR.

## Accepted security and operations direction

- Use tiered OS-native sandboxing; never claim equal enforcement across platforms.
- Use passkeys/WebAuthn with multiple credentials and hardened recovery.
- Use append-only accepted claims, transactional outbox, idempotent aggregation, and deterministic rebuild.
- Freeze canonical encoding and require cross-language, malformed-vector, fuzz, resource, and differential tests.
- Require consumer-side release verification and TUF conformance before updater acceptance.
- Use telemetry allowlists and seeded canaries; content-bearing GenAI telemetry fields are forbidden.
- Generate support claims from exercised adapter evidence, not documentation alone.

## Planning completion rule

A planning task is complete only when a later implementation model can build it without inventing critical behavior. Follow `MODEL_OPERATING_MANUAL.md` and the planning exit gate in `docs/planning/PLANNING_AUDIT.md`.