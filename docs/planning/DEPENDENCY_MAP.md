# VibeMaxxing Dependency Map

Updated: 2026-07-19

## Critical path

```text
P-000 repository truth and governance
  -> P-050 complete product scope, glossary, journeys, and launch gates
  -> P-100 accounting, pricing, comparability, and time semantics
  -> P-200 universal agent compatibility and adapter contracts
  -> P-300 VibeProof protocol contract
  -> P-400 native daemon, collector, storage, IPC, and device identity
  -> P-500 account identity, OAuth, sessions, recovery, and authorization
  -> P-600 server APIs, PostgreSQL, ingestion, aggregation, and ranking
  -> P-700 social graph, boards, countries, presence, notifications, moderation, and lifecycle
  -> P-800 anti-cheat control mapping, attack lab, detector decision, and red-team operations
  -> P-900 web/native UX, privacy verification, design, and accessibility
  -> P-1000 packaging, production operations, and open-source launch
  -> P-1100 final planning, implementation, and public-launch reviews
```

## Dependency rules

- Product scope and glossary precede domain schemas and user-facing terminology.
- Accounting semantics precede normalized agent events, claims, ranking, and pricing.
- Adapter contracts precede VibeProof claim semantics because claims preserve source/evidence provenance.
- VibeProof fields, errors, and sequences precede local storage, IPC, device, and ingestion contracts.
- Device identity and native authorization precede server account/device binding.
- OAuth/account/session state precedes social permissions, boards, moderation, export, and deletion.
- Claim acceptance transactions precede aggregation, ranking, overtakes, streaks, seasons, and notifications.
- Social and account state precede complete anti-abuse policy and appeals.
- Complete product/domain contracts precede routes, UI states, accessibility, and privacy-verification UX.
- Packaging and operations depend on all shipping binaries, services, schemas, data lifecycles, and recovery paths.
- Public launch depends on restored automated evidence, open-source governance, complete agent-family coverage, and explicit approval.

## Parallel planning tracks

After P-000 and P-050, these can proceed concurrently where dependencies are met:

- pricing data/provenance and cross-provider comparability;
- agent census and community adapter governance;
- platform capability/hardening research;
- GitHub/X authentication research;
- abuse taxonomy, moderator/appeal states, and insider controls;
- observability allowlist and privacy canaries;
- deployment/provider/region/cost research;
- license, DCO/CLA, trademark, maintainer, and release governance;
- route/information architecture based on frozen product scope.

## Cross-cutting requirements

Every domain task must reference:

- `PROJECT_CONTEXT.md` and current decision IDs;
- `docs/privacy/PRIVACY_CONTRACT.md`;
- `docs/security/THREAT_MODEL.md`;
- `docs/security/INTEGRITY_MODEL.md`;
- `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md` where relevant;
- `docs/engineering/PERFORMANCE_BUDGETS.md`;
- `docs/qa/ACCEPTANCE_GATES.md`;
- `docs/evals/EVAL_SYSTEM.md` as future evidence, not current automatic execution;
- relevant platform, lifecycle, accessibility, and operations contracts.

## Planning blockers

A task is blocked when any required upstream item lacks:

- canonical schema, field semantics, or invariant;
- source/evidence or platform capability assumption;
- privacy classification and outbound allowlist;
- authentication/authorization or threat/control mapping;
- error, limit, timeout, retry, degradation, and recovery behavior;
- storage, transaction, ordering, idempotency, migration, or deletion semantics;
- compatibility/versioning/deprecation policy;
- measurable positive, negative, adversarial, performance, or accessibility evidence plan;
- owner and closure condition for unresolved external facts.

## Phase changes

- No implementation task starts until P-1104 passes and the user explicitly opens implementation.
- Restoring automated implementation/launch checks occurs only in the implementation phase under P-1007.
- Public launch requires P-1105 and explicit user approval; passing an internal vertical slice or competitive beta is insufficient.
