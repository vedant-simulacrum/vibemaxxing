# VibeMaxxing Agent Operating Manual

This file is the sole agent initialization entrypoint. Do not create additional start prompts, master-context files, model-specific manuals, duplicate roadmaps, or parallel project repositories.

The rule is about authority, not about file count. Every tracked markdown file must be named in `docs/project/DOCUMENTATION.md`, which is where the single normative owner of each topic is declared, and `scripts/repository/doctor.py` fails on one that is not. A new document is fine when it owns something no existing document owns and says so in that table, beside everything else that owns something. It is not fine when it restates phase, gate, status, scope or plan that an existing authority already owns, because then two files answer the same question and a reader cannot tell which is stale.

That check replaced a blocklist of thirteen exact filenames. Those thirteen were real files that once competed with the authorities they duplicated, and they stay refused, but refusing names only caught what had already happened: a fourteenth competing file under any other name passed every check in this repository.

## Initialize

Before changing anything:

1. Confirm the repository is `vedant-simulacrum/vibemaxxing` or an authorized fork.
2. Resolve default branch, current branch, working-tree state, current issue/PR, linked issue, and unresolved review threads.
3. Run `python3 scripts/repository/doctor.py` from a clean checkout. Do not continue past a failure without repairing or documenting it.
4. Read, in order: `docs/project/PROJECT.md`, `docs/project/STATUS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/DECISION_REGISTER.md`, `docs/planning/TASK_CATALOG.md`, `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, and `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`, then relevant ADRs, contracts, schemas, fixtures, issues, and PR discussions.
5. Read `conformance/p1140f/gate-authorization-v1.json` before acting on anything this file says about phase, gate, or authorization state. The record is authoritative; this file restates it.
6. Use `docs/research/README.md` to locate primary evidence relevant to the active decision.

Do not treat chat history, generated indexes, stale branches, historical completion reports, external notes, another repository, green structural checks, or unexecuted fixtures as authority.

## Current phase

The repository is in the **implementation** phase. `conformance/p1140f/gate-authorization-v1.json` is the sole authority for phase and gate state. This section restates that record and may never contradict it; when the two disagree, the record is correct and this file is the defect.

- **P-1140E: complete-planning.** It proves structural consistency and nothing else.
- **P-1140F: complete-planning.** All thirteen semantic findings, SR-005 through SR-017, are closed in `conformance/p1140f/semantic-findings-v1.json` on reviewed head `46bf2fa47963261d48fa80a6980de85d80cfaad8`, graded under D-300 as nine P0, three P1 and one P2, each severity carrying its own non-regression ceiling. The gate was closed by owner decision D-635 over one unmet criterion: the exact-head review was not independent, having been performed under delegated owner authority by the same agent that performed the repairs. That is limitation 1 of the verdict and the limb of SR-016 that performing the review cannot close. Closing this gate is a decision, not evidence: it means the recorded contradictions are gone from the planning contracts and nothing more.
- **P-1104: authorized-open.** Product implementation is authorized. The gate was opened by owner decision on 2026-08-05 under `https://github.com/vedant-simulacrum/vibemaxxing/issues/44` while those thirteen findings were open and `conformance/p1140f/review-target-v1.json` was not pinned. The documented preconditions were knowingly accepted, not met. The findings are tracked and are not waived.

Opening P-1104 authorizes implementation work. It is not evidence that any component is implemented, correct, secure, private, certified, or launch-ready.

The owner has elected to finish the planning track first. Product code is permitted but is not the active program; the active program remains the semantic closure sequence in `docs/planning/TASK_CATALOG.md`.

The earlier P-1140F four-finding review at `f06f630619427ec7f0576b57c4b3ac914d9a4c87` is stale. Later commits added executable Rust/Go protocol and accounting prototypes and additional machine contracts. The canonical current semantic scope, findings, closed defaults, user decisions, and dependency order live only in `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`.

Allowed work:

