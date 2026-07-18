# VibeMaxxing

VibeMaxxing is a privacy-preserving competitive leaderboard and Steam-like social layer for AI-agent activity, built on the local-first VibeProof accounting and integrity protocol.

## Status

Technical planning and implementation contracts are complete. Product code has not begun. Implementation starts only after explicit user approval of P-1104.

## Start here

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `docs/planning/DECISION_REGISTER.md`
5. `docs/planning/TASK_CATALOG.md`
6. `docs/planning/SPECIFICATION_INDEX.md`
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md`

## Product principles

- No prompts, responses, transcripts, code, diffs, filenames, paths, project/repository names, tool contents, credentials, embeddings, summaries, classifications or personal insights are sent to VibeMaxxing servers.
- Token Burn is the default raw usage-volume metric.
- Cash Burn is always explicitly estimated.
- Historical imports remain private analytics and never enter active rankings.
- Genuine but intentionally wasteful activity counts when authentic and non-duplicated.
- Evidence states are Standard, Hardened and Imported.
- GitHub App and X OAuth 2.0 PKCE are primary identity paths; passkeys are optional stronger factors.
- Agent support is universal and tiered, with public claims generated from exact conformance evidence.
- Local UX includes collector, sync, daemon, CLI, macOS menu bar, Windows/Linux tray, local privacy controls and hosted web.
- Public launch targets the complete product; staged internal delivery does not reduce scope.

## Technical direction

- Rust 2024: VibeProof, adapters, native runtime, privacy boundaries and canonical accounting/claims.
- Go: OAuth, APIs, ingestion, verification, workers, ranking, presence and operations.
- Next.js/strict TypeScript: web product.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf internally; deterministic CBOR/CDDL/COSE for signed public claims.

## Repository map

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`: complete build order and no-invention rules.
- `docs/product/`: scope, accounting, social, integrity and UX contracts.
- `docs/architecture/`: protocol, native runtime, API/data/ranking contracts.
- `docs/security/`: privacy, threats, authentication and anti-cheat.
- `docs/operations/`: packaging, deployment, reliability, open-source and launch gates.
- `conformance/`: machine-readable agent and adversarial registries plus future executable fixtures.
- `apps/`, `crates/`, `packages/`: implementation areas.

## Readiness

- Technical planning: complete.
- Implementation: awaiting explicit approval.
- Competitive beta and public launch: no-go until executable evidence passes the complete gates.
