# Test Strategy

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-240, D-241

## What was missing

`docs/engineering/ENGINEERING_SYSTEM.md` names eight quality layers and eight required branch checks. `docs/verification/EVAL_SYSTEM.md` names 27 eval suites and the outcome vocabulary that keeps their status honest. Both are good and neither says how a change is tested: no shape, no coverage target, no framework, no rule about what belongs in a unit test rather than an integration test, and no load-test scenario. An engineer with a work unit in front of them had eight layer names and no method.

This document owns the method. It does not own the eval registry, the status baseline or the verification matrix — `EVAL_SYSTEM.md` owns those and this document defers to it. It does not own the branch protection check list — `ENGINEERING_SYSTEM.md` owns that.

## Shape

Not a pyramid with ratios. A ratio target produces tests written to move a ratio. The shape is stated as a rule about *where a test belongs*, which is checkable in review:

**A test lives at the lowest level that can observe the thing it asserts.**

| Level | Observes | Runs against |
|---|---|---|
| unit | a function or type in isolation | nothing external |
| integration | one boundary | a real instance of that one boundary |
| conformance | agreement between an implementation and a recorded expectation | fixtures under `conformance/` |
| eval | a product-level invariant | the suites in `evals/suites/suites.yaml` |
| end-to-end | a participant journey through the browser | the whole stack |

The boundaries that justify an integration test are exactly four: PostgreSQL, HTTP, local IPC, and the filesystem. A test that mocks all four is a unit test wearing a costume; a test that uses a real one is testing the boundary and belongs at the integration level.

Two consequences:

- **Business logic is not tested through HTTP.** Ranking arithmetic, accounting normalisation and canonical encoding are pure and are tested as pure functions. Routing them through a request to assert an integer is slow, flaky and tests the router.
- **SQL is not tested through mocks.** D-010 puts explicit SQL in the codebase and a mocked database asserts that the string was sent, not that PostgreSQL accepts it. Every query runs against `postgres:16`, which `ci` already provides and `docs/engineering/LOCAL_DEVELOPMENT.md` provides locally.

End-to-end browser journeys are **capped at 12**. The cap is a budget: each journey costs roughly a minute of CI across three browser engines, the full pull-request check must finish inside 10 minutes, and the planning workflow's own timeout is 15. Twelve is what fits. When a thirteenth is proposed, one is removed or the cap is raised deliberately with the cost stated.

## Frameworks

Every choice below is either already pinned in this repository or already named by ADR-002. Nothing new is introduced without that provenance.

| Purpose | Tool | Provenance |
|---|---|---|
| Go unit and integration | `testing` with `go test -race` | ADR-002 |
| Go comparison | `go-cmp` | the only widely used structural-diff helper; the standard library has no equivalent |
| Go property and malformed input | built-in `go test -fuzz` | ADR-002 names fuzzing; the standard library covers it, so no dependency |
| Go static analysis | `go vet`, Staticcheck, `govulncheck`, CodeQL | ADR-002 |
| Rust unit and integration | `cargo test` | ADR-002 |
| Rust property | `proptest` | canonical encoding and accounting arithmetic are exactly the shape property testing exists for |
| Rust fuzz | `cargo-fuzz` | ADR-002 |
| Rust undefined behaviour | Miri, on the crates that have any `unsafe` | ADR-002; the workspace sets `unsafe_code = "deny"`, so today this runs on nothing and stays configured for when an exception is granted |
| Rust benchmark | `criterion` | the performance budgets require statistical summaries, which the built-in bench harness does not produce on stable |
| Rust supply chain | `cargo-deny`, `cargo-audit` | ADR-002 |
| TypeScript unit | `vitest` | ADR-002 |
| TypeScript component | Testing Library | ADR-002 |
| Browser end-to-end | Playwright | ADR-002; already vendored at 1.62.1 in `scripts/ui/playwright-runtime/package.json` |
| Accessibility | `axe-core` via Playwright | ADR-002; already vendored at 4.12.1 |
| Validator tests | Python `unittest` | already in use under `tests/` and run by `make test` |
| Load | k6 | see below |

`packages/ui` currently runs its component test through `esbuild` and `node --test` rather than `vitest`. That is a working arrangement that predates this document; it is not a second decision, and it converges on `vitest` when that package next changes its test setup rather than in a separate migration.

