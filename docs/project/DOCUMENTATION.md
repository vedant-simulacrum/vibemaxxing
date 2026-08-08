# VibeMaxxing Documentation Map

This is the sole canonical documentation map. Do not create competing indexes, master-context files, duplicate roadmaps, parallel implementation plans, or numbered research waves.

## Initialization order

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. this file
5. `docs/planning/DECISION_REGISTER.md`
6. `docs/planning/TASK_CATALOG.md`
7. `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
8. `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
9. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`
10. relevant ADRs, normative contracts, schemas, registries and fixtures
11. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` only for planning future work or after explicit P-1104 authorization

Run `python3 scripts/repository/doctor.py` from a clean checkout before relying on repository state.

## Current authority note

P-1140F owns all open semantic findings, and all 13 remain open. P-1104 is `authorized-open` as of 2026-08-05 by owner decision, recorded in `conformance/p1140f/gate-authorization-v1.json` and GitHub issue 44. It was opened with its preconditions unmet; the findings are tracked and not waived, and authorization is a decision rather than evidence that anything is implemented, secure, or launch-ready.

Gate and finding state are owned by `conformance/p1140f/*.json`. This note summarizes them and may not redefine them — if the two disagree, the registries win and this paragraph is the defect.

`docs/planning/SR_SEVERITY_REGRADING_PROPOSAL.md` proposes a severity for each of the thirteen findings and awaits an owner decision under D-300. It is a proposal and decides nothing: the finding registry holds the live severity of every finding, and every finding remains open at the severity that registry records.

The earlier four-finding review is superseded by the current consolidated semantic register.

The technical-specification completeness authority is `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`. A concept is not planning-complete merely because prose mentions it; the inventory must name its normative owner, machine owner or planned path, lifecycle/persistence owner, repair dependency, implementation dependency and evidence gate.

