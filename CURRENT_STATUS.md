# VibeMaxxing Current Status

Updated: 2026-07-19

## Current phase

VibeMaxxing has completed the **technical planning and implementation-contract phase**. Product implementation has not begun. The next phase starts only after the user explicitly approves implementation.

Development remains local-first. Previous remote development/control-plane plans remain cancelled.

## Frozen product direction

- Public launch targets the complete initial product; internal delivery may be staged.
- Token Burn is the default ranking metric; Cash Burn is always explicitly estimated.
- Genuine but intentionally pointless usage counts.
- Historical imports are private analytics only and never affect active competition.
- Primary identity is GitHub App user authorization and X OAuth 2.0 PKCE; passkeys/hardware credentials are optional stronger factors.
- Agent support is a tiered universal compatibility system with family fallbacks and exact conformance-backed support claims.
- Local UX includes daemon, private collector, network-safe sync, CLI, macOS menu bar, Windows/Linux tray, local privacy/audit dashboard, and hosted web product.
- The repository is private during planning and becomes public open source before public launch.

## Accepted technology direction

- Rust 2024: VibeProof, adapters, collector, daemon/native core, privacy boundaries, canonical accounting/encoding/signing.
- Go: public APIs, OAuth callbacks, verification orchestration, ingestion, aggregation, ranking, presence, notifications, migrations, and operations tooling.
- Next.js/strict TypeScript: hosted web product.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf internally; deterministic CBOR/CDDL/COSE for signed public claims.

## Normative implementation contracts

The implementation phase is governed by `docs/implementation/IMPLEMENTATION_HANDOFF.md`, which links the complete contract set for:

- scope, stages, terminology and launch gates;
- accounting, pricing, periods, ties, corrections and comparability;
- universal adapters, normalized events and certification;
- VibeProof claims, canonical encoding, keys, sequences, replay and transport;
- native processes, storage, IPC, devices, CLI, shell, updates and budgets;
- OAuth identity, account linking, sessions, recovery and authorization;
- APIs, PostgreSQL schema, transactions, outbox, aggregation, ranking and cache;
- profiles, friends, rivals, boards, countries, presence, notifications and moderation;
- anti-cheat, detector/SLM gates, appeals and red-team operations;
- web/native routes and states, privacy UX, accessibility and performance;
- deployment, TUF, observability, SLOs, recovery, open-source governance and launch.

A machine-readable agent registry and adversarial registry are committed under `conformance/`.

## Automation state

During planning, CI, security, release and eval workflows remain manual-only or disabled, and Dependabot is removed. P-1007 requires restoring and proving tuned automation after implementation begins. GitHub repository-level security settings may still notify independently.

## Repository evidence state

The repository contains specifications, contracts, schemas/registries, planning fixtures and small seed executable material. It does not contain a production product. Planning completion must not be represented as implementation completion.

Stale hand-maintained manifest/checksum files were removed. `scripts/repository/generate_repository_metadata.py` owns deterministic metadata generation from a checkout.

## Readiness

- Technical planning contracts: **complete**.
- Cross-document P0/P1 contradiction review: **complete at planning level**.
- Begin implementation: **blocked only on explicit user approval**.
- Competitive beta: **no-go until implementation evidence passes**.
- Public launch: **no-go until the comprehensive launch gate passes**.

## Canonical authority order

1. User's latest explicit instruction.
2. `PROJECT_CONTEXT.md`.
3. `PROJECT_INSTRUCTIONS.md`.
4. `CURRENT_STATUS.md`.
5. `MODEL_OPERATING_MANUAL.md`.
6. `IMPLEMENTATION_ROADMAP.md`.
7. `RESEARCH_AND_EVIDENCE_BACKLOG.md`.
8. Nearest `AGENTS.md`.
9. Accepted ADRs and current normative specifications.
10. Historical research.

## Next legal action

P-1104: the user explicitly approves entry into implementation. After approval, follow the build order and no-invention rules in `docs/implementation/IMPLEMENTATION_HANDOFF.md`; restore automated checks as implementation becomes executable rather than pretending documents are evidence.
