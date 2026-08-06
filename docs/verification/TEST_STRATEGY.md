# Test Strategy

Status: normative planning contract
Version: 2
Updated: 2026-08-06
Decisions: D-240, D-241, D-460, D-461, D-462

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
| `scripts/ci` and `scripts/repository` | 55% line-and-branch | D-460. The planning validators, which are the only code in this repository that executes on every pull request. Line-and-branch because a validator is mostly branches and a line-only number over one flatters it. **This is the first measurement rounded down, not a considered target**, and it is stated with the intent to raise it; see the measured numbers below for why it starts where it does |
| generated bindings, `main` packages, migrations | excluded | measuring generated code measures the generator |

The non-regression rule: a pull request may not lower a scope's measured coverage by more than **1.0 percentage point** below its recorded baseline. The one-point band exists so that deleting a well-covered file does not fail an unrelated change; a deliberate reduction is a baseline edit, which leaves a reviewable diff, exactly as the eval status baseline does.

Coverage says a line executed. It does not say an assertion was made about it, which is why the floors above are floors and why the mutation check below exists.

### What the floors were measured against

Every floor above was written before anything had been measured, which made each one a threshold with nothing on the other side of it. D-460 records the first measurement. `scripts/ci/measure_coverage.py` produces it, `scripts/ci/measured-coverage-baseline-v1.json` records it, and the `measured-coverage` job runs it per pull request.

| Surface | Measured | Metric | Against its floor |
|---|---:|---|---|
| `crates/vibeproof-core` | **90.97%** | line, 292 of 321 | clears 90% by 0.97 points |
| `apps/api` | **72.86%** | statement, 51 of 70 | no floor applies |
| `scripts/ci` + `scripts/repository` | **55.89%** | line-and-branch, 3,969 of 7,102 | the floor is this number rounded down |

Three findings sit behind those three numbers, and none of them is resolved by having measured.

**Rust clears its floor by less than the non-regression band.** 90.97% against a 90% floor means a single uncovered branch added to `vibeproof-core` breaches the floor. That is the floor working as intended — this is the crate where a gap is a security defect — but it means the crate has no room, and a change that adds an error path adds a test with it or fails.

**Neither Go floor has a subject.** `apps/api` contains exactly one package and it is `main`, which the table above excludes. So 72.86% is recorded to stop it rotting unobserved and is compared against nothing; the 85% and 75% floors are waiting for the first non-`main` package. The measurer fails the moment one appears without a floor recorded for it, so the absence expires by itself rather than by somebody remembering.

**The Python floor is being written for the first time, not lowered.** This table had no Python row until now: it named Rust, Go, `packages/ui` and `apps/web`, and omitted the only code here that runs on every pull request. Ten of the twenty-two modules under `scripts/ci` and `scripts/repository` measure 0% — `generate_gate_ledger.py`, `repository_policy.py`, `run_evals.py`, `run_phase1_evidence.py`, `generate_issue_plan.py`, `generate_repository_metadata.py`, `run_ed25519_oracles.py`, `validate_p1140e_contracts.py`, `validate_planning_coverage.py` and `validate_t20_contract.py`. Every one of them runs in CI under `make validate`. Raising this floor means writing tests for those, not adjusting the number.

The Python figure is a **lower bound rather than an estimate**. Measurement is in-process only, and two of the ten modules above are in fact exercised by tests that invoke them as a child process. Child-process capture was tried and rejected: it reported about six points higher on one run and nothing on the next depending on whether a `.pth` file fired, and a ceiling that moves for that reason measures the environment rather than the tests. The undercount is stable and named; an unstable number that flattered would be worse.

**Distinguishing a real regression from a moved file.** A percentage falls for two very different reasons, so every scope records its denominator beside its percentage and the measurer classifies each fall by comparing denominators: grown means new uncovered code arrived, which is the signal; shrunk means covered code was deleted or moved out, which is usually noise; unchanged means a test was removed, skipped or weakened. A file moving *within* a scope is invisible, because a scope is a directory rather than a file list. A file moving *between* scopes appears as two opposite-signed denominator deltas, which the failure message names and a human resolves. That residual is accepted rather than solved.

Editing `scripts/ci/measured-coverage-baseline-v1.json` is the only sanctioned way to record a worse number. `--write` re-records the measurements and keeps every floor and note already written, so a deliberate reduction leaves a reviewable diff and a silent one turns the check red. A missing or malformed baseline fails closed, and a surface the toolchain could not measure fails rather than passing, because an unmeasured surface is an absence of evidence.

The `measured-coverage` job is separate from `planning-checks` on purpose. It costs about three and a half minutes — it re-runs the unit suite under `coverage.py` and builds the Rust workspace instrumented from cold — and `planning-checks` is already about four minutes since the node lane started building the npm workspaces. Running them concurrently keeps the wall-clock wait flat and roughly doubles billed runner minutes for the workflow. Rust is measured with the `llvm-profdata` and `llvm-cov` that ship in rustup's `llvm-tools-preview` component, so no third-party coverage runner is compiled on any run; `cargo-llvm-cov` produces the identical number and would be one more pinned dependency for it.

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

