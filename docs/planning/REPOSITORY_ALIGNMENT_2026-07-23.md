# Repository-wide authority alignment audit

Updated: 2026-07-24
Status: canonical planning audit and reconciliation record

## Purpose

This document records the repository-wide audit performed after the anti-cheat research and implementation planning work. It resolves which artifacts are authoritative, which are stale, which are planning placeholders, and which contracts must be repaired before product implementation may begin.

It does not authorize product code, infrastructure, deployment, product security automation, automated evaluation, signing, or release activity.

## Audit scope

The audit covered:

- `AGENTS.md`, `README.md`, project authority, status and documentation map;
- decision and task registers;
- launch-scope and consolidated audit records;
- accepted ADRs and implementation handoff documents;
- privacy, threat, integrity, evidence, identity and recovery contracts;
- accounting, ranking, pricing, social, presence, notification, moderation and UX contracts;
- adapter, VibeProof, native-runtime, daemon, updater, server/API and persistence contracts;
- planning-grade CDDL, JSON Schema, Protobuf, OpenAPI, SQL, reason-code and policy artifacts;
- research reports, including the anti-cheat research;
- recent commits, issues and pull requests;
- the bounded fixture-backed web/Storybook prototype.

## Executive finding

The repository has substantial and often strong planning material, but it is not internally synchronized.

The central inconsistency is temporal:

1. the July 19 authority files declare technical planning complete;
2. the July 23 consolidated audit proves that several machine contracts cannot express the prose guarantees;
3. the July 23 launch decisions close product-policy questions and change launch scope;
4. the July 23 privacy and anti-cheat work changes the trust architecture;
5. the top-level status, handoff, schemas and older subsystem contracts were not updated to adopt those later decisions.

Therefore the correct repository phase is **planning alignment and contract repair**, not “planning complete” and not implementation.

## July 24 handoff consolidation update

A connector-backed audit of current `main`, open pull requests, issues, authority files, implementation planning, planning schemas, seed packages and workflow state found:

- `main` at `111173b32ef972b600148f08675143d552cad4d9` remains a planning repository with one bounded web/Storybook prototype;
- no root Rust, Go or JavaScript workspace exists; `apps/api/go.mod` is a module seed without a server entrypoint, the planned Rust crates are not present, and `packages/protocol` is explicitly a future generated-bindings placeholder;
- the implementation handoff and PR-sized breakdown are broad and dependency ordered, but they cannot be treated as executable handoff authority while P-1140B through P-1140E remain incomplete;
- the July 19 schema/interface inventory and traceability dry-run still used current-sounding `validated`, `normative` and `complete` language even though later audits reopened their assumptions;
- open PR #30 contains the active UI application-lockdown work: 49 changed files and 24 branch commits, but it is two commits behind `main`, currently non-mergeable, and overlaps workflow/governance files changed by PR #31;
- open draft PR #31 is the ADR-014 workflow-boundary repair: five files, mergeable at audit time, with planning checks passing on its exact head while its prototype workflow was still running.

### Consolidation disposition

- `SCHEMA_AND_INTERFACE_INVENTORY.md` is a current repair index, not implementation-ready schema approval.
- `TRACEABILITY_AND_DRY_RUN_AUDIT.md` is historical evidence superseded by `decision-traceability/`, P-1140 and this alignment record.
- `IMPLEMENTATION_HANDOFF.md` remains the sole future build-order contract, but now carries an explicit handoff-health section and cannot graduate until repaired machine contracts and clean validation exist.
- Existing research and anti-cheat plans remain inputs. Unique decisions must flow into the accepted owners; they are not parallel roadmaps.

### Concurrent-work merge safety

1. Complete and merge PR #31 only after its exact-head planning and prototype checks finish successfully.
2. Update PR #30 onto the resulting `main`.
3. Resolve its workflow, documentation-map and UI-checker overlaps in favor of ADR-014 and the repaired repository doctor.
4. Re-run planning and scoped prototype validation on the reconciled UI head.
5. Refresh canonical status/alignment only from the merged state; never infer completion from a branch or a pre-merge run.

This ordering is coordination guidance, not authorization to merge a PR whose checks or review are incomplete.

## Current artifact maturity

### Implemented

Only one bounded fixture-backed hosted-web/Storybook slice exists. It is a runnable prototype using fixtures and design assets.

It is not:

- a production frontend;
- connected to a production API;
- evidence that identity, ranking, social or moderation behavior works;
- evidence that VibeProof, collection, privacy or anti-cheat works;
- authorization to continue product implementation.

### Specified but not implemented

The repository specifies intended behavior for:

