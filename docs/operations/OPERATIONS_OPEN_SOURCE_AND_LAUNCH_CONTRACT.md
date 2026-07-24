# Operations, Open-Source, and Launch Contract

Status: normative planning contract
Version: 3
Updated: 2026-07-23

## Deployment baseline

Production is cloud-portable: managed containers for Go services and Next.js, managed PostgreSQL with point-in-time recovery, optional Redis-compatible ephemeral cache, object storage/CDN for releases, managed KMS/secrets and workload identity, OpenTelemetry-compatible observability and a PostgreSQL transactional outbox before any broker.

Provider and region are selected during implementation through an ADR using latency, price, compliance, operational maturity, available credits and portability. Core behavior cannot depend on one provider.

Environments are local, test, preview, staging and production. Production data never enters lower environments. Preview uses synthetic fixtures. Configuration is typed and separate from secrets.

## Launch platform baseline

Public launch requires exercised exact support profiles for:

- macOS Apple silicon `arm64`;
- macOS Intel `x86_64`;
- maintained Windows desktop and applicable Server profiles on native x64;
- maintained Windows desktop and applicable Server profiles on native ARM64;
- maintained Linux desktop/headless/remote profiles across the accepted package ecosystems on x86_64 and aarch64;
- WSL;
- signed container images;
- CI/ephemeral tool profiles.

WSL, containers and CI are globally competitive by default at the verifier-awarded evidence level. Android, iOS, iPadOS and ChromeOS have no native release artifact, application, collector, companion or launch gate.

No platform family is considered launched because another platform family works. Each exact tuple passes its own release gate and appears in the support registry.

## Availability and recovery targets

- Public leaderboard/API: 99.9% monthly.
- Acknowledged claims: no loss.
- Leaderboard freshness p95: <=90 seconds.
- PostgreSQL RPO <=5 minutes and RTO <=60 minutes.
- Stateless service RTO <=15 minutes.
- Release/update metadata availability: 99.95%.
- OAuth outage degrades login/linking while existing sessions and local collection continue.
- Local daemon availability target: >=99.9% while its declared service context exists.
- Mandatory update service must preserve update, export and uninstall paths during ordinary control-plane degradation.

Backups are encrypted, cross-account where practical, retention-tiered and restore-tested monthly. Quarterly DR exercises rebuild from infrastructure code, backups, release artifacts and documented key procedures.

## Secrets, identities and release keys

Separate OAuth, session, device-enrollment, release-signing, TUF, database, backup and observability keys. Use least privilege, workload identity, no long-lived cloud CI credentials, rotation, dual control for root/release keys, offline TUF root where practical, revocation and compromise playbooks.

Privileged machine-supervisor artifacts and keys are separate from ordinary user claim keys. CI uses short-lived workload/job identity. Container images and platform packages bind provenance to exact source commits and release-set identity.

## TUF, release sets and mandatory updates

ADR-013 and D-068 are binding.

Use threshold-signed offline root, online timestamp/snapshot and delegated platform/channel targets. Clients defend against rollback, freeze, mix-and-match, fast-forward and endless-data attacks.

Every release set includes:

- platform artifact or image digests;
- source commit;
- SBOM and provenance;
- dependency/license report;
- TUF metadata;
- changelog;
- supported protocol, schema, database and adapter versions;
- supported exact platform tuples;
- upgrade path and rollback constraints;
- update class, deadline and allowed deferral;
- consumer-verification instructions.

Update classes are:

- emergency security/integrity;
- required compatibility;
- routine product.

Competitive profiles cannot permanently disable required updates. Users may select supported channels and bounded maintenance timing. Versions past a signed deadline may lose collection, claim finalization or sync according to the declared policy, while preserving diagnostics, update, export and uninstall where safely possible.

### Platform mechanisms

- macOS: signed/notarized coordinated app, daemon, helper and shell replacement with rollback.
- Windows: signed native x64/ARM64 installer and service replacement with rollback.
- Linux: project repositories or portable updater under the same release-set authority; package-manager and built-in paths cannot create mixed incompatible component sets.
- WSL: independent guest update lifecycle.
- Containers: immutable signed image replacement; no normal in-container self-update.
- CI: current pinned signed tool/action artifact; expired versions are rejected after the compatibility window.

Installation and update are atomic at the release-set level. Health checks cover daemon IPC, storage migration, privacy boundary, service registration and compatibility. Failure rolls back without resetting lineage or losing queued claims.

## Optional privileged supervision

ADR-012 permits optional machine-wide lifecycle supervision only as a separate, consented, least-privilege profile.

Release requirements include:

- separate signed/notarized artifacts;
- explicit capability and ACL manifest;
- no source-content or ordinary claim-key access;
- cross-user isolation;
- typed authenticated IPC;
- upgrade, rollback, downgrade and uninstall paths;
- independent security/privacy review;
- no automatic Hardened award.

## Planning versus product automation

During planning, read-only checks may validate documentation, schemas, registries, references, governance and deterministic generators without executing or deploying the product. `scripts/repository/doctor.py` and `.github/workflows/planning-checks.yml` are allowed by D-034.

ADR-014 permits `.github/workflows/storyboard-visuals.yml` only as prototype/design-system validation:

