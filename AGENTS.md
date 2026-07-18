# VibeMaxxing Agent Operating Manual

This file is the sole agent initialization entrypoint for the repository. Do not create additional start prompts, master-context files, model-specific instruction files, or competing agent manuals.

## 1. Initialize the repository context

Before proposing or changing anything:

1. Confirm the repository is `vedant-simulacrum/vibemaxxing` or an authorized fork of it.
2. Resolve the repository root, default branch, current branch, and working-tree state.
3. Identify the current pull request, linked issue, review threads, and requested changes when they exist.
4. Do not treat chat history, external notes, another repository, a stale branch, or generated indexes as authority.
5. Do not initialize a second product repository, protocol repository, documentation repository, or private context repository unless an accepted ADR explicitly requires it.
6. Do not revive the cancelled remote-development control-plane experiment.

When a task references another repository or dependency:

- use the exact upstream repository named by the relevant contract, lockfile, manifest, ADR, or issue;
- verify ownership, license, release status, compatibility, and maintenance before adoption;
- prefer official upstream repositories and primary documentation;
- do not copy or vendor a dependency merely to avoid understanding its integration;
- do not fork a dependency unless the decision register or a new ADR records the reason, divergence, update strategy, and exit plan.

## 2. Mandatory read order

Read only this bounded initialization set first:

1. `docs/project/PROJECT.md`
2. `docs/project/STATUS.md`
3. `docs/project/DOCUMENTATION.md`
4. `docs/planning/DECISION_REGISTER.md`
5. `docs/planning/TASK_CATALOG.md`
6. the relevant accepted ADRs and normative subsystem contracts
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `PR_SIZED_WORK_BREAKDOWN.md` only when implementation has been explicitly authorized
8. the nearest nested `AGENTS.md`, if one exists for the files being changed

Do not preload every research file. Use `docs/research/README.md` to locate only the evidence relevant to the active decision or task.

## 3. Phase gate

The current phase is defined by `docs/project/STATUS.md`.

At present, VibeMaxxing remains in **planning mode**:

- technical planning and implementation contracts are complete;
- product implementation has not begun;
- implementation requires a later explicit user instruction;
- do not write product code, deploy infrastructure, enable production automation, or claim executable evidence before that instruction.

Allowed planning work includes repository consolidation, targeted current research, external review, ADRs, contract refinement, schema/interface planning, issue decomposition, threat exercises, benchmark design, and evidence-plan improvement.

After explicit implementation approval, follow the build order and no-invention rules in `docs/implementation/IMPLEMENTATION_HANDOFF.md`. A narrow internal milestone never reduces the complete public-launch scope.

## 4. Binding product rules

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project or repository names, credentials, embeddings, summaries, classifications, or personal insights.
- Only fixed-schema safe claims cross the device boundary.
- Token Burn is the default raw ranking metric.
- Estimated Cash Burn is always explicitly estimated.
- Historical imports never enter active competition.
- Authentic intentionally pointless activity counts when non-duplicated.
- Public evidence states are Standard, Hardened, and Imported.
- GitHub App and X OAuth 2.0 PKCE are the primary identity paths; stronger credentials are optional.
- Agent support is tiered, versioned, and generated from exercised conformance evidence.
- The local topology includes collector, sync, daemon, CLI, menu-bar/tray, local privacy/audit UI, and hosted web.
- Public launch is comprehensive; staged development does not redefine scope.

## 5. Accepted technical ownership

- Rust 2024 owns VibeProof, adapters, collector, daemon/native core, privacy boundaries, deterministic accounting, canonical encoding, and signing.
- Go owns OAuth, public APIs, verification, ingestion, aggregation, ranking, presence, notifications, migrations, and operations tooling.
- Next.js App Router with strict TypeScript owns the hosted web product.
- PostgreSQL with pgx and explicit SQL is the server source of truth.
- Protobuf and Buf own internal contracts.
- Deterministic CBOR, CDDL, and COSE own signed public claims.

Do not add Kubernetes, Kafka, GraphQL, a service mesh, workflow engine, vector database, or ORM-heavy persistence without measured evidence and an accepted ADR.

## 6. Work selection and thread discipline

### Planning mode

Select work from a named open planning concern, user instruction, issue, review thread, or explicit contract defect. Broad replanning is prohibited unless a concrete contradiction, new requirement, or changed external fact exists.

### Implementation mode, once authorized

Use `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` in dependency order. One pull request should normally own one bounded unit.

### GitHub issues and pull requests

- Read the full issue or PR conversation before acting.
- Treat unresolved review threads and the latest maintainer instruction as active requirements.
- Do not create duplicate issues for work already represented in the task catalog or an existing issue.
- Link implementation PRs to the owning work item and decision IDs.
- Do not use comments or hidden branches as the only home for product decisions; merge durable conclusions into canonical docs.
- When a thread contradicts a canonical contract, stop and resolve the contradiction through the decision register and, when material, an ADR.

## 7. Dependency and schema discipline

- Define or update authoritative schemas before business logic that depends on them.
- Generated clients and bindings must originate from the authoritative schema; do not hand-maintain parallel types.
- Pin toolchains and lock dependencies.
- Add a dependency only with a clear owner, purpose, license, update path, security posture, and removal plan.
- Avoid overlapping libraries for the same responsibility.
- Database constraints, idempotency, migrations, rebuilds, corrections, deletion, and rollback are correctness requirements.
- Preserve transcript/network process separation in every dependency and integration decision.

## 8. Documentation ownership and anti-duplication

Use `docs/project/DOCUMENTATION.md` to find the one normative home for each concept.

Never create:

- another project-context file;
- another current-status file;
- another start prompt;
- another implementation roadmap;
- numbered research waves for conclusions already incorporated into contracts;
- duplicate architectural summaries that restate normative contracts.

When information belongs in an existing contract, update that contract and link to it. When a document becomes redundant, merge unique content, update references, and delete it.

Historical research remains under `docs/research/` and is classified by `docs/research/README.md`. Historical research does not override accepted ADRs or normative contracts.

## 9. Required quality standard

Every material change must account for:

- task and decision IDs;
- owning contract sections;
- interfaces and authoritative schemas;
- invariants, ordering, idempotency, limits, and errors;
- privacy and security impact;
- authorization and abuse behavior;
- storage, migrations, compatibility, and deletion;
- failure, retry, recovery, rollback, and rebuild behavior;
- observability allowlist;
- positive, negative, adversarial, performance, accessibility, and operational evidence where relevant.

Specifications, mocks, placeholders, skipped checks, empty fixtures, and unexecuted tests are not implementation evidence.

## 10. Completion report

At the end of a task report:

1. phase and task/decision IDs;
2. files or threads inspected;
3. files changed, created, moved, archived, or deleted;
4. decisions or contradictions resolved;
5. tests, validations, benchmarks, or reviews actually executed;
6. privacy, security, schema, migration, compatibility, and rollback impact;
7. remaining risks or blocked evidence;
8. next unblocked task, without silently changing phase.
