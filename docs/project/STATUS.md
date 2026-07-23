# VibeMaxxing Status

Updated: 2026-07-24

## Phase

The repository is in **planning contract repair**.

P-1140A and P-1140B are complete. P-1140C is active. Product implementation remains unauthorized.

The repository has planning traceability for D-001 through D-069 and accepted platform baselines for macOS, Windows, Linux, WSL, containers and CI.

One bounded fixture-backed hosted-web/Storybook slice exists and is classified as a **runnable prototype**. It is not production implementation, backend integration, launch evidence or authorization to continue product implementation.

## Current readiness

- Product thesis, privacy posture, Token Burn metric and broad social direction: accepted.
- Public launch scope: complete core social product except country leaderboards, which are post-launch.
- Local-model and delayed offline usage: first-class competitive usage when deterministically counted under a certified source/accounting profile.
- Global leaderboards: accepted Standard and Hardened claims both count; Imported records never count.
- Ranked identity: one active ranked identity per detected/resolved person, strongly enforced without claiming mathematically verified humanity.
- SLM: post-launch research only; not a launch dependency or authority.
- T20: provisional candidate engineering cohort under D-046; not a launch dependency and not current support evidence.
- Daemon lifecycle: D-061 and ADR-010 require an always-on OS-supervised background service that auto-starts, auto-restarts, survives shell closure and remains resident through paused/offline/degraded/recovery states within the declared platform lifecycle context.
- macOS: Apple silicon and Intel are launch requirements under rolling exact-profile certification.
- Windows: native x64 and ARM64 are launch requirements across maintained desktop and applicable Server profiles.
- Linux: maintained desktop, headless and remote profiles are launch requirements through exact distribution/package/architecture certification.
- WSL, containers and CI/ephemeral runners: globally competitive by default at the verifier-awarded evidence level; boards may impose stronger minimums.
- Android, iOS, iPadOS and ChromeOS: no native product scope.
- Optional privileged machine-wide supervision: accepted only as a separately consented, least-privilege lifecycle profile.
- Automatic updates: mandatory for competitive profiles with bounded deferral, signed release-set verification and rollback.
- Storybook automation: permitted only as prototype/design validation and cannot satisfy product, security or launch gates.
- Decision traceability: every registered decision has a normative owner, implementation work unit, state/schema owner where applicable, platform scope and executable evidence requirement.
- Planning tooling: doctor, coverage validation, artifact validation, provisional T20 validation, stable work-unit generation and prototype workflow dependency controls are aligned to D-001 through D-069.
- Historical planning-complete reports are explicitly non-authoritative.
- Exact machine-contract repair requirements are recorded in `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`.
- Current CDDL, JSON Schema, Protobuf, OpenAPI, SQL, reason codes and policy defaults remain planning placeholders blocked from implementation where P-1140 has not repaired their semantics.
- The SQL file is an explicitly blocked structural inventory, not a migration design.
- Backend, collector, protocol runtime, identity service, ranking service, production storage, installers, updater, deployment and operational systems are not implemented.
- No collector platform is currently production-complete or exercised.
- Competitive beta and public launch remain no-go pending implementation and executable evidence.

Clean-checkout planning and prototype validation passed on the exact PR heads merged through PR #28 and PR #29. Those successful runs validate only the planning/tooling and synthetic prototype changes they exercised; they are not a completed P-1140E pass, production evidence or launch evidence. The squash commits on `main` do not have separate post-merge runs attached.

## Active planning gates

### Completed P-1140B — core trust, privacy and accounting contracts

Candidate contract set now present:

- typed SourceObservation, NormalizedAccountingEvent and LocalDetectorResult schemas;
- typed local IPC with no opaque normalized-event JSON;
- digest/provenance/certification-bound adapter manifests and device-lineage transitions;
- immutable accounting-profile schema/registry and representative cloud/local containment fixtures;
- independent server appraisal policy and capability ceilings;
- server-owned pricing interpretation with immutable event-time alias resolution;
- deny-by-default claim-egress registry and positive/negative canaries for every required boundary.

Planning checks run #211 passed on the exact P-1140B candidate head. The gate-transition head must also pass before merge. Product implementation remains unauthorized.

### Active P-1140C — VibeProof v1 protocol rewrite

Active work is the deterministic CBOR/COSE claim, appraisal, checkpoint, batch, continuity, gap, rotation, correction and replay state contract. It must preserve the P-1140B authority and privacy boundaries.

### Following gates

 - **P-1140D:** OAuth/session, identity, API, SQL, ranking, social, native, always-on daemon, complete platform packaging, optional privileged supervision, mandatory updater and release state machines.
- **P-1140E:** cross-contract fixtures, D-001..D-069 traceability validation, exact platform-profile validation, clean-checkout planning validation and final P0/P1 review.

P-1104 remains blocked until P-1140B–E complete, all planning-only validation passes from a clean checkout, no P0/P1 contradiction remains and the user explicitly authorizes implementation.

## Artifact maturity

1. **Specification** — normative intended behavior without executable proof.
2. **Mock** — static or illustrative design artifact.
3. **Runnable prototype** — executable exploratory work using fixtures or incomplete integrations; non-normative unless separately adopted.
4. **Production implementation** — integrated product code satisfying accepted contracts and implementation gates.
5. **Executable evidence** — reproducible conformance, security, benchmark or operational output supporting a specific claim.

Planning artifacts and prototypes are not cryptographic interoperability evidence, certified adapter support, performance evidence, deployed infrastructure, security hardening or launch evidence.

## Canonical entrypoints

- `AGENTS.md`
- `docs/project/PROJECT.md`
- `docs/project/STATUS.md`
- `docs/project/DOCUMENTATION.md`
- `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- `docs/planning/decision-traceability/README.md`
- `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- `docs/planning/DECISION_REGISTER.md`
- `docs/planning/TASK_CATALOG.md`
- `docs/decisions/ADR-010-ALWAYS_ON_DAEMON_LIFECYCLE.md`
- `docs/decisions/ADR-011-UNIVERSAL_PLATFORM_SUPPORT_BASELINE.md`
- `docs/decisions/ADR-012-OPTIONAL_PRIVILEGED_SUPERVISION.md`
- `docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md`
- `docs/decisions/ADR-014-PROTOTYPE_VISUAL_VALIDATION_AUTOMATION.md`
- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Automation

Read-only planning validation may run. ADR-014 permits narrowly scoped Storybook prototype validation. Product build, dependency, security, fuzz, evaluation, release, signing, deployment and operational automation remain disabled until implementation is explicitly opened.

## Current gate

P-1140A–B are complete. P-1140C is active; P-1140D–E follow in dependency order. P-1131 and comprehensive launch review remain blocked until real implementation and exercised evidence exist.
