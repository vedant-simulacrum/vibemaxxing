# Service Expectations and Alerts

Status: normative planning contract
Version: 2
Updated: 2026-08-06
Decisions: D-243

## What changed and why

Version 1 of this document proposed seven service level objectives — 99.9% ingestion availability, 99.95% leaderboard read availability, latency percentiles — under a header saying they "must be validated against real traffic before commitment", and then advised paging for user-visible availability.

D-092 records the owner's decision that availability is best effort, that there is no paging, no on-call rotation and no committed response time, and that hours of downtime are acceptable. Those seven numbers were therefore not merely unvalidated; they described an operating posture the project had already decided against. 99.9% monthly is 43 minutes of downtime. One person, asleep, with no pager, cannot meet it, and a document that leaves it standing is a document that will be cited later as a broken promise.

This version restates the same subject as what a solo best-effort operator can actually deliver. It separates two things version 1 conflated: **commitments**, which are met by mechanisms that run whether or not the operator is awake, and **observations**, which are measured and reviewed and promise nothing.

## Commitments

Four, and each is met by a deterministic mechanism rather than by responsiveness. That is the property that makes them keepable by one person.

| Commitment | Value | Mechanism that keeps it |
|---|---|---|
| Forbidden content crossing the device boundary | **zero** | fixed-schema encoding, deny-by-default allowlists, boundary canaries in the privacy eval suite, enforced pre-merge |
| Duplicate and replay correctness | **100% of deterministic fixtures pass, every release** | the conformance suites, enforced pre-merge and at release |
| An accepted claim is never silently altered | **absolute** | the append-only ledger; corrections and reversals are new records, never edits |
| Public evidence status is assigned by the server verifier | **absolute** | the client cannot select it; the API has no field for it |

None of the four depends on anyone noticing anything. Each is enforced before a change reaches production or by a data model that has no operation capable of violating it, which is why they can be commitments while availability cannot.

## Observations

Measured, published, and reviewed. **None is a commitment and none carries a response time.** Each carries a review trigger: a threshold at which the operator looks, not a threshold at which anyone is obliged to act.

| Indicator | Measured over | Review trigger |
|---|---|---|
| Monthly availability of the public API | calendar month | below 99.0%, about 7 hours 18 minutes |
| Claim ingestion p95 latency | 28 days | above 1,000 ms sustained for 1 hour |
| Leaderboard read p95 latency | 28 days | above 600 ms sustained for 1 hour |
| Accepted claim to public aggregate p95 | 28 days | above 300 seconds |
| Time since last verified backup | continuous | above 26 hours |
| Monthly infrastructure spend | calendar month | above 80 USD |

99.0% rather than 99.9% is the whole restatement in one number. It is roughly seven hours a month, which is what a single-region deployment with one managed database, provider maintenance windows and an operator who sleeps produces when a fault happens overnight. It is chosen as the level below which something is structurally wrong rather than as a level anybody is promising.

The latency triggers sit at roughly twice the engineering budgets in `docs/engineering/PERFORMANCE_BUDGETS.md`, so a budget regression is caught by the pre-merge benchmark and this trigger fires only when production diverges from what the benchmarks predicted.

The 26-hour backup trigger follows from a daily backup schedule: 26 hours means one backup has been missed and the next has not arrived.

The 80 USD spend trigger was set against the fixed 100-USD ceiling D-360 has since replaced with the measured steady-state cost. It is retained as an absolute figure rather than rescaled, because the measurement D-363 schedules has not been taken and a trigger derived from an unmeasured ceiling would be arithmetic dressed as a threshold. It is re-derived when that number exists.

## The recovery objectives, and the conflict that is not resolved here

`docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` records a PostgreSQL recovery point objective of at most 5 minutes and a recovery time objective of at most 60 minutes. **Neither is currently underwritten and this document does not pretend otherwise.**

A 5-minute recovery point objective requires continuous point-in-time recovery: archived write-ahead logs, retained and restorable to an arbitrary instant. That is a paid tier on every provider on the ADR-017 shortlist. A daily snapshot, which is what the free and lowest tiers provide, is a recovery point objective of **24 hours**.

**The reason this is not underwritten has changed, and the fact has not.** D-094's three-way conflict is resolved: D-360 replaced the fixed ceiling with the measured steady-state cost and D-361 selected AWS, whose managed PostgreSQL offers continuous point-in-time recovery on a tier the credit balance can fund. So the objective is no longer unaffordable. It is unprovisioned — no account, no instance, no backup schedule and no restore drill exists — and an objective nothing implements is not met, however affordable it has become.

