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
9. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
10. relevant ADRs, normative contracts, schemas, registries and fixtures
11. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` only for planning future work or after explicit P-1104 authorization

Run `python3 scripts/repository/doctor.py` from a clean checkout before relying on repository state.

## Current authority note

P-1140F owns all open semantic findings, and all 13 remain open. P-1104 is `authorized-open` as of 2026-08-05 by owner decision, recorded in `conformance/p1140f/gate-authorization-v1.json` and GitHub issue 44. It was opened with its preconditions unmet; the findings are tracked and not waived, and authorization is a decision rather than evidence that anything is implemented, secure, or launch-ready.

Gate and finding state are owned by `conformance/p1140f/*.json`. This note summarizes them and may not redefine them — if the two disagree, the registries win and this paragraph is the defect.

The earlier four-finding review is superseded by the current consolidated semantic register.

The technical-specification completeness authority is `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`. A concept is not planning-complete merely because prose mentions it; the inventory must name its normative owner, machine owner or planned path, lifecycle/persistence owner, repair dependency, implementation dependency and evidence gate.

## Normative owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Documentation hierarchy: this file
- Decision authority: `docs/planning/DECISION_REGISTER.md`, `docs/decisions/`
- Task and gate state: `docs/planning/TASK_CATALOG.md`
- Technical-specification inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Structural review: `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
- Semantic review: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Adapter stages and VibeProof boundary: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- VibeProof wire/state protocol: `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `packages/schemas/vibeproof-claim-v1.cddl`
- Authoritative mutable state and platform behavior: `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`, ADR-015
- Ranking computation and the credited-score model: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`, ADR-020
- Accepted residual risks without a normative owner: ADR-019
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010 through ADR-013
- Operations/release/open source: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, ADR-013
- Hosting region, data residency and provider selection: ADR-017
- Database and migration tooling: ADR-018
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
| `planning/` | Decisions, gates, scope, policy | `DECISION_REGISTER.md`, `TASK_CATALOG.md`, `SCHEMA_AND_INTERFACE_INVENTORY.md`, `ARTIFACT_POLICY.md`, `PRODUCT_SCOPE_FREEZE.md`, `REPOSITORY_OPERATIONS.md`, `PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md`, `P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, `P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`, `CROSS_PLATFORM_COMPLETENESS_AUDIT.md`, `ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md`, `decision-traceability/` (D-001..D-069 + `README.md`) |
| `decisions/` | Accepted ADRs | `ADR-001` … `ADR-020` |
| `architecture/` | System contracts, including the canonical wire profile | `VIBEPROOF_V1_PROTOCOL.md`, `VIBEPROOF_V1_CANONICAL_PROFILE.md`, `ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `NATIVE_CLIENT_AND_DAEMON.md`, `LEADERBOARD_STORAGE_AND_RANKING.md`, `PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `ARCHITECTURE.md` |
| `product/` | Product surface and metrics | `PRODUCT_SPEC.md`, `ACCOUNTING_AND_TIME_CONTRACT.md`, `TOKEN_ACCOUNTING_SPEC.md`, `CASH_BURN_PRICING_PROVENANCE.md`, `SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, `ONBOARDING_AND_PRIVACY_VERIFICATION.md`, `METRICS.md`, `SOCIAL_RANKING_AND_ABUSE_RESEARCH.md` |
| `privacy/` | **The boundary.** The invariant everything else serves | `PRIVACY_CONTRACT.md`, `PRIVACY_PRESERVING_USAGE_EVIDENCE.md` |
| `security/` | Threat, integrity, attestation, abuse | `THREAT_MODEL.md`, `INTEGRITY_MODEL.md`, `EVIDENCE_AND_ATTESTATION_PROFILES.md`, `AUTHENTICATION_AND_RECOVERY.md`, `RANKED_IDENTITY_ELIGIBILITY.md`, `ANTI_CHEAT_ATTACK_CATALOG.md`, `ANTI_CHEAT_RESEARCH_PROGRAM.md`, `ADVERSARIAL_TABLETOPS.md`, `LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `PLATFORM_ISOLATION.md`, `ABUSE_AND_COUNTRY_PRIVACY.md` |
| `integrations/` | Agent compatibility and certification | `UNIVERSAL_AGENT_COMPATIBILITY.md`, `ADAPTER_CERTIFICATION_POLICY.md`, `AGENT_INTEGRATION_RESEARCH_MATRIX.md`, `T20_CERTIFICATION_AND_SELECTION_SPEC.md`, `T20_MODEL_HARDENING_CONTRACT.md` |
| `operations/` | Launch, running, recovery | `OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, `RELEASE_VERIFICATION.md`, `PRODUCTION_READINESS.md`, `COMPETITIVE_BETA_GATE.md`, `INCIDENT_RESPONSE.md`, `SLOS_AND_ALERTS.md`, `OBSERVABILITY_PRIVACY.md`, `DATA_LIFECYCLE_AND_RECOVERY.md` |
| `implementation/` | Work decomposition | `IMPLEMENTATION_HANDOFF.md`, `PR_SIZED_WORK_BREAKDOWN.md`, `ISSUE_GENERATION.md`, `REPOSITORY_LAYOUT.md` |
| `engineering/` | Engineering standards and budgets | `ENGINEERING_SYSTEM.md`, `PERFORMANCE_BUDGETS.md`, `COLLECTOR_PERFORMANCE_AND_POWER.md` |
| `verification/` | Acceptance gates, evaluation, benchmark and evidence protocol | `ACCEPTANCE_GATES.md`, `EVAL_SYSTEM.md`, `BENCHMARK_AND_EVIDENCE_PROTOCOLS.md` |
| `style-guide/` | UI system and brand, owned by `packages/ui` | `README.md` (entry point), `BRAND.md`, `UI_FOUNDATIONS.md`, `UI_ARCHITECTURE.md`, `COMPONENT_STANDARD.md`, `COMPONENT_INVENTORY.md`, `AI_UI_RULES.md`, `ASSET_SYSTEM.md`, `LEADERBOARD_FIRST_BASELINE.md`, `LEADERBOARD_BENTO_BASELINE.md`, `MIGRATION.md`, `RESEARCH.md`, `references/` (approved captures) |
| `research/` | Primary evidence, historical | `README.md` (sole entrypoint), `RESEARCH_AUDIT_2026-07{,_WAVE2..5}.md`, `ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md` |
| `history/` | **Non-authoritative.** Superseded reports | See `docs/history/README.md` |

### Small directories, with reasons

`privacy/` (2 files) is deliberately isolated: it holds the invariant the whole system exists to serve, and burying it inside `security/` would make it look like one control among many. `project/` (3) is the top authority and must stay at a short, obvious path. `engineering/` (3) and `verification/` (3) are coherent single subjects with room to grow and no better host. No other directory under `docs/` holds fewer than four files.

### Structural changes on 2026-08-06

- `protocol/` folded into `architecture/`; `qa/` and `evals/` combined into `verification/`; `design/` folded into `style-guide/`.
- `style-guide/ARCHITECTURE.md` renamed to `style-guide/UI_ARCHITECTURE.md` so it can no longer be confused with `architecture/ARCHITECTURE.md`.
- `style-guide/COMPONENTS.md` merged into `COMPONENT_INVENTORY.md`; `design/design.md` merged into `style-guide/UI_FOUNDATIONS.md`.
- `planning/REPOSITORY_ALIGNMENT_2026-07-23.md` and `planning/MACHINE_CONTRACT_REPAIR_SPEC.md` archived to `history/`.

Known duplication that genuinely remains, recorded rather than silently carried. Each cluster needs a single owner chosen and the rest merged or marked:

- Anti-cheat material spans `research/ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md`, `planning/ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md`, `security/ANTI_CHEAT_ATTACK_CATALOG.md`, `security/ANTI_CHEAT_RESEARCH_PROGRAM.md`, and `security/ADVERSARIAL_TABLETOPS.md`.
- `style-guide/COMPONENT_INVENTORY.md` records an unresolved naming overlap between the proposed generic `Notice`/`Dialog` and the implemented `ProductNotice`/`ProductDialog`. An owner must decide whether these are one concept or two.
- `style-guide/UI_FOUNDATIONS.md` §17 records the token, radius, type-scale, motion and logo values on which the retired `design.md` disagreed with `BRAND.md`. The approved column governs; the disagreement is kept visible rather than deleted.

## Machine-readable authorities

`packages/schemas/` and adjacent conformance registries own planning contracts for:

- VibeProof CDDL and exact vectors;
- adapter manifests, source observations and normalized accounting;
- accounting profiles, pricing interpretations and evidence policy;
- device lineage and privacy egress;
- local IPC and social/integrity events;
- OpenAPI and PostgreSQL planning schema;
- state machines, platform profiles, ranking views, release sets and export manifests;
- reason codes, policy defaults and observability allowlists.

Required but not-yet-present machine contracts are explicitly listed as `planned-missing` in `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`. These include source receipts, evidence bundles, verifier appraisal results, compatibility tuples, certification results/lifecycle, account consolidation, fork resolution, local persistence, ranking generations and contributions, notification delivery aggregates, deletion plans/tombstones, TUF client state, compatibility/migration graphs and other blocked owners.

No agent may invent those semantics directly in product code.

## Evidence classification

- **Specification** — intended behavior without runtime proof.
- **Mock** — static or illustrative artifact.
- **Runnable prototype** — executable exploratory work using fixtures or incomplete contracts.
- **Production implementation** — integrated code satisfying accepted contracts.
- **Executable evidence** — reproducible conformance, security, benchmark or operational evidence for a specific claim.

Structural validation is not semantic review. Semantic review is not runtime proof. A prototype is not product implementation. Empty or expired certification is not support evidence.

## Current important ADRs

- ADR-008 and ADR-009 remain accepted.
- ADR-010 owns always-on daemon lifecycle.
- ADR-011 owns candidate platform scope.
- ADR-012 owns optional privileged supervision.
- ADR-013 owns mandatory automatic updates.
- ADR-014 owns bounded prototype visual validation.
- ADR-015 owns the session authentication scheme, including token format, refresh rotation, revocation, device binding and the OAuth authorization-exchange requirements.
- ADR-016 owns provider-attested organization evidence.
- ADR-017 owns hosting region and data residency, and the provider selection procedure.
- ADR-018 owns the database and migration tooling, and the executable form of the expand-and-contract migration policy.
- ADR-019 is the register for accepted residual risks that no normative owner has adopted.
- ADR-020 owns confidence-weighted ranking, the discount function and the raw-versus-credited vocabulary.

The numbering gap at ADR-015 is closed. Every ADR from ADR-001 to ADR-020 exists.

## Research

`docs/research/README.md` is the sole research entrypoint. Research may inform an open decision or repair but never overrides accepted decisions, normative contracts or the technical-specification inventory.

## Generated and historical artifacts

`docs/history/` holds superseded point-in-time reports. Nothing in it is authority; it is retained so retracted conclusions stay visible rather than disappear. Do not cite it to justify a decision or close a finding.

Repository metadata under `artifacts/repository/`, story captures, old completion reports, stale review packets and stale branches are non-authoritative. Storybook captures are prototype evidence only. Later executable Rust/Go protocol/accounting code remains prototype-only where it contradicts the normative VibeProof authority.

## Duplication and completeness rules

A concept has one normative owner. When duplicates exist, merge unique content into that owner, repair references, and mark or remove the duplicate.

Every technical specification must be represented in `SCHEMA_AND_INTERFACE_INVENTORY.md`. Every mutable concept must have one lifecycle and persistence owner. Every future implementation unit must trace back to an accepted decision and repaired specification. Every public support or launch claim must trace forward to executable evidence.