# Environments and Secrets

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-238, D-239

## Environments

`docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` says, in one sentence: "Environments are local, test, preview, staging and production." Five names, no statement of what any of them is, what runs in it, what data it holds, or how a change moves between them. This document is the mechanism behind that sentence, and it reduces the count, because five environments is not something one person on under 100 USD a month operates and writing down five was a description of an ambition rather than of a system.

### Four environments, and why not five

| Environment | Where it runs | Database | Data | Cost |
|---|---|---|---|---|
| `local` | the engineer's machine | containerised PostgreSQL 16 | synthetic fixtures | none |
| `ci` | GitHub Actions ephemeral runner | `postgres:16` service container, destroyed with the job | synthetic fixtures | included in the free tier |
| `preview` | per-pull-request static hosting | **none** | synthetic fixtures compiled into the build | none |
| `production` | one European Union region, AWS under D-361 | one managed PostgreSQL instance | real | the whole measured budget under D-360 |

`ci` is the environment the launch contract calls `test`. The name changes to the one everybody actually uses; nothing else about it does.

`preview` is deliberately narrower than the launch contract implies. It is a static build of the hosted web application with fixtures compiled in, served per pull request, with no database and no API. That is enough to review a layout, an interaction and an accessibility result, which is what a preview is for. A preview with its own database and API would need a per-pull-request managed PostgreSQL instance, and at the ADR-017 shortlist's prices that is the budget several times over for a facility that would be used a handful of times a week.

**`staging` does not exist.** No standing pre-production environment is provisioned, and the launch contract's sentence is amended by D-238 to say so rather than continuing to list an environment that has never existed and has no funding line.

That removal has real consequences and they are not hidden:

- ADR-018 requires a preproduction restore drill that applies a migration to a restored copy of production-shaped data, exercises the down section and re-applies. Without a standing staging environment this runs **in `ci`**, against an ephemeral database restored from the most recent production backup, as a manually dispatched job. It is the same drill; it lives for the duration of a job rather than permanently.
- The operations contract's quarterly disaster-recovery exercise runs the same way: restore into an ephemeral environment, verify, destroy.
- There is no place to observe a build under realistic load before production. The compensation is the private beta ring itself. Under D-180 the beta is invite-only and the owner issues every invite, so the participant set *is* the pre-production population, and the honest description is that beta participants absorb the risk a staging environment would otherwise absorb. `TERMS.md` already states that availability figures are aspirational rather than committed, which is the same admission from the participant's side.
- A change reaching production has been exercised in `ci` and by the author locally, and nowhere else.

`staging` is reinstated when either of the two things that make it affordable happens: a second maintainer under D-091, or a measured steady-state cost under D-360 that leaves room for a second environment. The fixed 100-USD ceiling this originally named no longer exists; the constraint is now what the configuration actually costs, which D-363 schedules the measurement of.

### Promotion

A change moves `local` → `ci` → `production`. `preview` is a branch off `ci` for web changes and is not on the promotion path; nothing is ever promoted from a preview.

Production deployment is a manually dispatched workflow against a tagged release set, never an automatic consequence of a merge. Under D-092 there is no on-call, so an automatic deployment is an automatic deployment into an unattended service. A human choosing the moment is the compensating control, and it is the only one available.

Migrations are applied as a separate, deliberate step before the deployment that needs them, per ADR-018, and never by the API process at startup.

### Data separation

Production data never enters a lower environment, in any form, including a subset, an anonymised extract or a single row copied into a bug report.

The one flow that crosses the boundary is the restore drill above, and it is bounded: the restore target is an ephemeral CI database that exists for the duration of one job in the same European Union region, no artifact from it is retained, and the job's logs carry no row content. Under ADR-017 a restore into any other region would be a residency violation regardless of how briefly it existed.

Every environment other than `production` uses a synthetic provider-identity namespace, so a mis-pointed development client cannot act against a real GitHub or X account.

### Configuration

Configuration is typed, validated at start, and separate from secrets, which the launch contract already requires. Two consequences are stated here because they are where the rule is usually broken:

- A process that cannot resolve a required configuration value **fails to start**. It does not fall back to a default. A default for a value that differs per environment is how a production process ends up running with development settings.
- The set of required values is identical across environments. `.env.example` lists every name with an empty value and is committed, and a CI check asserts that the names in it match the names the code reads. A variable that exists only in production is a variable nobody tests.

## Secrets

### What exists

The launch contract requires separate OAuth, session, device-enrollment, release-signing, TUF, database, backup and observability keys, with least privilege, workload identity, no long-lived cloud CI credentials, rotation, dual control for root and release keys, an offline TUF root where practical, revocation and compromise playbooks. All of that is right and none of it had a cadence, a mechanism or an owner. This section supplies them.

### Mechanism

| Class | Held in | Reaches the process as |
|---|---|---|
| runtime service secrets | the provider's managed secret store, selected under ADR-017 | environment variables injected at start |
| database credentials | issued by the managed PostgreSQL service | a connection string injected at start |
| CI credentials to the cloud | **none exist** | short-lived OIDC workload identity, ≤ 1 hour |
| release signing and TUF root | offline, on removable media, in the owner's physical custody | never reaches a process; used at signing time only |
| local development | generated on first run, or the engineer's own registered application | a git-ignored `.env.local` |

Criterion 1 of ADR-017 requires that every persistent store holding personal data is pinned to a European Union region. A managed secret store holds credentials rather than personal data, but a provider whose secret store is outside the region is a provider whose control plane holds the keys to the data inside it, so the same pin applies and it is a selection input rather than an afterthought.

