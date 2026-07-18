# Prompt for a new coding or research agent

Read `PROJECT_CONTEXT.md`, `PROJECT_INSTRUCTIONS.md`, `AGENTS.md`, and the relevant specifications under `docs/` before changing anything.

VibeMaxxing remains the active project. Build it locally in this repository. Do not configure or propose a remote development machine, remote orchestration stack, autonomous cloud bootstrap, persistent remote worker fleet, remote model router, or remote private-context store. All previous plans of that kind are cancelled.

First audit the repository and report:

1. What is implemented versus specification-only.
2. Contradictions, unsupported claims, stale assumptions, and placeholder files.
3. The smallest secure vertical slice that can be completed end to end.
4. Exact tests and acceptance gates required.
5. Any current external facts that need verification.

Then execute the highest-value local implementation work. Prefer a complete tested vertical slice over broad scaffolding. Preserve the privacy contract and keep the public repository independently buildable.

Before implementation, read the accepted polyglot-stack ADR and performance budgets. Do not default the server to Rust merely because the collector uses Rust; new online services use Go unless benchmarked evidence and an ADR justify an exception.


Before implementing collector isolation, authentication, active ranking, release distribution, or telemetry, read ADR-003 and the Wave 2 research audit. Do not use email-only account recovery, naive minute-by-minute materialized-view refreshes, unbounded auto-instrumentation, or release signing without a consumer verification test.

Also read the Wave 3 materials:

- `docs/research/RESEARCH_AUDIT_2026-07_WAVE3.md`
- `docs/decisions/ADR-004-LIBRARIES_IPC_PRICING_AND_ABUSE.md`
- `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`
- `docs/security/ABUSE_AND_COUNTRY_PRIVACY.md`
- `docs/product/CASH_BURN_PRICING_PROVENANCE.md`

Implement these as executable contracts and tests, not documentation-only claims.

## Research wave 4 decisions

- Stop broad architecture expansion. New research must close a named decision with executable probes, fixtures, benchmarks, or attack evidence.
- Generate product support claims from a machine-readable adapter registry; never claim an agent is supported from documentation alone.
- Competitive beta requires three exercised live adapters, protocol differential tests, ranking benchmarks, platform IPC attack tests, adversarial integrity results, consumer release verification, and telemetry canary scans.
- Gemini CLI is currently the strongest documented telemetry candidate, but prompt/content logging must be explicitly disabled and tested. Claude Code and Codex require mode-specific structured-output or telemetry probes. All other agents remain unresolved until exercised.
- Keep the protocol codec behind a narrow internal boundary and defer final CBOR/COSE crate selection until malformed-vector, fuzz, resource-limit, and differential tests pass.
- Do not use full materialized-view refreshes as the minute-fresh ranking path. Benchmark transactional outbox plus period score tables.
- Secure updater selection requires upstream TUF conformance and malicious metadata tests.
- GenAI telemetry fields capable of carrying prompts, responses, tool definitions, system instructions, paths, or free text are forbidden. CI must use seeded canaries to prove absence.

