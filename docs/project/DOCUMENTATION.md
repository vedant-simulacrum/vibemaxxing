# VibeMaxxing Documentation Map

This is the only canonical map of repository documentation. Do not create competing indexes, start prompts, master-context files, or duplicate roadmaps.

## Initialization

1. `AGENTS.md` — initialization, phase gate, repository/thread/dependency rules.
2. `docs/project/PROJECT.md` — product, privacy, stack, topology, and authority.
3. `docs/project/STATUS.md` — current phase, readiness, and allowed work.
4. `docs/planning/DECISION_REGISTER.md` — accepted, provisional, superseded, and conditional decisions.
5. `docs/planning/TASK_CATALOG.md` — planning and implementation gates.
6. `docs/implementation/IMPLEMENTATION_HANDOFF.md` — build order and no-invention rules.
7. `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` — dependency-ordered implementation units.

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

Planning evidence is maintained under `docs/planning/`:

- traceability and dry-run audit;
- schema/interface inventory;
- provisional defaults and reversal thresholds;
- mock implementation handoff review;
- final planning-exit audit;
- dependency map and task catalog.

These documents validate planning completeness but do not override normative subsystem contracts.

## Research

`docs/research/` contains evidence and historical research. `docs/research/RESEARCH_PROVENANCE_INDEX.md` classifies research as current, incorporated, partially superseded, or historical.

Research is never an authority when an accepted ADR or normative contract exists. Do not produce a new research wave when an existing question can be appended to the provenance index and resolved in the relevant contract or ADR.

## Machine-readable planning artifacts

- `conformance/adapters/agent-registry-v1.json`
- `conformance/adversarial/anti-cheat-registry-v1.json`
- existing schemas, suites, fixtures, and benchmark definitions under `conformance/`, `evals/`, and `benchmarks/`.

## Implementation areas

- `crates/`: Rust native and VibeProof components.
- `apps/api/`: Go online services.
- `apps/web/`: Next.js web product.
- `packages/`: shared schemas, generated clients, UI, and configuration.

## Duplication rule

A concept has exactly one normative home. Other documents link to it rather than restating it. When consolidation is required:

1. choose the normative owner;
2. merge unique content into that owner;
3. update links;
4. delete the duplicate;
5. record any changed decision in the decision register.
