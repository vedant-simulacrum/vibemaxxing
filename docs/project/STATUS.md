# VibeMaxxing Status

Updated: 2026-07-23

## Phase

The repository is in **planning contract repair**.

P-1140A, the authority reset and launch-scope alignment, is complete. The second-pass technical audit converted the remaining cross-contract defects into a detailed machine-contract repair specification and expanded the canonical privacy and threat-model owners.

P-1140B is now active. Product implementation remains unauthorized.

One bounded fixture-backed hosted-web/Storybook slice exists and is classified as a **runnable prototype**. It is not production implementation, backend integration, launch evidence or authorization to continue product implementation.

## Current readiness

- Product thesis, privacy posture, Token Burn metric and broad social direction: accepted.
- Public launch scope: complete core social product except country leaderboards, which are post-launch.
- Local-model and delayed offline usage: first-class competitive usage when deterministically counted under a certified source/accounting profile.
- Global leaderboards: accepted Standard and Hardened claims both count; Imported records never count.
- Ranked identity: one active ranked identity per detected/resolved person, strongly enforced without claiming mathematically verified humanity.
- SLM: post-launch research only; not a launch dependency or authority.
- Repository authority, launch scope, stale PR disposition and implementation entrance gates: aligned.
- Exact machine-contract repair requirements: recorded in `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`.
- Canonical privacy and threat models: expanded with process, field, state-machine, transaction, release and validation requirements.
- Current CDDL, JSON Schema, Protobuf, OpenAPI, SQL, reason codes and policy defaults: planning placeholders blocked from implementation where they conflict with P-1140.
- Backend, collector, protocol runtime, identity service, ranking service, production storage, updater, deployment and operational systems: not implemented.
- Competitive beta and public launch: no-go pending implementation and executable evidence.

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
- **P-1140D:** OAuth/session, identity, API, SQL, ranking, social, native, updater and release state machines.
- **P-1140E:** cross-contract fixtures, traceability, clean-checkout planning validation and final P0/P1 review.

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
- `docs/planning/DECISION_REGISTER.md`
- `docs/planning/TASK_CATALOG.md`
- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Automation

Read-only planning validation may run. Product build, dependency, security, fuzz, evaluation, release, signing, deployment and operational automation remain disabled until implementation is explicitly opened.

## Current gate

P-1140A is complete. P-1140B is active. P-1140C–E follow in dependency order. P-1131 and comprehensive launch review remain blocked until real implementation and exercised evidence exist.