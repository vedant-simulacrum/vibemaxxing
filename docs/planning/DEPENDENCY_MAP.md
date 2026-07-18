# VibeMaxxing Dependency Map

Updated: 2026-07-19

## Critical path

```text
P-000 repository truth and planning gate
  -> P-100 product glossary and accounting semantics
  -> P-200 adapter contract and certification
  -> P-300 VibeProof protocol contract
  -> P-400 collector, IPC, storage, and device identity contract
  -> P-500 ingestion API, ledger, outbox, aggregates, and ranking contract
  -> P-600 web leaderboard and privacy-verification contract
  -> P-700 authentication, social graph, boards, abuse, and moderation contract
  -> P-800 packaging, updater, observability, deployment, recovery, and release contract
  -> P-900 final implementation-readiness review
```

## Why this order exists

- Adapter work depends on frozen accounting categories and privacy rules.
- Signed claims depend on normalized events and accounting semantics.
- Collector boundaries depend on the claim schema, key lifecycle, and deduplication model.
- Server ingestion depends on the signed claim and identity contracts.
- Ranking depends on accepted-claim semantics, time policy, late-event policy, and rebuild rules.
- Web and social contracts depend on ranking, evidence labels, privacy states, and authentication.
- Packaging and operations depend on all supported binaries, services, schemas, and recovery paths.

## Parallel planning tracks

These may proceed concurrently after P-000:

- product glossary, onboarding language, and design information architecture;
- provider pricing dataset format and provenance operations;
- platform capability matrix for macOS, Windows, Linux, WSL, and containers;
- abuse taxonomy, moderation workflow, appeal states, and retention rules;
- observability event allowlist and canary plan;
- deployment environments, configuration, secrets, release promotion, and rollback model.

## Cross-cutting dependencies

Every domain task must reference:

- `docs/privacy/PRIVACY_CONTRACT.md`;
- `docs/security/THREAT_MODEL.md`;
- `docs/security/INTEGRITY_MODEL.md`;
- `docs/engineering/PERFORMANCE_BUDGETS.md`;
- `docs/qa/ACCEPTANCE_GATES.md`;
- `docs/evals/EVAL_SYSTEM.md`;
- applicable ADRs and decision IDs.

## Planning blockers

A task is blocked when any of these is missing:

- upstream schema or invariant;
- platform capability assumption;
- privacy allowlist;
- threat/control mapping;
- error and degradation behavior;
- storage or transaction semantics;
- deterministic acceptance evidence;
- owner for an unresolved external fact.

## Phase change dependency

No implementation task may start until P-900 passes and the user explicitly changes the phase from planning to implementation.