## Normative owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Documentation hierarchy: this file
- Decision authority: `docs/planning/DECISION_REGISTER.md`, `docs/decisions/`
- Task and gate state: `docs/planning/TASK_CATALOG.md`
- Technical-specification inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Structural review: `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
- Semantic review: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Adapter stages and VibeProof boundary: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- VibeProof wire/state protocol: `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `packages/schemas/vibeproof-claim-v1.cddl`
- Authoritative mutable state and platform behavior: `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`
- Per-adapter integration contracts, one file per adapter: `docs/integrations/`. The first is `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md`, which owns the Claude Code OTLP receive surface, its attribute strip list, its stage mapping and its certification tuple
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Personal-data inventory, lawful bases, retention windows and the Article 30 record of processing activities: `docs/privacy/DATA_MAP.md`
- Participant-facing privacy notice under Articles 13 and 14: `PRIVACY.md`, derived from `docs/privacy/DATA_MAP.md` and never stating more than it
- Participant-facing service terms, eligibility, acceptable use and the sanction and appeal process: `TERMS.md`
- Public-by-default publication risk acceptance and the legal analysis behind the three documents above: ADR-021
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`, ADR-015
- Ranking computation, the credited-score model, sealed generations and durable cursors: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`, ADR-020
- API edge numbers — rate-limit classes and quotas, API versioning and deprecation policy, and client retry, backoff, retry-budget and circuit obligations: `docs/architecture/API_EDGE_CONTRACT.md`. The server API contract owns the rules; this document owns the numbers underneath them and defers to the authoritative state contract on idempotency
- Origin validation, both for the public API and for every loopback listener, including the DNS-rebinding and cross-site request forgery defence for the local dashboard and the OTLP receiver: `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`
- Private-beta admission — invite code format and storage, issuance, quota, expiry, revocation, redemption atomicity, the order the age and account-age gates are evaluated in, and the guessing controls: `docs/security/PRIVATE_BETA_ADMISSION.md`
- Article 17 erasure, key material, proof of destruction, and backup and restore behaviour: `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md`, ADR-022
- Retention window per persistence owner, in machine-readable form: `packages/schemas/data-disposition-v1.json`, derived from `docs/privacy/DATA_MAP.md` and never disagreeing with it
- Accepted residual risks without a normative owner: ADR-019
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010 through ADR-013
- Operations/release/open source: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, ADR-013
- Service expectations, review triggers and alert routing under best-effort availability: `docs/operations/SLOS_AND_ALERTS.md`
- Environments, the promotion path, data separation, and secrets mechanism and rotation cadence: `docs/operations/ENVIRONMENTS_AND_SECRETS.md`
- Structured logging conventions, the never-logged list, and the emitted metric and span inventory: `docs/operations/LOGGING_AND_INSTRUMENTATION.md`. `docs/operations/OBSERVABILITY_PRIVACY.md` keeps the principle and the forbidden classes; the allowlist in `packages/schemas/observability-allowlist-v1.yaml` governs log fields as well as telemetry attributes
- Hosting region, data residency and provider selection: ADR-017
- Database and migration tooling: ADR-018
- Local development environment and stack bring-up: `docs/engineering/LOCAL_DEVELOPMENT.md`
- Test shape, frameworks, coverage floors, flake policy and load scenarios: `docs/verification/TEST_STRATEGY.md`
- Conformance fixture, manifest and runner design: `docs/verification/CONFORMANCE_HARNESS.md`
- Future implementation order: `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- Future PR-sized units: `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`
- Future repository layout: `docs/implementation/REPOSITORY_LAYOUT.md`
- UI system entry point: `docs/style-guide/README.md`
- Brand identity, palette and voice: `docs/style-guide/BRAND.md`
- Product UI layout, interaction and screen composition: `docs/style-guide/UI_FOUNDATIONS.md`
- UI layer model and dependency direction: `docs/style-guide/UI_ARCHITECTURE.md`
- Component rules: `docs/style-guide/COMPONENT_STANDARD.md`; component registry and usage contracts: `docs/style-guide/COMPONENT_INVENTORY.md`
- Acceptance gates, evaluation and benchmark protocol: `docs/verification/`

## Conflict resolution order

Merged from the archived `REPOSITORY_ALIGNMENT_2026-07-23.md`, which was the only place this hierarchy was written down. When repository artifacts disagree, resolve in this order:

1. latest explicit user instruction;
2. `docs/project/PROJECT.md`;
3. `docs/project/STATUS.md`;
4. accepted decisions in `docs/planning/DECISION_REGISTER.md`;
5. accepted ADRs;
6. normative subsystem contracts and authoritative schemas that are not marked blocked or superseded;
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`;
8. research and audit evidence;
9. historical completion reports, generated artifacts, stale branches and closed planning assumptions.

Where a machine-readable registry exists for a concept, it outranks prose describing the same concept at the same level. `conformance/p1140f/*.json` owns semantic finding, artifact-authority and gate state; prose summarizes it and may not redefine it.

## Complete file map

Every directory under `docs/`, and every file in it. The **Normative owners** list above names the documents that decide things; this section exists so no document is unaccounted for. A file that appears here but nowhere above is supporting material — it may inform an owner, but it does not decide.

