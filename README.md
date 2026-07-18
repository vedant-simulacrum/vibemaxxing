# VibeMaxxing

VibeMaxxing is a privacy-preserving competitive leaderboard and social layer for AI-agent activity, built on the local-first VibeProof accounting and integrity protocol.

## Current phase

The project is in **planning and decision-closing mode**. The repository is being prepared as a complete source of truth for later implementation. Do not begin product implementation until the planning exit gate passes and the user explicitly opens the implementation phase.

## Start here

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `IMPLEMENTATION_ROADMAP.md`
6. `RESEARCH_AND_EVIDENCE_BACKLOG.md`
7. `docs/planning/PLANNING_AUDIT.md`
8. `docs/planning/DECISION_REGISTER.md`
9. `docs/planning/DEPENDENCY_MAP.md`
10. `docs/planning/TASK_CATALOG.md`
11. `START_HERE_PROMPT.md`

## Product principles

- No prompts, responses, transcripts, code, diffs, filenames, paths, project or repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights are sent to VibeMaxxing servers.
- Competitive rankings use live, source-bound activity claims rather than editable retrospective logs.
- Token Burn is the default ranking metric.
- Cash Burn is always explicitly an estimate, not actual spend.
- Historical imports remain private analytics and never enter active rankings.
- Weak evidence never masquerades as strong evidence.
- Public evidence language is `Standard`, `Hardened`, and `Imported`.
- Development is local-first; prior remote-control-plane and persistent remote-agent plans are cancelled.

## Repository map

- `docs/product/`: product behavior, metrics, accounting, pricing, social, and onboarding.
- `docs/privacy/`: privacy contract.
- `docs/security/`: threats, integrity, platform isolation, IPC, authentication, and abuse.
- `docs/architecture/`: system and ranking architecture.
- `docs/decisions/`: accepted ADRs.
- `docs/research/`: historical research evidence.
- `docs/planning/`: current planning audit, decisions, dependencies, and atomic task catalog.
- `docs/engineering/`, `docs/evals/`, `docs/qa/`, `docs/operations/`: engineering and production evidence requirements.
- `conformance/`, `benchmarks/`, `evals/`, `artifacts/`: future executable evidence and current seed material.
- `apps/`, `crates/`, `packages/`: implementation areas; most are currently scaffolds or specifications.

## Current readiness

Planning may continue. Product implementation, competitive beta, and production release are currently no-go. See `CURRENT_STATUS.md` and `docs/planning/PLANNING_AUDIT.md`.