Load tests are not run per pull request. They cost runner minutes against the free tier and they require a deployed target, and under D-238 no standing pre-production environment is provisioned. They run **before each ring expansion of the private beta and before public launch**, on a manually dispatched workflow, against a `ci`-provisioned ephemeral stack sized to match the configuration selected under D-361 rather than against production itself.

### The scenarios

Each names a load derived from the product, a duration, and a pass condition that can be read off a result rather than judged.

`evals/load/load-scenarios-v1.json` is the machine owner of the set: it writes each scenario out operation by operation, and every rate in it names the `policy_ref` it was derived from. `scripts/repository/validate_load_scenarios.py` resolves those against `packages/schemas/policy-defaults-v1.json` and cross-checks the scenario names against the table below, so a rate cannot drift away from the limit it claims to come from and the two files cannot hold different sets. D-461 records that binding.

The population is 200 participants with one device each. That is not a round number: D-180 bounds the private beta by the invite codes the owner issues by hand, `invite_outstanding_max` holds that quota at 200, and `docs/architecture/API_EDGE_CONTRACT.md` derives every rate limit from the same figure. The validator fails if the scenario population and the quota stop agreeing.

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

**These scenarios say nothing about the 100,000 ranked-identity scale target.** They are sized at 200 participants because that is the private beta, and a system that passes at 200 has demonstrated nothing at 100,000. Passing every scenario above must never be cited as evidence that the scale target is reachable.

The reason for that has changed, and the conclusion has not. D-094 used to record the 100,000 target, the sub-100-USD ceiling of D-093 and the 5-minute recovery point objective as a three-way conflict that could not all hold. **D-360 resolved it by amending the ceiling** to the measured steady-state monthly cost of the configuration selected under D-361, which is one of the three amendments ADR-017 step 4 permits; the scale target and the recovery objectives are unchanged, and D-093 and D-094 are both superseded. So the scenarios above are no longer in tension with a fixed budget figure.

That removes the reason not to specify a larger scenario set and leaves a better one: **nothing has measured the 100,000 figure.** A scenario asserting it would be this repository inventing a number and then testing against its own invention, which is the pattern the eval registry and the coverage floors were both repaired for. A scale scenario becomes specifiable when there is a measured steady-state cost curve for the selected configuration to size it against, and not before. D-462 records that condition so the absence expires against evidence rather than against somebody's memory.

**Nothing below has been run.** None of these scenarios has been written as a k6 script, no ephemeral stack has been provisioned to run one against, and `evals/load/load-scenarios-v1.json` carries `claim_scope: specification-only` to say so. One of them, `offline-drain`, is expected to fail when it is first run: SR-012 is open, the persistence half of exact idempotent replay is unrepaired, and the scenario asserts exactly what that gap breaks. Writing down a scenario that is known to fail is the point of writing it down.

## Where this connects

| Concern | Owner |
|---|---|
| eval suites, statuses, result schema, verification matrix | `docs/verification/EVAL_SYSTEM.md` |
| the measured coverage ceiling and the non-regression gate | `scripts/ci/measured-coverage-baseline-v1.json`, measured by `scripts/ci/measure_coverage.py` |
| the load scenarios operation by operation | `evals/load/load-scenarios-v1.json`, validated by `scripts/repository/validate_load_scenarios.py` |
| rate-limit classes and the quotas the scenarios are derived from | `docs/architecture/API_EDGE_CONTRACT.md`, `packages/schemas/policy-defaults-v1.json` |
| conformance fixture and runner design | `docs/verification/CONFORMANCE_HARNESS.md` |
| acceptance gates per milestone | `docs/verification/ACCEPTANCE_GATES.md` |
| performance budgets and benchmark metadata | `docs/engineering/PERFORMANCE_BUDGETS.md`, `docs/verification/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md` |
| branch checks and change risk classes | `docs/engineering/ENGINEERING_SYSTEM.md` |
| local execution | `docs/engineering/LOCAL_DEVELOPMENT.md` |

## Evidence

Most of this still does not run, and the parts that do are now measured rather than asserted.

**Measured.** `make test` runs 16 Python validator test files. Three surfaces carry a real coverage number, recorded in `scripts/ci/measured-coverage-baseline-v1.json` and re-measured per pull request by the `measured-coverage` job: Rust at 90.97% line, Go at 72.86% statement, Python at 55.89% line-and-branch. The non-regression rule has something to regress against for the first time, and `tests/ci/test_measure_coverage.py` drives each direction of the comparison — worse fails with the fall attributed, the same passes, better passes and is reported, and a missing, malformed or unmeasurable input fails closed — because a gate that cannot be shown to fire is not evidence either.

**Still not measured, and not claimed.** `packages/ui` and `apps/web` build under the node lane and have no coverage number, so their 70% and 60% floors remain thresholds with nothing on the other side of them; that is the same defect this section previously recorded for all five scopes, now reduced to two. Both Go floors have no subject, because `apps/api` holds one `main` package. 24 of 27 eval suites still execute nothing. No mutation pass has run.

**No load test has been written or run.** The six scenarios are specified in `evals/load/load-scenarios-v1.json` and validated for internal consistency against the policy defaults, which is a specification being checkable rather than a system being tested. `claim_scope: specification-only` says so in the file itself, and the validator fails if it stops saying so.

What converted the coverage floors from intentions into a check was the first measurement. What would convert the load scenarios is a run, and there has not been one.
