# Local Development Environment

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-244

## What this is

An engineer clones this repository and needs the whole stack running on their machine. Before this document there was no path to that: no compose file, no development container, no `make dev`, and no statement of which PostgreSQL the planning validators expect when `PLANNING_DATABASE_URL` is set. `README.md` gets a reader as far as `make validate`, and `Makefile` says explicitly that "no target builds or runs a product", which is accurate today and is not a plan for the day after the first service exists.

This document is that plan. It is a specification an engineer can execute from, not an executable. The compose definition below is written out in full so it can be copied into `compose.yaml` by the work unit that creates it; it is reproduced here rather than committed because committing it now would add a product-infrastructure artifact to a repository whose current phase forbids production infrastructure, and because the file belongs with the first service that needs it.

## Prerequisites, pinned

Every version below is the version this repository already pins somewhere. None is chosen here; they are collected here because they were previously scattered across four files and a reader had to find them.

| Tool | Version | Pinned by |
|---|---|---|
| Rust | 1.96.0, with `rustfmt` and `clippy` | `rust-toolchain.toml` |
| Go | 1.26.5 | `apps/api/go.mod` |
| Node.js | 22.23.1 | `.node-version` |
| Python | 3.11 or later | `Makefile` creates `.venv` from the system interpreter |
| Python packages | exact pins | `requirements-planning.txt` |
| PostgreSQL | 16 | `.github/workflows/planning-checks.yml` runs `postgres:16`; ADR-018 sets the floor at 16 |
| Container runtime | any OCI-compatible engine with a Compose v2 implementation | this document |

The container runtime is deliberately not named. Docker Desktop, Podman, OrbStack and Colima all satisfy the requirement, the compose file uses nothing engine-specific, and naming one would make a licensing question out of a development convenience.

## The three layers

Local development has three layers and an engineer usually needs only the first.

**Layer 1 — planning validation. No containers, no database.** This is the whole of what exists today and it stays the default.

```
make doctor      # repository invariants, standard library only
make venv        # creates .venv from requirements-planning.txt
make validate    # the validator suite, skipping the PostgreSQL DDL stage
make test        # validator unit tests
```

`make validate` skips one stage without a database and says so in its own output. Layer 2 is what unskips it.

**Layer 2 — PostgreSQL.** The planning validators apply `packages/schemas/planning-schema.sql` against a real instance to prove the DDL is executable, which no amount of parsing establishes. CI does this against a `postgres:16` service; locally it needs the same thing.

```
docker compose up -d postgres
export PLANNING_DATABASE_URL=postgresql://vibemaxxing:vibemaxxing@127.0.0.1:5432/vibemaxxing_dev
make validate
```

The connection string is the one the compose definition below produces. `.github/workflows/planning-checks.yml` uses a different database name and credential set because CI's instance is ephemeral and single-purpose; the two are not required to match and neither is a secret.

**Layer 3 — the product stack.** Does not exist. `apps/api` is a `main.go` that listens and logs, `apps/web` has never rendered, and there is no migration to apply. The compose definition below includes the API and web services so the file does not need rewriting when they arrive, and both are commented in the definition as not-yet-runnable rather than silently broken.

## The compose definition

Copy into `compose.yaml` at the repository root. Every value is fixed rather than templated, because a development compose file that reads from the environment is a compose file that behaves differently on two machines.

```yaml
name: vibemaxxing

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: vibemaxxing
      POSTGRES_PASSWORD: vibemaxxing
      POSTGRES_DB: vibemaxxing_dev
      # Deterministic collation. The ranking contract orders by score and then by
      # identifiers; a locale-dependent text collation would make an ORDER BY
      # produce a different sequence on a developer machine than in CI.
      POSTGRES_INITDB_ARGS: "--locale=C --encoding=UTF8"
    command:
      - postgres
      # Log every statement over 200 ms. The migration policy in ADR-018 requires
      # lock timeouts on DDL; seeing the slow statement locally is how an engineer
      # discovers a missing one before it reaches a table with rows.
      - -c
      - log_min_duration_statement=200
      - -c
      - max_connections=50
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vibemaxxing -d vibemaxxing_dev"]
      interval: 5s
      timeout: 3s
      retries: 12

volumes:
  postgres-data:
```

Three properties of that definition are load-bearing and would be wrong if changed casually.

**The port binding is `127.0.0.1:5432:5432` and not `5432:5432`.** The short form binds to every interface on most engines, which puts a database with the password `vibemaxxing` on the developer's local network. The explicit loopback prefix is the same control `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md` requires of every other listener in this product.

**The locale is `C`.** Text ordering under a locale-aware collation depends on the operating system's collation library version. Two engineers on different distributions can then get different `ORDER BY` results from the same data, and a leaderboard is an ordering. Fixing the collation at initialisation is the only point at which this is cheap; changing it later requires a reindex.

**The volume is named.** An anonymous volume is recreated on `docker compose down`, which silently discards a database an engineer was mid-way through debugging. Named means `docker compose down -v` is the deliberate act that destroys it.

### Services to add, and when

