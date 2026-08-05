# ADR-018: Database and migration tooling

Status: accepted, awaiting owner ratification
Date: 2026-08-06
Decision: D-097

## Context

The owner delegated this choice and reserved ratification, so the status above is precise: the decision is made and usable, and it carries an outstanding owner signature rather than an outstanding analysis.

The surrounding constraints are already binding and they eliminate most of the option space before any tool is compared. D-010 fixes PostgreSQL with pgx and explicit SQL as the server source of truth. D-026 excludes ORM-heavy persistence absent evidence-backed reversal. D-039 fixes managed PostgreSQL as the production shape. `packages/schemas/planning-schema.sql` is the authoritative schema and `docs/project/DOCUMENTATION.md` names it as such. `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` already requires expand and contract migrations, backward-compatible deployments, version gates, online index creation, tested rollback and preproduction restore drills, and requires that a destructive migration have a verified backup and explicit data-lifecycle approval. `docs/implementation/REPOSITORY_LAYOUT.md` reserves `/migrations` for the executable migration history.

What was missing was not a policy. It was the executable that applies the policy, and the absence blocked the first migration, which blocks every unit that needs a table.

There is a specific trap in this choice that the repository's own rules make sharper than usual. A migration tool that wants a declarative schema source becomes a second place where the schema is defined. `packages/schemas/planning-schema.sql` is the authoritative schema; a second declarative source would either duplicate it or replace it, and either outcome creates the exact condition the documentation map forbids — two artifacts describing one concept with no stated owner. That is the dominant selection criterion here, ahead of features.

The runtime target is PostgreSQL 16 or later. That floor is not arbitrary: the planning validation already runs against `postgres:16`, and 16 or later is what every managed offering on the ADR-017 shortlist provides. Anything the schema uses must be available at 16, so a later minor or major version is permitted and a feature that requires one is not.

## Decision

**Managed PostgreSQL 16 or later is the server database.** No self-managed instance, no alternative engine, no compatibility layer. The exact managed offering follows from the ADR-017 provider selection and does not change this decision.

**`goose` is the migration tool**, used as a command-line runner in operations and as an embedded library in the API binary for version-gate checks. Migrations are plain `.sql` files with explicit `-- +goose Up` and `-- +goose Down` sections, live in `/migrations` as `docs/implementation/REPOSITORY_LAYOUT.md` reserves, and are named `NNNNN_short_description.sql` with sequential zero-padded numbering.

Sequential numbering rather than timestamps is chosen because D-091 fixes a single maintainer and requires linear history on `main`, which removes the concurrent-authoring collision that timestamps exist to prevent, and because a sequential file listing reads in application order. If a second maintainer joins and concurrent authoring begins, `goose fix` converts timestamped files to sequential ones at merge, so this is a reversible preference rather than a structural commitment.

`goose` is invoked with an explicit connection string supplied by the deployment environment and never with an embedded credential. Migration application is a deliberate operator or deployment-pipeline step, never a side effect of the API process starting.

### Why goose

