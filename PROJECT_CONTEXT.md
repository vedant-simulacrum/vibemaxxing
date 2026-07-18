# VibeMaxxing — authoritative project context

## Identity

- Canonical name: **VibeMaxxing**.
- Canonical lowercase wordmark: `vibemaxxing`.
- Domain: `vibemaxxing.dev`.
- Greenfield rebuild inspired by WhoBurnedMore; do not migrate old accounts, rankings, or scores.
- Product thesis: **Codex restraint × Steam social competition**.
- Visual thesis: **The Competitive Ledger**.
- Fully open source.

## Current development decision

VibeMaxxing remains active. The abandoned remote-development experiment is not part of the project.

Development is local-first. Do not assume or introduce:

- a remote development control plane;
- autonomous remote-machine setup;
- SSH-driven bootstrap;
- remote model routing;
- remote multi-agent orchestration;
- persistent remote coding workers;
- remote service-manager setup;
- remote development secret migration;
- a remote source of truth for project context.

Cloud infrastructure may still be evaluated later for the production product, but it is not a prerequisite for development and should not be confused with the cancelled development architecture.

## Product

VibeMaxxing is a privacy-preserving public leaderboard and social competition layer for AI-agent activity.

Primary metrics:

1. **Token Burn** — default ranking metric.
2. **Estimated Cash Burn** — always explicitly an estimate of API-equivalent value, never represented as actual user spend.

Genuine but pointless usage counts. The product does not judge usefulness, quality, productivity, or commercial value.

Leaderboard periods:

- today/daily;
- weekly;
- monthly;
- seasonal;
- yearly;
- lifetime/all-time.

Scopes:

- global;
- friends;
- private boards;
- organizations;
- hacker houses;
- communities;
- countries.

Historical imports are private analytics only, labelled **Imported**, and must not enter active competitive rankings.

## Social system

The social experience should feel Steam-like rather than enterprise-analytics-like:

- friend requests;
- rivals;
- overtakes;
- rank movement;
- active-session presence;
- private groups and boards;
- organization and community boards;
- notifications.

Presence exists only during a genuine qualifying active agent session. It must never reveal prompts, responses, code, diffs, tools, filenames, paths, repositories, or project names.

## Privacy contract

The server must never receive:

- prompts or responses;
- conversations or transcripts;
- code or diffs;
- tool arguments or outputs;
- filenames or paths;
- repository or project names;
- API keys or credentials;
- embeddings;
- semantic summaries;
- classifications;
- personal insights;
- local coaching or search data.

Only fixed-schema safe claims may cross the network boundary, including token categories, model/agent enums, coarse time buckets, evidence categories, protocol versions, sequence information, commitments, signatures, and pseudonymous revocable device identifiers.

The process that can inspect transcript content must be unable to access the network. The networked synchronization process must be unable to inspect transcript content. This is a technical boundary, not a policy sentence.

## VibeProof

VibeProof is the open local-first accounting and integrity protocol under VibeMaxxing.

Recommended integration ladder:

1. ACP broker/proxy;
2. native OpenTelemetry;
3. official hooks/plugins;
4. PTY or stdio wrapper;
5. live source-bound log observation;
6. historical import only.

Core responsibilities:

- deterministic normalization and accounting;
- live observation;
- secret redaction;
- replay and duplicate prevention;
- monotonic sequences;
- hash-chain or Merkle commitments;
- device keys;
- fixed-schema claims;
- deterministic encoding such as CBOR/CDDL;
- signatures such as COSE;
- separate collector and synchronization processes;
- inspectable outbound audit ledger;
- safe-field-only records;
- encryption at rest;
- export and deletion controls.

Do not promise that manipulation is impossible on a root-controlled machine. Use honest evidence levels. Consumer language should prefer **Standard**, **Hardened**, and **Imported**, and avoid absolute “verified” claims.

## Integrity

Cheating includes fabricated or edited logs, replay, backdating, modified counts or metadata, fake events, copied records, snapshot reuse, duplicate device submissions, and modified collectors/verifiers.

Deterministic code owns exact counting, normalization, deduplication, sequence validation, replay protection, and claim construction.

Local semantic models may assess structural authenticity and influence eligibility, quarantine, or review priority. They must not directly rewrite Token Burn totals or permanently ban users without stronger evidence and review.

## Platform and agent scope

