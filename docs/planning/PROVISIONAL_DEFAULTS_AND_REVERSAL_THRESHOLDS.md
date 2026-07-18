# Provisional Defaults and Reversal Thresholds

Status: normative planning contract
Updated: 2026-07-19

These defaults prevent implementation-time invention. Evidence may reopen them through an ADR.

| Topic | Default | Reversal threshold |
|---|---|---|
| Ranking ties | SQL `rank()` with visible shared score and rank gaps | user testing shows material confusion or abuse |
| Global period timezone | UTC boundaries; user locale only changes display | competitive fairness research supports another canonical boundary |
| Country board | user assertion with cooldown, hidden by default, minimum cohort 25 | privacy/abuse testing requires stronger or larger threshold |
| Profile privacy | presence, country, friends and detailed activity off until user enables; aggregate public rank on | validated onboarding or growth evidence with privacy approval |
| License | Apache-2.0; DCO, no CLA initially | dependency/IP counsel or contributor governance requires change |
| VibeProof repository | remain in monorepo through launch | independent ecosystem demand and release ownership justify split |
| Rust CBOR/COSE libraries | select mature maintained crates behind internal interfaces after bakeoff | malformed/fuzz/resource/differential failure |
| SLM | do not ship in initial release unless it materially beats rules/statistics within budgets | detector bakeoff demonstrates calibrated lift and privacy safety |
| Production architecture | managed container runtime + managed PostgreSQL; no Kubernetes/Kafka initially | measured scale, isolation or operational evidence |
| Cache/queue | PostgreSQL outbox/source of truth; Redis only for ephemeral presence/rate limits | benchmark demonstrates necessary durable broker or cache |
| Regions | one primary region plus tested backup before multi-region active/active | residency, latency or resilience requirements justify expansion |
| RPO/RTO | target RPO <=15 minutes, RTO <=4 hours for launch; accepted-claim ledger prioritized | business/risk review requires stricter targets |
| Notifications | in-app first; transactional email for account/security; push deferred until justified | retention/user testing demonstrates push need |
| Release signing | platform-native signing/notarization + Sigstore provenance + TUF updates | platform or ecosystem requirements change |
| Pricing updates | scheduled weekly check plus event-driven urgent corrections; immutable versions | provider volatility requires higher cadence |
| Abuse thresholds | private versioned policy configuration; principles public | independent review recommends different disclosure balance |

## Rule

An implementation model must use these defaults when evidence is absent. It may not reopen a choice based on preference. Reversal requires recorded evidence, affected-contract updates, migrations or compatibility consequences, and an ADR when material.