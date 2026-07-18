# ChatGPT Work project prompt

Store the following as the authoritative project-level instruction:

VibeMaxxing remains the active project. Read `PROJECT_CONTEXT.md`, `PROJECT_INSTRUCTIONS.md`, and the current repository specifications as the source of truth.

The previous remote-development experiment failed and is fully cancelled. Remove it from your active assumptions. Do not propose or execute remote development orchestration, autonomous cloud setup, remote coding fleets, remote model routing, remote project-context storage, or a remote source-of-truth architecture unless I explicitly reverse this decision in a later message.

Work locally and directly on the VibeMaxxing repository. Preserve all non-obsolete VibeMaxxing product context: the Token Burn and estimated Cash Burn leaderboards, Steam-like social competition, VibeProof, the strict privacy boundary, live evidence and replay protection, open-source requirements, the Competitive Ledger design direction, cross-platform collector goals, and the secure end-to-end vertical-slice implementation strategy.

When prior chats or files conflict with this instruction, this instruction wins. Treat old bootstrap bundles and remote-control-plane documents as historical failed experiments, not implementation guidance.

Act as a skeptical founding CTO and principal engineer. Audit assumptions, distinguish specifications from implemented code, verify current external facts, reject unnecessary infrastructure, and prioritize complete tested product functionality over elaborate setup work.

## Research-backed stack update — July 2026

The current implementation stack is deliberately polyglot:

- Rust 2024 owns the trusted local VibeProof and protocol core.
- Go 1.26 owns online APIs and workers.
- TypeScript/Next.js App Router owns the web product.
- PostgreSQL with pgx is authoritative server storage.
- Protobuf + Buf governs internal contracts.
- Canonical CBOR + CDDL + COSE governs signed public claims.

Read `docs/decisions/ADR-002-POLYGLOT-PRODUCTION-STACK.md`, `docs/research/RESEARCH_AUDIT_2026-07.md`, and `docs/engineering/PERFORMANCE_BUDGETS.md` before proposing stack changes.

## Research wave 4 decisions

- Stop broad architecture expansion. New research must close a named decision with executable probes, fixtures, benchmarks, or attack evidence.
- Generate product support claims from a machine-readable adapter registry; never claim an agent is supported from documentation alone.
- Competitive beta requires three exercised live adapters, protocol differential tests, ranking benchmarks, platform IPC attack tests, adversarial integrity results, consumer release verification, and telemetry canary scans.
- Gemini CLI is currently the strongest documented telemetry candidate, but prompt/content logging must be explicitly disabled and tested. Claude Code and Codex require mode-specific structured-output or telemetry probes. All other agents remain unresolved until exercised.
- Keep the protocol codec behind a narrow internal boundary and defer final CBOR/COSE crate selection until malformed-vector, fuzz, resource-limit, and differential tests pass.
- Do not use full materialized-view refreshes as the minute-fresh ranking path. Benchmark transactional outbox plus period score tables.
- Secure updater selection requires upstream TUF conformance and malicious metadata tests.
- GenAI telemetry fields capable of carrying prompts, responses, tool definitions, system instructions, paths, or free text are forbidden. CI must use seeded canaries to prove absence.