- primary-source research tied to an unresolved P-1140F finding;
- repository-wide authority alignment and contradiction repair;
- normative contract, ADR, schema, state, policy, fixture, and planning-validator refinement;
- implementation decomposition and issue preparation;
- product code, under an accepted contract and a work unit that names its files and acceptance criteria.

Still not allowed, and not unlocked by P-1104:

- production infrastructure or deployments;
- activation of product CI, fuzz, dependency, security, evaluation, signing, release, or deployment workflows;
- certified-support, production-hardening, or launch-readiness claims;
- closing, downgrading, or waiving a P-1140F finding without recorded closure evidence and a review verdict;
- changing any gate state. Gates are opened and closed by the owner, never by an agent.

## Evidence discipline

- P-1140E proves structural consistency only.
- P-1140F owns semantic and standards closure.
- A green validator does not prove security, privacy, standards conformance, implementability, transaction safety, or runtime behavior.
- Specifications, mocks, placeholders, skipped checks, empty fixtures, and unexecuted tests are not implementation evidence.
- Cross-language agreement is not conformance when both implementations consume the wrong authority.
- A suite name must describe what it actually executes.
- An eval suite reported as `not_applicable` is an absence of evidence, never a pass.
- This file is not authority for phase or gate state. `conformance/p1140f/gate-authorization-v1.json` is. Repair this file when it drifts; do not repair the record to match it.
- P-1104 being open is a decision, not evidence. No agent may report a P-1140F finding as closed without recorded closure evidence and a review verdict in `conformance/p1140f/semantic-findings-v1.json`, and no agent may claim launch readiness while any semantic P0 or P1 remains open.

## Binding product rules

- Servers never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights, or content-derived hashes.
- Only fixed-schema aggregate accounting and integrity claims cross the device boundary.
- Token Burn is the raw ranking metric of record: accepted, immutable, unnormalized. Public rank is computed on Credited Token Burn, which is Token Burn times a server-assigned confidence weight under ADR-020. Public surfaces publish the credited figure only; the raw figure is confined to the participant's own surface and to viewers they authorize, because publishing both recovers the weight by division and therefore recovers a sanction the product keeps private. Estimated Cash Burn is always labelled estimated and server interpreted.
- Historical imports never enter active competition.
- Authentic intentionally pointless activity counts when non-duplicated.
- Public evidence status and competitive eligibility are assigned by the server verifier, never selected by the client.
- Local-model and delayed offline usage count competitively only when deterministically captured under one active exact certified source/accounting tuple.
- OAuth proves provider-account control, not unique humanity.
- Account, linked provider identity, and ranked identity are separate aggregates.
- One person may have only one active resolved ranked identity, with private evidence, appeals, and no automatic summation of duplicate account scores.
- Continuity is lineage-scoped rather than device-row-scoped.
- Accepted claims and historical facts remain immutable; corrections, consolidation, deletion effects, and reversals are append-only. An Article 17 erasure deletes the live personal records, including accepted claims, and appends a signed erasure record; it never deletes a row from a sealed ranking generation, never renumbers one, and makes the retained entry unattributable by destroying the key that binds its pseudonym to the person.
- Generic ACP, OpenTelemetry, proxy, wrapper, and unknown-version integrations remain private analytics until an exact tuple is certified.
- Only global leaderboard views are universally public by default. Friend, rival, private, and unlisted board views require current viewer authorization.
- Blocks are directional and independent from symmetric friendship state.
- Presence is server-derived from qualifying device activity; private is a visibility policy.
- The server inbox is notification authority; push and email are best-effort hints.
- Deterministic controls are authoritative. Statistical/SLM detection remains local-only, advisory, and post-launch.
- Country leaderboards remain post-launch.
- Public launch still targets the complete core social product except country leaderboards; staged implementation does not redefine launch scope.

## Active semantic program

Follow `docs/planning/TASK_CATALOG.md` exactly:

