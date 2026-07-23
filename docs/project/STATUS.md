# VibeMaxxing Status

Updated: 2026-07-23

## Phase

The repository is in **planning contract repair**.

P-1140A, the authority reset and launch-scope alignment, is complete. P-1140B is active. Product implementation remains unauthorized.

The repository now has complete planning traceability for D-001 through D-061 and a cross-platform completeness audit for macOS, Windows, Linux desktop/headless, WSL, containers, CI and remote/headless environments.

One bounded fixture-backed hosted-web/Storybook slice exists and is classified as a **runnable prototype**. It is not production implementation, backend integration, launch evidence or authorization to continue product implementation.

## Current readiness

- Product thesis, privacy posture, Token Burn metric and broad social direction: accepted.
- Public launch scope: complete core social product except country leaderboards, which are post-launch.
- Local-model and delayed offline usage: first-class competitive usage when deterministically counted under a certified source/accounting profile.
- Global leaderboards: accepted Standard and Hardened claims both count; Imported records never count.
- Ranked identity: one active ranked identity per detected/resolved person, strongly enforced without claiming mathematically verified humanity.
- SLM: post-launch research only; not a launch dependency or authority.
- Daemon lifecycle: D-061 and ADR-010 require an always-on OS-supervised per-user background service that auto-starts, auto-restarts, survives shell closure, and remains resident through paused/offline/degraded/recovery states.
- Decision traceability: every registered decision has a normative owner, implementation work unit, state/schema owner where applicable, platform scope and executable evidence requirement.
- Cross-platform planning: mandatory capabilities, OS-specific implementations, integration sequences and release gates are defined in `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`.
- Platform lifecycle limitations must be disclosed honestly; “always-on” excludes powered-off hardware, full suspension, disabled/uninstalled service and unavailable service contexts.
- Exact machine-contract repair requirements are recorded in `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`.
- Current CDDL, JSON Schema, Protobuf, OpenAPI, SQL, reason codes and policy defaults remain planning placeholders blocked from implementation where they conflict with P-1140.
- Backend, collector, protocol runtime, identity service, ranking service, production storage, installers, updater, deployment and operational systems are not implemented.
- No collector platform is currently production-complete or exercised.
- Competitive beta and public launch remain no-go pending implementation and executable evidence.

## Active planning gates

### P-1140B — core trust, privacy and accounting contracts

Active work:

- replace client-owned evidence state with evidence facts plus server verifier appraisal;
- define typed `SourceObservation`, `NormalizedAccountingEvent`, `LocalDetectorResult`, `EvidenceClaim`, `VerifierAppraisal` and `CheckpointReceipt` boundaries;
- define immutable provider/runtime accounting profiles and mutually exclusive canonical token totals;
- define delayed/offline synchronization, time uncertainty, device lineage and requalification;
- define digest/provenance-bound adapter and collector certification;
- define server-owned pricing interpretations and immutable event-time alias resolution;
- repair privacy allowlists and typed local IPC.

### Following gates

- **P-1140C:** VibeProof v1 CDDL/COSE, batch, continuity, rotation, correction and exact-byte protocol rewrite.
- **P-1140D:** OAuth/session, identity, API, SQL, ranking, social, native, always-on daemon, platform packaging, updater and release state machines.
- **P-1140E:** cross-contract fixtures, complete D-001..D-061 traceability validation, platform baseline validation, clean-checkout planning validation and final P0/P1 review.

P-1104 remains blocked until P-1140B–E complete, all planning-only validation passes from a clean checkout, every platform advertised for launch has a frozen support profile, no P0/P1 contradiction remains and the user explicitly authorizes implementation.

## Open platform-scope decisions

The exact launch matrix still requires user decisions on:

- Intel Mac versus Apple-silicon-only support;
- Windows ARM64 versus x64-only initial support;
- first-class Linux distributions, versions, desktop environments and CPU architectures;
- Linux lingering/across-logout behavior;
- competitive eligibility for WSL, containers and CI;
- ChromeOS and mobile scope;
- whether machine-wide privileged service modes are ever allowed;
- mandatory automatic updates versus optional manual/notify-only channels.

Until resolved, no document may claim complete support for “every platform.”

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
- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Automation

Read-only planning validation may run. Product build, dependency, security, fuzz, evaluation, release, signing, deployment and operational automation remain disabled until implementation is explicitly opened.

## Current gate

P-1140A is complete. P-1140B is active. P-1140C–E follow in dependency order. P-1131 and comprehensive launch review remain blocked until real implementation and exercised evidence exist.