| Directory | Role | Files |
|---|---|---|
| `project/` | **Top authority.** Product, phase, and this map | `PROJECT.md`, `STATUS.md`, `DOCUMENTATION.md` |
| `planning/` | Decisions, gates, scope, policy | `DECISION_REGISTER.md`, `TASK_CATALOG.md`, `SCHEMA_AND_INTERFACE_INVENTORY.md`, `ARTIFACT_POLICY.md`, `PRODUCT_SCOPE_FREEZE.md`, `REPOSITORY_OPERATIONS.md`, `PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md`, `P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, `P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`, `SR_SEVERITY_REGRADING_PROPOSAL.md` (proposal, no authority), `CROSS_PLATFORM_COMPLETENESS_AUDIT.md`, `ANTI_CHEAT_IMPLEMENTATION_PLAN.md`, `decision-traceability/` (`D-001-D-020.md`, `D-021-D-040.md`, `D-041-D-061.md`, `D-062-D-069.md`, `D-070-D-099.md`, `D-100-D-199.md`, `D-200-D-299.md`, `D-300-D-399.md`, `D-400-D-499.md`, `D-500-D-599.md`, `D-600-D-699.md`, `README.md`; the `D-*.md` shards are generated from `conformance/planning/decision-traceability-v1.json`) |
| `decisions/` | Accepted ADRs | `ADR-001` … `ADR-022` |
| `architecture/` | System contracts, including the canonical wire profile | `VIBEPROOF_V1_PROTOCOL.md`, `VIBEPROOF_V1_CANONICAL_PROFILE.md`, `ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `API_EDGE_CONTRACT.md`, `NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `NATIVE_CLIENT_AND_DAEMON.md`, `LEADERBOARD_STORAGE_AND_RANKING.md`, `PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `ARCHITECTURE.md` |
| `decisions/` | Accepted ADRs | `ADR-001` … `ADR-022` |
| `architecture/` | System contracts, including the canonical wire profile | `VIBEPROOF_V1_PROTOCOL.md`, `VIBEPROOF_V1_CANONICAL_PROFILE.md`, `ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `NATIVE_CLIENT_AND_DAEMON.md`, `LEADERBOARD_STORAGE_AND_RANKING.md`, `PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `ARCHITECTURE.md` |
| `product/` | Product surface and metrics | `PRODUCT_SPEC.md`, `ACCOUNTING_AND_TIME_CONTRACT.md`, `TOKEN_ACCOUNTING_SPEC.md`, `CASH_BURN_PRICING_PROVENANCE.md`, `SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, `ONBOARDING_AND_PRIVACY_VERIFICATION.md`, `METRICS.md`, `SOCIAL_RANKING_AND_ABUSE_RESEARCH.md` |
| `privacy/` | **The boundary.** The invariant everything else serves, plus the personal-data record that follows from it | `PRIVACY_CONTRACT.md`, `PRIVACY_PRESERVING_USAGE_EVIDENCE.md`, `DATA_MAP.md` |
| `security/` | Threat, integrity, attestation, abuse | `THREAT_MODEL.md`, `INTEGRITY_MODEL.md`, `EVIDENCE_AND_ATTESTATION_PROFILES.md`, `AUTHENTICATION_AND_RECOVERY.md`, `RANKED_IDENTITY_ELIGIBILITY.md`, `ANTI_CHEAT_ATTACK_CATALOG.md`, `ANTI_CHEAT_RESEARCH_PROGRAM.md`, `ADVERSARIAL_TABLETOPS.md`, `LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `ORIGIN_AND_LOOPBACK_CONTROLS.md`, `PRIVATE_BETA_ADMISSION.md`, `PLATFORM_ISOLATION.md`, `ABUSE_AND_COUNTRY_PRIVACY.md` |
| `privacy/` | **The boundary.** The invariant everything else serves, the personal-data record that follows from it, and what an Article 17 erasure does | `PRIVACY_CONTRACT.md`, `PRIVACY_PRESERVING_USAGE_EVIDENCE.md`, `DATA_MAP.md`, `ERASURE_AND_KEY_DESTRUCTION.md` |
| `security/` | Threat, integrity, attestation, abuse | `THREAT_MODEL.md`, `INTEGRITY_MODEL.md`, `EVIDENCE_AND_ATTESTATION_PROFILES.md`, `AUTHENTICATION_AND_RECOVERY.md`, `RANKED_IDENTITY_ELIGIBILITY.md`, `ANTI_CHEAT_ATTACK_CATALOG.md`, `ANTI_CHEAT_RESEARCH_PROGRAM.md`, `ADVERSARIAL_TABLETOPS.md`, `LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `PLATFORM_ISOLATION.md`, `ABUSE_AND_COUNTRY_PRIVACY.md` |
| `integrations/` | Agent compatibility and certification | `UNIVERSAL_AGENT_COMPATIBILITY.md`, `ADAPTER_CERTIFICATION_POLICY.md`, `ADAPTER_ONE_CLAUDE_CODE_OTEL.md`, `AGENT_INTEGRATION_RESEARCH_MATRIX.md`, `T20_CERTIFICATION_AND_SELECTION_SPEC.md`, `T20_MODEL_HARDENING_CONTRACT.md` |
| `operations/` | Launch, running, recovery | `OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, `RELEASE_VERIFICATION.md`, `PRODUCTION_READINESS.md`, `COMPETITIVE_BETA_GATE.md`, `INCIDENT_RESPONSE.md`, `SLOS_AND_ALERTS.md`, `OBSERVABILITY_PRIVACY.md`, `LOGGING_AND_INSTRUMENTATION.md`, `ENVIRONMENTS_AND_SECRETS.md`, `DATA_LIFECYCLE_AND_RECOVERY.md` |
| `implementation/` | Work decomposition | `IMPLEMENTATION_HANDOFF.md`, `PR_SIZED_WORK_BREAKDOWN.md`, `ISSUE_GENERATION.md`, `REPOSITORY_LAYOUT.md` |
| `engineering/` | Engineering standards and budgets | `ENGINEERING_SYSTEM.md`, `LOCAL_DEVELOPMENT.md`, `PERFORMANCE_BUDGETS.md`, `COLLECTOR_PERFORMANCE_AND_POWER.md` |
| `verification/` | Acceptance gates, evaluation, benchmark and evidence protocol | `ACCEPTANCE_GATES.md`, `EVAL_SYSTEM.md`, `TEST_STRATEGY.md`, `CONFORMANCE_HARNESS.md`, `BENCHMARK_AND_EVIDENCE_PROTOCOLS.md` |
| `style-guide/` | UI system and brand, owned by `packages/ui` | `README.md` (entry point), `BRAND.md`, `UI_FOUNDATIONS.md`, `UI_ARCHITECTURE.md`, `COMPONENT_STANDARD.md`, `COMPONENT_INVENTORY.md`, `AI_UI_RULES.md`, `ASSET_SYSTEM.md`, `LEADERBOARD_FIRST_BASELINE.md`, `LEADERBOARD_BENTO_BASELINE.md`, `MIGRATION.md`, `RESEARCH.md`, `references/` (approved captures) |
| `research/` | Primary evidence, historical | `README.md` (sole entrypoint), `RESEARCH_AUDIT_2026-07{,_WAVE2..5}.md`, `ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md` |
| `history/` | **Non-authoritative.** Superseded reports | See `docs/history/README.md` |

