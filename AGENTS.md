# VibeMaxxing Agent Instructions

## Current phase

The project is in **planning and decision-closing mode**. Do not implement the product unless the user explicitly changes the phase. Start with `MODEL_OPERATING_MANUAL.md` and `docs/planning/TASK_CATALOG.md`.

## Mission

Prepare and later build a privacy-preserving, cross-platform, open-source AI-agent activity protocol and social leaderboard without compromising the local/server trust boundary.

## Privacy boundary

Servers must never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project or repository names, credentials, embeddings, summaries, classifications, or personal insights. Only fixed-schema safe claims may cross the network boundary.

## Repository independence

The repository must be understandable, buildable, and testable without hidden chat context, private task logs, unpublished credentials, or proprietary infrastructure.

## Planning rules

- Read the mandatory files in `MODEL_OPERATING_MANUAL.md`.
- Select work by task ID from `docs/planning/TASK_CATALOG.md`.
- Respect `docs/planning/DEPENDENCY_MAP.md`.
- Update `docs/planning/DECISION_REGISTER.md` when a choice changes.
- Define interfaces, schemas, invariants, errors, state machines, limits, privacy, security, storage, migrations, recovery, compatibility, observability, tests, and evidence.
- Verify unstable external facts using primary sources.
- Do not treat specifications, empty fixtures, skipped tests, or placeholders as implementation evidence.
- Do not begin implementation because an older prompt says to do so.

## Binding product rules

- Token Burn is the default ranking metric.
- Cash Burn is always explicitly estimated.
- Historical imports never enter active rankings.
- Public evidence language is `Standard`, `Hardened`, and `Imported`.
- Development remains local-first.
- Follow accepted ADRs unless reopened through the decision register and an evidence-backed ADR.

## Review requirements

Every change must state its planning task and decision IDs, scope, privacy and security impact, future evidence contract, compatibility and migration impact, rollback implications, and unresolved questions.