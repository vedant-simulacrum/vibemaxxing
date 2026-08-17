# Evaluation System

## Principles

- Evals are versioned repository assets.
- Every critical invariant has positive and negative fixtures.
- Results are machine-readable and retained as CI artifacts.
- A model-generated judgment can supplement but never replace deterministic protocol, privacy or security assertions.
- Regressions block merge when they affect a frozen invariant.

## Suites

### `protocol-conformance`

Required cases:

- Canonical claim bytes are identical across implementations.
- Valid signatures verify and altered claims fail.
- Replayed identifiers produce no additional accepted activity.
- Duplicate requests are idempotent.
- Missing, repeated and reordered sequences are detected.
- Unknown protocol or adapter versions fail closed or downgrade explicitly.
- Imported history cannot enter competitive rankings.

### `privacy-boundary`

Required cases:

- Arbitrary text fields are rejected at schema and decoder boundaries.
- Prompts, responses, code, paths, filenames, repository names and credentials cannot be serialized.
- Transcript-reading components fail network-connectivity tests.
- Sync components cannot open transcript stores.
- Packet-capture fixtures contain only allowlisted fields.
- Prompt-injection fixtures cannot grant additional tools, files or network access.

### `ranking-accounting`

Required cases. **One of the six executes.** The suite's `scope_note` in
`evals/suites/suites.yaml` carries the same statement, so the registry and this document
agree about the gap rather than one of them implying coverage the other denies. A required
case that does not run is a specification of what the suite must cover before it may be
cited for ranking, not a claim about what it covers now.

- Token categories normalize deterministically. — **not executed**
- Cash Burn is labelled and computed as an estimate. — **not executed**
- Minute, daily, weekly, monthly, seasonal, yearly and lifetime aggregation agree with reference fixtures. — **not executed**
- Rank ties and movement are deterministic. — **not executed**
- Current-user rank is returned correctly. — **not executed**
- Host/environment duplicate observations do not double-count. — executed by `imported-exclusion-and-dedupe`.

Nothing in this suite ranks anything. Until that changes it may not be cited as
ranking-conformance, aggregation evidence, a launch gate, or a support claim.

### `frontend-quality`

Required cases:

- 320px, 768px, 1280px and ultrawide layouts.
- Chromium, Firefox and WebKit smoke coverage.
- WCAG 2.2 AA automated checks and keyboard tests.
- Loading, empty, error, offline, unauthorized, private, hidden and suspicious states.
- Visual-regression baselines for leaderboard, profile and settings.
- No dead controls or placeholder interactions.

### `resilience`

Required cases:

- Safe retry after transient ingestion failure.
- Idempotent recovery after interrupted writes.
- Queue redelivery does not duplicate totals.
- Database migration rollback or forward-fix is tested.
- Clock skew and delayed claims behave according to policy.

## Result schema

Every suite writes JSON with:

```json
{
  "suite": "privacy-boundary",
  "version": "1",
  "commit": "<sha>",
  "status": "pass|fail|not_applicable",
  "cases": [{"id": "PB-001", "status": "pass", "evidence": "path"}],
  "started_at": "RFC3339",
  "finished_at": "RFC3339"
}
```

`not_applicable` requires a documented milestone reason. It must not be used after the owning component is introduced.

That rule was prose with nothing enforcing it until the status baseline and the absence justification below were added. A `not_applicable` result is not a pass; `scripts/ci/verify_repository.py` reports it as its own outcome so the verification matrix cannot count a suite that executed nothing as coverage.

## Suite status is a recorded ceiling

`evals/suites/status-baseline-v1.json` records the status every declared suite carried when it was written. `scripts/ci/run_evals.py --validate-registry` compares the registry against it and exits non-zero when:

- a suite recorded `ready` is declared `not_applicable`;
- a recorded suite disappears from the registry;
- the registry declares a suite the baseline does not record.

The last two exist because without them the gate is evaded by deleting or renaming the suite rather than downgrading it. Raising a suite from `not_applicable` to `ready` never fails validation, so improving coverage cannot turn CI red; lowering the recorded ceiling afterwards is optional and manual. A baseline that is missing, unparseable, or carries an unrecognised status fails closed with exit code 2 — a broken constraint is treated as a violated one, not an absent one.

Recording a downgrade is deliberately a file edit, so it leaves a reviewable diff. An undeclared downgrade turns validation red.

