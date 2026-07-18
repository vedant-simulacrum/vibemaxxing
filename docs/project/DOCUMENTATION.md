# VibeMaxxing Documentation Map

This is the only canonical map of repository documentation. Do not create competing indexes, start prompts, master-context files, duplicate roadmaps, or duplicate research waves.

## Initialization

1. `AGENTS.md` — repository initialization, phase gate, thread handling, dependency policy, and completion rules.
2. `docs/project/PROJECT.md` — authoritative product, privacy, topology, stack, and authority.
3. `docs/project/STATUS.md` — current phase, readiness, automation state, and allowed work.
4. `docs/planning/DECISION_REGISTER.md` — accepted, provisional, superseded, and conditional decisions.
5. `docs/planning/TASK_CATALOG.md` — completed planning groups and evidence-gated future tasks.
6. Relevant accepted ADRs and normative subsystem contracts.
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `PR_SIZED_WORK_BREAKDOWN.md` only after explicit implementation approval.

## Normative subsystem contracts

### Product

- `docs/planning/PRODUCT_SCOPE_FREEZE.md`
- `docs/product/PRODUCT_SPEC.md`
- `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`

### Architecture and protocol

- `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
- `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
- `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
- accepted ADRs in `docs/decisions/`

### Security and privacy

- `docs/privacy/PRIVACY_CONTRACT.md`
- `docs/security/THREAT_MODEL.md`
- `docs/security/INTEGRITY_MODEL.md`
- `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- `docs/security/ANTI_CHEAT_RESEARCH_PROGRAM.md`
- `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`
- `docs/security/ADVERSARIAL_TABLETOPS.md`

### Operations and quality

- `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
- `docs/evals/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md`
- `docs/qa/ACCEPTANCE_GATES.md`
- `docs/reviews/INDEPENDENT_ARCHITECTURE_REVIEWS.md`

## Planning evidence

`docs/planning/` contains distinct planning evidence, not competing product specifications:

- `DECISION_REGISTER.md` — material decisions and reopen conditions.
- `TASK_CATALOG.md` — planning completion and future gates.
- `TRACEABILITY_AND_DRY_RUN_AUDIT.md` — requirement-to-contract traceability.
- `SCHEMA_AND_INTERFACE_INVENTORY.md` — authoritative schema ownership inventory.
- `PROVISIONAL_DEFAULTS_AND_REVERSAL_THRESHOLDS.md` — implementation defaults where measured evidence may later reverse a choice.
- `MOCK_IMPLEMENTATION_HANDOFF_REVIEW.md` — context-free handoff test.
- `FINAL_PLANNING_EXIT_AUDIT.md` — final planning result.

## Implementation planning

There are exactly two implementation-planning documents:

- `docs/implementation/IMPLEMENTATION_HANDOFF.md` — single build-order and ownership contract.
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` — granular dependency-ordered work units.

Do not create another roadmap, build plan, execution master plan, or implementation checklist. Add missing behavior to the owning subsystem contract; add execution detail to the work breakdown.

## Research

`docs/research/README.md` is the only research entrypoint. Numbered July 2026 research reports are retained as incorporated, partially superseded historical evidence.

Do not create new numbered research waves. Resolve a current question in the owning ADR or normative contract and add provenance to the research README only when durable attribution is needed.

## Machine-readable planning artifacts

- `conformance/adapters/agent-registry-v1.json`
- `conformance/adversarial/anti-cheat-registry-v1.json`
- schemas, suites, fixtures, and benchmark definitions under `conformance/`, `evals/`, and `benchmarks/`.

## Generated repository metadata

`scripts/repository/generate_repository_metadata.py` writes generated inventory and checksum files under `artifacts/repository/`. Generated metadata is never an authority for product behavior.

## Implementation areas

- `crates/` — Rust native and VibeProof components.
- `apps/api/` — Go online services.
- `apps/web/` — Next.js web product.
- `packages/` — schemas, generated clients, UI, and configuration.

## Duplication rule

A concept has exactly one normative owner. Other documents link to it rather than restating it.

When consolidating:

1. choose the normative owner;
2. merge unique content into that owner;
3. update all surviving links;
4. delete the duplicate;
5. record material behavioral changes in the decision register and an ADR where required.
