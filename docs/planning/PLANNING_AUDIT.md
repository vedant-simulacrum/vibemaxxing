# VibeMaxxing Planning Readiness Audit

Updated: 2026-07-19

## Conclusion

The repository is now internally aligned on authority, phase, complete public-launch scope, staged internal delivery, OAuth-first identity with optional stronger factors, tiered universal agent compatibility, native daemon/menu-bar/tray topology, Rust/Go/TypeScript ownership, manual-only planning automation, and the anti-cheat control hierarchy.

The remaining work is no longer primarily contradiction repair. It is genuine specification, research, validation, and implementation-readiness work tracked in `docs/planning/TASK_CATALOG.md`.

The project remains in planning and decision-closing mode. Product implementation must not begin until P-1104 passes and the user explicitly changes the phase.

## Closed P0 discrepancies

- Authority order is consistent across root control files.
- Planning-only phase is enforced in root prompts and roadmaps.
- `PROJECT_CONTEXT.md` now uses the accepted Rust native/protocol + Go server + TypeScript web stack.
- Mandatory passkeys were superseded by GitHub/X OAuth with optional stronger factors.
- Public launch scope is explicitly comprehensive; staged delivery no longer implies a narrow launch MVP.
- Agent support is a tiered living compatibility system rather than a fixed three-agent target.
- Native daemon, CLI, menu-bar/tray, local audit, and hosted-web responsibilities are represented.
- Decision-register status values are normalized and superseded decisions are retained explicitly.
- The old task catalog and dependency map were rebuilt around the full product.
- Stale hand-maintained manifest/checksum outputs were removed from authority and a deterministic generator was added.
- The truncated product-scope file was repaired.
- The anti-cheat catalog is now a populated control matrix with a machine-readable adversarial registry.
- README, start prompt, project prompt, ADR-003, build plan, tech stack, product spec, current status, specification index, and roadmap were reconciled.

## Remaining implementation-grade planning work

### Product and launch

- Complete feature matrix, glossary, user journeys, and milestone/launch gates.
- Exact profiles, usernames, friends, rivals, blocks, boards, organizations, communities, countries, seasons, notifications, moderation, appeals, export, and deletion behavior.

### Accounting and pricing

- Normative Token Burn formula and all provider/local-model edge cases.
- Cross-provider comparability policy.
- Estimated Cash Burn datasets, aliases, subscriptions, credits, regional pricing, local compute, and correction policy.
- Period, timezone, late/offline event, tie, streak, reset, and correction semantics.

### Universal compatibility

- Current machine-readable agent census.
- Adapter manifest and normalized event schemas.
- Source reconciliation, double-count prevention, lifecycle, conformance, community governance, and generated compatibility claims.

### VibeProof and native core

- Claim fields, CDDL, COSE profile, errors, compatibility, batching, acknowledgements, sequences, forks, corrections, and test vectors.
- Process/privilege diagram, local database, crash/offline recovery, IPC messages, platform matrix, device lifecycle, CLI commands, installer/update/uninstall, and resource budgets.

### Identity, server, and ranking

- GitHub App versus OAuth App and X/Twitter protocol decision.
- Account/link/merge/session/recovery/provider-loss/native-auth/authorization state machines.
- Complete APIs, PostgreSQL schema, transactions, outbox/workers, ranking queries, caching, corrections, rebuild, and benchmarks.

### Integrity and anti-abuse

- Executable fixtures and attack campaigns for every catalog class.
- Deterministic reason-code and evidence qualification registries.
- Privacy-safe feature schema.
- Rules/statistics/graph/classical/SLM detector bakeoff.
- Calibration budgets, moderation/appeal state machines, red-team operations, and accepted residual risks.

### UX, operations, and open source

- Complete route/state/data/copy contracts and local-to-hosted UX.
- Accessibility, responsive, browser, native, visual, battery, and performance plans.
- Packaging, signing, notarization, TUF, consumer verification, deployment, SLOs, observability, backup/restore, DR, incidents, key compromise, and legal/privacy operations.
- License, DCO/CLA, trademark, contributor/maintainer, security advisory, adapter, signing-key, and release governance.
- Restored and validated automated checks in the implementation phase.

## Domain readiness

| Domain | State | Main remaining gap |
|---|---|---|
| Repository truth and authority | strong | run metadata generator from complete checkout |
| Product scope and staging | strong direction | exact feature/journey/gate contracts |
| Token accounting and pricing | partial | normative semantics and comparability |
| Agent compatibility | strong architecture | registry, schemas, exercised evidence |
| VibeProof | partial | exact wire and state contracts |
| Native daemon/client | strong architecture | IPC/storage/lifecycle/platform contracts |
| Authentication | strong direction | provider decision and complete state machines |
| Server and ranking | partial | APIs, SQL, transactions, rebuild, benchmarks |
| Social and groups | partial | complete domain and permission behavior |
| Anti-cheat | strong control model | executable validation and detector decision |
| Web/native UX | partial | routes, data, states, accessibility, tests |
| Operations/open source | partial | concrete provider, recovery, governance, launch evidence |

## Planning exit gate

Implementation may begin only when all are true or explicitly waived:

1. No unresolved P0 contradiction or damaged authoritative artifact.
2. Complete public-launch matrix and staged milestone gates are frozen.
3. Every material decision has an ID, status, owner/condition, and dependent updates.
4. Core interfaces, schemas, state machines, limits, errors, authorization, and privacy classes are specified.
5. Accounting, adapter, claim, IPC, device, API, SQL, ranking, identity, social, moderation, lifecycle, and operations contracts are implementation-grade.
6. Threats map to controls, tests, residual risk, policy outcomes, and appeals.
7. Storage, migration, rebuild, correction, export, deletion, recovery, and rollback are specified.
8. Platform capability and degradation are explicit.
9. Performance, battery, accessibility, onboarding, reliability, and operations budgets have evidence plans.
10. Release, updater, key rotation, incident, moderation, appeal, backup, and DR flows are specified.
11. Repository metadata is regenerated and future CI can detect stale indexes, invalid task links, malformed schemas, and fake evidence.
12. User explicitly changes the phase to implementation.

## Status

- Continue planning: **go**.
- Begin product implementation: **no-go**.
- Competitive beta: **no-go**.
- Public launch: **no-go**.

These no-go outcomes reflect uncompleted contracts and evidence, not unresolved product direction or a recommendation to narrow scope.
