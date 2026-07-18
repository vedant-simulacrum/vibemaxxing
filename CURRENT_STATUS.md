# VibeMaxxing Current Status

Updated: 2026-07-19

## Current phase

VibeMaxxing is in **planning and decision-closing mode**. Internal work may be staged. Product implementation begins only after the planning exit review and explicit user approval.

Development is local-first. Previous remote development/control-plane plans remain cancelled.

## Product direction now frozen

- Public launch targets the complete initial product rather than a narrow public MVP.
- Internal milestones and private testing may be narrow and staged.
- Token Burn is the default ranking metric; Cash Burn is always explicitly estimated.
- Genuine but intentionally pointless usage counts.
- Historical imports are private analytics only and never affect active competition.
- Primary sign-in is GitHub and X/Twitter OAuth; passkeys/hardware credentials are optional stronger factors.
- Agent support is a tiered universal compatibility system, not a fixed list.
- Local UX includes a background daemon installed/controlled by CLI, macOS menu-bar, Windows/Linux tray, local audit/control UX, and hosted web dashboard.
- The repository is private during planning and becomes public open source before public launch.

## Accepted technology direction

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundary, canonical encoding/signing.
- Go: ingestion, verification orchestration, aggregation, ranking, presence, migrations, and operations tooling.
- Next.js/strict TypeScript: hosted web product.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf internally; canonical CBOR/CDDL/COSE for signed public claims.

## Repository state

The repository contains substantial product, privacy, integrity, architecture, design, engineering, operations, research, and planning material. Authority-level contradictions involving backend language, authentication, launch scope, agent coverage, and native UX have been corrected.

The repository also contains seed executable material such as a minimal Go health endpoint, policy/eval runners, telemetry canary scanner, capability probe, benchmark seed, and conformance declarations. These are not a production implementation.

## Automation state

During planning:

- CI is manual-only.
- Security workflows are manual-only.
- Release evidence is manual-only.
- Automated eval matrices are disabled.
- Dependabot configuration is removed.

These controls must be restored, redesigned where necessary, and validated before launch. Repository-level GitHub security settings may still create notifications independently of workflow files.

## Remaining planning work

The complete dependency-ordered program is in `docs/planning/TASK_CATALOG.md`. Major unresolved work includes:

- complete launch matrix, user journeys, glossary, and gates;
- normative token accounting, cross-provider comparability, pricing, periods, and corrections;
- machine-readable agent census, adapter/event schemas, certification, and community governance;
- complete VibeProof claim, encoding, signing, error, transport, and state-machine contracts;
- daemon/collector/sync/CLI/shell IPC, storage, lifecycle, device, installer, update, and platform contracts;
- GitHub/X identity research, account linking, sessions, recovery, native authorization, and permission matrices;
- complete APIs, PostgreSQL schema, transactions, workers, ranking, and benchmark plans;
- social, boards, countries, presence, notifications, moderation, appeals, retention, export, and deletion;
- populated anti-cheat control catalog, attack lab, detector bakeoff, SLM decision, and red-team operations;
- route/state contracts, accessibility, privacy verification, design QA, packaging, deployment, SLOs, incident response, backup/restore, and open-source governance;
- final contradiction, traceability, completeness, implementation, and launch reviews.

## Generated metadata

`MANIFEST_FILES.txt`, `FILE_INDEX.md`, `SHA256SUMS`, and related generated indexes must not be treated as authoritative until regenerated from the live repository tree. A deterministic generator is required; hand-maintained indexes are prohibited.

## Readiness

- Continue planning: **go**.
- Begin product implementation: **no-go**.
- Competitive beta: **no-go**.
- Public launch: **no-go**.

These no-go results reflect intentionally incomplete specifications and evidence, not a recommendation to narrow the complete launch scope.

## Canonical authority order

1. User's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. `PROJECT_INSTRUCTIONS.md`.
4. `CURRENT_STATUS.md`.
5. `MODEL_OPERATING_MANUAL.md`.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. Nearest `AGENTS.md`.
9. Accepted ADRs and current specifications.
10. Historical research documents.

## Next work

Use `docs/planning/TASK_CATALOG.md`. The immediate sequence is P-007/P-008/P-009, then P-051 through P-055, followed by accounting and agent compatibility. Update the decision register and every affected canonical specification when closing a decision.