- accounting and pricing;
- adapters and universal support;
- VibeProof claims;
- local collection and native topology;
- authentication, sessions and recovery;
- identity uniqueness policy;
- server APIs and persistence;
- ranking and corrections;
- friends, rivals, boards and presence;
- notifications, moderation and appeals;
- updater, release, operations and open-source governance;
- privacy and anti-cheat.

These artifacts have no production implementation or executable product evidence.

### Planning placeholders

The following are structural planning inputs, not final implementation contracts:

- `packages/schemas/vibeproof-claim-v1.cddl`;
- `packages/schemas/normalized-event.schema.json`;
- adapter manifest, local-control, OpenAPI and planning SQL schemas;
- conformance registries with empty or planned certification records;
- provisional policy defaults and reason codes;
- implementation directory trees that do not yet exist.

They must not be used as final generated-code sources until the relevant P-1140 repair gate closes.

## Canonical authority hierarchy

When repository artifacts conflict, use this order:

1. latest explicit user instruction;
2. `docs/project/PROJECT.md`;
3. `docs/project/STATUS.md`;
4. accepted decisions in `docs/planning/DECISION_REGISTER.md`;
5. accepted ADRs;
6. normative subsystem contracts and authoritative schemas that are not marked blocked or superseded;
7. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `PR_SIZED_WORK_BREAKDOWN.md`;
8. research and audit evidence;
9. historical completion reports, generated artifacts, stale branches and closed planning assumptions.

`docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md` records the reconciliation but does not override the product authority or decision register.

## Locked product and architecture decisions

The following are now repository-wide constraints:

### Product and launch

- VibeMaxxing is a greenfield rebuild; no old accounts or scores migrate.
- Token Burn is the default raw-volume competitive metric.
- Estimated Cash Burn is always explicitly estimated and server interpreted.
- Genuine but intentionally wasteful usage counts when authentic and non-duplicated.
- Public launch targets the complete core social product.
- Country leaderboards are post-launch and are not part of public-launch readiness.
- Development may be staged internally without redefining public launch scope.

### Privacy

- Prompts, responses, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications and personal insights never reach VibeMaxxing servers.
- Content-derived hashes or embeddings are not uploaded as a workaround.
- Only fixed-schema aggregate accounting and integrity metadata may cross the device boundary.
- Transcript-capable processes have no network access; networked synchronization processes cannot read transcript content.
- Server reviewers and moderators cannot access local raw records.

### Competition and evidence

- Imported historical records are private analytics only.
- Standard and Hardened claims may both contribute to the global leaderboard.
- Hardened is awarded by a server verifier under a named, versioned profile; the client cannot self-award it.
- Local-model and delayed offline usage are first-class competitive usage when deterministically counted by a certified source profile.
- Connectivity alone does not define authenticity.
- Unanchored, rollback-prone or uncertain intervals lower assurance rather than automatically erasing legitimate activity.
- Provider API usage metadata is accounting evidence, not a cryptographic provider receipt.
- Default launch architecture does not proxy model traffic through VibeMaxxing.
- Kernel anti-cheat is rejected.

### Identity

- Launch strongly enforces one active ranked identity per detected/resolved person without government-ID or biometric proofing by default.
- OAuth proves control of provider accounts, not one unique human.
- Public profiles remain separated from private identity-integrity signals.
- High-impact duplicate-identity outcomes require corroborating evidence, human review and appeal.
- GitHub and X are the currently accepted primary provider paths. Google is not a launch provider until authentication, API and persistence contracts add it coherently.
- Private organizations may require stronger organization-managed checks.

### Anti-cheat

- Deterministic accounting, schema, signature, sequence, replay, duplicate, continuity and eligibility checks are authoritative.
- An SLM is post-launch research, local-only, sandboxed, advisory and non-authoritative.
- The SLM may not alter totals, award Hardened or permanently ban.
- Server anomaly detection uses aggregate privacy-safe features and begins in shadow mode.
- Enforcement is progressive, reason-coded, appealable and reversible.

### Platform and release

- The default collector is an unprivileged per-user process.
- macOS uses a per-user service/LaunchAgent and menu-bar shell; Windows uses a per-user background collector and tray shell; Linux uses a user service where available.
- Privileged helpers require a separate accepted capability and privacy decision.
- Official adapter, collector and detector artifacts are digest-addressed and provenance-bound.
- Release integrity requires signed artifacts, rollback/freeze-resistant metadata and compromise recovery; signatures alone are insufficient.

## Cross-repository contradiction matrix