The consequence for this document, stated plainly: **the operations contract's commitment that acknowledged claims are never lost is not underwritten at a 24-hour recovery point objective.** A restore from yesterday's snapshot loses up to a day of accepted claims, and the append-only ledger cannot recreate them because the originating device has already advanced its sequence past them. That is a real gap between two documents in this repository. It is no longer blocked on a decision — it is blocked on provisioning, and on D-363's measurement showing that continuous recovery fits inside the steady-state cost once the credits are gone.

Until an instance exists with a verified recovery configuration, the honest statement of the recovery position is: recovery point objective 24 hours, recovery time objective best effort, and the 5-minute and 60-minute figures in the operations contract are a target that nothing implements. D-094, now superseded, made them a target nothing could *afford*; they are now a target nothing has *built*.

## Alerts

Three classes. There is no pager, no rotation, no acknowledgement requirement and no escalation path, because under D-092 and D-091 there is nobody to escalate to.

### `immediate`

Delivered as an email and a push notification to the owner, at any hour. Reserved for conditions where continuing to run makes the outcome worse than stopping.

- A privacy-boundary canary violation. `vibemaxxing.privacy.canary.violation` is the one metric whose correct value is a constant; any non-zero reading is the operations contract's highest severity until scoped.
- Detected data loss or corruption in the claim ledger.
- Monthly spend exceeding 100 USD. That figure is the superseded D-093 ceiling retained as an absolute trigger, not a derived one: D-360 makes the ceiling the measured steady-state cost, and D-363 schedules the measurement. The trigger is re-derived when that number exists.
- Release-signing or TUF key material used outside a recorded signing event.

There is no committed response time even for these. What exists instead is that each has a **single documented containment action the owner can take from a phone**: disable ingestion, disable the affected route, or revoke a key. Containment is one command; diagnosis waits for morning. That is the realistic shape of a solo operator's incident response and it is better written down than improvised.

### `daily-digest`

One email a day, containing everything that fired in the previous 24 hours. Nothing here is urgent and batching them is what keeps the `immediate` class credible.

- A review trigger from the observations table crossing its threshold.
- Ingestion or outbox delivery failure rate above baseline.
- Database saturation: connection pool or storage above 80%.
- OAuth provider failures above baseline.
- Replay, fork or duplicate-claim rate above baseline.
- Backup or restore failure.
- Certificate or TUF metadata approaching expiry — timestamp at 12 hours, snapshot at 3 days, targets at 30 days, root at 90 days, each roughly a third of its validity remaining.
- Platform service-registration failures reported by clients.
- Update deadline non-compliance counts.
- Moderation queue depth beyond the 72-hour review target.

### `ticket`

An issue in the repository, reviewed when the owner next reviews issues. Capacity trends, cost trends, dependency advisories that are not exploitable, and eval-suite status changes.

### What is deliberately absent

No error budget, because there is no availability commitment for a budget to be spent against. No burn-rate alert. No paging policy. No severity-based response-time matrix — `docs/operations/INCIDENT_RESPONSE.md` classifies severity for the purpose of ordering the work, not for promising a clock.

## Alert quality

Two rules, both of which exist because a solo operator has exactly one thing to protect: their willingness to read the digest.

- **Symptom-based.** Alert on aggregate freshness, not on worker queue depth; on error rate, not on a restarted process. A cause-based alert fires for every cause and a symptom-based alert fires when a participant would notice.
- **An alert that fires more than once a week without producing an action is deleted or its threshold moved**, and the change is recorded. An alert nobody acts on trains the operator to skim, and a skimmed digest is where the privacy canary gets missed.

## Publication

Monthly availability and the latency percentiles are published on a status page. `TERMS.md` already states that any availability or latency figure published in this repository is an aspirational target and not a commitment, and the status page repeats it, so that publishing a measurement is never read as making a promise about the next one.

## Evidence

Nothing here is measured. There is no deployment, no metric pipeline, no alert routing, no status page, no backup and no restore. Every threshold above is derived from a decision or an arithmetic consequence of one, not from an observation. The first month of real traffic is expected to move the observation triggers, and moving them is a version bump to this document rather than a silent edit.
