# VibeMaxxing Agent Operating Manual

This file is the sole agent initialization entrypoint. Do not create additional start prompts, master-context files, model-specific manuals, duplicate roadmaps, or parallel project repositories.

## Initialize

Before changing anything:

1. Confirm the repository is `vedant-simulacrum/vibemaxxing` or an authorized fork.
2. Resolve root, default branch, current branch, working-tree state, current issue/PR, linked issue, and unresolved review threads.
3. Run `python3 scripts/repository/doctor.py` from a clean checkout. Do not continue past a failure without repairing or documenting it.
4. Read, in order: `docs/project/PROJECT.md`, `docs/project/STATUS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/DECISION_REGISTER.md`, `docs/planning/TASK_CATALOG.md`, then relevant ADRs, schemas, and subsystem contracts.
5. Read the implementation handoff and PR work breakdown only for implementation planning or after explicit implementation authorization.
6. Use `docs/research/README.md` to locate only research relevant to the active decision.

Do not treat chat history, generated indexes, stale branches, external notes, another repository, or unexecuted fixtures as authority.

## Current phase

The current phase is defined only by `docs/project/STATUS.md`.

Technical planning is complete at validated contract level. Product implementation has not begun and requires a later explicit user instruction under P-1104.

Allowed planning work includes targeted current research, external review, contract refinement, issue preparation, and evidence-plan maintenance tied to a concrete new fact, requirement, or contradiction. Do not restart broad planning without such a trigger. Do not write product code, deploy infrastructure, activate product security/release automation, or claim implementation evidence.

## Binding rules

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims cross the device boundary.
- Token Burn is the default raw ranking metric; Estimated Cash Burn is always labelled estimated.
- Historical imports never enter active competition.
- Authentic intentionally pointless activity counts when non-duplicated.
- Public evidence states are Standard, Hardened, and Imported.
- GitHub App and X OAuth 2.0 PKCE are primary identity paths; stronger credentials are optional.
- Agent support is tiered, versioned, and generated from exercised exact-version/mode/platform evidence.
- Public launch is comprehensive; staged development never redefines scope.

## Technical ownership

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundary, accounting, canonical encoding and signing.
- Go: OAuth, APIs, verification, ingestion, aggregation, ranking, presence, notifications, migrations and operations tooling.
- Strict TypeScript/Next.js: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal contracts.
- Deterministic CBOR/CDDL/COSE: signed public claims.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases, or ORM-heavy persistence without measured evidence and an accepted ADR.

## Repository and dependency discipline

- Use exact upstreams named by a contract, lockfile, manifest, ADR, or issue.
- Verify ownership, license, release status, maintenance, compatibility, security posture, update path, and removal plan before adoption.
- Prefer official upstreams and primary documentation.
- Forks require an ADR, divergence policy, update strategy, and exit plan.
- Pin toolchains and dependencies; avoid overlapping libraries for the same responsibility.
- `docs/implementation/REPOSITORY_LAYOUT.md` distinguishes current paths from future paths.

## Schema and policy discipline

- Authoritative schemas live in `packages/schemas/`; update them before dependent business logic.
- Generated bindings originate from authoritative schemas; do not hand-maintain parallel types.
- Stable reasons come from `reason-codes-v1.json`; configurable defaults come from `policy-defaults-v1.json`.
- Registries validate against adjacent schemas and may not imply exercised support when certifications are empty.
- Database constraints, idempotency, migrations, corrections, rebuilds, deletion, recovery, and rollback are correctness requirements.

## Work and thread discipline

Planning work must map to a user instruction, issue/review thread, decision, or concrete contract defect. After implementation authorization, use `PR_SIZED_WORK_BREAKDOWN.md` in dependency order and generate GitHub threads through `docs/implementation/ISSUE_GENERATION.md`.

Read complete issue and PR conversations. Durable conclusions belong in canonical docs, ADRs, schemas, or registries—not only comments or hidden branches.

## Documentation ownership

Use `docs/project/DOCUMENTATION.md` to locate the single normative owner. When duplicates appear: choose the owner, merge unique content, repair links, delete the duplicate, and record material changes.

Never create another project context, status file, start prompt, implementation roadmap, duplicate architecture summary, or numbered research wave.

## Completion report

Report the phase and IDs, files/threads inspected, changes, decisions resolved, validations actually run, privacy/security/schema/migration/compatibility impact, remaining risks, and next unblocked task without silently changing phase.

Specifications, mocks, placeholders, skipped checks, empty fixtures, and unexecuted tests are not implementation evidence.