| Area | Stale or contradictory artifact | Canonical resolution | Repair gate |
|---|---|---|---|
| Repository phase | README, AGENTS, PROJECT, STATUS and task catalog say planning complete | phase is planning alignment and contract repair | P-1140A |
| Launch scope | PROJECT, social contract, handoff and PR breakdown include countries | countries are post-launch only | P-1140A/P-1140D |
| Evidence authority | claim CDDL and adapter contract let clients submit Standard/Hardened | client submits evidence facts; server creates verifier appraisal | P-1140B/P-1140C |
| Provider evidence | evidence profiles and normalized event use provider-receipt/server-observed language | ordinary provider usage metadata is not a receipt; no hosted model-call proxy in launch path | P-1140B |
| Token accounting | one additive formula assumes provider categories are mutually exclusive | versioned provider/API accounting profile defines category containment | P-1140B |
| Pricing | client claim names a pricing dataset | pricing and Estimated Cash Burn are server interpretations | P-1140B/P-1140D |
| Competitive time | fixed 24-hour lateness and client source time select eligibility | server-anchored interval and profile-specific delayed-sync policy | P-1140B |
| Offline continuity | previous accepted claim and upload-time challenge are treated as sufficient | separate local commitment head, server checkpoint receipt and offline interval | P-1140B/P-1140C |
| Protocol extension | generic signed extension map permits arbitrary bytes | no unregistered generic extension channel in v1 | P-1140C |
| Batching | prose and schema disagree on atomicity and sequence behavior | one normative batch/checkpoint/replay design | P-1140C |
| Rotation | old/new signatures required without a wire transition | typed dual-authorization rotation transition | P-1140C |
| Local IPC | opaque normalized-event JSON bytes are allowed | typed messages only across privileged boundaries | P-1140B/P-1140C |
| Device recovery | new devices can discard a quarantined chain | explicit device lineage, recovery reason and requalification | P-1140B/P-1140D |
| SLM | threat model implies raw-log inspection; evidence profile permits only structured features; old text conditionally puts it near launch | post-launch bakeoff with structured mode first and optional raw-local sandbox | P-1140A/P-1140B |
| OAuth providers | ranked identity includes Google; auth/API/SQL do not | GitHub and X at launch; Google deferred until fully contracted | P-1140A/P-1140D |
| OAuth sessions | rotation, token families, replay and native binding are prose-only | typed transaction/session/token-family state machines | P-1140D |
| Human uniqueness | policy wording can imply verified humans | actively enforced one-ranked-identity policy, not mathematical proof | P-1140A/P-1140D |
| Ranking identity | filters and snapshots lack a canonical identity | introduce immutable `ranking_view_id` | P-1140D |
| Social relationships | friend edges, ownership and board transitions have conflicting persistence authorities | typed canonical state machines and constraints | P-1140D |
| Presence | web/session client can renew without collector-observed activity | presence derives from accepted/signed qualifying collector activity | P-1140D |
| Notifications | open JSON payloads and preferences can leak data | typed event and preference schemas | P-1140D |
| Moderation | actions cannot bind exact claims/views/periods or rebuild reversals | immutable moderation ledger and deterministic ranking rebuild | P-1140D |
| API governance | generic resources and incomplete quotas | typed resources, authorization matrices, limits, `429` and load shedding | P-1140D |
| Updater | TUF named without root/role/release-set/compromise policy | complete update trust and release-set contract | P-1140D/P-1140E |
| Support claims | version names can imply certification | digest-addressed certification bundles and exercised evidence only | P-1140B/P-1140E |

## Subsystem readiness

| Subsystem | Planning maturity | Implementation | Executable evidence | Current judgment |
|---|---|---|---|---|
| Product scope | mostly closed; country correction required | none | none | repair authority |
| Privacy boundary | strong direction; machine boundaries incomplete | none | none | repair contracts |
| Accounting | broad prose; provider category semantics incomplete | none | none | redesign profiles |
| Adapter platform | broad prose and registry shapes | none | empty certifications | redesign capability/certification binding |
| VibeProof | structurally drafted but contradictory | none | no interoperability | protocol rewrite required |
| Native collector | topology drafted; IPC/storage/lineage incomplete | none | none | detailed implementation planning ready after repair |
| Authentication | broad flows; provider/session state mismatches | none | none | state-machine repair required |
| Ranked identity | policy mostly closed; signals/appeals untyped | none | none | implementation contract required |
| Server ingestion | transaction outline exists; schema does not support final model | none | none | redesign required |
| Ranking/pricing | algorithms outlined; canonical view and pricing line items missing | none | none | contract repair required |
| Social | complete feature list; state machines and schemas incomplete | UI prototype only | none | contract repair required |
| Moderation/appeals | policy outlined; reversal ledger incomplete | none | none | contract repair required |
| Anomaly/SLM | research direction complete | none | no bakeoff | post-launch research |
| Updater/release | technologies named; trust model incomplete | none | none | contract repair required |
| Operations | planning only | none | none | blocked by implementation |