- synthetic fixtures only;
- read-only repository permissions;
- scoped UI/asset/style-guide pull requests or manual dispatch;
- no production secrets or services;
- no daemon, collector, protocol, server, database, installer, security or anti-cheat evaluation;
- short-lived artifacts labelled as runnable-prototype review evidence.

Storyboard output is not product CI, implementation evidence, security evidence, accessibility completion, deployment evidence or launch evidence.

All other product build, dependency, CodeQL, fuzz, security, release, signing, deployment and evaluation automation remains disabled until P-1104 opens implementation. Before protected implementation merges, restore and tune:

- format/lint/unit/integration/property tests;
- Rust/Go/TypeScript and all cross-platform builds;
- generated-contract drift and breaking checks;
- schema/CDDL/Protobuf/OpenAPI/SQL validation;
- privacy canaries;
- pinned-action CodeQL, secret, dependency and license scans;
- fuzz/regression tests;
- package/image/installer consumer tests;
- reproducible release, SBOM, provenance, TUF and update-deadline verification.

Scheduled expensive audits must be actionable and deduplicated.

## Observability

The canonical allowlist is `packages/schemas/observability-allowlist-v1.yaml`. Collection is deny-by-default. Never export prompts, responses, claim payloads, handles, repository names, paths, OAuth tokens, cookies, headers or free-text exceptions.

Alerts cover:

- ingestion and queue failure;
- database saturation and SLO burn;
- OAuth failures;
- replay/fork/duplicate spikes;
- privacy canaries;
- platform service-registration failure;
- updater metadata expiry and deadline compliance;
- release verification and rollback;
- CI expired-artifact rejection;
- container rollout failure;
- backup/restore failure;
- moderator/security anomalies.

Numeric retention defaults are versioned. Access is role-based and audited.

## Incidents and lifecycle

Severity defines commander, communication, containment, evidence, recovery, user notice, legal/regulatory review and postmortem deadlines. Privacy-boundary violations are highest severity until scoped. Security fixes use private advisories and coordinated disclosure.

Release compromise playbooks cover:

- TUF/release-key compromise;
- malicious or vulnerable adapter/collector artifact;
- emergency minimum-version deadlines;
- platform package revocation;
- compromised privileged supervisor;
- container-image recall;
- CI tool expiry;
- rollback and safe-mode recovery.

Every data table requires purpose, owner, basis, visibility, retention, deletion, export, backup treatment and legal-hold policy. Deletion jobs are idempotent. Restores reapply deletion tombstones before production use.

## Open-source governance

Licensing follows ADR-009 and `LICENSES.md`: Apache-2.0 original code, CC BY 4.0 docs/specs, DCO and no CLA initially, subject to final dependency/license/counsel review. Third-party notices remain intact.

Before public release provide maintainers and succession, real CODEOWNERS, semantic versioning/changelog, public issue workflow, private advisories, contributor guide, code of conduct, adapter ownership/certification/transfer policy, trademark policy and release-key custody.

The repository becomes public before public launch only after history/secret scan, license review, security review, issue-template cleanup, contributor documentation and signing readiness.

## Launch stages

1. Planning repair: P-1140A–E complete within their stated scopes, P-1140F closed with zero open semantic P0/P1 findings, clean planning validation, and explicit P-1104 authorization.
2. Implementation alpha: synthetic secure spine and one real adapter, no public competition.
3. Private alpha: native runtime, OAuth, ranking, privacy and initial exact platform tuples.
4. Private competitive beta: complete platform families, multiple adapters, social loop, attack campaigns and operational drills.
5. Release candidate: complete product and platform matrix, packages/images/tool artifacts, public repository and independent review.
6. Public launch: every advertised profile passes and explicit approval is recorded.

Internal staging may deliver platform lanes incrementally, but public launch cannot silently omit Mac Intel, Mac Apple silicon, Windows x64, Windows ARM64, accepted Linux profiles, WSL, containers or CI.

## Public launch gates

Require:

- complete product scope except explicitly post-launch countries/SLM;
- exercised support registry and honest unsupported cases;
- exact platform tuple evidence for installation, supervision, keys, IPC, adapters, offline operation, update, rollback and uninstall;
- native Mac/Windows architecture evidence;
- Linux package/init/desktop/headless evidence;
- WSL host/guest duplicate and lifecycle evidence;
- container replica/state-volume and immutable-update evidence;
- CI retry/matrix/workload identity and expired-tool evidence;
- privileged-profile least-privilege and cross-user review where offered;
- mandatory-update deadline, blocked-version and compromise-recovery evidence;
- accounting/protocol agreement and zero forbidden outbound content;
- adversarial campaigns within budgets;
- accessibility/browser/battery/performance/load/failover/restore evidence;
- OAuth/recovery/deletion/moderation abuse tests;
- legal/privacy/governance/support readiness;
- no Android/iOS/iPadOS/ChromeOS native release dependency;
- no unresolved P0/P1 blocker or ownerless accepted risk.

Runbooks, diagrams, inventories, dashboards, alert tests, restore logs, incident exercises, key-rotation drills, release artifacts, consumer install tests, update tests, status page, support escalation and signed launch decision are retained as versioned evidence without exposing sensitive thresholds.
