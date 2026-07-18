# VibeMaxxing Technical Specification Index

Updated: 2026-07-19

Use this index to locate authoritative contracts and identify work that still requires implementation-grade planning.

| Component | Primary sources | Remaining contract work |
|---|---|---|
| Identity, thesis, privacy, stack | `PROJECT_CONTEXT.md`, `PROJECT_INSTRUCTIONS.md` | only explicit open decisions listed there |
| Complete launch scope | `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md` | feature matrix, journeys, launch gates |
| Staged delivery | `IMPLEMENTATION_ROADMAP.md` | milestone acceptance evidence |
| Decisions and tasks | `DECISION_REGISTER.md`, `DEPENDENCY_MAP.md`, `TASK_CATALOG.md` | continuous maintenance and closure evidence |
| Metrics and Token Burn | `docs/product/METRICS.md`, `TOKEN_ACCOUNTING_SPEC.md` | normative formula, edge cases, comparability |
| Estimated Cash Burn | `CASH_BURN_PRICING_PROVENANCE.md` | dataset schema, provider aliases, subscriptions, local compute, corrections |
| Universal agent compatibility | `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md` | machine census, manifest/event schemas, exercised certification |
| Adapter certification | `ADAPTER_CERTIFICATION_POLICY.md`, `AGENT_INTEGRATION_RESEARCH_MATRIX.md` | lifecycle, community governance, downgrade tests |
| VibeProof claims | `INTEGRITY_MODEL.md`, ADR-002..005 | fields, CDDL, COSE profile, transport, errors, compatibility |
| Native client topology | `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md` | process diagram, CLI, IPC, storage, installer/update state machines |
| Collector performance | `COLLECTOR_PERFORMANCE_AND_POWER.md`, `PERFORMANCE_BUDGETS.md` | representative platform benchmarks |
| IPC and device identity | `LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `PLATFORM_ISOLATION.md` | complete messages, lifecycle, platform capability matrix |
| Authentication and recovery | `AUTHENTICATION_AND_RECOVERY.md`, amended ADR-003 | GitHub/X ADR, native auth, merge, provider loss, optional factors |
| Server ingestion/API | `ARCHITECTURE.md`, `BUILD_PLAN.md` | normative endpoints, schemas, auth, limits, errors, privacy classes |
| PostgreSQL and transactions | `LEADERBOARD_STORAGE_AND_RANKING.md`, benchmark SQL | complete logical schema, migrations, idempotency, rebuild |
| Ranking/time | `METRICS.md`, ranking architecture | ties, periods, late/offline claims, corrections, privacy, evidence filters |
| Profiles and social graph | `PRODUCT_SPEC.md`, social research | usernames, friends, blocks, rivals, movement, streaks |
| Boards and groups | `PRODUCT_SPEC.md`, social research | ownership, invitations, roles, eligibility, lifecycle |
| Presence and notifications | `PRODUCT_SPEC.md`, architecture | heartbeats, expiry, privacy, channels, hysteresis, rate limits |
| Country boards | `ABUSE_AND_COUNTRY_PRIVACY.md` | assertion, cohort privacy, changes, abuse, deletion |
| Abuse and anti-cheat | `ANTI_CHEAT_RESEARCH_PROGRAM.md`, `ANTI_CHEAT_ATTACK_CATALOG.md`, `THREAT_MODEL.md` | fixtures, reason registry, detector bakeoff, red-team evidence |
| Moderation and appeals | anti-cheat catalog, social/abuse docs | complete state machine, permissions, restoration, insider controls |
| Web information architecture | design/brand/product docs | routes, data contracts, complete UI states, copy |
| Local privacy verification | privacy contract, native architecture, onboarding | outbound viewer, permission, adapter, export/deletion UX |
| Accessibility and design QA | design docs, acceptance gates | browser/device matrix, keyboard, screen reader, reduced motion, visual tests |
| Observability | `OBSERVABILITY_PRIVACY.md` | event schema, allowlist, sampling, access, retention, canaries |
| Packaging and updater | `RELEASE_VERIFICATION.md`, ADR-005, native architecture | platform matrix, signing, notarization, TUF state machine |
| Deployment and secrets | `TECH_STACK.md`, `PRODUCTION_READINESS.md` | providers, regions, environments, configuration, promotion |
| SLOs, incidents, backup, DR | operations docs | budgets, RPO/RTO, restore, rollback, key compromise |
| Open-source governance | root community/security files | final license, DCO/CLA, trademark, maintainer/release governance |
| Evaluation and automation | `EVAL_SYSTEM.md`, `ACCEPTANCE_GATES.md`, suites | activation conditions, task traceability, restored launch checks |
| Repository metadata | `scripts/repository/generate_repository_metadata.py` | run from complete checkout before handoff/release |

## Cross-cutting requirements

Every component must define:

- owner and authority;
- scope and non-goals;
- interfaces and schemas;
- invariants, ordering, idempotency, and limits;
- privacy and security classification;
- authorization and abuse behavior;
- failures, timeouts, retries, crash recovery, rollback, and deletion;
- compatibility, versioning, migration, and deprecation;
- observability allowlist;
- positive, negative, adversarial, performance, and accessibility evidence where relevant;
- explicit unresolved decisions and closure condition.

## Handoff rule

A future implementation model must not invent critical behavior for any incomplete row. It must complete the owning planning task or obtain an explicit user waiver. Prose, empty fixtures, `not_applicable`, or unexecuted test definitions do not prove readiness.
