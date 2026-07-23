# VibeMaxxing Documentation Map

This is the sole canonical map. Do not create competing indexes, start prompts, master-context files, duplicate roadmaps or numbered research waves.

## Initialization

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. this file
5. `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
6. `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
7. `docs/planning/decision-traceability/README.md`
8. `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
9. `docs/planning/DECISION_REGISTER.md`
10. `docs/planning/TASK_CATALOG.md`
11. relevant ADRs, contracts and schemas
12. implementation handoff only for implementation planning or after explicit approval

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Current authority note

The repository is in planning contract repair. P-1140A is complete and P-1140B is active.

Historical reports that declare planning complete or platform scope unresolved do not override current project authority, D-062 through D-069, ADR-011 through ADR-014, decision traceability or the frozen cross-platform audit.

Where a contract conflicts with an accepted decision, the decision is authoritative and the dependent contract/schema is blocked until its P-1140 repair task closes.

## Normative product and architecture owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Repository reconciliation: `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- Exact machine-contract target: `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- Decision-to-code/platform/evidence mapping: `docs/planning/decision-traceability/`
- Cross-platform profiles and release gates: `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`, subject to D-052 and D-066
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`, blocked for P-1140B/D repairs
- Social/integrity/UX: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, blocked for P-1140D repairs and country removal
- Adapter and VibeProof: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`, blocked for P-1140B/C rewrite
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, blocked where certification is not digest/provenance/profile bound
- T20 planning: `docs/integrations/T20_MODEL_HARDENING_CONTRACT.md`, `docs/integrations/T20_CERTIFICATION_AND_SELECTION_SPEC.md`; D-046 remains provisional
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010 through ADR-013
- Server/data/ranking: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, blocked for P-1140C/D
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
- Operations/launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, ADR-013, subject to P-1140D release repair
- Prototype visual validation: ADR-014 and `.github/workflows/storyboard-visuals.yml`
- Accepted decisions: `docs/decisions/` and `docs/planning/DECISION_REGISTER.md`

## Important ADRs

- `ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md` is provisional where P-1140C finds contradictions.
- `ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md` remains accepted.
- `ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` remains accepted.
- `ADR-010-ALWAYS_ON_DAEMON_LIFECYCLE.md` owns D-061.
- `ADR-011-UNIVERSAL_PLATFORM_SUPPORT_BASELINE.md` owns D-062 through D-066.
- `ADR-012-OPTIONAL_PRIVILEGED_SUPERVISION.md` owns D-067.
- `ADR-013-MANDATORY_AUTOMATIC_UPDATES.md` owns D-068.
- `ADR-014-PROTOTYPE_VISUAL_VALIDATION_AUTOMATION.md` owns D-069.

## Authoritative planning-grade schemas

`packages/schemas/` currently owns draft planning interfaces:

- `adapter-manifest.schema.json`
- `source-observation.schema.json`
- `normalized-event.schema.json` (`NormalizedAccountingEvent`)
- `local-detector-result.schema.json`
- `accounting-profile.schema.json`
- `device-lineage.schema.json`
- `pricing-interpretation.schema.json`
- `evidence-profile-policy-v1.json`
- `egress-allowlist-v1.schema.json` and `egress-allowlist-v1.json`
- `vibeproof-claim-v1.cddl`
- `local-control-v1.proto`
- `openapi-v1.yaml`
- `planning-schema.sql`
- `reason-codes-v1.json`
- `policy-defaults-v1.json`
- `observability-allowlist-v1.yaml`

These are not implemented or production-proven artifacts.

Until P-1140B–E close:

- adapter manifest, typed local stages, accounting profiles, device lineage, pricing interpretation, evidence policy and claim-egress registry are repaired P-1140B planning contracts; P-1140C owns wire binding and P-1140E owns final cross-validation;
- VibeProof CDDL retains blocked evidence, pricing, checkpoint, batch, correction and rotation issues;
- local Protobuf retains blocked opaque transport and missing process/deadline semantics;
- OpenAPI retains blocked generic resources plus unresolved presence, deletion and authorization semantics;
- planning SQL lacks complete token families, lineages, appraisals, receipts, idempotency, ranking views, typed social and release/update state;
- reason codes/defaults remain provisional where state machines are unresolved.

No generated production types should be based on a blocked schema.

## Machine registries and conformance planning

- Adapter compatibility: `conformance/adapters/agent-registry-v1.json` and adjacent schema.
- Adversarial cases: `conformance/adversarial/anti-cheat-registry-v1.json` and adjacent schema.
- T20 model registry: `conformance/models/t20-model-registry-v1.json` and adjacent schema.
- T20 optimization evidence: `conformance/models/t20-optimization-evidence-v1.schema.json`.
- T20 planning fixtures: `conformance/models/fixtures/`.
- T20 planning validator: `scripts/repository/validate_t20_contract.py`.

An empty certification list means no product-level support claim. Certification must ultimately bind artifact digest, provenance, source version, exact platform tuple, mode and immutable result bundle.

## Planning control and evidence

- Decisions: `docs/planning/DECISION_REGISTER.md`
- Tasks and gates: `docs/planning/TASK_CATALOG.md`
- Alignment audit: `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- Machine-contract target: `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- Complete D-001..D-069 traceability: `docs/planning/decision-traceability/`
- Frozen platform baseline: `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- Consolidated findings: `docs/planning/CONSOLIDATED_AUDIT_2026-07-23.md`
- Launch decisions: `docs/planning/LAUNCH_POLICY_DECISIONS_2026-07-23.md`
- Anti-cheat implementation input: `docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md`
- Historical traceability audit: `docs/planning/TRACEABILITY_AND_DRY_RUN_AUDIT.md`
- Schema inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Defaults/reversal: `docs/planning/PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md`

## Implementation planning

Only these are canonical for future build execution:

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`
- `docs/implementation/REPOSITORY_LAYOUT.md`
- `docs/implementation/ISSUE_GENERATION.md`

The anti-cheat plan, decision traceability, platform audit and ADR-010 through ADR-014 are normative inputs. Do not create another roadmap.

## Research

`docs/research/README.md` is the sole research entrypoint. Research informs decisions but never overrides accepted decisions or repaired contracts.

## Generated artifacts

Repository metadata and issue plans under `artifacts/repository/` are non-authoritative. Storybook captures are short-lived prototype review artifacts under ADR-014.

## Duplication rule

A concept has one normative owner. Merge unique content into that owner, repair links, delete or clearly mark duplicates and record material changes through the decision register and an ADR when needed.