**k6 is AGPL-3.0**, which is worth stating explicitly in a repository whose own code is Apache-2.0 under ADR-009. It is acceptable because it is invoked as a separate process from a test script, is never linked into a distributed artifact, and is not distributed by this project. The scripts written for it are project code and are Apache-2.0. If that separation ever stops holding, the alternative is a Go-native generator under a permissive licence and the load scenarios are portable between them, because the scenarios are the specification and the tool is the runner.

## Coverage

Coverage is a floor with a non-regression rule, not a target to be met. The rule is the one `scripts/ci/coverage-baseline-v1.json` already applies to lane outcomes: a number may not get worse than the recorded one.

| Scope | Floor | Why this number |
|---|---:|---|
| `crates/vibeproof-core` and any future protocol crate | 90% line | canonical encoding, signature verification and replay handling are where a gap is a security defect; the code is pure and has no boundary that makes coverage expensive |
| Go accounting, ranking and verification packages | 85% statement | the same argument, one language over |
| Go handlers, middleware and repositories | 75% statement | boundary code where the last quarter is error paths that cost more to reach than they return |
| `packages/ui` | 70% statement | component logic; visual correctness is covered by regression baselines rather than by coverage |
| `apps/web` route and page code | 60% statement | thin composition over the two above |
| generated bindings, `main` packages, migrations | excluded | measuring generated code measures the generator |

The non-regression rule: a pull request may not lower a scope's measured coverage by more than **1.0 percentage point** below its recorded baseline. The one-point band exists so that deleting a well-covered file does not fail an unrelated change; a deliberate reduction is a baseline edit, which leaves a reviewable diff, exactly as the eval status baseline does.

Coverage says a line executed. It does not say an assertion was made about it, which is why the floors above are floors and why the mutation check below exists.

**A mutation-testing pass runs on the protocol and accounting crates before each ring expansion of the private beta**, not per pull request, because it is slow. A surviving mutant in canonical encoding or in score arithmetic is a defect in the test suite and is fixed before the ring expands.

## Required negative cases

Every one of these must exist somewhere in the suite before its subject is considered tested. They are listed because they are the cases that get skipped:

- a malformed input at every decoder boundary, from the existing malformed and resource corpora;
- a valid signature over altered content;
- a replayed identifier;
- a duplicate request with an identical idempotency key, and one with the same key and different bytes;
- a request from a foreign origin against every state-changing route, per `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`;
- a request exceeding every rate-limit class in `docs/architecture/API_EDGE_CONTRACT.md`;
- a claim whose event time is beyond the future skew tolerance, and one beyond the lateness window;
- a migration down section, executed;
- a forbidden field at the privacy boundary, per the canary fixtures;
- a binary outside its declared migration version range, asserted to fail readiness.

## Test data

Synthetic only, in every environment, without exception. The fixtures live in `evals/fixtures/` and `conformance/`, and the same fixture serves a test, a local seed and a preview build so that the three cannot diverge.

Fixtures that are generated are generated by a committed deterministic generator and the generated output is committed alongside it, with a validation stage that fails when a regeneration differs. `scripts/repository/generate_vibeproof_vectors.py` is the pattern and D-194 is the rule; a hand-edited signed fixture is internally consistent and proves nothing.

## Flakes

A test that fails and then passes on unchanged code is a flake, and a flake is a defect with a deadline.

- Failing twice within 30 days on unchanged code is the threshold.
- A test crossing it is quarantined within 7 days: skipped, listed in a tracked quarantine file with the reason and an expiry date **no more than 30 days out**.
- At expiry it is fixed or deleted. It is not re-quarantined.

Deleting a flaky test is an acceptable outcome and is better than the alternative, which is a suite everybody has learned to re-run. A deleted test leaves a gap that coverage reports; a tolerated flake teaches the team to ignore red.

## Runtime budget

| Stage | Budget |
|---|---|
| pull-request checks, end to end | 10 minutes |
| the unit portion alone | 2 minutes |
| a single test | 5 seconds, or it is not a unit test |

Ten minutes is set by attention rather than by cost: a check that outlives the engineer's willingness to wait becomes a check they merge without reading.

## Load testing