| Service | Added by the work unit that | Notes |
|---|---|---|
| `api` | introduces the first Go handler | needs `depends_on: postgres: condition: service_healthy` and the `goose` migration step as a separate one-shot service, never at API startup, per ADR-018 |
| `web` | introduces the first rendered page | `node:22.23.1`, `npm run dev`, port bound to `127.0.0.1:3000` |
| `otel-receiver` | introduces the adapter-one collector | loopback only; `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` owns its configuration |

No Redis service is defined. `docs/architecture/ARCHITECTURE.md` scopes the Redis-compatible service to ephemeral presence, rate limiting and measured hot caches, all of which have a correct in-process fallback for a single-process development stack. Adding it now would make every engineer run a service the product does not yet require.

## `make dev`

The following targets are added to `Makefile` by the work unit that adds the first service. They are specified here so that the target names are decided once rather than invented per-engineer.

| Target | Does |
|---|---|
| `dev-up` | `docker compose up -d postgres` and wait for the health check |
| `dev-down` | `docker compose down` — keeps the volume |
| `dev-reset` | `docker compose down -v && make dev-up && make migrate` |
| `migrate` | applies the `goose` migration history in `/migrations` against `PLANNING_DATABASE_URL` |
| `migrate-verify` | applies the full history to an empty database and diffs the result against `packages/schemas/planning-schema.sql` |
| `dev` | `dev-up`, `migrate`, then runs the API and web processes in the foreground |
| `seed` | loads synthetic fixtures |

`migrate-verify` is the check ADR-018 names as the thing that stops the migration history and the authoritative schema drifting. Having it as a local target rather than only a CI job is what makes an engineer notice the drift in the minute they created it.

## Fixtures and data

Local databases carry **synthetic data only**. Production data never enters a lower environment, which the operations contract already requires and `docs/operations/ENVIRONMENTS_AND_SECRETS.md` restates with the mechanism.

`seed` loads from `evals/fixtures/`, which is where the repository already keeps deterministic fixtures, so the same rows a test asserts against are the rows an engineer sees in a browser. A fixture set that exists only for local development would drift from the one tests use within a month.

Seeded accounts use handles from a reserved synthetic namespace and provider identifiers that cannot correspond to a real GitHub or X account, so that a mis-pointed development client cannot act against a real identity.

## Secrets in local development

There are none, and that is a rule rather than an accident of the current state.

Local development runs against no real provider. OAuth uses a stub authorization server that issues tokens for the synthetic accounts above; it is part of the development stack and is never reachable from any other environment. Release signing uses a throwaway key generated on first run and stored in the local state directory. Nothing in the local stack holds a credential that is valid anywhere else.

An engineer who needs to exercise a real OAuth flow registers their own application with the provider and puts the client identifier and secret in a git-ignored `.env.local`. `.env.example` lists every variable name with an empty value and is committed; `.env.local` is in `.gitignore` and is never committed. There is no shared development credential, because a shared credential is a credential whose compromise nobody notices.

## First hour

For a new engineer, in order:

1. Install the pinned toolchains. Clone. Run `make doctor` — it needs nothing installed beyond Python and must pass on a clean checkout.
2. Run `make venv && make validate && make test`. All three exit 0 on `main`; if they do not, the checkout is the problem and not the change you were about to make.
3. Read `AGENTS.md`, then `docs/project/PROJECT.md`, `docs/project/STATUS.md`, and this repository's documentation map at `docs/project/DOCUMENTATION.md`.
4. Bring up PostgreSQL, export `PLANNING_DATABASE_URL`, and run `make validate` again. The DDL stage now runs and the skip notice disappears.
5. Read `docs/planning/TASK_CATALOG.md` for the active program before choosing anything to work on.

Expect steps 1 and 2 to take about twenty minutes on a machine with the toolchains already present, and the container image pull to dominate step 4.

## Troubleshooting, for the failures this stack actually produces

- **`make validate` reports a skipped PostgreSQL stage.** `PLANNING_DATABASE_URL` is unset. This is the intended default, not a failure.
- **The DDL stage fails with a permission error.** The compose user is `vibemaxxing` and owns `vibemaxxing_dev`; a connection string pointing at the `postgres` superuser database will not have the schema.
- **Port 5432 is already bound.** Another PostgreSQL is running, frequently a system service. Stop it or change the host side of the port mapping; do not change the container side, because the health check and the connection string both assume it.
- **`ORDER BY` results differ from CI.** The volume was created before the `--locale=C` initialisation argument was added. `POSTGRES_INITDB_ARGS` applies only at first initialisation, so `make dev-reset` is required and no amount of restarting will apply it.
- **`make doctor` fails immediately after a rebase.** It checks the phase record against prose in several documents; a rebase that took one side of a conflict in `AGENTS.md` or `docs/project/STATUS.md` will trip it. Read the error, which names the document and the missing token.

## Evidence

The layer 1 path in this document is executed today, on every machine and in CI, and works. Layer 2 is executed in CI and has not been exercised from the compose definition below, because the file does not exist yet. Layer 3 describes services that do not exist. Nothing here is evidence that the product runs; it is a specification for bringing up a stack that is, at this head, one database.
