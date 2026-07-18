# VibeMaxxing Planning Readiness Audit

Updated: 2026-07-19

## Conclusion

The repository is a strong research and specification baseline, but it is not yet fully planning-ready for autonomous implementation. The remaining risk is ambiguity between specification layers, incomplete task decomposition, missing interface-level contracts, and unclear evidence ownership.

The project remains in planning and decision-closing mode. Product implementation must not begin until the planning exit gate is satisfied or the user explicitly changes the phase.

## Strengths

- Stable product thesis, privacy boundary, metrics, evidence language, social direction, and local-first architecture.
- Five ADRs and five research waves covering protocol, platform security, authentication, ranking, pricing, abuse, updater, observability, and operations.
- Honest separation between specifications, prototypes, and unproven production capability.
- Initial conformance fixtures, eval registry, benchmark seed, capability probe, telemetry scanner, and Go health endpoint.

## Priority findings

### P0 — Instruction precedence was inconsistent

`PROJECT_INSTRUCTIONS.md` and `CURRENT_STATUS.md` used different authority orders. `MODEL_OPERATING_MANUAL.md` now defines the canonical order. Root control files must align with it.

### P0 — Planning stage was not enforced everywhere

Some prompts instructed agents to begin implementation immediately. Root prompts must now prohibit product implementation until the user explicitly opens that phase.

### P0 — Roadmap items were not atomic task contracts

The roadmap defines phases, but not every task has a stable ID, dependencies, inputs, outputs, evidence, and blockers. `TASK_CATALOG.md` owns that decomposition.

### P0 — No single dependency graph existed

Ordering was implicit across many files. `DEPENDENCY_MAP.md` now records the critical path and parallel tracks.

### P1 — Decision status was unclear

Accepted decisions, leading candidates, unresolved bakeoffs, and deferred choices were mixed. `DECISION_REGISTER.md` labels each major choice.

### P1 — Core implementation contracts remain incomplete

Planning must still freeze:

- adapter manifests and normalized usage events;
- provider-neutral token accounting and reconciliation;
- signed claim envelope, canonical encoding profile, algorithms, and errors;
- collector-to-sync IPC schemas and state machines;
- device registration, rotation, loss, and revocation;
- ingestion APIs, rejection codes, idempotency, and transaction boundaries;
- SQL schemas for ledger, outbox, aggregates, identity, pricing, social, and moderation;
- ranking, pagination, ties, late events, rebuild, and cache behavior;
- privacy-verification payloads and UI copy;
- native install, update, rollback, and uninstall behavior.

## Domain readiness

| Domain | State | Main gap |
|---|---|---|
| Product and metrics | strong | edge cases and glossary |
| Token accounting | partial | complete normalized semantics |
| Agent adapters | partial | manifest, events, degradation, certification |
| VibeProof | partial | exact schemas, errors, key lifecycle |
| Collector | partial | process, storage, crash consistency |
| IPC and identity | partial | messages and platform state machines |
| Server and ranking | partial | APIs, SQL, transactions, rebuild |
| Authentication and social | partial | complete user and moderation flows |
| Web and design | partial | routes, states, copy, data contracts |
| Release and operations | partial | environments, updater, recovery, promotion |

## Planning exit gate

Implementation may begin only when all are true or explicitly waived:

1. Root instructions share one authority order and phase.
2. Every milestone has atomic task IDs, dependencies, and evidence.
3. Every major choice is in the decision register.
4. Core interfaces, schemas, state machines, limits, and errors are specified.
5. Privacy allowlists exist for every boundary.
6. Threats map to controls and negative tests.
7. Storage, migrations, rebuild, deletion, and recovery are specified.
8. Platform capability and degradation are explicit.
9. Performance, battery, accessibility, and onboarding budgets have test plans.
10. Release, rollback, key rotation, incident, moderation, and appeal flows are specified.
11. CI can detect stale manifests, invalid task links, malformed schemas, and fake evidence.
12. The user explicitly changes the phase to implementation.

## Status

- Continue planning: **go**.
- Begin product implementation: **no-go**.
- Competitive beta: **no-go**.
- Production release: **no-go**.