- **It is Go, which is the server stack.** D-010 puts OAuth, APIs, ingestion, aggregation, ranking, migrations and operations tooling in Go. A Go migration tool is installed by the toolchain the project already pins, is embeddable in the API binary so a version gate can assert the applied migration version before serving traffic, and adds no second language runtime to the operational surface. The repository's dependency discipline asks for exactly this: no overlapping toolchains for one responsibility.
- **It applies plain `.sql` files and holds no opinion about the schema.** `goose` is a version ledger and an executor. It does not parse the schema, does not maintain a model of it, and does not need a source of truth of its own. `packages/schemas/planning-schema.sql` stays the single authority and the migration history stays the record of how the database got there. This is the criterion that decides the choice.
- **It supports `-- +goose NO TRANSACTION`,** which is what makes online index creation actually possible. `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block, and the operations contract requires online index creation on a table that is serving traffic. A runner that wraps every migration in a transaction with no escape hatch cannot execute a required migration class at all. This is a hard capability requirement, not a convenience.
- **`-- +goose StatementBegin` and `-- +goose StatementEnd`** let a single migration carry a function or `DO` block containing semicolons without the runner mis-splitting it, which a backfill or a constraint-validation step needs.
- **Down sections are ordinary SQL in the same file**, so a rollback is reviewable in the same diff as the change it reverses and is executable in a preproduction restore drill. The contract requires tested rollback; a tool whose rollback is generated rather than written is a tool whose rollback is not reviewed.
- **It is Apache-2.0 licensed and has no commercial tier**, so there is no feature boundary that a project on a sub-100-USD budget under D-093 might collide with later.

### Rejected alternatives

- **`golang-migrate`.** The closest call, and the runner-up. It is also Go-native, also plain `.sql`, also supports skipping the transaction wrapper, and would satisfy most of this ADR. It is rejected on two smaller margins rather than one large one: its up and down migrations live in separate files, so a change and its reversal are reviewed apart from each other, which is precisely the review property the tested-rollback requirement depends on; and its library surface is oriented around the command-line use rather than around embedding a version assertion in a service, which is how the version gate is implemented here. The decision is deliberately cheap to reverse — the migration artifacts are plain PostgreSQL DDL and the differences are in file layout and directive syntax, so moving the history between the two runners is mechanical rather than a rewrite.
- **Atlas.** Rejected for the reason that dominates this ADR. Atlas's value is declarative schema management: it wants an HCL or SQL schema definition as the source of truth and it generates the migration by diffing against the database. That definition would compete with `packages/schemas/planning-schema.sql` for authority over the same concept, and the repository's duplication rule requires one owner per concept. Using Atlas in versioned-only mode discards the feature that justifies adopting it and leaves a heavier dependency doing what `goose` does. Atlas additionally splits capabilities between a community edition and a commercial tier, which makes the feature boundary a procurement question the project does not need.
- **`sqlx`.** Two different libraries carry this name and neither fits. Rust's `sqlx` has a capable migration facility, but migrations are server-owned and the server is Go under D-010; adopting it would move a Go responsibility into the Rust workspace and put a second database driver in the tree. Go's `jmoiron/sqlx` is a query and struct-scanning helper with no migration facility at all, and it would overlap with pgx, which D-010 names.
- **Application-managed migrations run at API startup.** Rejected because it makes migration application a function of process restarts, which under managed containers means several replicas racing on deploy, and because it removes the operator's ability to take a verified backup between the decision to migrate and the migration — a step the contract requires for destructive changes.
- **Hand-applied SQL with a changelog document.** Rejected because it produces no machine-checkable applied-version state, which the version gate needs, and because it has no rollback artifact to test.

## Migration policy

The policy already exists in `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`. This section states how `goose` executes it, so that the two documents are one procedure rather than a rule and an unrelated tool.

### Expand and contract

Every schema change that is not additive-and-inert is split into separate migrations applied in separate deployments:

1. **Expand.** Add the new column, table, index or constraint in a form the currently deployed code tolerates. New columns are nullable or carry a default that the old code ignores. New constraints are added `NOT VALID` and validated separately.
2. **Deploy.** Ship code that writes both the old and new shapes and reads the new one when present.
3. **Backfill.** Populate the new shape in bounded batches, in its own migration or its own operational job, so that a long-running statement never holds a lock across the deployment.
4. **Deploy.** Ship code that reads and writes only the new shape.
5. **Contract.** Drop the old column, table, index or constraint.

The contract step is separated from the expand step by at least one complete deployment cycle. A single migration that adds and removes in one step defeats the backward-compatible-deployment requirement, because there is then no version pair that can run simultaneously — and rolling deployments always run two versions simultaneously.

A `NOT NULL` addition is expand-and-contract in three steps: add the column nullable, backfill, then add a `CHECK (col IS NOT NULL) NOT VALID` constraint and validate it, which acquires a weaker lock than setting `NOT NULL` directly on a populated table.

### Version gates

The API binary reads the `goose` version table at startup and refuses to serve if the applied version is outside the range it declares support for. The range is a floor and a ceiling: a binary that requires a migration that has not been applied fails closed, and a binary older than a contract migration that has already run also fails closed, because the columns it reads are gone. This is the mechanism that makes the two-deployment expand-and-contract sequence safe against an out-of-order rollout.

### Online index creation

Indexes on tables carrying traffic are created with `CREATE INDEX CONCURRENTLY` in a migration marked `-- +goose NO TRANSACTION`. Concurrent creation can leave an invalid index behind on failure; the corresponding down section drops the index unconditionally, and the migration is re-runnable after a failure because the drop precedes the create.

Every migration that takes a lock on a table with rows sets a `lock_timeout` and a `statement_timeout` at the top of the migration, so that a blocked DDL statement fails quickly instead of queueing behind a long read and blocking every subsequent query on that table. A migration that cannot acquire its lock inside the timeout is retried during a quieter window, which under D-092's best-effort availability is an acceptable operator action.

### Tested rollback

Every migration has a down section that is executed, not merely written. The preproduction restore drill required by the operations contract applies the migration to a restored copy of production-shaped data, exercises the down section, and re-applies. A migration whose down section has never run is not evidence of a rollback path.

Rollback has a stated boundary, and it is the one D-074 already draws: a down section reverses a schema change, and it does not reverse data that the forward migration destroyed or a later write that depended on the new shape. Once a contract step has dropped a column, recovery is roll-forward or restoration from a verified pre-migration snapshot. A down section is not a time machine and this ADR does not present it as one.

### Destructive migrations

A migration that drops a column, drops a table, or rewrites data irreversibly requires a verified backup taken and confirmed restorable before application, and explicit data-lifecycle approval, both of which the operations contract already requires. Under D-091 the single maintainer performs both roles, so the control is a recorded checklist rather than a second person — which is weaker, and is recorded as weaker rather than described as dual control.

## Consequences

- The first migration is unblocked, and every work unit that needs a table has a defined place to put its DDL and a defined way to apply it.
- `packages/schemas/planning-schema.sql` remains the single schema authority. The migration history is the record of how a database reaches that schema, and the two are reconciled by a check that applying the full migration history to an empty database produces the authoritative schema. That check is a work unit's acceptance criterion, and it is what stops the two artifacts drifting.
- One dependency is added to the Go module and to the pinned toolchain. It is Apache-2.0, Go-native, and its artifacts are plain PostgreSQL DDL, so the exit cost is the cost of renaming directives.
- Expand-and-contract makes every non-additive schema change at least two deployments. Under a single maintainer with best-effort availability this is real friction, and it is accepted because the alternative is a deployment window in which the running code and the database disagree.
- The version gate means a mismatched binary refuses to start rather than serving errors. That converts a class of silent data corruption into a visible outage, which is the correct trade under D-092.
- Nothing is implemented. No migration exists, `/migrations` does not exist, no database has been provisioned, and this ADR authorizes the tool rather than evidencing its use.
- Owner ratification is outstanding. The decision is usable for planning and for authoring the first migrations; a ratification that goes the other way costs the mechanical conversion described above and no schema work.

## What would cause this to be revisited

- **The owner declines to ratify**, or ratifies with an amendment.
- **`goose` changes licence, is archived, or drops the `NO TRANSACTION` directive.** The `NO TRANSACTION` capability is a hard requirement; losing it forces a move to `golang-migrate`, and the plain-SQL artifacts make that mechanical.
- **The authoritative schema and the migration history diverge** in a way the reconciliation check cannot catch, which would mean the check is the defect and the ownership boundary needs restating rather than the tool replaced.
- **A measured need for declarative schema management** — for example, a schema large enough that hand-written migrations routinely drift from the authority. That reopens the Atlas rejection, and adopting it requires first deciding which artifact is the schema authority, because Atlas cannot be adopted without answering that.
- **A second maintainer joins**, which reintroduces concurrent authoring and makes timestamped numbering worth the loss of readable ordering, and which makes the destructive-migration control a genuine second pair of eyes rather than a checklist.
- **The managed PostgreSQL selection under ADR-017 constrains the available version below 16** or restricts the DDL a customer may execute, which would change the floor stated here.
