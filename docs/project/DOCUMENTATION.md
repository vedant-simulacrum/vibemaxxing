# VibeMaxxing Documentation Map

This is the sole canonical map. Do not create competing indexes, start prompts, master-context files, duplicate roadmaps or numbered research waves.

## Initialization

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. this file
5. `docs/planning/DECISION_REGISTER.md`
6. `docs/planning/TASK_CATALOG.md`
7. relevant ADRs, schemas and subsystem contracts
8. implementation handoff only for implementation planning or after explicit approval

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Normative product and architecture

- Scope and product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Social/integrity/UX: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
- Adapter and VibeProof: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
- Platform key/privilege boundary: `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`
- Server/data/ranking: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
- Privacy/security: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- Operations/launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
- Accepted decisions: `docs/decisions/`

Important edge decisions:

- `ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md`
- `ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md`
- `ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md`

## Authoritative planning-grade schemas

`packages/schemas/` owns:

- `adapter-manifest.schema.json`
- `normalized-event.schema.json`
- `vibeproof-claim-v1.cddl`
- `local-control-v1.proto`
- `openapi-v1.yaml`
- `planning-schema.sql`
- `reason-codes-v1.json`
- `policy-defaults-v1.json`
- `observability-allowlist-v1.yaml`

These are validated planning-grade interfaces, not implemented production artifacts. The previously recorded planning workflow passed schema, OpenAPI, CDDL, Protobuf and PostgreSQL DDL checks; any changed interface requires renewed validation before targeted hardening can close.

## Machine registries

- Adapter compatibility: `conformance/adapters/agent-registry-v1.json` and adjacent schema.
- T20 model hardening: `conformance/models/t20-model-registry-v1.json` and adjacent schema.
- Adversarial cases: `conformance/adversarial/anti-cheat-registry-v1.json` and adjacent schema.

An empty certification list means no product-level support claim. Registry status `planned` or `prelaunch-pending` is not executable evidence.

## Planning control and evidence

- Decisions: `docs/planning/DECISION_REGISTER.md`
- Tasks and gates: `docs/planning/TASK_CATALOG.md`
- Traceability: `docs/planning/TRACEABILITY_AND_DRY_RUN_AUDIT.md`
- Schema inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Defaults/reversal: `docs/planning/PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md`
- Handoff review: `docs/planning/MOCK_IMPLEMENTATION_HANDOFF_REVIEW.md`
- Validated broad hardening evidence: `docs/planning/PLANNING_HARDENING_VALIDATION_REPORT.md`
- Historical exit audit: `docs/planning/FINAL_PLANNING_EXIT_AUDIT.md`; historical conclusions do not override current D-045/D-046 targeted reopen status.
- Current targeted hardening thread: GitHub issue #12 and P-1130A through P-1130E.

## Artifact maturity

The authoritative maturity taxonomy is in `docs/project/STATUS.md` and D-047. Specifications, mocks, runnable prototypes, production implementation and executable evidence are distinct. `apps/web` is a bounded fixture-backed runnable prototype unless a later accepted phase decision changes that classification.

## Implementation planning

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`: build-order contract.
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`: bounded implementation units.
- `docs/implementation/REPOSITORY_LAYOUT.md`: current versus approved future tree.
- `docs/implementation/ISSUE_GENERATION.md`: deterministic issue-thread contract.

Do not create another roadmap or build plan.

## Research

`docs/research/README.md` is the sole research entrypoint. Historical reports never override accepted decisions or normative contracts.

## Generated artifacts

Repository metadata and issue plans are generated under `artifacts/repository/` and are non-authoritative. Generators live under `scripts/repository/`.

## Duplication rule

A concept has one normative owner. Merge unique content into that owner, repair all links, delete the duplicate and record material changes through the decision register and an ADR when needed.