## Planning program

### P-1140A — authority reset and launch-scope alignment

Status after this audit: active.

Deliverables:

- update repository entrypoints and phase language;
- apply the July 23 launch decisions;
- retire stale PR #17;
- make country post-launch everywhere;
- make SLM post-launch everywhere;
- align GitHub/X provider scope and defer Google;
- mark draft machine contracts blocked from implementation until repaired;
- activate P-1140B through P-1140E in the task catalog.

### P-1140B — core trust, privacy and accounting contracts

Deliverables:

- evidence fact versus verifier appraisal model;
- source/capture/accounting/device/continuity/environment/freshness dimensions;
- provider/API accounting profile schema;
- canonical mutually exclusive token totals;
- local-model accounting profiles;
- server-derived pricing interpretations;
- server-anchored event intervals;
- device lineage and requalification;
- typed local evidence stages and IPC boundaries;
- fixed outbound allowlist;
- support/certification digest and provenance binding.

### P-1140C — VibeProof v1 protocol rewrite

Deliverables:

- `EvidenceClaim`, `VerifierAppraisal`, `CheckpointReceipt`, rotation and correction formats;
- exact deterministic CBOR profile;
- complete COSE headers, key representation, external AAD and signed-byte definition;
- batch atomicity and replay behavior;
- local commitment and server checkpoint semantics;
- delayed/offline synchronization rules;
- integer/time/resource bounds compatible across Rust, Go, TypeScript and PostgreSQL;
- removal of generic extension channel;
- exact-byte golden vectors and independent decoder plan.

### P-1140D — identity, API, ranking, social, native and release state machines

Deliverables:

- OAuth transaction and session/token-family state machines;
- native-to-web bootstrap and DPoP decision;
- one-ranked-identity investigation, restriction, merge, recovery and appeal states;
- typed idempotency ledger;
- ranking view, snapshot, correction and rebuild identities;
- pricing rule line items and immutable alias resolution;
- friendship, block, rival, board, role, ownership and invitation state machines;
- collector-derived presence and privacy projection;
- typed notifications and preferences;
- moderation ledger and deterministic reversal;
- export and server/local deletion separation;
- API quotas and resource governance;
- platform packaging, IPC, storage, updater and release-set contracts.

### P-1140E — cross-contract validation

Deliverables:

- planning-only negative fixtures covering every repaired invariant;
- reference and schema consistency checks;
- protocol golden vectors and malformed corpus definitions;
- SQL constraint/race plans;
- privacy canaries across source observation, local IPC, claims, API, telemetry and moderation;
- traceability from decisions to prose, schema, test and launch gate;
- clean-checkout repository doctor result.

P-1140E does not enable product CI, product security automation, fuzz infrastructure, deployment or release workflows.

## Implementation authorization boundary

P-1104 remains blocked until:

1. P-1140A through P-1140E are complete;
2. the repository doctor and all planning-only validators pass from a clean checkout;
3. no P0/P1 contradiction remains open;
4. the user explicitly authorizes implementation.

After approval, implementation follows only:

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`;
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`;
- subsystem contracts and schemas repaired by P-1140;
- `docs/implementation/ISSUE_GENERATION.md` for execution threads.

## Stale PR and issue disposition

### Pull request #17

PR #17 is superseded by later work on `main`:

- consolidated repository audit;
- launch policy decisions;
- privacy-preserving usage evidence;
- anti-cheat research;
- anti-cheat implementation plan;
- this authority alignment.

Its eight-file documentation patch is non-mergeable and does not repair the machine contracts. It should be closed without merge, with useful ideas retained through the canonical contracts and P-1140 tasks.

### Issue #24

Issue #24 is the tracking issue for P-1140A. It may close when the authority entrypoints, launch scope, task/decision registers, documentation map and stale PR disposition are synchronized.

## Definition of repository alignment

The repository is “on the same page” only when:

- every entrypoint reports the same phase and maturity;
- every launch-scope document excludes country boards from launch;
- every evidence document makes the server verifier authoritative;
- every privacy document and schema blocks content-bearing egress;
- every implementation document begins behind P-1140 and P-1104;
- every future path is clearly distinguished from current implementation;
- stale PRs and completion claims cannot be mistaken for authority;
- decisions, tasks, contracts, schemas, fixtures and launch gates are traceable.
