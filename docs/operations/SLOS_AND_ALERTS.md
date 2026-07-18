# SLOs and Alerts

These are proposed launch targets and must be validated against real traffic before commitment.

| Service indicator | Proposed target | Window |
|---|---:|---:|
| Claim ingestion availability | 99.9% | 30 days |
| Leaderboard read availability | 99.95% | 30 days |
| Claim ingestion p95 latency | <= 500 ms | 28 days |
| Leaderboard read p95 latency | <= 300 ms | 28 days |
| Accepted claim to public aggregate p95 | <= 90 s | 28 days |
| Duplicate/replay correctness | 100% deterministic fixture pass | every release |
| Forbidden-field acceptance | 0 | continuous |

Alerts should be symptom-based and actionable. Page only for user-visible availability, integrity, privacy or data-loss risk. Ticket non-urgent capacity and trend alerts.
