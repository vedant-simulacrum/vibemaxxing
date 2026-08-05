# Production Readiness Review

No production launch is permitted until all applicable items have evidence links.

## Legal and data protection

Every item in this section is **unmet at this head**. They are listed first because none of them is closed by engineering work, and because a launch decision that reached the reliability section without noticing them would be reading this document in the wrong order. D-109 owns the set.

- **Counsel review of `PRIVACY.md`, `TERMS.md`, `docs/privacy/DATA_MAP.md` and ADR-009 is complete**, with a named reviewer, a date, and a record of what changed. **Unmet.** No lawyer has read any of them.
- **The data protection impact assessment required by Article 35 is complete.** **Unmet.** ADR-021 records that it is mandatory on two independent routes and has not been carried out. If it produces a residual high risk, Article 36 prior consultation is a further gate.
- **The controller's legal name, postal address, supervisory authority and governing jurisdiction are filled in.** **Unmet.** They are bracketed placeholders in `PRIVACY.md` and `TERMS.md`, which therefore cannot be published as they stand.
- **Every processor and sub-processor is named**, with an executed Article 28 data processing agreement. **Unmet.** ADR-017 fixes the region and the selection procedure and deliberately does not name a provider, so an Article 15(1)(c) request could not currently be answered accurately.
- **A United Kingdom Article 27 representative is appointed**, if participants in the United Kingdom are accepted. **Unmet**, and D-106 makes it a precondition on accepting them rather than on launching.
- **The consent, withdrawal, erasure, export and portability paths have been executed end to end**, not specified. Portability scope follows D-108: raw counts are portable, derived figures are not.
- **A documented process exists for answering a data subject request within the Article 12(3) month and for answering a supervisory authority.** ADR-021 identifies failure at either as the behaviour that converts a modest enforcement outcome into a processing ban, and D-092 accepts best-effort availability with no on-call, which is the operational profile that makes it plausible.

## Product and data

- Product scope and unsupported behavior are documented.
- Data classification and retention are approved.
- User export, deletion and device revocation are tested.
- Cash Burn is visibly labelled as an estimate.

## Privacy and security

- Privacy threat model is current.
- External security review is complete for the launch scope.
- Secrets, dependencies, containers and release artifacts are scanned.
- Authentication, authorization and abuse controls have negative tests.
- Transcript/network process separation is demonstrated.
- Incident contacts and disclosure process are operational.

## Reliability

- SLOs and error budgets are approved.
- Load, soak and failure-injection results meet targets.
- Backups have been restored in a clean environment.
- Data migrations have rollback or forward-fix plans.
- Rate limits, queue backpressure and degraded modes are tested.

## Release

- Versioning and changelog are complete.
- SBOM and provenance are published.
- Binaries and containers are signed.
- Deployment is progressive and reversible.
- Post-deploy smoke tests and automatic rollback criteria exist.

## Operations

- Dashboards and alerts cover availability, latency, error rate, ingestion lag, rejected claims, replay attempts and privacy-boundary violations.
- On-call ownership and escalation paths are defined.
- Runbooks have been exercised.
- A game day has validated one critical recovery path.
