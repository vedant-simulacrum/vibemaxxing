# Performance and Efficiency Budgets

These are initial engineering budgets, not production SLO promises. They become blocking after the owning vertical-slice component exists and must be recalibrated from measured representative workloads.

## Local collector

| Metric | Initial budget |
|---|---:|
| Idle CPU, steady state | < 0.5% of one core |
| Idle RSS, common adapter set | < 80 MiB |
| p99 event normalization latency | < 10 ms |
| Sustained normalized events | >= 10,000 events/s in synthetic benchmark |
| Safe claim encoded size | < 4 KiB typical, < 16 KiB hard limit |
| Cold startup | < 250 ms on representative modern laptop |

## Go online services

| Metric | Initial budget |
|---|---:|
| Claim ingestion p95, excluding network | < 75 ms |
| Claim ingestion p99, excluding network | < 200 ms |
| Verification throughput per vCPU | benchmarked and non-regressing by > 10% |
| Leaderboard read p95 | < 100 ms |
| Minute aggregate freshness | < 90 seconds p99 |
| Graceful shutdown drain | < 30 seconds |
| Goroutine growth under steady load | no unbounded growth |
| Allocations/request | tracked; > 15% regression blocks merge unless approved |

## Database

- Every production query has a bounded result set or streaming plan.
- Critical query plans are captured in versioned benchmark evidence.
- No sequential scan on unbounded claim or event tables in latency-critical paths without explicit approval.
- Migrations include forward, rollback or roll-forward, lock-risk, and estimated duration evidence.

## Web

| Metric | Initial budget |
|---|---:|
| Route JavaScript, leaderboard initial load | <= 180 KiB compressed |
| Route CSS | <= 60 KiB compressed |
| LCP p75 | <= 2.5 s on target profile |
| INP p75 | <= 200 ms |
| CLS p75 | <= 0.1 |
| Leaderboard interaction response | <= 100 ms local feedback |

## Enforcement

- Microbenchmarks run on pull requests but are advisory until stable runners and noise controls exist.
- A scheduled benchmark workflow stores trends and compares against a blessed baseline.
- Load and soak tests are required before beta and release candidates.
- Any budget exception requires measured evidence, owner approval, expiry date, and follow-up issue.
