# VibeMaxxing Planning Task Catalog

Updated: 2026-08-05

Statuses: `complete-planning`, `in-progress-planning`, `blocked-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`, `authorized-open`.

A task is `complete-planning` only when its normative artifacts exist, references resolve, applicable planning checks pass, and its stated review scope is satisfied. It never implies implementation, security evidence, certification, or launch readiness.

A gate is `authorized-open` when the owner has explicitly opened it. `authorized-open` records a decision and never asserts that the gate's own preconditions were met; where they were not, the record in `conformance/p1140f/gate-authorization-v1.json` states so. Gate state is owned by that file. This catalog summarizes it.

## Historical planning groups

P-001 through P-1130 produced useful planning inputs. Where P-1140 work repairs or supersedes them, the later contract is authoritative. Historical completion reports and stale review heads are not current authority.

## Active planning-repair program

<!-- generated: task-catalog -->

### P-1140A — authority reset and launch-scope alignment

Status: `complete-planning`

Authority hierarchy, scope corrections, decision traceability, implementation-handoff ownership, and repository consolidation were established. Country leaderboards remain post-launch, native mobile/ChromeOS are out of scope, SLM remains post-launch advisory research, and implementation remains gated.

### P-1140B — core trust, privacy, and accounting contracts

Status: `complete-planning`

Typed source observations, normalized accounting, local detector results, local IPC, device lineage, accounting profiles, server-owned appraisal/pricing, and deny-by-default egress contracts are present. Their semantic implementation dependencies are reopened under P-1140F.

### P-1140C — VibeProof v1 protocol rewrite

Status: `complete-planning`

Closed deterministic CBOR/COSE contracts, exact vectors, replay/continuity/rotation/recovery plans, and malformed/resource cases are present as normative planning authority. Later executable Rust/Go prototypes do not conform to that authority and are tracked under P-1140F-1.

### P-1140D — identity, API, ranking, social, native, and release contracts

Status: `complete-planning`

Candidate contracts are present, but their semantic readiness is reopened under P-1140F. `complete-planning` here means the candidate contract set exists, not that it is implementation-ready.

### P-1140E — structural cross-contract validation

Status: `complete-planning`

P-1140E proves structural repository consistency only. It does not prove semantic correctness, standards conformance, authorization safety, privacy, runtime behavior, database transactions, platform behavior, or implementation readiness.

### P-1140F — semantic review and standards mapping

Status: `in-progress-planning`

Canonical prose record: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`.

Machine-readable authorities:

- finding state: `conformance/p1140f/semantic-findings-v1.json`;
- artifact maturity and evidence ceilings: `conformance/p1140f/artifact-authority-v1.json`;
- exact-head review state: `conformance/p1140f/review-target-v1.json`.

P-1140F has 13 active P1 clusters, SR-005 through SR-017. Current semantic work is organized into five dependency-ordered tasks.

#### P-1140F-1 — re-establish protocol and repository authority

Status: `in-progress-planning`

Scope:

- quarantine or remove the unsigned 11-field shadow protocol from normative/product paths;
- retain CDDL, COSE, and `conformance/vibeproof/v1/` as sole VibeProof v1 authority;
- enforce artifact maturity and evidence ceilings;
- rename misleading evaluation suites and fixtures;
- make status, task, semantic and review records consume the structured registries;
- register every mutable authority and persistence owner.

Blocks: all later P-1140F tasks.

#### P-1140F-2 — identity, OAuth, lineage, replay, and recovery

Status: `in-progress-planning`

Dependencies: P-1140F-1.

Scope:

- one account-bound OAuth transaction authority;
- linked-identity, provider-loss, compromise, and recovery lifecycle;
- duplicate-account consolidation and canonical ranked identity;
- lineage-scoped continuity;
- canonical challenge, checkpoint, rotation, fork, appeal, and reversal semantics.

#### P-1140F-3 — local trust boundary, adapters, source evidence, and accounting inputs

Status: `in-progress-planning`

Dependencies: P-1140F-2.

Scope:

- process trust domains, role-bound IPC, process generations, local persistence, and platform supervision;
- atomic compatibility tuples and signed certification lifecycle;
- source receipts, evidence bundles and immutable verifier appraisals under SR-017;
- deterministic observation-to-profile selection;
- nested/multi-observer deduplication and checked arithmetic;
- ACP/OTel/proxy/wrapper paths remain private until exact certification.

#### P-1140F-4 — server product state and privacy projection

Status: `in-progress-planning`

Dependencies: P-1140F-2 and P-1140F-3.

Scope:

- exact idempotent replay and ambiguous-commit recovery;
- ranking authorization, immutable generations, periods, ties, contributions, appraisals, and corrections;
- friendship, directional blocks, rivals, boards, roles, ownership, presence, and notifications;
- export, deletion, retention, legal hold, per-device completion, and backup tombstones;
- current authorization for historical snapshots, cursors, grants, and delivery.

#### P-1140F-5 — release trust and exact-head semantic closure

Status: `in-progress-planning`

Dependencies: P-1140F-1 through P-1140F-4.

Scope:

- TUF-backed release authorization;
- component, compatibility, provenance, native-signing, update-class, migration, health, and rollback contracts;
- aligned API, SQL, state, event, policy, reason, and fixture vocabularies;
- planning-safe validation;
- one new exact review head with zero active semantic P0/P1 findings.

<!-- end generated: task-catalog -->

## P-1140F acceptance

P-1140F becomes `complete-planning` only when:

1. SR-005 through SR-017 in the semantic finding registry are closed in every affected owner.
2. No executable prototype contradicts or bypasses the sole normative protocol/accounting authority.
3. Every mutable aggregate has one reachable lifecycle, persistence owner, revision model, stable outcome vocabulary, and transaction boundary.
4. API, SQL, Protobuf/CDDL, fixtures, policies, and state machines cross-resolve without hidden security-critical mappings.
5. Privacy and authorization are current at every display and delivery boundary.
6. Structural validators pass without claiming semantic proof.
7. `review-target-v1.json` binds one exact repaired commit, validation run and passing independent semantic verdict.
8. The user separately authorizes P-1104.

Criterion 8 was satisfied on 2026-08-05, out of the intended order: P-1104 was opened while criteria 1 and 7 were unmet. That ordering inversion is recorded, not corrected. Criteria 1 through 7 still bind P-1140F, and P-1140F remains `in-progress-planning`.

## Implementation and launch tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore product CI, security, dependency, evaluation, and release checks | blocked-implementation | requires executable product code to check; P-1104 is no longer the blocker |
| P-1104 | Enter implementation phase | authorized-open | opened by owner decision on 2026-08-05 under GitHub issue 44 with 13 P1 findings (SR-005 through SR-017) open and no pinned review head; preconditions accepted rather than met — see `conformance/p1140f/gate-authorization-v1.json` |
| P-1105 | Public-launch readiness review | blocked-launch-evidence | requires implemented system and executable evidence on every advertised profile |
| P-1131 | Select golden source/model paths and produce non-expired exact-tuple certifications | blocked-launch-evidence | requires real adapters, benchmarks, and conformance |
| P-1150 | Country leaderboard research and planning | blocked-launch-evidence | post-launch only |
| P-1151 | SLM detector bakeoff | blocked-implementation | post-launch after deterministic baselines and data |

## Current conclusion

Product implementation is authorized and P-1140F-1 continues alongside it. Automated product, security, evaluation, and release workflows are still disabled under `P-1007`. Certification claims and launch-readiness claims remain prohibited: `P-1105` and `P-1131` are unchanged, and no evidence has been produced by opening `P-1104`.
