# Production Readiness Review

No production launch is permitted until all applicable items have evidence links.

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