Target major agents through capability-specific integrations, including Codex, Claude Code, Cursor, OpenCode, Cline, Gemini CLI, GitHub Copilot, Goose, OpenHands, Kimi, Qwen, Factory Droid, Kiro, OpenClaw, Mistral Vibe, ACP-compatible agents, and lower-evidence wrappers for unknown tools.

Target macOS, Windows, Linux, WSL, containers, local development environments, Codespaces, and CI. Baseline support must not require elevated privileges. Optional platform-specific hardening may produce stronger evidence.

## Design

Launch direction: light theme, indigo accent, premium and technically precise.

Approximate palette:

- background `#F7F7F5`;
- surface `#FFFFFF`;
- text `#111113`;
- secondary `#6B6B73`;
- hairline `#E7E7E4`;
- indigo `#5856E8`;
- indigo-soft `#F0EFFF`;
- positive `#14804A`;
- warning `#A56400`;
- critical `#C9362B`.

The leaderboard is the dominant object. The first screen should immediately answer who is winning, by how much, where the current user is, and what changed.

Avoid generic card grids, donut-chart filler, glassmorphism, cyberpunk, crypto aesthetics, esports medals, excessive gradients, flames, coins, gauges, literal token icons, and default component-library appearance.

Use spacious typography, hairlines, tabular numerals, precise alignment, restrained motion, excellent states, keyboard navigation, accessible status signals, and mobile recomposition.

## Suggested implementation stack

Local protocol and collector:

- Rust, Tokio, Clap;
- CBOR/CDDL and COSE;
- SQLite/SQLCipher;
- OS credential stores;
- local inference runtime where justified;
- Unix sockets or Windows named pipes;
- TUF, Sigstore, SBOM and provenance tooling.

Web:

- Next.js, React, TypeScript;
- custom design tokens with Tailwind utilities;
- selective Radix primitives;
- TanStack Query/Table/Virtual;
- custom D3 visualizations;
- Zod, React Hook Form;
- Vitest, Testing Library, Playwright, Axe, Storybook.

Server:

- Rust, Axum;
- PostgreSQL and SQLx;
- Redis-compatible caching where justified;
- durable queue when required;
- SSE/WebSockets;
- OpenAPI-generated clients;
- OpenTelemetry.

Production infrastructure remains a separate decision. Do not make it a prerequisite for starting local implementation.

## Repository rules

- One public open-source repository is sufficient.
- It must be independently buildable and testable.
- Do not hide required product source in private context.
- Keep secrets, unpublished incidents, hidden abuse thresholds, and private business material outside public Git.
- Public pull requests should use disposable hosted CI with minimal permissions and no production secrets.
- Do not use hidden branches as secret storage.

## Model and agent usage

No model is permanently designated as orchestrator. Choose tools by measured capability for the current task.

Cheap/fast models may handle searching, file classification, symbol extraction, dependency mapping, log summarization, and test triage. Strong models may handle architecture, difficult implementation, synthesis, protocol work, and independent review.

“Token maximization” means maximizing useful parallel reasoning while avoiding duplicated context. Reuse repository maps, symbol indexes, dependency graphs, file summaries, compact task packets, and structured findings. Do not build a complex orchestration platform before product code.

## First implementation milestone

Build one complete secure vertical slice:

synthetic live agent session
→ deterministic local accounting
→ signed fixed-schema safe claim
→ isolated synchronization boundary
→ server verification
→ invalid-signature rejection
→ replay rejection
→ deterministic duplicate handling
→ idempotent persistence
→ one-minute aggregation
→ leaderboard API
→ polished leaderboard row.

Acceptance must prove that transcript content never crosses the boundary, invalid claims fail, duplicate and replay behavior is deterministic, ranking works, the public repository builds from a clean checkout, and the UI follows the Competitive Ledger direction.

## Open decisions

Do not silently turn these into facts:

- final licences;
- production regions and providers;
- production RPO/RTO and budgets;
- exact model assignments;
- exact local verifier models;
- country verification;
- privacy defaults;
- pricing-source update process;
- strongest-evidence eligibility policy;
- whether VibeProof later becomes a separate repository;
- release-signing and notarization details;
- exact public launch scope.

## Assistant behaviour

Act like a skeptical founding CTO and principal engineer. Audit contradictions, security gaps, privacy hazards, unnecessary complexity, weak UX, generic design, placeholder architecture, and unverified external assumptions. Prefer execution-grade output and tested product progress over elaborate setup projects.