## Every suite declares an authority class and a bounded evidence ceiling

Each suite in `evals/suites/suites.yaml` carries `authority_class` and `evidence_ceiling`, both drawn from the vocabulary in `conformance/p1140f/artifact-authority-v1.json`, which `docs/planning/ARTIFACT_POLICY.md` owns. `scripts/ci/run_evals.py --validate-registry` refuses a value the registry does not declare and refuses a ceiling higher than the lowest applicable cap:

- the suite's `authority_class` caps it — `exploratory-prototype` cannot reach `normative-conformance`;
- a `not_applicable` suite is capped at `none`. It has no fixture manifest by construction, and the status is an absence of evidence rather than a pass. Twenty-four of the twenty-seven suites carry it;
- a `ready` suite is capped by its fixture manifest: the manifest's own `evidence_ceiling` if it declares one, otherwise `fixture-consistent` when it binds at least one fixture, otherwise `none`.

The last clause is the one worth reading twice. A ceiling check that only asked whether the fixtures contradicted the claim would be satisfied by a suite with no fixtures at all — the absence would satisfy the absence-check, and the emptiest suite in the registry would be the one it never questioned. The cap is therefore derived from what the manifest *binds*, so having nothing lowers the ceiling instead of leaving it unexamined.

Both keys were added in commit `31a6539` to satisfy `scripts/repository/validate_p1140f_authority.py` and were then declaratively inert: `run_evals.py` admitted them to its key allowlist and read neither, and only one of the twenty-seven suites carried them at all.

## `not_applicable` names what it is waiting for

Every `not_applicable` suite declares `not_applicable_until`: the repository-relative paths whose *absence* is the justification for the status. Validation fails as soon as any one of them exists, which is what makes "must not be used after the owning component is introduced" checkable rather than aspirational. A reviewer decides whether the justification still holds by asking whether the named paths exist, not by reading the prose reason.

Paths must be repository-relative, without traversal or a trailing separator, and are allowed — required, in fact — to name something that does not exist yet. A `ready` suite may not declare the field. Running a suite whose named component has appeared produces `fail`, not a benign skip.

## Verification outcomes are also a recorded ceiling

`scripts/ci/verify_repository.py` distinguishes five lane outcomes:

| Outcome | Meaning | Recordable |
| --- | --- | --- |
| `pass` | the lane ran and every command exited 0 | yes |
| `partial` | the lane ran and part of it had nothing to execute | yes |
| `not_applicable` | nothing exists for the lane to run | yes |
| `uncovered` | something exists for the lane to run and no lane runs it | yes |
| `fail` | the lane ran and a command exited non-zero | **no** |

They are ordered `uncovered` < `not_applicable` < `partial` < `pass`. `scripts/ci/coverage-baseline-v1.json` records what every lane produced, and the matrix exits non-zero only when coverage gets *worse* than that record:

- a lane drops below its recorded outcome;
- a recorded lane disappears from the matrix;
- a lane appears that the baseline does not record;
- any lane actually fails.

A lane sitting at its recorded outcome does not fail the build, so a hole the repository has knowingly accepted stays visible without holding a required check red. Improving a lane never fails either, and the matrix prints which lanes now beat their record. `fail` is not a recordable outcome, so a genuinely broken lane can never be baselined into silence. A missing or malformed baseline exits 2.

Every lane recorded as anything other than `pass` must carry a justification naming a reference and a note, so a recorded hole is always attributable to a decision somebody can go and read. Two are recorded today: `evaluator-all-suites` is `partial` because 24 of 27 suites execute nothing, and `node` is `uncovered` because no root `package.json` exists while `apps/web`, `packages/ui` and `scripts/brand` are npm workspaces with lockfiles that nothing builds.

## Performance and efficiency suite

The `performance-efficiency` suite owns:

- collector CPU, RSS, startup, throughput, and claim-size budgets;
- Go service latency, allocation, throughput, race, and goroutine-leak checks;
- database query-plan and migration-lock evidence;
- frontend bundle, Core Web Vitals, rendering, and interaction budgets;
- benchmark regression comparison against a versioned baseline.

Performance evidence must record hardware/runner class, OS, toolchain versions, dataset/fixture version, warmup policy, sample count, statistical summary, and commit SHA. A benchmark number without environment metadata is not valid evidence.
