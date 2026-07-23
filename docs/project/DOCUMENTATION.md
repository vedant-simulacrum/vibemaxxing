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

Historical reports that declare planning complete are retained as history and do not override the July 23 status, decision register, alignment audit, machine-contract repair specification, decision traceability or platform completeness audit.

Where a contract conflicts with an accepted July 23 decision, the decision is authoritative and the dependent contract/schema is blocked until its P-1140 repair task closes.

## Normative product and architecture owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Repository reconciliation: `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- Exact machine-contract target: `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- Decision-to-code/platform/evidence mapping: `docs/planning/decision-traceability/`
- Cross-platform capability and release gates: `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`, subject to D-052 country removal
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`, blocked for P-1140B/D repairs
- Social/integrity/UX: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, blocked for P-1140D repairs and country removal
- Adapter and VibeProof: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`, blocked for P-1140B/C rewrite
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, blocked where certification is not digest/provenance bound
- T20 planning: `docs/integrations/T20_MODEL_HARDENING_CONTRACT.md`, `docs/integrations/T20_CERTIFICATION_AND_SELECTION_SPEC.md`; D-046 is provisional pending P-1140B/E
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010, blocked for typed IPC, lineage, updater and exercised platform-state evidence
- Server/data/ranking: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, blocked for P-1140C/D
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
- Operations/launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, subject to P-1140D release/updater repair and D-052/D-053
- Accepted decisions: `docs/decisions/` and `docs/planning/DECISION_REGISTER.md`

Important edge decisions:

- `ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md` is provisional in effect where P-1140C finds contradictions.
- `ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md` remains accepted.
- `ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` remains accepted.
- `ADR-010-ALWAYS_ON_DAEMON_LIFECYCLE.md` is accepted and owns D-061.

## Authoritative planning-grade schemas

`packages/schemas/` currently owns draft planning interfaces:

- `adapter-manifest.schema.json`
- `normalized-event.schema.json`
- `vibeproof-claim-v1.cddl`
- `local-control-v1.proto`
- `openapi-v1.yaml`
- `planning-schema.sql`
- `reason-codes-v1.json`
- `policy-defaults-v1.json`
- `observability-allowlist-v1.yaml`

These are not implemented or production-proven artifacts.

Until P-1140B–E close:

- `adapter-manifest.schema.json` is blocked by mutable version naming, provider-receipt language and missing artifact/provenance/certification digests;
- `normalized-event.schema.json` is blocked by provider-receipt, unrestricted metadata, raw alias and timing issues;
- `vibeproof-claim-v1.cddl` is blocked by client evidence-state, pricing, extension, checkpoint, batch, correction and rotation issues;
- `local-control-v1.proto` is blocked where it transports opaque JSON/bytes and lacks typed message sequence/deadline/process-role fields;
- `openapi-v1.yaml` is blocked by generic resources, base64 CBOR, country endpoints, browser-renewed presence, server-claimed local deletion and missing authorization/idempotency/rate semantics;
- `planning-schema.sql` is blocked by missing token families, lineages, appraisals, receipts, idempotency ledger, ranking views, typed social state and release/update facts;
- reason codes and defaults remain provisional where the owning state machine is unresolved.

No generated production types should be based on a blocked schema.

## Machine registries and conformance planning

- Adapter compatibility: `conformance/adapters/agent-registry-v1.json` and adjacent schema.
- Adversarial cases: `conformance/adversarial/anti-cheat-registry-v1.json` and adjacent schema.
- T20 model registry: `conformance/models/t20-model-registry-v1.json` and adjacent schema.
- T20 quantitative optimization evidence: `conformance/models/t20-optimization-evidence-v1.schema.json`.
- T20 planning fixtures: `conformance/models/fixtures/`.
- T20 planning validator: `scripts/repository/validate_t20_contract.py`.

An empty certification list means no product-level support claim. Registry status `planned` or `prelaunch-pending` is not executable evidence. Certification must ultimately bind exact artifact digests, provenance, source versions, platform/mode and immutable conformance result bundles.

## Planning control and evidence

- Decisions: `docs/planning/DECISION_REGISTER.md`
- Tasks and gates: `docs/planning/TASK_CATALOG.md`
- Alignment audit: `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- Machine-contract target: `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- Complete decision traceability: `docs/planning/decision-traceability/`
- Cross-platform completeness and open scope questions: `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- Consolidated findings: `docs/planning/CONSOLIDATED_AUDIT_2026-07-23.md`
- Launch policy decisions: `docs/planning/PUBLIC_LAUNCH_POLICY_DECISIONS_2026-07-23.md`
- Anti-cheat implementation input: `docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md`
- Historical traceability audit: `docs/planning/TRACEABILITY_AND_DRY_RUN_AUDIT.md`
- Schema inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Defaults/reversal: `docs/planning/PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md`
- Historical completion records: retained as evidence of prior work but superseded where current status/audits conflict.

## Implementation planning

Only these are canonical for future build execution:

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`
- `docs/implementation/REPOSITORY_LAYOUT.md`
- `docs/implementation/ISSUE_GENERATION.md`

The anti-cheat implementation plan, decision traceability and cross-platform completeness audit are normative inputs to the canonical handoff/work breakdown. Do not create another roadmap or build plan.

## Research

`docs/research/README.md` is the sole research entrypoint. Current anti-cheat evidence is `docs/research/ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md`.

Research informs decisions but never overrides accepted decisions or repaired normative contracts.

## Generated artifacts

Repository metadata and issue plans under `artifacts/repository/` are non-authoritative. Generators live under `scripts/repository/`.

## Duplication rule

A concept has one normative owner. Merge unique content into that owner, repair all links, delete or clearly mark the duplicate and record material changes through the decision register and an ADR when needed.
