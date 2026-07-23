# VibeMaxxing Agent Operating Manual

This file is the sole agent initialization entrypoint. Do not create additional start prompts, master-context files, model-specific manuals, duplicate roadmaps or parallel project repositories.

## Initialize

Before changing anything:

1. Confirm the repository is `vedant-simulacrum/vibemaxxing` or an authorized fork.
2. Resolve root, default branch, current branch, working-tree state, current issue/PR, linked issue and unresolved review threads.
3. Run `python3 scripts/repository/doctor.py` from a clean checkout. Do not continue past a failure without repairing or documenting it.
4. Read, in order: `docs/project/PROJECT.md`, `docs/project/STATUS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`, `docs/planning/DECISION_REGISTER.md`, `docs/planning/TASK_CATALOG.md`, then relevant ADRs, contracts and schemas.
5. Read the implementation handoff and PR work breakdown only for implementation planning or after explicit implementation authorization.
6. Use `docs/research/README.md` to locate evidence relevant to the active decision.

Do not treat chat history, generated indexes, stale branches, historical completion reports, external notes, another repository or unexecuted fixtures as authority.

## Current phase

The current phase is defined only by `docs/project/STATUS.md`.

The repository is in **planning alignment and contract repair** under P-1140A–E. Product implementation has not begun and remains blocked by P-1104.

Allowed work:

- current primary-source research tied to an unresolved contract;
- repository-wide alignment and contradiction repair;
- normative contract, ADR, schema and planning-fixture refinement;
- planning-only validators and traceability checks;
- implementation decomposition and issue preparation without product code.

Not allowed until explicit implementation authorization:

- product code beyond the existing bounded prototype;
- production infrastructure or deployments;
- activation of product CI, fuzz, dependency, security, evaluation, signing or release workflows;
- claims of certified support, production hardening or launch readiness.

## Binding product rules

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications or personal insights.
- Only fixed-schema aggregate accounting and integrity claims cross the device boundary.
- Token Burn is the default raw ranking metric; Estimated Cash Burn is always labelled estimated and is server interpreted.
- Historical imports never enter active competition.
- Authentic intentionally pointless activity counts when non-duplicated.
- Standard and Hardened accepted claims may both count globally; Imported does not.
- Public evidence status is assigned by the server verifier, never selected by the client.
- Local-model and delayed offline usage are first-class when deterministically captured under a certified profile.
- OAuth proves provider-account control, not one unique human.
- VibeMaxxing actively enforces one ranked identity per detected/resolved person with privacy safeguards and appeals.
- Country leaderboards are post-launch.
- The SLM detector is post-launch research, local-only and non-authoritative.
- Public launch targets the complete core social product except country leaderboards; staged implementation does not redefine launch scope.

## Technical ownership

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundary, accounting, canonical encoding and signing.
- Go: OAuth, APIs, server verification and appraisal, ingestion, aggregation, ranking, presence, notifications, migrations and operations tooling.
- Strict TypeScript/Next.js: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal typed contracts.
- Deterministic CBOR/CDDL/COSE: signed public evidence claims and server receipts/appraisals.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases or ORM-heavy persistence without measured evidence and an accepted ADR.

## Repository and dependency discipline

- Use exact upstreams named by a contract, lockfile, manifest, ADR or issue.
- Verify ownership, license, release status, maintenance, compatibility, security posture, update path and removal plan before adoption.
- Prefer official upstreams and primary documentation.
- Forks require an ADR, divergence policy, update strategy and exit plan.
- Pin toolchains and dependencies; avoid overlapping libraries for the same responsibility.
- `docs/implementation/REPOSITORY_LAYOUT.md` distinguishes current paths from future paths.

## Schema and policy discipline

- Authoritative schemas live in `packages/schemas/`.
- Current schemas are planning-grade and must not be treated as implementation-ready where P-1140 marks them contradictory.
- Repair the authoritative schema before dependent business logic; generated bindings originate from the repaired source and are not hand-maintained in parallel.
- Stable reasons come from `reason-codes-v1.json`; configurable defaults come from `policy-defaults-v1.json` after their owning contracts are reconciled.
- Registries validate against adjacent schemas and may not imply exercised support when certifications are empty, planned or expired.
- Database constraints, idempotency, migrations, corrections, rebuilds, deletion, recovery and rollback are correctness requirements.

## Work and thread discipline

Planning work must map to a user instruction, issue/review thread, accepted decision or concrete contract defect. During P-1140, follow the dependency order in `docs/planning/TASK_CATALOG.md`.

After implementation authorization, use `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `PR_SIZED_WORK_BREAKDOWN.md`; generate execution threads through `docs/implementation/ISSUE_GENERATION.md`.

Read complete issue and PR conversations. Durable conclusions belong in canonical docs, ADRs, schemas or registries—not only comments or hidden branches.

## Documentation ownership

Use `docs/project/DOCUMENTATION.md` to locate the single normative owner. When duplicates appear: choose the owner, merge unique content, repair links, mark or delete the duplicate and record material changes.

Do not create another project context, status file, start prompt, roadmap, architecture summary, implementation plan or numbered research wave. The anti-cheat research and implementation plan are inputs to the single canonical handoff, not parallel authorities.

## Completion report

Report the phase and IDs, files and threads inspected, changes, decisions resolved, validations actually run, privacy/security/schema/migration/compatibility impact, remaining risks and next unblocked task without silently changing phase.

Specifications, mocks, placeholders, skipped checks, empty fixtures and unexecuted tests are not implementation evidence.