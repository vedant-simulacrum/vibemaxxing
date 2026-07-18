# VibeMaxxing Research Index

Research is evidence, not product authority. Accepted ADRs and normative contracts always win when conclusions conflict.

## Historical research set

The July 2026 research audits are retained as historical evidence only:

| Report | Classification | Current owners |
|---|---|---|
| `RESEARCH_AUDIT_2026-07.md` | incorporated; partially superseded | ADR-002, stack contracts, performance budgets |
| `RESEARCH_AUDIT_2026-07_WAVE2.md` | incorporated; partially superseded | privacy, platform isolation, IPC, operations |
| `RESEARCH_AUDIT_2026-07_WAVE3.md` | incorporated; partially superseded | accounting, adapters, ranking |
| `RESEARCH_AUDIT_2026-07_WAVE4.md` | incorporated; partially superseded | ADR-005, VibeProof, adapter registry, operations |
| `RESEARCH_AUDIT_2026-07_WAVE5.md` | incorporated; partially superseded | planning controls and implementation handoff |

Superseded conclusions include passkey-first authentication, a three-adapter public target, unresolved public-launch scope, Rust server recommendations, and any assumption that planning artifacts prove implementation.

## Research workflow

Do not create additional numbered research waves.

For a new research question:

1. identify the exact decision, contract section, or implementation blocker;
2. search this directory and the decision register for existing evidence;
3. verify unstable facts with current primary sources;
4. record the result directly in the owning ADR or normative contract;
5. add a short provenance entry here only when the evidence needs durable attribution;
6. define the implementation/conformance evidence needed to validate it.

Research must not duplicate product specifications, roadmaps, implementation plans, or task catalogs.

## Evidence boundary

Provider, standard, library, platform, pricing, and ecosystem facts must be reverified when they may have changed. Documentation alone never certifies an adapter, platform, dependency, detector, or release path; executable conformance evidence is required.