### Root-level participant-facing and governance documents

`docs/` holds documents written for the people building this. The repository root holds the ones written for everyone else, and they are listed here so no tracked file is unaccounted for.

| File | Role | Owner it derives from |
|---|---|---|
| `README.md` | Repository entry point | `docs/project/PROJECT.md` |
| `AGENTS.md` | Sole agent initialization manual | Itself; `conformance/p1140f/gate-authorization-v1.json` owns the phase state it restates |
| `PRIVACY.md` | **Participant-facing privacy notice** under Articles 13 and 14 | `docs/privacy/DATA_MAP.md` |
| `TERMS.md` | **Participant-facing service terms** | `docs/decisions/ADR-021-PUBLIC_BY_DEFAULT_RISK_ACCEPTANCE.md`, and `PRIVACY.md` on any personal-data question |
| `SECURITY.md` | Vulnerability reporting and response targets | `docs/security/THREAT_MODEL.md` |
| `LICENSES.md` | Licensing summary | `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | Contribution process and conduct | `docs/planning/REPOSITORY_OPERATIONS.md` |
| `CHANGELOG.md` | Release history | `docs/operations/RELEASE_VERIFICATION.md` |

`PRIVACY.md`, `TERMS.md` and `docs/privacy/DATA_MAP.md` are one set and are read together. None of the three has been reviewed by counsel, and D-109 records that review as an unmet release gate alongside the data protection impact assessment, the unfilled controller identity placeholders and the missing sub-processor list.

### Small directories, with reasons

`privacy/` (3 files) is deliberately isolated: it holds the invariant the whole system exists to serve, and burying it inside `security/` would make it look like one control among many. `project/` (3) is the top authority and must stay at a short, obvious path. `engineering/` (4) and `verification/` (5) were the two that had room to grow and did, absorbing the local-development, test-strategy and conformance-harness owners added on 2026-08-06. No other directory under `docs/` holds fewer than four files.
`privacy/` (4 files) is deliberately isolated: it holds the invariant the whole system exists to serve, and burying it inside `security/` would make it look like one control among many. `project/` (3) is the top authority and must stay at a short, obvious path. `engineering/` (3) and `verification/` (3) are coherent single subjects with room to grow and no better host.

### Structural changes on 2026-08-06

- `protocol/` folded into `architecture/`; `qa/` and `evals/` combined into `verification/`; `design/` folded into `style-guide/`.
- `style-guide/ARCHITECTURE.md` renamed to `style-guide/UI_ARCHITECTURE.md` so it can no longer be confused with `architecture/ARCHITECTURE.md`.
- `style-guide/COMPONENTS.md` merged into `COMPONENT_INVENTORY.md`; `design/design.md` merged into `style-guide/UI_FOUNDATIONS.md`.
- `planning/REPOSITORY_ALIGNMENT_2026-07-23.md` and `planning/MACHINE_CONTRACT_REPAIR_SPEC.md` archived to `history/`.

### Operational surfaces added on 2026-08-06

Seven documents were added for surfaces an audit found either entirely absent from the repository or named without a single number behind them. Each has one owner and none duplicates an existing one:

- `architecture/API_EDGE_CONTRACT.md` — rate-limit quotas, API versioning and deprecation, client retry and backoff. The server API contract keeps the rules; this holds the numbers, and idempotency stays with the authoritative state contract.
- `security/ORIGIN_AND_LOOPBACK_CONTROLS.md` — origin validation for the public API and for every loopback listener, including the DNS-rebinding defence the local dashboard and the OTLP receiver had no control against.
- `operations/LOGGING_AND_INSTRUMENTATION.md` — application logging, which the observability privacy policy governed only by implication, and the emitted metric inventory, which nothing stated at all.
- `operations/ENVIRONMENTS_AND_SECRETS.md` — the mechanism behind the launch contract's one-sentence environment list, and the rotation cadence its secrets paragraph never carried.
- `engineering/LOCAL_DEVELOPMENT.md` — how the stack comes up.
- `verification/TEST_STRATEGY.md` and `verification/CONFORMANCE_HARNESS.md` — the method under the engineering system's eight layers, and the fixture and runner contract under `conformance/`.

`operations/SLOS_AND_ALERTS.md` was rewritten rather than added: its seven proposed objectives described an operating posture D-092 had already rejected.

Known duplication that genuinely remains, recorded rather than silently carried. Each cluster needs a single owner chosen and the rest merged or marked:

- Anti-cheat material spans `research/ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md`, `planning/ANTI_CHEAT_IMPLEMENTATION_PLAN.md`, `security/ANTI_CHEAT_ATTACK_CATALOG.md`, `security/ANTI_CHEAT_RESEARCH_PROGRAM.md`, and `security/ADVERSARIAL_TABLETOPS.md`.
- `style-guide/COMPONENT_INVENTORY.md` records an unresolved naming overlap between the proposed generic `Notice`/`Dialog` and the implemented `ProductNotice`/`ProductDialog`. An owner must decide whether these are one concept or two.
- `style-guide/UI_FOUNDATIONS.md` §17 records the token, radius, type-scale, motion and logo values on which the retired `design.md` disagreed with `BRAND.md`. The approved column governs; the disagreement is kept visible rather than deleted.

## Every document declares an owner

`scripts/repository/doctor.py` requires every tracked markdown file to be named in
this document, either individually or by a directory class declared below. Adding a
file without naming it here fails the doctor.

This replaces a blocklist of thirteen exact filenames. Those thirteen — starting with
`PROJECT_CONTEXT.md`, `START_HERE_PROMPT.md` and `IMPLEMENTATION_ROADMAP.md` — were
real files that once competed with the authorities they duplicated, and deleting them
was correct. Forbidding those names was not the same rule: it caught the thirteen that
had already happened and nothing else. A fourteenth competing file under any other
name passed every check, which was verified by creating `MASTER_CONTEXT.md` asserting
"P-1140F complete, gate P-1104 closed" — a direct contradiction of
`conformance/p1140f/gate-authorization-v1.json` — and watching the full validator
suite pass. The thirteen names remain refused, as history that should stay dead.

The rule is now positive: a new document must say what it owns, in the table that
lists what everything else owns, where a duplicate is visible to a reviewer. That is
the check the principle always needed, and a rename does not evade it.

Two directory classes are covered in bulk rather than per file, because both are
explicitly non-authoritative and grow by accumulation:

| Class | Why bulk coverage is admissible |
|---|---|
| `docs/history/` | Superseded point-in-time reports. Nothing in it is authority, and it is retained so retracted conclusions stay visible. |
| `docs/research/` | Primary evidence behind `README.md`, its sole entrypoint. Research informs an open decision and never overrides an accepted one. |

Four files outside `docs/` are named here so the rule holds over the whole tree:

| File | What it is |
|---|---|
| `CLAUDE.md` | A symlink to `AGENTS.md`. It is the same file, not a second manual. |
| `.github/PULL_REQUEST_TEMPLATE.md` | GitHub tooling; owns no content. |
| `assets/brand/FONT_PROVENANCE.md` | Licence and provenance for the repository-owned type. |
| `conformance/p1140f/REPAIR_HEAD_REVIEW.md` | The P-1140F repair-head review record. |

## Machine-readable authorities

`packages/schemas/` and adjacent conformance registries own planning contracts for:

- VibeProof CDDL and exact vectors;
- adapter manifests, source observations and normalized accounting;
- accounting profiles, pricing interpretations and evidence policy;
- device lineage and privacy egress;
- local IPC and social/integrity events;
- OpenAPI and PostgreSQL planning schema;
- state machines, platform profiles, ranking views, sealed ranking generations, release sets and export manifests;
- erasure records, tombstones and restore receipts, and the data-disposition registry;
- reason codes, policy defaults and observability allowlists.

Required but not-yet-present machine contracts are explicitly listed as `planned-missing` in `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`. These include source receipts, evidence bundles, verifier appraisal results, compatibility tuples, certification results/lifecycle, account consolidation, fork resolution, local persistence, notification delivery aggregates, per-device deletion receipts, TUF client state, compatibility/migration graphs and other blocked owners.

No agent may invent those semantics directly in product code.

## Evidence classification

- **Specification** — intended behavior without runtime proof.
- **Mock** — static or illustrative artifact.
- **Runnable prototype** — executable exploratory work using fixtures or incomplete contracts.
- **Production implementation** — integrated code satisfying accepted contracts.
- **Executable evidence** — reproducible conformance, security, benchmark or operational evidence for a specific claim.

Structural validation is not semantic review. Semantic review is not runtime proof. A prototype is not product implementation. Empty or expired certification is not support evidence.

## Accepted ADRs

Every accepted ADR, with the path a reader can follow. ADRs are cited by identifier
throughout this repository and were previously linked by path from nowhere, so a
reader who met `ADR-004` in prose had no way to reach the document short of guessing
its filename. `scripts/repository/validate_cross_references.py` now requires every
file in `docs/decisions/` to be reachable by path from this table.

| ADR | Owns | Path |
|---|---|---|
| ADR-001 | Local-first development | `docs/decisions/ADR-001-LOCAL-FIRST-DEVELOPMENT.md` |
| ADR-002 | Deliberate Polyglot Production Stack | `docs/decisions/ADR-002-POLYGLOT-PRODUCTION-STACK.md` |
| ADR-003 | Platform Isolation, Authentication, Ranking, and Release Verification | `docs/decisions/ADR-003-PLATFORM-SECURITY_AUTH_AND_RANKING.md` |
| ADR-004 | Protocol Libraries, Local IPC, Pricing Provenance, and Abuse Controls | `docs/decisions/ADR-004-LIBRARIES_IPC_PRICING_AND_ABUSE.md` |
| ADR-005 | Decision-Closing Research and Beta Gates | `docs/decisions/ADR-005-DECISION-CLOSING-RESEARCH.md` |
| ADR-006 | Identity and Native Authorization | `docs/decisions/ADR-006-IDENTITY_AND_NATIVE_AUTH.md` |
| ADR-007 | Batch Challenge and Sequence Recovery | `docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md` |
| ADR-008 | Handle Normalization and Policy Registry | `docs/decisions/ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md` |
| ADR-009 | Licensing and Contribution Model | `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` |
| ADR-010 | Always-on daemon lifecycle | `docs/decisions/ADR-010-ALWAYS_ON_DAEMON_LIFECYCLE.md` |
| ADR-011 | Universal platform support baseline | `docs/decisions/ADR-011-UNIVERSAL_PLATFORM_SUPPORT_BASELINE.md` |
| ADR-012 | Optional privileged machine-wide supervision | `docs/decisions/ADR-012-OPTIONAL_PRIVILEGED_SUPERVISION.md` |
| ADR-013 | Mandatory automatic updates | `docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md` |
| ADR-014 | Prototype visual-validation automation | `docs/decisions/ADR-014-PROTOTYPE_VISUAL_VALIDATION_AUTOMATION.md` |
| ADR-015 | Session authentication | `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md` |
| ADR-016 | Provider-attested organization evidence | `docs/decisions/ADR-016-PROVIDER_ATTESTED_ORG_EVIDENCE.md` |
| ADR-017 | Hosting region and residency | `docs/decisions/ADR-017-HOSTING_REGION_AND_RESIDENCY.md` |
| ADR-018 | Database and migration tooling | `docs/decisions/ADR-018-DATABASE_AND_MIGRATION_TOOLING.md` |
| ADR-019 | Accepted residual risks | `docs/decisions/ADR-019-ACCEPTED_RESIDUAL_RISKS.md` |
| ADR-020 | Confidence-weighted ranking | `docs/decisions/ADR-020-CONFIDENCE_WEIGHTED_RANKING.md` |
| ADR-021 | Public-by-default leaderboard, and the risk the owner accepted | `docs/decisions/ADR-021-PUBLIC_BY_DEFAULT_RISK_ACCEPTANCE.md` |
| ADR-022 | Erasure by cryptographic tombstone and key destruction | `docs/decisions/ADR-022-ERASURE_BY_KEY_DESTRUCTION.md` |

The numbering gap at ADR-015 is closed. Every ADR from ADR-001 to ADR-022 exists.

## Research

`docs/research/README.md` is the sole research entrypoint. Research may inform an open decision or repair but never overrides accepted decisions, normative contracts or the technical-specification inventory.

## Generated and historical artifacts

`docs/history/` holds superseded point-in-time reports. Nothing in it is authority; it is retained so retracted conclusions stay visible rather than disappear. Do not cite it to justify a decision or close a finding.

Repository metadata under `artifacts/repository/`, story captures, old completion reports, stale review packets and stale branches are non-authoritative. Storybook captures are prototype evidence only. Later executable Rust/Go protocol/accounting code remains prototype-only where it contradicts the normative VibeProof authority.

## Duplication and completeness rules

A concept has one normative owner. When duplicates exist, merge unique content into that owner, repair references, and mark or remove the duplicate.

Every technical specification must be represented in `SCHEMA_AND_INTERFACE_INVENTORY.md`. Every mutable concept must have one lifecycle and persistence owner. Every future implementation unit must trace back to an accepted decision and repaired specification. Every public support or launch claim must trace forward to executable evidence.