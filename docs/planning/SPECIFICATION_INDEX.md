# VibeMaxxing Technical Specification Index

Use this index to locate authoritative context and identify missing planning contracts.

| Component | Primary sources | Planning contract still required |
|---|---|---|
| Product thesis and scope | `PROJECT_CONTEXT.md`, `docs/product/PRODUCT_SPEC.md` | glossary, non-goals, launch scope |
| Metrics and periods | `docs/product/METRICS.md`, `TOKEN_ACCOUNTING_SPEC.md` | complete edge-case and time policy |
| Cash Burn | `CASH_BURN_PRICING_PROVENANCE.md` | dataset schema, aliases, corrections, subscription/local policy |
| Agent adapters | `AGENT_INTEGRATION_RESEARCH_MATRIX.md`, `ADAPTER_CERTIFICATION_POLICY.md` | manifest and normalized event schemas |
| VibeProof claims | `INTEGRITY_MODEL.md`, ADR-003..005 | field inventory, CDDL, signing profile, error registry |
| Collector | `ARCHITECTURE.md`, `COLLECTOR_PERFORMANCE_AND_POWER.md` | process, persistence, checkpoint, offline queue contracts |
| IPC and device identity | `LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `PLATFORM_ISOLATION.md` | wire messages and platform state machines |
| Authentication | `AUTHENTICATION_AND_RECOVERY.md` | enrollment, session, recovery, revocation, deletion APIs |
| Server ingestion | `ARCHITECTURE.md`, `BUILD_PLAN.md` | HTTP/API contracts, rejection taxonomy, limits |
| Database and aggregation | `LEADERBOARD_STORAGE_AND_RANKING.md`, benchmark SQL | complete SQL model, transactions, migrations, rebuild |
| Ranking | `METRICS.md`, ranking architecture | ties, pagination, late events, cache, current-user rank |
| Web product | `design.md`, `BRAND.md`, product spec | route map, data contracts, all UI states and copy |
| Privacy verification | `PRIVACY_CONTRACT.md`, onboarding spec | outbound-claim viewer and audit UX payload |
| Social system | product and social research docs | graph, presence, boards, notifications, permissions |
| Abuse and moderation | `ABUSE_AND_COUNTRY_PRIVACY.md`, social research | quarantine, restrictions, appeals, audit and retention states |
| Observability | `OBSERVABILITY_PRIVACY.md` | event schema, allowlisted fields, access and retention |
| Packaging and updater | `RELEASE_VERIFICATION.md`, ADR-005 | platform matrix, TUF roles and updater state machine |
| Deployment | `TECH_STACK.md`, `PRODUCTION_READINESS.md` | environments, config, secrets, migrations, promotion |
| Recovery and lifecycle | `DATA_LIFECYCLE_AND_RECOVERY.md`, incident docs | deletion mapping, backup scope, RPO/RTO, playbooks |
| Evaluation | `EVAL_SYSTEM.md`, `ACCEPTANCE_GATES.md`, suites YAML | task-to-eval traceability and activation conditions |

## Cross-cutting sources

Every component must comply with:

- `PROJECT_INSTRUCTIONS.md`;
- `MODEL_OPERATING_MANUAL.md`;
- `docs/privacy/PRIVACY_CONTRACT.md`;
- `docs/security/THREAT_MODEL.md`;
- `docs/security/INTEGRITY_MODEL.md`;
- `docs/engineering/PERFORMANCE_BUDGETS.md`;
- `docs/qa/ACCEPTANCE_GATES.md`;
- `docs/planning/DECISION_REGISTER.md`;
- `docs/planning/TASK_CATALOG.md`.

## Handoff rule

A future implementation model must not invent behavior for an item listed as a missing contract. It must either complete the owning planning task first or request an explicit phase/decision waiver.