### Why it is separate

Load tests are not run per pull request. They cost runner minutes against the free tier and they require a deployed target, and under D-093 the deployed target is production. They run **before each ring expansion of the private beta and before public launch**, on a manually dispatched workflow, against a `ci`-provisioned ephemeral stack sized to match production rather than against production itself.

### The scenarios

Each names a load derived from the product, a duration, and a pass condition that can be read off a result rather than judged.

| Scenario | Load | Duration | Passes when |
|---|---|---|---|
| `beta-steady` | 200 participants: one claim batch and one leaderboard read per participant per 60 s, one presence heartbeat per 30 s — about 20 requests per second | 30 min | ingest p95 ≤ 500 ms, read p95 ≤ 300 ms, zero 5xx, aggregate freshness ≤ 90 s throughout |
| `beta-peak` | 10× `beta-steady`, about 200 requests per second, the aggregate admission ceiling | 5 min | no 5xx; requests refused by rate limits return 429 with `Retry-After`; freshness recovers to ≤ 90 s within 5 minutes of the peak ending |
| `offline-drain` | 50 devices reconnect simultaneously, each carrying 24 h of queued minutes — 1,440 rows, three batches of 500 | until drained | every claim accepted exactly once, zero duplicates admitted, drain completes in ≤ 10 min, and no other principal's latency degrades by more than 50% |
| `leaderboard-thunder` | 2,000 unauthenticated readers arrive within 60 s against the global board — the shape of an announcement | 10 min | origin request rate stays ≤ 60 per second because the 60-second public cache absorbs the rest; read p95 ≤ 300 ms; no database connection exhaustion |
| `ratelimit-breach` | one principal at 10× its class limit, concurrently with `beta-steady` | 10 min | the breaching principal receives 429s with correct `Retry-After`; every other principal's latency and error rate are statistically unchanged; zero 5xx |
| `soak` | `beta-steady` unchanged | 12 h | resident memory growth ≤ 10%, no goroutine leak, no connection-pool growth, no unbounded table growth outside the append-only ledger |

`offline-drain` and `ratelimit-breach` are the two that test something no synthetic throughput number would find: the first is where duplicate admission and idempotency actually get exercised at scale, and the second is the only test that asserts a limit protects the people it is meant to protect rather than merely refusing someone.

### Recording

Every run records what `docs/verification/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md` already requires of a benchmark: runner class, operating system, toolchain versions, dataset version, warmup policy, sample count, statistical summary and commit SHA. A load result without that metadata is not evidence.

### The honest limit

**These scenarios say nothing about the 100,000 ranked-identity scale target.** They are sized at 200 participants because that is the private beta, and a system that passes at 200 has demonstrated nothing at 100,000. D-094 records that the 100,000 target, the sub-100-USD ceiling and the 5-minute recovery point objective cannot all hold; a load test is not the instrument that resolves that, and passing every scenario above must never be cited as evidence that the scale target is reachable.

A scenario set for the 100,000 target would need a production-shaped environment at production-shaped cost. It is not specified here because specifying it would imply a plan to run it, and there is no budget line for one.

## Where this connects

| Concern | Owner |
|---|---|
| eval suites, statuses, result schema, verification matrix | `docs/verification/EVAL_SYSTEM.md` |
| conformance fixture and runner design | `docs/verification/CONFORMANCE_HARNESS.md` |
| acceptance gates per milestone | `docs/verification/ACCEPTANCE_GATES.md` |
| performance budgets and benchmark metadata | `docs/engineering/PERFORMANCE_BUDGETS.md`, `docs/verification/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md` |
| branch checks and change risk classes | `docs/engineering/ENGINEERING_SYSTEM.md` |
| local execution | `docs/engineering/LOCAL_DEVELOPMENT.md` |

## Evidence

Almost none of this runs. `make test` runs nine Python validator test files. Go, Rust and node lanes exist in the verification matrix; the node lane is recorded `uncovered` because no root `package.json` exists, and 24 of 27 eval suites execute nothing. No coverage number has ever been measured, so every floor above is a target with no baseline behind it and the non-regression rule has nothing to regress against until the first measurement. No load test has been written or run.

The first measurement — a real coverage number per scope, recorded as a baseline — is what converts the floors from intentions into a check.
