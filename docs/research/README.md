# VibeMaxxing Research Index

Research is evidence, not product authority. Accepted decisions and repaired normative contracts always win when conclusions conflict.

## Current decision-grade research

| Report | Purpose | Owning decisions/contracts |
|---|---|---|
| `ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md` | current primary-source research on deterministic anti-cheat, attestation, replay, cloning, OAuth, local SLM feasibility, desktop services and release provenance | D-049–D-060; P-1140B–E; privacy, evidence, VibeProof, native, identity and release contracts |

Its derived engineering input is `docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md`. That file is not a parallel roadmap: its unique content must flow into the canonical implementation handoff and PR-sized work breakdown.

## Historical research set

The earlier July 2026 audits are retained as historical evidence:

| Report | Classification | Current owners |
|---|---|---|
| `RESEARCH_AUDIT_2026-07.md` | incorporated; partially superseded | ADR-002, stack contracts, performance budgets |
| `RESEARCH_AUDIT_2026-07_WAVE2.md` | incorporated; partially superseded | privacy, platform isolation, IPC, operations |
| `RESEARCH_AUDIT_2026-07_WAVE3.md` | incorporated; partially superseded | accounting, adapters, ranking |
| `RESEARCH_AUDIT_2026-07_WAVE4.md` | incorporated; partially superseded | ADR-005, VibeProof, adapter registry, operations |
| `RESEARCH_AUDIT_2026-07_WAVE5.md` | incorporated; partially superseded | planning controls and implementation handoff |

Superseded conclusions include passkey-first authentication, a three-adapter public target, countries as a launch requirement, an SLM as a possible launch dependency, unresolved public-launch scope, Rust server recommendations and any assumption that planning artifacts prove implementation.

## Research workflow

Do not create additional numbered research waves.

For a new research question:

1. identify the exact decision, contract section or implementation blocker;
2. search this directory and the decision register for existing evidence;
3. verify unstable facts with current primary sources;
4. record conclusions in the owning decision/ADR/contract;
5. add a short provenance entry here only when evidence needs durable attribution;
6. define implementation/conformance evidence needed to validate it.

Research must not duplicate product specifications, roadmaps, implementation handoffs or task catalogs.

## Evidence boundary

Provider, standard, library, platform, pricing and ecosystem facts must be reverified when they may have changed. Documentation alone never certifies an adapter, platform, dependency, detector or release path; executable conformance evidence is required.