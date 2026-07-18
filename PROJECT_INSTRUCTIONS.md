# VibeMaxxing project instructions

## Authority

Use this precedence when materials disagree:

1. The user's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. This file.
4. The nearest `AGENTS.md`.
5. Current ADRs and specifications.
6. Older research and planning documents.

## Current operating constraint

The project is local-first. Do not propose, configure, or assume any remote development control plane, remote coding environment, autonomous cloud bootstrap, persistent remote agent service, remote model router, or remote private-context store.

Do not revive prior plans involving remote orchestration merely because they appear in old chat history or obsolete archives.

## Working style

- Audit assumptions rather than agreeing automatically.
- Verify current platform, model, library, and pricing facts before relying on them.
- Prefer primary documentation for technical claims.
- Make implementation-grade changes rather than producing empty scaffolding.
- Keep the public repository independently buildable.
- Protect the privacy contract over convenience.
- Keep secrets outside prompts, logs, source control, and generated artifacts.
- Use isolated local worktrees or branches for parallel tasks when useful.
- Use model routing only when it demonstrably improves quality or cost; do not build an orchestration platform as a prerequisite.
- Treat model names and deployment availability as runtime facts, not permanent architecture.

## Explicitly cancelled

The previous remote-development experiment, including its orchestration, bootstrap, model-routing, secret-migration, backup, and source-of-truth design, is superseded. Do not use its archived instructions.

## Enterprise engineering requirement

Treat `docs/engineering/ENGINEERING_SYSTEM.md`, `docs/evals/EVAL_SYSTEM.md`, and `docs/operations/PRODUCTION_READINESS.md` as mandatory engineering contracts. Do not claim production readiness from scaffolding alone. Add implementation and fixture evidence progressively, and turn each applicable eval from `not_applicable` into a blocking pass before the owning milestone is complete.

## Current technology decision

Use the deliberate polyglot stack in `docs/decisions/ADR-002-POLYGLOT-PRODUCTION-STACK.md`:

- Rust 2024 for VibeProof, native collection, privacy boundaries, canonical encoding, signing, replay, and protocol reference logic.
- Go 1.26 for server APIs, ingestion, verification orchestration, aggregation workers, presence, and operational tooling.
- Next.js App Router and strict TypeScript for the web product.
- PostgreSQL with pgx and explicit SQL as the server source of truth.
- Protobuf + Buf for internal contracts; canonical CBOR + CDDL + COSE for signed public claims.

Do not replace this with a single-language ideology. Do not add Kubernetes, Kafka, GraphQL, a service mesh, workflow engine, vector database, or ORM-heavy persistence layer without a separate evidence-backed ADR.


## Research wave 2 decisions

Also treat `docs/decisions/ADR-003-PLATFORM-SECURITY_AUTH_AND_RANKING.md` and `docs/research/RESEARCH_AUDIT_2026-07_WAVE2.md` as current accepted direction. In particular:

- use tiered OS-native sandboxing rather than claiming one equally strong portable sandbox;
- use passkeys/WebAuthn with multiple credentials and hardened recovery;
- maintain active rankings through transactional outbox and idempotent incremental aggregate tables, not frequent full materialized-view refreshes;
- freeze canonical CBOR rules and require differential golden-vector tests;
- require consumer-side release verification;
- enforce observability through telemetry allowlists and privacy tests;
- add active adversarial integrity campaigns before competitive beta.

## Research wave 3 decisions

- Prefer `github.com/go-webauthn/webauthn`; the Duo Labs predecessor is deprecated.
- Treat `coset` as a candidate COSE building block, not proof of canonical VibeProof compliance. Enforce canonical CBOR and malformed-input rejection independently.
- Local IPC must combine OS peer identity, explicit ACLs, fresh challenge/response, role negotiation, sequences, and strict limits.
- Device identities are revocable public keys with explicit rotation; lost keys do not silently inherit prior trust.
- Cash Burn uses immutable versioned pricing datasets with source provenance and effective dates. Usage facts remain separate from pricing.
- Country boards use coarse privacy-controlled assertions and minimum cohort protections.
- Anti-abuse is progressive and appealable; government identity is not required for ordinary participation.

## Research wave 4 decisions

- Stop broad architecture expansion. New research must close a named decision with executable probes, fixtures, benchmarks, or attack evidence.
- Generate product support claims from a machine-readable adapter registry; never claim an agent is supported from documentation alone.
- Competitive beta requires three exercised live adapters, protocol differential tests, ranking benchmarks, platform IPC attack tests, adversarial integrity results, consumer release verification, and telemetry canary scans.
- Gemini CLI is currently the strongest documented telemetry candidate, but prompt/content logging must be explicitly disabled and tested. Claude Code and Codex require mode-specific structured-output or telemetry probes. All other agents remain unresolved until exercised.
- Keep the protocol codec behind a narrow internal boundary and defer final CBOR/COSE crate selection until malformed-vector, fuzz, resource-limit, and differential tests pass.
- Do not use full materialized-view refreshes as the minute-fresh ranking path. Benchmark transactional outbox plus period score tables.
- Secure updater selection requires upstream TUF conformance and malicious metadata tests.
- GenAI telemetry fields capable of carrying prompts, responses, tool definitions, system instructions, paths, or free text are forbidden. CI must use seeded canaries to prove absence.