No secret is ever committed, including to a private branch, including base64-encoded, including in a test fixture. Repository history is scanned before the repository becomes public, which the launch contract already requires; a secret found there is rotated regardless of whether it was ever used, because rotation is cheap and certainty about exposure is not available.

### Rotation cadence

Each interval below is derived from the lifetime of the thing the secret protects, not chosen for tidiness.

| Secret | Interval | Derived from |
|---|---|---|
| OAuth client secret, per provider | 365 days | no credential derived from it outlives a session family; annual is the shortest interval a manual re-registration at two providers is sustainable at |
| Session signing key | 90 days, with the previous two generations retained for verification | the web refresh family cap in ADR-015 is 90 days absolute, so a 90-day rotation with two retained generations verifies every handle that can still be valid |
| Device-enrollment signing key | 180 days | enrollment grants are short-lived; the key's exposure is bounded by how long an enrollment endpoint is reachable, not by a credential lifetime |
| Database credential | 180 days, and immediately on any maintainer change | the managed provider rotates on request; 180 days is two rotations a year, which one operator sustains |
| Backup encryption key | 365 days, previous keys retained for the full backup retention period | a backup must remain decryptable for as long as it is retained, so the key outlives its rotation by the retention window |
| Observability and log-store ingest key | 180 days | matches the database credential so the two rotate together in one maintenance action |
| Log pseudonymisation salt | 90 days | matches `operational_telemetry_retention_days` at 30 days with margin: after 90 days no live log line was written under an expired salt, so an expired salt can be destroyed rather than retained |
| TUF timestamp key | online, metadata expires in 1 day | standard TUF practice; the timestamp exists to bound freshness |
| TUF snapshot key | online, metadata expires in 7 days | bounds a mix-and-match window to one week |
| TUF targets key | online, metadata expires in 90 days | one quarter, so a release cadence slower than quarterly still refreshes it |
| TUF root key | offline, metadata expires in 365 days, re-signed at 270 days | the 90-day margin is the time available to notice and act on an expiring root before clients begin refusing updates |
| Release signing key | 730 days, or immediately on suspicion | rotating a signing key invalidates nothing already signed but requires every client to learn the new one through a root-signed delegation, which is a two-year-scale event |
| Cloud CI credential | not applicable | none exists; OIDC tokens are minted per job and expire in ≤ 1 hour |

Rotation is prospective. A rotation never invalidates an artifact signed under the previous key; it stops the previous key being used for new signatures and retains it for verification for the stated window.

Any secret is rotated **immediately**, outside its cadence, on: a maintainer change, a suspected exposure, a provider breach notification, a lost device holding a credential, or a repository history scan finding it.

### Dual control, and the fact that there is none

The launch contract requires dual control for root and release keys. **Under D-091 there is one maintainer and dual control is unsatisfiable.** It is recorded as unsatisfiable rather than described as satisfied by a substitute.

What exists instead: the offline root and release keys are held on removable media in physical custody, use at signing time is recorded in a signed operations log with the release-set identity and the reason, and the record is retained as launch evidence alongside the artifacts. That is a single-operator checklist. It detects an error the operator makes and notices afterwards; it does not prevent one, and it provides no protection at all against a compromised operator. ADR-018 draws exactly this line for destructive migrations and this is the same line for keys.

Dual control becomes satisfiable when a second maintainer joins, which is the same trigger that withdraws the administrator bypass under D-091.

The same limitation applies to `packages/schemas/policy-defaults-v1.json`, where every policy carries `emergency_override: signed-two-person-approval`. Sixteen of those rows describe a control the project cannot perform. The rows added by the pull request that introduced this document use `owner-recorded-checklist` instead; the pre-existing rows are left alone because changing them is a policy-registry edit with its own review path, and it is listed as a work unit rather than made silently here.

### Revocation and compromise

Each class has a stated blast radius, because "rotate the key" is not a plan without one.

| Compromised | Effect | Action |
|---|---|---|
| OAuth client secret | an attacker can impersonate the application to the provider during an authorization exchange | rotate at the provider, invalidate in-flight transactions, no session effect |
| Session signing key | every session is forgeable | rotate, invalidate every session and refresh family, force re-authentication for everyone |
| Database credential | full read and write of all personal data | rotate, audit access logs, assess as a personal-data breach under Article 33 with the 72-hour clock running |
| Backup encryption key | historical personal data readable | rotate, re-encrypt retained backups, same Article 33 assessment |
| Release signing or TUF targets key | arbitrary code to every installed client | the release-compromise playbook in the operations contract: revoke, emergency minimum-version deadline, recall |
| TUF root key | complete loss of update trust | offline root recovery, out-of-band re-establishment, and there is no fast path |
| Log ingest key | write access to the log store | rotate; no personal data is exposed because the streams hold none beyond `account_ref` |

A personal-data breach triggers the Article 33 notification path in `docs/privacy/DATA_MAP.md` and the severity classification in `docs/operations/INCIDENT_RESPONSE.md`. Under D-092 there is no committed response time, and the 72-hour statutory clock is not a service commitment and is not affected by that.

## Evidence

No environment is provisioned. No provider is selected, no account exists, no secret has been created, no rotation has been performed, and no restore drill has been run. Every interval above is a policy for a system that does not exist. The first thing that makes any of it evidence is a provisioned production environment with a recorded first rotation date per class, and the first restore drill executed in `ci` against a real backup.
