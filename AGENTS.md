# VibeMaxxing Agent Instructions

## Current phase

Technical planning is complete. Product implementation begins only after explicit user approval. Before approval, do not write product code or enable production workflows. After approval, start with `docs/implementation/IMPLEMENTATION_HANDOFF.md`.

## Mission

Build a privacy-preserving, cross-platform, open-source AI-agent activity protocol and complete social competition product without compromising the local/server trust boundary.

## Binding rules

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications or personal insights.
- Token Burn is the default raw metric; Cash Burn is always estimated.
- Historical imports never enter active competition.
- Evidence states are Standard, Hardened and Imported.
- Public launch is comprehensive; internal implementation may be staged.
- GitHub App and X PKCE are primary identity paths; stronger credentials are optional.
- Agent support is tiered and conformance-backed.
- Local topology includes collector, sync, daemon, CLI, menu-bar/tray, local privacy UI and hosted web.
- Follow accepted ADRs and normative contracts unless reopened through the decision register.

## Work selection

Use `docs/planning/TASK_CATALOG.md`. P-1104 is the current gate. Once approved, follow the build order and PR completion contract in `docs/implementation/IMPLEMENTATION_HANDOFF.md`.

## Review requirements

Every implementation change states task/decision IDs, contract sections, schema/migration impact, privacy/security impact, compatibility, rollback, tests, benchmark impact and remaining risk. Specifications, mocks, placeholders, skipped tests and unexecuted fixtures are not implementation evidence.
