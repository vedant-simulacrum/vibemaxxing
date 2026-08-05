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

Required cases:

- Token categories normalize deterministically.
- Cash Burn is labelled and computed as an estimate.
- Minute, daily, weekly, monthly, seasonal, yearly and lifetime aggregation agree with reference fixtures.
- Rank ties and movement are deterministic.
- Current-user rank is returned correctly.
- Host/environment duplicate observations do not double-count.

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

## Performance and efficiency suite

The `performance-efficiency` suite owns:

- collector CPU, RSS, startup, throughput, and claim-size budgets;
- Go service latency, allocation, throughput, race, and goroutine-leak checks;
- database query-plan and migration-lock evidence;
- frontend bundle, Core Web Vitals, rendering, and interaction budgets;
- benchmark regression comparison against a versioned baseline.

Performance evidence must record hardware/runner class, OS, toolchain versions, dataset/fixture version, warmup policy, sample count, statistical summary, and commit SHA. A benchmark number without environment metadata is not valid evidence.