1. **P-1140F-1:** re-establish sole protocol and repository authority.
2. **P-1140F-2:** close OAuth, identity, lineage, replay, fork, appeal, and recovery.
3. **P-1140F-3:** close native trust domains, role-bound IPC, adapters, certification, and accounting inputs.
4. **P-1140F-4:** close idempotency, ranking, social, boards, presence, notifications, export, deletion, retention, and current privacy authorization.
5. **P-1140F-5:** close TUF-backed release, compatibility, migration, rollback, and exact-head semantic review.

Do not silently work around a finding in code or duplicate its authority in a new file.

## Technical ownership

- Rust 2024: normative VibeProof codecs, adapters, collector, native core, privacy boundary, accounting, canonical encoding, signing, daemon, CLI, and interactive shell.
- Go: OAuth, APIs, server verification/appraisal, ingestion, aggregation, ranking, presence, notifications, migrations, and operations tooling.
- Strict TypeScript/Next.js: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal typed contracts.
- Deterministic CBOR/CDDL/COSE: signed public evidence claims and server receipts/appraisals.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases, or ORM-heavy persistence without measured evidence and an accepted ADR.

## Schema and state discipline

- Authoritative schemas live in `packages/schemas/`.
- Repair the authoritative schema before dependent business logic; generated bindings originate from that source and are not hand-maintained in parallel.
- Every mutable aggregate must have one reachable state machine, one persistence owner, a revision model, stable outcomes, transaction boundaries, and reversal/expiry behavior where applicable.
- API, SQL, Protobuf/CDDL, policies, reasons, fixtures, and state vocabularies must cross-resolve without hidden security-critical mappings.
- Stable reasons come from `reason-codes-v1.json`; configurable defaults come from `policy-defaults-v1.json` only after their owning contract is reconciled.
- Registries may not imply exercised support when certifications are empty, planned, expired, suspended, or do not bind the exact tuple.
- Database constraints, exact idempotent replay, migrations, corrections, rebuilds, deletion, recovery, and rollback are correctness requirements.

## Repository and dependency discipline

- Use exact upstreams named by a contract, lockfile, manifest, ADR, or issue.
- Verify ownership, license, release status, maintenance, compatibility, security posture, update path, and removal plan before adoption.
- Prefer official upstreams and primary documentation.
- Forks require an ADR, divergence policy, update strategy, and exit plan.
- Pin toolchains and dependencies; avoid overlapping libraries for the same responsibility.
- `docs/implementation/REPOSITORY_LAYOUT.md` distinguishes current paths from future paths.

## Workspace boundary

Commit only reviewed source, contracts, schemas, synthetic fixtures, governed assets, reproducible baselines, and explicitly classified generated metadata that satisfy `docs/planning/ARTIFACT_POLICY.md`.

Keep agent sessions, prompts, transcripts, private repository material, credentials, machine-specific settings, caches, generated builds, dependencies, and transient captures outside Git. `assets/` is the canonical repository-owned visual library. `artifacts/` is non-authoritative unless explicitly classified.

## Work and documentation discipline

Planning work must map to a user instruction, issue/review thread, accepted decision, or concrete contract defect. Read complete issue and PR conversations. Durable conclusions belong in canonical docs, ADRs, schemas, registries, or issue scope—not only comments or hidden branches.

Use `docs/project/DOCUMENTATION.md` to locate the single normative owner. When duplicates appear, choose the owner, merge unique content, repair references, and delete or clearly mark the duplicate. Do not create another project context, status file, start prompt, roadmap, architecture summary, implementation plan, or numbered research wave.

After implementation authorization, use `docs/implementation/IMPLEMENTATION_HANDOFF.md`, `PR_SIZED_WORK_BREAKDOWN.md`, and `ISSUE_GENERATION.md`.

## Completion report

Report the phase and IDs, exact head, files and threads inspected, changes made, decisions resolved, validations actually run, privacy/security/schema/migration/compatibility impact, remaining risks, and next unblocked task. Never silently change phase or claim checks that were not executed.
