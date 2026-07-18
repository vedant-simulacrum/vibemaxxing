# Operations, Open-Source, and Launch Contract

Status: normative planning contract
Version: 1

## Deployment baseline

The production reference architecture is cloud-portable:

- managed container runtime for Go API/workers and Next.js web;
- managed PostgreSQL with point-in-time recovery and read replicas where measured;
- Redis-compatible ephemeral cache for presence/rate limiting only;
- object storage/CDN for public releases, SBOMs, provenance, and static assets;
- managed KMS/secrets and workload identity;
- OpenTelemetry-compatible observability;
- transactional outbox rather than Kafka initially.

Provider and region are deployment configuration selected through an ADR using latency, price, compliance, operational maturity, credits, and portability. No core contract depends on one provider.

Environments: local, test, preview, staging, production. Production data never enters lower environments. Preview environments use synthetic fixtures. Configuration is typed, validated at startup, and separated from secrets.

## Availability and recovery targets

Initial launch targets:

- public leaderboard/API availability: 99.9% monthly;
- claim ingestion durability after acknowledgement: no acknowledged claim loss;
- leaderboard freshness p95: <=90 seconds;
- PostgreSQL RPO: <=5 minutes, RTO: <=60 minutes;
- stateless service RTO: <=15 minutes;
- release/update metadata availability: 99.95%;
- OAuth provider outage degrades login/linking but existing sessions and collection continue.

Backups are encrypted, cross-account where possible, retention-tiered, and restore-tested monthly. Quarterly disaster-recovery exercises rebuild a clean environment from infrastructure code, backups, release artifacts, and documented key procedures.

## Secrets and keys

Separate keys for OAuth clients, sessions, device enrollment, release signing, TUF roles, database, backups, and observability. Least privilege, workload identity, no long-lived cloud credentials in CI, documented rotation, dual control for root/release keys, offline TUF root where practical, emergency revocation and compromise playbooks.

## TUF and release chain

TUF roles: offline root with threshold signatures; online timestamp; snapshot; delegated targets by platform/channel. Metadata has bounded expiry. Client defends against rollback, freeze, mix-and-match, fast-forward, and endless-data attacks; root rotation follows the specification and is tested.

Every release includes platform-native signature/notarization, SHA-256 checksums, SBOM, source commit, build provenance, dependency/license report, TUF metadata, changelog, supported protocol/database versions, rollback constraints, and consumer verification instructions.

Install is atomic. Health checks validate daemon IPC, database migration, privacy boundary, and version compatibility. Failure rolls back to the retained known-good version. Security-blocked versions still permit export and uninstall.

## CI and security automation

During planning, automatic checks remain disabled to avoid noise. Before implementation merge protection, restore staged checks:

- formatting, lint, unit/integration/property tests;
- Rust/Go/TypeScript builds and generated-contract drift;
- schema/CDDL/Protobuf breaking checks;
- privacy canary and forbidden-field scans;
- CodeQL/secret/dependency/license scans with tuned severity;
- fuzz/regression corpus smoke tests;
- reproducible release and clean-consumer verification;
- SBOM/provenance/TUF validation;
- task/decision/reference and generated-metadata validation.

Scheduled expensive audits run at sensible cadence; notifications are actionable and deduplicated.

## Observability

Metrics and logs are allowlisted. Retention: detailed operational telemetry 30 days, aggregates 13 months, security audit according to documented legal/security need. Access is role-based and audited. No prompts, responses, claim payloads, handles, repository names, paths, OAuth tokens, cookies, headers, or free-text exception bodies.

Alerts cover ingestion failure, queue age, database saturation, replica lag, error/latency SLO burn, OAuth failures, challenge/replay spikes, privacy-canary violations, updater metadata expiry, release-verification failure, backup failure, and moderator/security anomalies.

## Incident response

Severity levels define commander, communication, containment, evidence preservation, recovery, user notice, regulator/legal review, and postmortem deadlines. Privacy-boundary violation is automatically highest severity until scoped. Security incidents use private advisories and embargoed fixes; public disclosure occurs after users can update unless active exploitation requires earlier warning.

## Data lifecycle

Document per-table purpose, owner, lawful/product basis, visibility, retention, deletion, export, backup treatment, and legal hold. Deletion jobs are idempotent and auditable. Backups age out deleted data on the published schedule; restores reapply deletion tombstones before production use.

## Open-source governance

License plan: Apache-2.0 for original code unless dependency or trademark considerations require an approved exception; protocol specifications and documentation use CC BY 4.0 where appropriate. Final license scan and counsel review precede public release.

Use Developer Certificate of Origin with signed-off commits; no CLA initially. Add a CLA only if a concrete relicensing or corporate-contribution need arises.

Governance:

- maintainers with documented areas and succession;
- CODEOWNERS for security/privacy/protocol/release paths;
- semantic versioning and changelog;
- public roadmap/issues for product work;
- private security advisories for vulnerabilities;
- contributor guide, code of conduct, threat-model and privacy requirements;
- adapter maintainer ownership, conformance badges, emergency suspension, and transfer process;
- trademark policy protecting `VibeMaxxing`, `vibemaxxing`, and `VibeProof` while allowing accurate nominative use.

The repository becomes public before public launch after secret/history scan, license review, security review, issue-template cleanup, contributor documentation, and release-signing readiness.

## Launch stages

1. Planning complete: all normative contracts committed and contradiction review passes.
2. Implementation alpha: synthetic vertical slice and one real adapter, no public competition.
3. Private alpha: native clients, OAuth, core ranking, privacy tests, limited users.
4. Private competitive beta: multiple adapter families, social loop, attack campaigns, operational drills.
5. Release candidate: full launch feature matrix, universal compatibility fallback, supported-platform packages, open-source repository, independent security/privacy review.
6. Public launch: all launch gates pass; no scope reduction hidden as staging.

## Public launch gates

- Complete feature matrix across leaderboard scopes/periods, profiles, friends, rivals, overtakes, presence, boards, organizations, communities, countries, notifications, moderation, export/deletion, native shell/daemon/CLI/web.
- Exercised support registry covers every target adapter family and generic fallback; unsupported cases are explicit.
- Accounting/protocol conformance and independent implementations agree.
- Privacy packet captures/canaries show zero forbidden outbound content.
- Replay, duplicate, fork, clone, downgrade, Sybil, collusion, poisoning, and supply-chain campaigns meet approved budgets.
- Accessibility, browser, platform, battery, performance, load, soak, failover, backup/restore, update/rollback, clean install/uninstall, and disaster recovery evidence passes.
- OAuth, account-linking, recovery, privilege, deletion, and moderator workflows pass abuse tests.
- Legal/privacy terms, security policy, open-source governance, licenses, trademarks, support and incident channels are ready.
- No unresolved P0/P1 launch blocker; every accepted risk has owner, rationale, expiry/review date, and user impact.

## Operational acceptance evidence

Runbooks, architecture diagrams, inventories, dashboards, alert tests, restore logs, incident exercises, key-rotation drills, release-verification artifacts, consumer install tests, public status page, support escalation, and signed launch decision are retained as versioned evidence outside sensitive public thresholds.
