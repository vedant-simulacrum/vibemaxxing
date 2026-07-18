# Prompt for a new VibeMaxxing model

Read, in order:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `docs/planning/PRODUCT_SCOPE_FREEZE.md`
6. `IMPLEMENTATION_ROADMAP.md`
7. `docs/planning/DECISION_REGISTER.md`
8. `docs/planning/DEPENDENCY_MAP.md`
9. `docs/planning/TASK_CATALOG.md`
10. `docs/planning/SPECIFICATION_INDEX.md`
11. Nearest `AGENTS.md` and relevant ADRs/specifications

## Current phase

VibeMaxxing is in planning and decision-closing mode. Do not implement the product, deploy infrastructure, build production adapters, execute eval suites, or create placeholder scaffolding unless the user explicitly opens implementation.

The repository must become sufficient for a future implementation model to work without hidden chat context.

## Frozen direction

- Internal delivery may be staged; public launch targets the complete initial product.
- The complete product includes every leaderboard scope/period, full social/group/presence/notification/moderation/lifecycle behavior, native daemon/CLI/menu-bar/tray UX, hosted web, and broad agent-family coverage.
- Primary sign-in is GitHub and X/Twitter OAuth. Passkeys or hardware credentials are optional stronger factors.
- Agent coverage is a tiered living compatibility system, not a fixed list.
- Rust owns the native/protocol core; Go owns server services; Next.js/TypeScript owns hosted web; PostgreSQL/pgx is the server source of truth.
- Deterministic controls own counting, signatures, sequences, replay, duplicates, and hard eligibility. SLMs are optional residual-risk signals only.
- The repository is private during planning and becomes public open source before public launch.
- CI, security, release, dependency, and eval automation remain manual-only or disabled during planning.

## First response

Report:

1. Files read and current phase.
2. Highest-priority unblocked planning task ID.
3. Contradictions, stale assumptions, unsupported claims, incomplete contracts, or damaged/generated artifacts found.
4. Exact files to update.
5. Confirmation that no product implementation will begin.

## Planning work standard

For the selected task:

- close a named decision or ambiguity;
- verify unstable facts with current primary sources;
- define interfaces, schemas, state machines, invariants, limits, ordering, idempotency, failures, privacy, security, authorization, storage, migration, recovery, deletion, compatibility, observability, and user states;
- define positive, negative, adversarial, performance, and accessibility evidence where relevant;
- update the decision register, dependency map, task catalog, roadmap, status, and affected specifications;
- leave no dependency on hidden chat context.

Do not mark planning complete from broad prose, skipped checks, empty fixtures, or placeholders. A later implementation agent must not need to invent critical behavior.

## Non-negotiable constraints

- No prompts, responses, transcripts, code, diffs, filenames, paths, project/repository names, tool contents, credentials, embeddings, summaries, classifications, or personal insights may be sent to VibeMaxxing servers.
- Historical imports never enter active competitive rankings.
- Token Burn is default; Cash Burn is explicitly estimated.
- Genuine but intentionally pointless usage counts.
- Weak evidence never masquerades as strong evidence.
- Development remains local-first; cancelled remote-control-plane plans must not return.

At the end, report decisions closed, files changed, remaining blockers, newly unblocked task IDs, and the next exact planning task.
