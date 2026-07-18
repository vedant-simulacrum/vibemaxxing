# Defaults and Reversal Thresholds

Status: normative planning contract
Updated: 2026-07-19

Machine-readable configurable values are owned by `packages/schemas/policy-defaults-v1.json`. This document owns non-numeric architectural defaults and reversal evidence. Where a value appears in both places, the policy registry is canonical.

| Topic | Default | Reversal threshold |
|---|---|---|
| Ranking ties | SQL `rank()` with shared score and rank gaps | user testing shows material confusion or abuse |
| Global period timezone | UTC boundaries; locale changes display only | fairness research supports another canonical boundary |
| Country board | user assertion, hidden by default, cooldown and policy-registry cohort minimum | privacy/abuse testing requires stronger evidence or a larger cohort |
| Profile privacy | presence, country, friends and detailed activity off until enabled; aggregate public rank on | validated onboarding evidence plus privacy approval |
| License | Apache-2.0 code, CC BY 4.0 docs/specs, DCO and no CLA initially | ADR-009 release review identifies incompatible dependency or legal requirement |
| VibeProof repository | remain in monorepo through launch | ecosystem demand and independent release ownership justify split |
| Rust CBOR/COSE libraries | select maintained crates behind internal interfaces after bakeoff | malformed/fuzz/resource/differential failure |
| SLM | do not ship unless it materially beats rules/statistics within budgets | detector bakeoff demonstrates calibrated lift and privacy safety |
| Production architecture | managed containers + managed PostgreSQL; no Kubernetes/Kafka initially | measured scale, isolation or operational evidence |
| Cache/queue | PostgreSQL outbox/source of truth; Redis only for ephemeral state | benchmarks justify durable broker or additional cache |
| Regions | one primary region plus tested recovery region before active/active | residency, latency or resilience requirements justify expansion |
| RPO/RTO | operations contract targets: PostgreSQL RPO <=5 minutes, RTO <=60 minutes; stateless RTO <=15 minutes | exercised recovery cannot meet targets or risk review requires stricter targets |
| Notifications | in-app first; email only by explicit preference except mandatory security/recovery notices | user testing demonstrates additional channel need |
| Release signing | platform-native signing/notarization + provenance + TUF | platform or ecosystem requirements change |
| Pricing updates | weekly scheduled checks plus urgent event-driven corrections; immutable versions | provider volatility requires higher cadence |
| Abuse thresholds | private versioned configuration; public principles and appeal rights | independent review recommends different disclosure balance |

## Change rule

Evidence may reopen a default through the decision register and an ADR where material. Numeric values, ranges, owners, versioning and retroactivity follow the policy registry. No implementation may silently choose another value or reinterpret an existing record.
