# Operations, Open-Source, and Launch Contract

Status: normative planning contract
Version: 2

## Deployment baseline

Production is cloud-portable: managed containers for Go services and Next.js, managed PostgreSQL with point-in-time recovery, optional Redis-compatible ephemeral cache, object storage/CDN for releases, managed KMS/secrets and workload identity, OpenTelemetry-compatible observability, and a PostgreSQL transactional outbox before any broker.

Provider and region are selected during implementation through an ADR using latency, price, compliance, operational maturity, available credits and portability. Core behavior cannot depend on one provider.

Environments are local, test, preview, staging and production. Production data never enters lower environments. Preview uses synthetic fixtures. Configuration is typed and separated from secrets.

## Availability and recovery targets

- Public leaderboard/API: 99.9% monthly.
- Acknowledged claims: no loss.
- Leaderboard freshness p95: <=90 seconds.
- PostgreSQL RPO <=5 minutes and RTO <=60 minutes.
- Stateless service RTO <=15 minutes.
- Release/update metadata availability: 99.95%.
- OAuth outage degrades login/linking while existing sessions and local collection continue.

Backups are encrypted, cross-account where practical, retention-tiered and restore-tested monthly. Quarterly DR exercises rebuild from infrastructure code, backups, release artifacts and documented key procedures.

## Secrets and release keys

Separate OAuth, session, device-enrollment, release-signing, TUF, database, backup and observability keys. Use least privilege, workload identity, no long-lived cloud CI credentials, rotation, dual control for root/release keys, offline TUF root where practical, revocation and compromise playbooks.

## TUF and release chain

Use threshold-signed offline root, online timestamp/snapshot and delegated platform/channel targets. Clients defend against rollback, freeze, mix-and-match, fast-forward and endless-data attacks. Every release includes platform signature/notarization, checksums, SBOM, source commit, provenance, dependency/license report, TUF metadata, changelog, supported protocol/database versions, rollback constraints and consumer verification.

Install is atomic. Health checks cover daemon IPC, database migration, privacy boundary and compatibility. Failure rolls back. Security-blocked versions retain export and uninstall.

## Planning versus product automation

During planning-hardening, read-only checks may run automatically or manually when they validate documentation, schemas, registries, references, governance and deterministic generators without building or deploying the product. `scripts/repository/doctor.py` and `.github/workflows/planning-checks.yml` are allowed by D-034.

Product build, dependency, CodeQL, fuzz, security, release, signing, deployment and evaluation automation remains disabled until implementation begins. Before protected implementation merges, restore and tune:

- format/lint/unit/integration/property tests;
- Rust/Go/TypeScript builds and generated-contract drift;
- schema/CDDL/Protobuf/OpenAPI/SQL validation and breaking checks;
- privacy canaries and forbidden-field scans;
- pinned-action CodeQL, secret, dependency and license scans;
- fuzz/regression smoke tests;
- reproducible release, SBOM, provenance, TUF and consumer verification.

Scheduled expensive audits must be actionable and deduplicated.

## Observability

The canonical planning allowlist is `packages/schemas/observability-allowlist-v1.yaml`. Collection is deny-by-default. Never export prompts, responses, claim payloads, handles, repository names, paths, OAuth tokens, cookies, headers or free-text exceptions. Alerts cover ingestion failure, queue age, database saturation, SLO burn, OAuth failures, replay spikes, privacy canaries, updater expiry, release verification, backups and moderator/security anomalies.

Numeric retention defaults are versioned in the policy registry. Access is role-based and audited.

## Incidents and lifecycle

Severity defines commander, communication, containment, evidence, recovery, user notice, legal/regulatory review and postmortem deadlines. Privacy-boundary violations are highest severity until scoped. Security fixes use private advisories and coordinated disclosure.

Every data table requires purpose, owner, basis, visibility, retention, deletion, export, backup treatment and legal-hold policy. Deletion jobs are idempotent. Restores reapply deletion tombstones before production use.

## Open-source governance

Licensing follows ADR-009 and `LICENSES.md`: Apache-2.0 original code, CC BY 4.0 docs/specs, DCO and no CLA initially, subject to final dependency/license/counsel review. Third-party notices remain intact.

Before public release provide maintainers and succession, real CODEOWNERS, semantic versioning/changelog, public issue workflow, private advisories, contributor guide, code of conduct, adapter ownership/certification/transfer policy, trademark policy and release-key custody.

The repository becomes public before public launch only after history/secret scan, license review, security review, issue-template cleanup, contributor documentation and signing readiness.

## Launch stages

1. Planning-hardening: schemas, governance, validation and P-1120..P-1128 pass.
2. Implementation alpha: synthetic secure spine and one real adapter, no public competition.
3. Private alpha: native clients, OAuth, core ranking and privacy tests.
4. Private competitive beta: multiple adapter families, social loop, attack campaigns and operational drills.
5. Release candidate: complete feature matrix, universal fallback, packages, public repository and independent review.
6. Public launch: all gates and explicit approval.

## Public launch gates

Require complete product scope; exercised support registry and honest unsupported cases; accounting/protocol agreement; zero forbidden outbound content; adversarial campaigns within budgets; accessibility/browser/platform/battery/performance/load/failover/restore/update evidence; OAuth/recovery/privilege/deletion/moderation abuse tests; legal/privacy/governance/support readiness; and no unresolved P0/P1 blocker or ownerless accepted risk.

Runbooks, diagrams, inventories, dashboards, alert tests, restore logs, incident exercises, key-rotation drills, release artifacts, consumer install tests, status page, support escalation and signed launch decision are retained as versioned evidence without exposing sensitive thresholds.
