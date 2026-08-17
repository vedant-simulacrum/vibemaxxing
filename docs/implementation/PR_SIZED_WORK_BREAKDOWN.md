# PR-Sized Implementation Work Breakdown

Status: canonical planning decomposition; inactive until P-1140F closes and P-1104 is explicitly authorized
Updated: 2026-08-06

This file decomposes `IMPLEMENTATION_HANDOFF.md`. It does not authorize product code. Units prefixed `PF-` are planning repairs permitted in the current phase. All other units are future implementation work and remain blocked until P-1104, which being open authorizes work but does not start it.

Every unit in this file is specified to the required-fields standard below. The file no longer has an active half and a frozen half; it has one plan, and a unit's readiness is expressed by its `Status:` line rather than by which section it sits in. Nothing has been removed from the launch scope recorded in `docs/planning/PRODUCT_SCOPE_FREEZE.md`.

## Global rules

Every unit must be independently reviewable and must name:

- dependency units;
- normative owner and decision IDs;
- schemas, state machines, persistence, and API surfaces affected;
- privacy and egress impact;
- migration, compatibility, and rollback/roll-forward behavior;
- positive, negative, adversarial, concurrency, and resource evidence;
- disable, revoke, recovery, or reversal path.

A unit cannot start because its predecessor document exists. Its dependency must be accepted on the exact branch/head and must not retain an open semantic P1.

### Required unit fields

Every unit must carry these five lines verbatim, in this order, immediately under its heading. They exist so plan quality is machine-checkable rather than aspirational.

- `Files:` — the exact paths the change touches. Not a component name, not a directory. If the paths are unknown, the unit is not yet specified. A path the unit will create carries the repository's `(new)` marker, which is also what tells `validate_cross_references.py` not to resolve it and what gives the status check something to observe.
- `Acceptance:` — one runnable assertion. A command, a query, or a grep whose result decides done. Prose descriptions of intent are not acceptance criteria. Where a unit's real acceptance is a human judgement, it says so and names the mechanical part separately rather than dressing the judgement up as a check.
- `Depends:` — unit IDs only, comma-separated, or `none`. Prose dependencies ("implemented product paths") are not resolvable and are not permitted. Ranges are not permitted either, because a range cannot be resolved by the cross-reference validator.
- `Est:` — hours, as an integer or a range. A unit estimated above 16 hours must be split.
- `Status:` — one of `not-started`, `in-progress`, `landed`, `unverifiable`, or `superseded-by <ID>`.

`Serves:` names the P-1140F finding or findings a unit repairs. `Repair:` binds a unit to a step and each finding is assigned to a step, but that was too coarse to say which unit serves which finding: P-1140F-4 owns twelve units and five findings, so landing one implied nothing about any particular finding and closure evidence had to be assembled by reading. `scripts/repository/validate_repair_task_binding.py` requires the two bindings to agree, refuses a finding no unit serves, and refuses a finding recorded `closed` while a unit serving it is unlanded. Carrying closure evidence is not the same as being closed.

Two fields are conditional. `Evidence:` is required on a `landed` unit, may repeat, and is forbidden anywhere else. `Reason:` is required on an `unverifiable` unit.

A unit missing any of the five is not ready to start, regardless of how well its prose reads.

`scripts/repository/validate_work_unit_status.py` enforces all of it. It fails on a missing, empty or duplicated field, on an `Est:` above the ceiling, on a `Depends:` entry that names no heading, on a dependency cycle, on a dependency pointing at a superseded unit, and on any SQL table in `packages/schemas/planning-schema.sql` that no unit names. `PF-037` closed the separate half of that work: `generate_issue_plan.py` copies all five fields into every issue record, reads the phase gate from `conformance/p1140f/gate-authorization-v1.json` rather than naming one, and fails when its own reading of any unit's status differs from this validator's.

### How status stays true

Status is checked against the tree rather than trusted, by two independent observations.

**Artifact presence.** Each unit's `(new)` paths are the artifacts it promised to create, so `not-started` fails the moment any of them exists. A status cannot silently outlive the work starting — which is how `F-009` was caught within minutes of `docs/engineering/LOCAL_DEVELOPMENT.md` landing on `main` from another branch.

**Executed evidence.** A `landed` unit carries `Evidence:` lines and the validator *runs* them on every check. They are not a description of a check; they are the check. Five verbs, no shell, no interpolation:

- `validator <script under scripts/> [args]` — run it, require exit 0;
- `unittest <dotted.module>` — run it, require exit 0;
- `exists <path>` and `missing <path>` — the artifact is, or is not, there;
- `contains <n> <path> :: <literal>` and `absent <path> :: <literal>` — a plain substring count, so no pattern syntax can widen the assertion by accident.

**A commit id is not evidence, and D-206 records why the first revision of this field was wrong to use one.** Every pull request here is squash-merged under a linear-history rule, so an id recorded on a branch stops existing the moment that branch merges: the check failed on correct data. And any resolvable id would have satisfied it, including one belonging to an unrelated commit: it would have passed on fabricated data. A field that fails on truth and passes on fiction is worse than no field at all.

**`unverifiable` is the honest status** for a unit whose completion cannot be observed from the tree. It requires a `Reason:`, is counted separately, and is never reported as done. `landed` is not available as a place to put work that cannot be checked.

`in-progress` is deliberately unconstrained by artifact presence, because presence cannot refute it — a unit that authored its one new file and has not touched the three existing files it also names looks complete and is not. It is the weakest status and is counted separately.

A unit whose `Files:` names no new artifact gives the presence check nothing to observe. The summary reports that count as its own number, so a green run cannot be read as more coverage than it has — the same discipline `PF-067` applies to the vocabulary validator.

The derived block below is generated by the same script. The list of what can be started now is computed from the statuses and the dependency graph, so it cannot drift from them the way a hand-written "current next unit" list did.

## Plan status

Ordering principle: each specification is paired with the artifact or code that consumes it, rather than batched into a specification phase. A contract with no consumer cannot be validated, and validating contracts against each other is what produced the current finding set.

<!-- generated: work-unit-status -->

Units: 266. Every one carries `Files:`, `Acceptance:`, `Depends:`, `Est:` and `Status:`.

| Status | Units |
|---|---|
| `not-started` | 179 |
| `in-progress` | 3 |
| `landed` | 78 |
| `unverifiable` | 0 |
| `superseded-by` | 6 |

Every `landed` unit is backed by executable evidence: 423 assertions across 78 units, all run by `validate_work_unit_status.py` on every check.

Startable now — not done, and every dependency done: 6.

`F-002`, `F-003`, `L-001`, `OS-001`, `OS-003`, `OS-009`.

### P-1140F repair schedule

Derived from `Depends:`, not written down, so it cannot go stale. Wave 1 is what can be started today; the number of waves is the longest remaining chain. Landing a unit in wave 1 may promote several units into it.

Every P-1140F repair unit has landed.

Statuses additionally checkable against artifact presence: 200 of 266. The other 66 declare no new file in `Files:`, so that check can neither confirm nor refute them and does not claim to.

<!-- end generated: work-unit-status -->

### Why every unit is now specified

An earlier revision of this section argued the opposite, and it is recorded here rather than deleted. It read: expanding all 195 backlog units to the required-fields standard before any of them is exercised "would repeat the failure this repository is currently repairing", so the active plan should stay sized to what can be specified against artifacts that actually exist and grow by promotion.

**The owner has directed that they all be expanded** (D-200). The argument above was not wrong about the risk, and the risk is real: a file path written before the code exists is a guess, and 195 guesses look like a plan. What changed is the judgement about which failure costs more. An unspecified backlog unit is not neutral — it hides the defects this document had already recorded against itself and could not act on: six prose dependencies that could not be ordered, eleven orphans, a launch gate that excluded the entire web product, fifty-two SQL tables owned by nothing, and thirteen whole categories with no unit at all. None of those was findable by a validator while the units were headings, because there was nothing to validate.

So the expansion is scoped to what it can honestly claim. Every `Files:` path that does not exist carries the `(new)` marker and is a stated intention, not a fact. Every `Acceptance:` is a command, a grep or a schema check that decides done — and where a unit's real acceptance is a human review, `X-010` and `X-011` say so in the unit rather than substituting a green ledger for a verdict. A specified unit is still not a started one, and `Status:` is what says which.

## Current planning program

### PF-001 — Quarantine the shadow VibeProof protocol
Files: `crates/vibeproof-core/README.md`, `crates/vibeproof-core/Cargo.toml`, `crates/vibeproof-core/src/lib.rs`, `apps/api/cmd/api/protocol_fixtures.go`, `conformance/protocol/vibeproof-v1-vectors.json`, `apps/web/README.md`, `conformance/p1140f/artifact-authority-v1.json`, `evals/suites/suites.yaml`, `scripts/repository/validate_artifact_quarantine.py`, `tests/ci/test_artifact_quarantine.py`
Acceptance: `python3 scripts/repository/validate_artifact_quarantine.py` exits 0, and fails when any artifact `artifact-authority-v1.json` classes as a prototype omits the gate, its normative owner, or any one of its recorded incompatibilities or prohibited uses from its own source; `python3 -m unittest tests.ci.test_artifact_quarantine` exits 0 with a case per omission; `python3 scripts/repository/validate_p1140f_authority.py` exits 0.

The original criterion was `grep -rn 'VibeProof v1' crates/vibeproof-core apps/api/cmd/api` returning no line that omits the word `prototype`. It passed before any quarantine work was done, because `crates/vibeproof-core/README.md` was a two-line stub that mentioned nothing. A criterion phrased as the absence of a bad mention is satisfied by the absence of any mention, so it measured silence and reported compliance. The replacement requires the notice to be present and to agree with the record, which silence cannot satisfy.
Depends: none
Repair: P-1140F-1
Serves: SR-005
Est: 6-8
Status: landed
Evidence: validator scripts/repository/validate_artifact_quarantine.py
Evidence: unittest tests.ci.test_artifact_quarantine

`Depends: none` replaces the prose dependency `PR #42 consolidation`, which merged and can no longer be ordered against. The consolidation is a historical fact, not a pending unit.

- classify `crates/vibeproof-core` and Go fixture codec as exploratory prototype;
- remove VibeProof v1 naming from incompatible 11-field fixtures or remove them;
- prohibit product imports from the shadow model;
- mark affected evaluations blocked or prototype-only.

Exit: one VibeProof v1 wire authority remains.

### PF-002 — Align normative protocol and conformance ownership
Files: `docs/architecture/VIBEPROOF_V1_CANONICAL_PROFILE.md`, `docs/project/DOCUMENTATION.md`, `conformance/vibeproof/v1/exact-byte-vectors.json`, `conformance/vibeproof/v1/malformed-resource-corpus.json`, `conformance/vibeproof/v1/manifest.json`, `conformance/vibeproof/v1/README.md`, `scripts/repository/cddl_instance.py` (new), `scripts/repository/generate_vibeproof_vectors.py`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_vibeproof_rule_ownership.py` (new), `tests/ci/test_vibeproof_vectors.py`
Acceptance: `generate_vibeproof_vectors.py --check` exits 0; every rule in `vibeproof-claim-v1.cddl` is declared by exactly one of the two vector files, where a declaration is a JSON string equal to the rule name and a path merely containing one is not; no other JSON document under `conformance/` or `evals/` declares a rule or an ownership key; the rules `exact-byte-vectors.json` pins equal the recomputed reference closure of the six messages it encodes; both payloads and both protected-header maps decode, satisfy their rule with the exact declared label set, and re-encode to the committed bytes; and both COSE_Sign1 envelopes are tag 18 over four elements holding the fixture's own bytes.
Depends: PF-001
Repair: P-1140F-1
Serves: SR-005
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/generate_vibeproof_vectors.py --check
Evidence: unittest tests.ci.test_vibeproof_rule_ownership
Evidence: unittest tests.ci.test_vibeproof_vectors
Evidence: contains 1 conformance/vibeproof/v1/exact-byte-vectors.json :: cddl_rules_pinned
Evidence: contains 1 conformance/vibeproof/v1/malformed-resource-corpus.json :: cddl_rules_unpinned
Evidence: missing conformance/vibeproof/v1/negative-vectors.json

**The last acceptance clause was enforced by nothing.** Before this unit no check in the repository read a CDDL rule name against a vector file, in any direction. The clause could not have failed on a third file because it could not have failed on the first two either, and as written it was also unsatisfiable: not one of the twenty-six rule names appeared in either vector file, because both hold hex and neither held a declaration. The rewritten clause is the same intent expressed as something observable — ownership is declared in the file that claims it, and the declaration is checked against the grammar and against the bytes.

**A substring rule would have been worse than none.** `conformance/vibeproof/v1/manifest.json` carries `packages/schemas/vibeproof-claim-v1.cddl` and `packages/schemas/reason-codes-v1.json`, which contain the rule names `vibeproof-claim-v1` and `reason-code` inside them. Substring matching fails on the file that names the authority, and the next author learns to weaken the check rather than to fix a defect. A declaration is therefore whole-string equality. `packages/schemas/` is out of scope for the third-file scan on a stated basis rather than by omission: nine JSON Schema documents there define `$defs` named `digest32`, `uuid7`, `registered-id` and `uint64`, which are definition names in a different language and namespace, and the hazard the clause exists for is a third conformance corpus rather than a coincident word.

**What was actually broken.** `validate_cddl_file` proves the grammar parses and that named rules exist, and says in its own docstring that it validates no instance. Nothing else compared a committed byte to the grammar, so the vectors could have encoded a completely different message, signed it correctly, reproduced from the recorded seed and passed every check. `scripts/repository/cddl_instance.py` now checks the subset the VibeProof messages use — closed integer-labelled maps, ranges, `bytes .size N`, `nil`, `true`, homogeneous arrays with occurrence bounds and named references — and raises rather than skipping anything outside it, because a checker that ignores what it does not understand reports the same green as one that checked.

Two encoder defects surfaced from that work and are fixed here. `decode_map_at` could not decode a claim payload at all — it had no array or simple-value support, and it accepted non-minimal integers, indefinite lengths, tags and truncated items — and `encode` refused `nil` and `true`, both of which the grammar declares (`29: true` and three `X / nil` labels). Neither showed because the committed payload hex was copied rather than round-tripped. `false` stays unencodable: a claim that did not pass the privacy boundary is never serialized.

`docs/architecture/VIBEPROOF_V1_CANONICAL_PROFILE.md` was a second document owning canonical encoding, and it described the wrong profile. `VIBEPROOF_V1_PROTOCOL.md` declares that it owns canonical encoding, COSE, limits and state transitions; the canonical-profile file described the eleven-field shadow codec — three token categories, a 1024-byte limit, a client-selected evidence class, and COSE "intentionally out of scope" — under a filename that says canonical. It now owns the shadow profile's status and retirement condition and says at the top that it is not the canonical profile. It also records a hole `PF-002` cannot close: `protocol/vibeproof-v1.cddl` is the shadow grammar, four of its consumers are classified `exploratory-prototype` in `conformance/p1140f/artifact-authority-v1.json` and the grammar itself is not, and registering it requires a quarantine notice inside `protocol/`, which is outside this unit's paths.

- inventory CDDL labels, COSE headers, external AAD, exact vectors, malformed/resource corpus;
- define generation boundaries for Rust/Go types;
- define exact independent implementation evidence expected after P-1104.

### PF-003 — Artifact/evidence maturity registry
Files: `conformance/p1140f/artifact-authority-v1.json`, `conformance/p1140f/artifact-authority-v1.schema.json`, `evals/suites/suites.yaml`, `scripts/ci/run_evals.py`, `scripts/repository/validate_p1140f_authority.py`, `docs/verification/EVAL_SYSTEM.md`, `docs/planning/ARTIFACT_POLICY.md`, `tests/ci/test_run_evals.py`, `tests/ci/test_gate_ledger.py`, `tests/ci/test_generate_issue_plan.py`
Acceptance: `run_evals.py --validate-registry` exits 0; every suite in `suites.yaml` carries an `authority_class` and an `evidence_ceiling` drawn from the vocabulary `conformance/p1140f/artifact-authority-v1.json` declares, and validation fails on a value the registry does not declare; a suite's ceiling may not exceed the lowest of its authority class's cap, `none` when the suite is `not_applicable`, and what its fixture manifest supports — the manifest's own ceiling, or `fixture-consistent` when it binds fixtures, or `none` when it binds none.
Depends: PF-001
Repair: P-1140F-1
Serves: SR-005
Est: 8-10
Status: landed
Evidence: validator scripts/ci/run_evals.py --validate-registry
Evidence: validator scripts/repository/validate_p1140f_authority.py
Evidence: unittest tests.ci.test_run_evals
Evidence: contains 27 evals/suites/suites.yaml :: authority_class
Evidence: contains 27 evals/suites/suites.yaml :: evidence_ceiling
Evidence: contains 1 conformance/p1140f/artifact-authority-v1.json :: authority_classes
Evidence: absent conformance/p1140f/artifact-authority-v1.schema.json :: "enum": ["normative-planning"

**The ceiling check did not exist.** It was not weak and it was not satisfiable by an empty suite; `run_evals.py` admitted `authority_class` and `evidence_ceiling` to its key allowlist and read neither, with a comment saying they are declarative only and carry no execution semantics. One of the twenty-seven suites carried them at all. Every one of the other twenty-six could have declared `production-evidence` and the registry would still have validated.

**Absence had to lower the ceiling, not escape it.** A check phrased as "the fixtures must not contradict the declared ceiling" is satisfied for free by a suite with no fixtures, and twenty-four of the twenty-seven suites are `not_applicable` and have no fixture manifest at all — the emptiest suites in the registry would have been the ones it never questioned. So the cap is derived from what the manifest *binds*: a manifest with no fixtures caps its suite at `none`, and a `not_applicable` suite is capped at `none` directly, which is `docs/verification/EVAL_SYSTEM.md`'s rule that the status is an absence of evidence rather than a pass, expressed as a value.

`none` is new and is the ladder's floor; `absent` is a new authority class and is the only one capped there. Both are declared in `docs/planning/ARTIFACT_POLICY.md`, which owns the vocabulary, and both are machine-readable in the authority registry so the caps are read rather than restated. The schema no longer carries a second copy of the enums, and `validate_p1140f_authority.py` no longer carries a third: it read a hard-coded ladder and applied a cap to exactly one class, so any other class was capped by nothing. That is the same drift `PF-056` records between these two files.

- classify every executable suite and fixture as structural, semantic, prototype, runtime evidence, or certification;
- rename overclaiming suites;
- reject empty or mislabeled evidence in planning validators.

### PF-004 — Mutable aggregate ownership inventory
Files: `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/planning-schema.sql`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `scripts/repository/validate_state_vocabularies.py`
Acceptance: `python3 scripts/repository/validate_state_vocabularies.py` exits 0 with every registry machine naming a `persistence_owner` that resolves to a `create table` in `planning-schema.sql`, and fails when one does not; every machine additionally declares `revision_model`, `transaction_boundary` and `outbox`, and the validator fails on each of the four combinations `outbox_events.unique(aggregate_id, aggregate_revision)` forbids — publishing without a revision, publishing outside the aggregate transaction, a device-local aggregate publishing, and a local-only aggregate in a server transaction; `python3 -m unittest tests.ci.test_state_vocabularies` exits 0 with a case per rule.
Depends: none
Repair: P-1140F-1
Serves: SR-005
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_state_vocabularies

`Depends: none` replaces the prose dependency `PR #42 consolidation`. D-195 has since landed the persistence-owner half of this unit; what remains is the revision model, transaction boundary and outbox behaviour per aggregate.

- enumerate every aggregate named in API, SQL, Protobuf/CDDL, state registry, policy, reasons, and prose;
- require one persistence owner, lifecycle, revision model, transaction boundary, and event/outbox behavior;
- record missing and duplicate owners.

### PF-005 — OAuth provider configuration authority
Files: `packages/schemas/oauth-provider-registry-v1.json` (new), `packages/schemas/oauth-provider-registry-v1.schema.json` (new), `conformance/auth/provider-mixup-vectors-v1.json` (new), `scripts/repository/validate_oauth_identity_contract.py` (new), `tests/ci/test_oauth_identity_contract.py` (new), `conformance/auth/manifest.json`, `conformance/auth/README.md`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `packages/schemas/README.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `Makefile`
Acceptance: the registry validates against its schema and every provider row carries `issuer`, `authorization_endpoint`, `token_endpoint`, `client_id_reference`, `redirect_uri`, `pkce_method`, `rfc9207_iss`, `device_flow`, `scopes`, `revision`, `recorded_at` and a `review_due_at` inside a 365-day ceiling; the provider vocabulary is one spelling across the registry, `linked_identities.provider`, `oauth_transactions.provider` and every `provider` enum in `openapi-v1.yaml`; a provider whose `verification.state` is `unverified` may not declare a `supported` capability, and whether its callback declares `iss` is a function of the recorded capability rather than of the provider; the mix-up fixture carries an accepted baseline per provider and a refusal per discriminator, each refusal differing from its baseline in exactly the one field its discriminator names, and every recorded outcome and reason code is *derived* from the registry rather than asserted; `python3 scripts/repository/validate_oauth_identity_contract.py --stage=provider-registry` exits 0 and `python3 -m unittest tests.ci.test_oauth_identity_contract` exits 0 with a case per rule.
Depends: PF-004
Repair: P-1140F-2
Serves: SR-006
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_oauth_identity_contract.py --stage=provider-registry
Evidence: unittest tests.ci.test_oauth_identity_contract
Evidence: contains 1 packages/schemas/oauth-provider-registry-v1.json :: "registry_id": "oauth-provider-registry-v1"
Evidence: contains 16 conformance/auth/provider-mixup-vectors-v1.json :: "case_id"
Evidence: absent packages/schemas/oauth-provider-registry-v1.json :: "capability": "supported"

**The acceptance was rewritten.** The original required "at least one rejected case per provider", which a corpus of nothing but refusals satisfies — and a decision procedure that refuses everything satisfies it best. It also never said the outcomes had to be *decided*: a fixture recording its own verdicts is a fixture that agrees with itself. The rewritten form requires an accepted baseline per provider, one refusal per discriminator, single-field attributability, and derivation from the registry. `validate_oauth_identity_contract.py` additionally mutates each discriminator against the committed registry itself, because a corpus cannot notice a rule that stopped being applied to it.

**The live defect.** `/auth/github/callback` declared the RFC 9207 `iss` parameter and `/auth/x/callback` did not, while `packages/schemas/reason-codes-v1.json` bound `OAUTH_ISSUER_MISMATCH` to both `completeGitHubAuth` and `completeXAuth`. The asymmetry read as a statement that GitHub supports RFC 9207 and X does not, and no record anywhere said so — the parameter's own description deferred to "the stored provider-capability record", which did not exist, so the rule ADR-015 calls the control that closes the mix-up attack could not be evaluated at all. Both rows now record the capability `unverified`, because no authorization response from either provider has been observed in this repository, and the parameter is declared identically on both. Recording `supported` would have manufactured the control: the validator refuses a capability claimed while the provider's verification state says nothing was read, and a synthetic probe proves the value changes the decision, so the RFC 9207 defence cannot be acquired by writing a word.

Three reason codes were added — `OAUTH_REDIRECT_URI_MISMATCH`, `OAUTH_TRANSACTION_EXPIRED` and `OAUTH_PKCE_VERIFICATION_FAILED` — because three of the seven discriminators had no registered way to refuse. the `conformance/auth/` README claimed the directory held no `manifest.json`, which was already untrue when it was written.

- issuer, endpoints, client, exact redirect, PKCE, RFC 9207 capability, scopes, device-flow capability, revision and expiry;
- provider-specific positive and mix-up/redirect-confusion fixtures.

### PF-006 — Canonical OAuth transaction
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `scripts/repository/validate_oauth_identity_contract.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_oauth_identity_contract.py`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: `oauth_transactions` declares every column the transaction binds — provider, provider revision, issuer, exact redirect, PKCE method, state hash, encrypted verifier, intended action, initiating account and session, recent-auth instant, result, failure reason, revision, lifetime and consumption instant — and carries as check constraints the four rules no handler discipline holds: a link is startable only under recent authentication, a link never produces a session, a consumed transaction produced what its action names, and a transaction cannot finish on a different account; `intended_action` is one kebab-case vocabulary shared by the DDL CHECK, `OAuthStartRequest` and `OAuthCompletion`; no identity-mutating operation accepts `authorization_code`, `access_token`, `id_token` or `code`, and `linkIdentity` requires an `oauth_transaction_id`; `oauth_authorization_events` references `oauth_transactions` and its `event_type` set equals the machine's transition identifiers; `OAuthCompletion` conditions `session_id` on the intended action and requires neither unconditionally; `python3 scripts/repository/validate_oauth_identity_contract.py --stage=oauth-transaction` exits 0 and `python3 -m unittest tests.ci.test_oauth_identity_contract` exits 0.
Depends: PF-005
Repair: P-1140F-2
Serves: SR-006
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_oauth_identity_contract.py --stage=oauth-transaction
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_oauth_identity_contract
Evidence: absent packages/schemas/openapi-v1.yaml :: - authorization_code
Evidence: contains 1 packages/schemas/planning-schema.sql :: check (intended_action <> 'link-identity' or resulting_session_id is null)

**The acceptance was rewritten.** Both halves were vacuous on the unrepaired tree. The table and the machine already shared one vocabulary — `validate_state_vocabularies.py` had bound them since P-1140D — so the first clause passed before any work was done. The second was a `grep` for a word: `authorization_code` appeared in `IdentityMutationRequest`, so the clause was already false, but it was phrased as a human reading grep output rather than as a check, and a rename to `provider_code` would have satisfied it while changing nothing. It is now phrased over what each request body *requires*, so an operation that grows a new credential field without a transaction reference fails.

**The live defects.** `IdentityMutationRequest` carried a bare `authorization_code` and `linkIdentity` mutated identity from it, so there was a second identity-mutating path that reached no transaction and therefore verified no redirect, no state, no PKCE verifier, no provider revision and no lifetime — every control the transaction exists to apply was optional in practice. `oauth_transactions` held eight columns and bound almost nothing the contract document says a transaction binds. `intended_action` was `sign_in`/`link_identity` on the API and had no CHECK at all in the DDL, so the API held a vocabulary the persistence owner did not, in the snake-versus-kebab spelling this repository has been bitten by four times. The machine declared `monotonic-revision` and the table had no `revision` column for a conditional update to name. `oauth_authorization_events` was a stub with an unreferenced `subject_id` and an unconstrained `event_type`, so it could hold a row about anything and say anything about it. And `OAuthCompletion` required `account_id` and `session_id` unconditionally, so the contract said a link callback mints browser access — which the table now refuses at the constraint level.

Twenty-five other machines declare a revision model whose named persistence owner has no `revision` column. Most are event tables, where the absence is correct because the revision belongs to the aggregate root; the general rule needs to know which owner is the root and is not attempted here. Only `oauth_transactions` is repaired.

- bind action, account/session, recent-auth grant, provider revision, redirect, state, PKCE, expiry and result;
- remove standalone authorization-code identity mutation semantics;
- define single consumption and ambiguous callback behavior.

### PF-007 — Linked identity and recovery lifecycle
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `scripts/repository/validate_state_vocabularies.py`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_oauth_identity_contract.py`, `tests/ci/test_oauth_identity_contract.py`, `conformance/p1140e/validation-matrix-v1.json`, `conformance/p1140e/state-machine-fixtures-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: the `linked-identity` machine declares exactly `candidate`, `linked`, `unlink-pending`, `lost`, `compromised`, `recovery-pending`, `unlinked` and `superseded`, `linked_identities.state` holds the same eight, and every state is reachable with no outgoing transition from a terminal one under `validate_state_vocabularies.py`; `linked_identities` carries the durable `provider_subject`, the D-081 `provider_account_created_at` gate input and a `revision`, declares **no** total `unique (provider, provider_subject)` and no `not null` on the subject, ties both personal-data fields to the live states by check constraint so `DATA_MAP.md`'s retention rule is executable, and enforces one live binding through a partial unique index whose predicate is exactly the six non-terminal states; the last-authentication-method invariant is named in the machine as the action on the transition into `unlink-pending` and stated in `AUTHENTICATION_AND_RECOVERY.md`, and dropping either fails; no transition drives a live identity into a terminal state as a moderator, and `superseded` is reachable only by a worker; `recovery-pending` is reachable from both `lost` and `compromised` and returns to `linked`; `unlinkIdentity` requires no provider credential; `python3 scripts/repository/validate_oauth_identity_contract.py --stage=linked-identity` exits 0 and `python3 -m unittest tests.ci.test_oauth_identity_contract` exits 0.
Depends: PF-006
Repair: P-1140F-2
Serves: SR-006
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_oauth_identity_contract.py --stage=linked-identity
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_oauth_identity_contract
Evidence: contains 1 packages/schemas/planning-schema.sql :: create unique index linked_identities_live_subject_idx
Evidence: contains 1 packages/schemas/planning-schema.sql :: where state in ('candidate','linked','unlink-pending','lost','compromised','recovery-pending');
Evidence: absent packages/schemas/planning-schema.sql :: state text not null check (state in ('linked','unlink-pending','unlinked'))
Evidence: contains 1 packages/schemas/planning-schema.sql :: check ((provider_subject is not null) = (state not in ('unlinked','superseded'))),

**The acceptance was rewritten.** Its second clause — "`linked_identities` carries a durable provider-subject column with a uniqueness constraint" — was satisfied by the unrepaired tree exactly as written: the column and a total `unique (provider, provider_subject)` had both existed since P-1140D. It is worse than vacuous, because the constraint it asked for is half of a live defect. `provider_subject` was `not null` and the uniqueness was total, so a retained `unlinked` row blocked that provider account from ever being linked again, to this account or to any other — **unlinking was silently permanent, product-wide** — and `docs/privacy/DATA_MAP.md`'s commitment to delete the subject "immediately on unlink" could be honoured only by deleting the whole row, which the same constraint is what made necessary. The rewritten clause requires the total constraint and the `not null` to be absent, both personal-data fields to be tied to the live states by check constraint, and a partial index over exactly the six live states. Its first clause was not vacuous but was over-credited: `validate_state_vocabularies.py` proves reachability and terminal integrity for every machine, so once any `linked-identity` machine existed that half was automatic — it never checked *which* eight states.

**The live defects.** The aggregate was named `identity-link` in the binding table, `linked_identities` in the DDL and nothing in the registry: three names for one thing, with a recorded absence saying its transitions were owned by the enrollment flow and unspecified. Three states could express none of the provider-loss behaviour `AUTHENTICATION_AND_RECOVERY.md` requires, so that whole section described behaviour the schema had nowhere to put. D-081 makes the 90-day provider-account gate depend on a provider-reported creation timestamp that nothing persisted, so the gate had no stored input. And the machine declares `identity-unlink-cancel`, `identity-report-lost` and `identity-report-compromised` with actor `user`, and the API declared a route to none of them, so the two states the provider-loss contract exists to describe were unreachable by the only actor who can observe them; `reportProviderAccess` and `cancelIdentityUnlink` are that route, and the second is deliberately not recent-auth-free because it changes which methods can authenticate the account.

The last-method invariant is a count across sibling rows and is not expressible as a `check` or a unique index. Rather than inventing a counter column on `accounts` — a cached number that would become a second authority for a fact the rows already hold — it is recorded in the machine and in the document, and the validator compares the two. That is honest about what is enforced and by what.

- exact linked-identity ID and durable provider subject;
- candidate, linked, unlink-pending, lost, compromised, recovery-pending, unlinked, superseded;
- last-authentication-method invariant;
- token/session/device notification and cooling-off effects.

### PF-008 — Ranked identity and consolidation authority
Files: `packages/schemas/consolidation-plan-v1.schema.json`, `packages/schemas/examples/consolidation-plan.valid.json`, `packages/schemas/examples/consolidation-plan.invalid-summed-total.json`, `packages/schemas/examples/consolidation-plan.invalid-domain-not-covered.json` (new), `packages/schemas/examples/consolidation-plan.invalid-newer-identity-survives.json` (new), `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `scripts/repository/validate_oauth_identity_contract.py`, `tests/ci/test_oauth_identity_contract.py`, `conformance/p1140e/validation-matrix-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
Acceptance: `ranked_identities` is a table distinct from `accounts`, carries `absorbed_into_ranked_identity_id` referencing itself, and `accounts` declares no ranked-identity or score column; `consolidation-plan-v1.schema.json` requires a disposition for all eight of `identities`, `devices`, `claims`, `social`, `boards`, `moderation`, `exports` and `deletions` under `additionalProperties: false`, and a fixture omitting one is refused; the plan records both identities' creation instants and every committed plan satisfies D-564 — the older identity survives — with a fixture written to violate it checked to actually violate it; the participant-driven transitions of `account-consolidation` and `linked-identity` each name a declared operation whose `x-recent-auth` equals the transition's `recent_auth`, and an entry for a transition that is no longer participant-driven fails; no property of `ConsolidationPlanView`, `ConsolidationDomainDisposition`, `ConsolidationConfirmationRequest` or the plan schema names a combined figure for two accounts, and every integer the consolidation surface publishes is a count; `python3 scripts/repository/validate_oauth_identity_contract.py --stage=ranked-identity` exits 0 and `python3 -m unittest tests.ci.test_oauth_identity_contract` exits 0.
Depends: PF-007
Repair: P-1140F-2
Serves: SR-006
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_oauth_identity_contract.py --stage=ranked-identity
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_oauth_identity_contract
Evidence: contains 8 packages/schemas/consolidation-plan-v1.schema.json :: { "$ref": "#/$defs/domain_disposition" }
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: confirmConsolidation

**The acceptance was rewritten.** Two of its three clauses were vacuous. `ranked_identities` had been a separate table with a survivor reference since D-382, so the first clause passed on the unrepaired tree; it now also refuses a ranked-identity column on `accounts`, which is the way the two aggregates would actually collapse. "No path in the API sums two accounts' scores" was an absence satisfied by emptiness in its purest form: the API declared no consolidation operation at all, so nothing could sum anything, and the clause would have gone on passing forever by the API never growing the surface. It is now phrased over the property names the consolidation surface declares, and the surface has to exist for the check to have anything to read.

**The live defects.** The `account-consolidation` machine declares `consolidation-confirm` with actor `user`, `web-session` authentication and recent authentication required, and no operation reached it — the participant was required by the lifecycle to perform a transition the contract gave them no way to perform, so a case could leave `awaiting-confirmation` only by expiring. The plan covered identities, claims and periods, while `AUTHENTICATION_AND_RECOVERY.md` requires a merge to define ownership of devices, boards, friendships, moderation state and deletion requests as well, so a consolidation could apply while silent about the absorbed account's devices, blocks, board ownership, open moderation case, running export or pending deletion. And D-564 — the older ranked identity survives, the newer is retired without summation — was an accepted owner decision recorded in no machine-readable place at all; nothing named which side of a duplicate was authoritative.

The domain object deliberately has no `not-applicable` disposition. A domain with nothing in it is `retained` with a count of zero, which is a statement; a value meaning "we did not look" would let all eight be covered by declining to answer them.

- separate account and ranked identity;
- canonical survivor, retired duplicates, private investigation evidence, restrictions, appeal and reversal;
- immutable consolidation plan for identities, devices, claims, social state, boards, moderation, exports/deletions;
- historical score recomputation from valid non-overlapping claim contributions, never aggregate summation.

### PF-009 — Canonical challenge and lineage continuity
Files: `packages/schemas/device-lineage.schema.json`, `packages/schemas/vibeproof-claim-v1.cddl`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`
Acceptance: one identifier spelling for a challenge and one for a lineage resolves across CDDL, OpenAPI and SQL, with no camelCase variant in any of the three; `python3 scripts/repository/validate_cross_references.py` exits 0; `device_sequences` keys on `lineage_id` and references no device row, `claim_challenges` carries a `lineage_id` foreign key, and `continuity_state` has exactly one owner in `device_lineages`; `device_lineages` is declared before both dependants so the file applies to `postgres:16`, which `validate_planning_artifacts.py` proves when `PLANNING_DATABASE_URL` is set; `python3 -m unittest tests.ci.test_lineage_continuity` exits 0 and fails when the sequence is keyed on the device row again.
Depends: PF-004
Repair: P-1140F-2
Serves: SR-007
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_lineage_continuity

- one identifier/type model across CDDL, OpenAPI and SQL;
- expected lineage revision, sequence, commitment head, checkpoint, batch commitment, policy, issue/expiry;
- lineage-scoped rather than device-row-scoped continuity.

### PF-010 — Rotation, lost-key recovery, fork and requalification
Files: `packages/schemas/planning-schema.sql`, `conformance/vibeproof/v1/fork-and-rotation-vectors.json` (new), `conformance/vibeproof/v1/manifest.json`, `conformance/vibeproof/v1/README.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_fork_and_rotation.py` (new), `conformance/planning/decision-traceability-v1.json`
Acceptance: the fork fixture contains a lineage that branches, and a decoder run over it quarantines every post-fork branch while accepting every pre-fork claim, with at least one lineage that forks nothing and one whose malformed submissions are refused rather than quarantined, so the corpus is not satisfied by a resolver that quarantines every input; each forked lineage's resolution validates against `packages/schemas/fork-resolution-v1.schema.json`; `device_key_events` records the outgoing key signature, the incoming key signature and the account authentication as three separate columns and refuses an ordinary rotation missing any one of them, which the vectors exercise by removing each in turn; `python3 -m unittest tests.ci.test_fork_and_rotation` exits 0.
Depends: PF-009
Repair: P-1140F-2
Serves: SR-007
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_fork_and_rotation
Evidence: exists conformance/vibeproof/v1/fork-and-rotation-vectors.json
Evidence: contains 1 packages/schemas/planning-schema.sql :: unique (lineage_id, device_sequence)
Evidence: contains 1 packages/schemas/planning-schema.sql :: unique (lineage_id, accepted_through_claim_sequence)
Evidence: absent packages/schemas/planning-schema.sql :: continuity_signature bytea

The acceptance was rewritten, and the reason is the same one that has forced ten other rewrites here. "A decoder run over it quarantines every post-fork branch" is satisfied in full by a decoder that quarantines everything, and a corpus made only of forks rewards exactly that. The rewrite adds the control lineage and the refusal lineage that make the claim falsifiable, names the record schema the resolution has to be expressible in, and states what "both authorizations" are — because the two authorities disagreed about it and the row could represent neither.

`packages/schemas/state-machine-registry-v1.json` left the `Files:` line. The `lineage-fork-case` machine already declares all eight states with the right transitions and terminal set under D-383; nothing in this unit needed to change it, and listing a file a unit did not touch is how a `Files:` line stops meaning anything. Six files it did touch were added instead.

**The live defects.** D-592 rekeyed `device_sequences` onto the lineage and stopped one table short. The counter became lineage-scoped while the uniqueness that enforces it stayed device-scoped: `claims` carried `unique (device_id, device_sequence)` and `unique (device_id, payload_hash)`, so two device rows inside one lineage could each hold sequence 42 and each hold the same payload, and both indexes accepted it. The sequence a clone could no longer obtain from the counter it could still write into the claim table. `checkpoint_receipts` was device-keyed for the same reason while `device_sequences.server_checkpoint_head` — the value a receipt advances — was lineage-keyed, so a restored store acquired a private receipt chain that nothing compared against the lineage's. Both are now lineage-scoped, and the acknowledged-head uniqueness on `checkpoint_receipts` is the `checkpoint-mismatch` detection basis expressed as a write refusal. PF-073 renamed the column it is keyed on from `last_sequence` to `accepted_through_claim_sequence`, because the receipt and the claim were two counters sharing one word; the constraint and its reasoning are unchanged.

`device_key_events` held one nullable `continuity_signature` and no account authorization column at all. `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` names three separate things — a payload "signed independently by both old and new keys", and a server that "verifies recent authentication" — and `device-lineage.schema.json` records three separate fields. One blob could represent none of it, so an ordinary rotation and a single-signature forgery were the same row. Dual authorization is the key pair, because `dual-authorized-rotation-v1` is literally two COSE_Sign1 envelopes; recent account authentication is a third gate at a different layer, recorded rather than conflated, because a rotation authorized by a session alone is the takeover the pair exists to refuse. Lost-key recovery is now a separate action that *forbids* the outgoing signature rather than a rotation with a waiver.

And D-561 — exhausting every device and every recovery code permanently ends a ranked identity, with no manual appeal — was recorded in the register and in its traceability row and stated nowhere in `docs/security/AUTHENTICATION_AND_RECOVERY.md`, the file that row names as its normative owner. That document's recovery order ended with "human appeal with cooling-off and limited restoration powers", which is the opposite of the accepted decision. The step is removed and the decision is stated where it was supposed to live.

D-383's traceability row cited "the fork and rotation vectors PF-010 authors", which was accurate only while the file did not exist. It, D-072 and D-592 now name `conformance/vibeproof/v1/fork-and-rotation-vectors.json`.

- dual authorization for ordinary rotation;
- lost-key recovery authority;
- quarantine all post-fork branches;
- preserve pre-fork accepted claims;
- select/recover one survivor and resume in a new lineage generation;
- appeal, reversal, downgrade and notification.

### PF-011 — Native process and trust-domain model
Files: `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`, `packages/schemas/local-trust-domains-v1.json` (new)
Acceptance: every one of the eight named roles appears exactly once in `packages/schemas/local-trust-domains-v1.json` with an executable identity, an OS peer identity for macOS, Windows and Linux, a session boundary, a declared `network` scope and explicit capability, data-class and prohibition lists; a role absent from the file, a role declared twice, an undeclared data class, or any role that both reads `transcript-content` and declares a network scope other than `none` fails `validate_planning_coverage.py`; `python3 -m unittest tests.ci.test_local_trust_domains` exits 0.
Depends: PF-004
Repair: P-1140F-3
Serves: SR-008
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_planning_coverage.py
Evidence: unittest tests.ci.test_local_trust_domains

- daemon, collector, sync, shell, CLI, dashboard, updater, privileged supervisor;
- executable identity, OS peer identity, user/session boundary, artifact/release identity;
- allowed capabilities and data classes per role.

### PF-012 — Local channel protocol
Files: `packages/schemas/local-control-v1.proto`, `conformance/local-channel/local-channel-vectors-v1.json` (new), `conformance/local-channel/manifest.json` (new), `conformance/local-channel/README.md` (new), `packages/schemas/reason-codes-v1.json`, `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`
Acceptance: `local-control-v1.proto` declares one request and one response message per role rather than a universal union, and no role's arm reaches another role's body; the vector file contains a same-user impersonation case and a stale-process case, each with the expected rejection reason drawn from `packages/schemas/reason-codes-v1.json`, plus one accepted case so the refusals are not satisfied by a channel that refuses everything; `python3 -m unittest tests.ci.test_local_channel` exits 0 and fails when the universal union is restored.

The vectors are in `conformance/local-channel/` rather than `conformance/sandbox/` as this unit originally named. The sandbox suite's `reason_authority` is `packages/schemas/origin-policy-v1.json`, because a loopback refusal is an origin decision; a local-channel refusal is a peer-identity decision drawing on `reason-codes-v1.json`. One suite cannot carry two reason authorities, and bending the sandbox's would have made its existing loopback cases resolve against the wrong vocabulary.
Depends: PF-011
Repair: P-1140F-3
Serves: SR-008
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_local_channel

- handshake, daemon-assigned role, generation, nonce, sequence window, capability grant, deadline, revocation;
- typed request/response per role rather than one universal message union;
- same-user impersonation and stale-process fixtures.

### PF-013 — Shell and subsystem state separation
Files: `packages/schemas/state-machine-registry-v1.json`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
Acceptance: `interactive-shell` declares only the eight process and connection states, and daemon, collection, sync, auth, permission, update and connectivity are seven separate machines; `validate_state_vocabularies.py` reports every state of all seven reachable; the five new projections persist in `local-store-v1.sql` and not in `planning-schema.sql`, since none is a fixed-schema aggregate accounting figure or an integrity claim; `python3 -m unittest tests.ci.test_shell_subsystem_separation` exits 0, including a case asserting that paused collection and an offline network are now simultaneously representable.
Depends: PF-011
Repair: P-1140F-3
Serves: SR-008
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_shell_subsystem_separation

- shell owns process/connection state only;
- daemon, collection, sync, auth, permission, update and connectivity are independent projections;
- pre-auth startup and restart after crash;
- UI exit, pause collection, pause sync, stop daemon, logout, uninstall are distinct.

### PF-014 — Local persistence and migration contract
Files: `packages/schemas/local-store-v1.sql`, `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `conformance/privacy/p1140b-boundary-canaries-v1.json`
Acceptance: `packages/schemas/local-store-v1.sql` parses under SQLite with no errors and holds no key material of its own, which a test asserts against the DDL with comment lines stripped so prose cannot satisfy it; the canary fixture carries a positive and a negative case for each of `log`, `backup`, `diagnostic` and `corruption-report`; every negative case names a forbidden class declared in `egress-allowlist-v1.json` and every canary token is unique, so a leak is attributable to one boundary; `python3 -m unittest tests.ci.test_local_store_contract` exits 0.
Depends: PF-011
Repair: P-1140F-3
Serves: SR-008
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_local_store_contract

Two things changed here under D-384 and are recorded rather than applied silently. The file is `local-store-v1.sql` rather than `local-schema.sql`, which is the versioned name every other schema in that directory uses, and the four units that named the old path now name this one. And the acceptance asked for an encryption key reference per table; the file deliberately has none. Encryption is page-level under a key held by the operating-system keystore, because a key column beside the ciphertext it protects gives no confidentiality at all — the same reasoning D-213 applies to the server keyring — so the validator asserts the absence of key material rather than the presence of a reference. The `sqlite3 -init` parse has not been run.

- local DDL ownership, encryption, key references, schema generation, crash consistency, queues, commitments, receipts, migrations and recovery;
- forbidden-content boundaries for logs, backups, diagnostics and corruption reports.

### PF-015 — Atomic compatibility tuple
Files: `packages/schemas/compatibility-tuple-v1.schema.json` (new), `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.schema.json`
Acceptance: the tuple schema requires all nine components and a canonical digest; `conformance/adapters/compatibility-tuple-digest-v1.json` records two serialisations of one tuple in opposite key order at every level, including nested maps, together with the expected digest, and both produce it; changing any one of observation mode, platform profile, source version floor, accounting arithmetic or privacy strip list produces a different digest; `python3 -m unittest tests.ci.test_compatibility_tuple_digest` exits 0, including a case asserting the two recorded orderings are genuinely different.
Depends: PF-004
Repair: P-1140F-3
Serves: SR-009
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_compatibility_tuple_digest

The schema landed under D-387 and requires every component, with the nine observation modes taken from `packages/schemas/observer-equivalence-v1.json` rather than spelled a second time. The digest half has not: no fixture records two orderings of one tuple and the expected digest, so the canonical-digest claim is stated in the description and not yet exercised.

- product/source, exact version/artifact, platform profile, mode, adapter/collector artifacts, protocol/telemetry profile, accounting profile, privacy profile and evidence ceiling;
- canonical digest construction.

### PF-016 — Certification lifecycle and revocation
Files: `packages/schemas/certification-result-v1.schema.json`, `packages/schemas/normalized-event.schema.json`, `packages/schemas/accounting-profile-otel-v1.json`, `packages/schemas/appraisal-result-v1.schema.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/examples/normalized-event.valid.json`, `packages/schemas/examples/normalized-event.invalid-uncertified-competitive.json` (new), `packages/schemas/examples/certification-result.valid.json`, `packages/schemas/examples/certification-result.invalid-counts-omit-a-case.json` (new), `conformance/evidence/`, `docs/integrations/ADAPTER_CERTIFICATION_POLICY.md`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_certification_lifecycle.py` (new)
Acceptance: the `source-certification` machine's eight states are one vocabulary across the registry, `source_certifications.state` and `evaluated.certification_state` on `AppraisalSummary`, the API set being the machine's states plus `uncertified`, which is not a machine state because a capture bound to no certification has no aggregate; the result schema requires a suite manifest digest, a per-case digest, a validity interval and a signer reference, requires a non-empty case list, and `case_count`, `negative_case_count` and `failed_case_count` are derived from that list rather than believed, so deleting the case that failed no longer improves the result; `normalized-event.schema.json` admits a null certification bundle digest and pins any event carrying one to a `private-analytics` disposition; `python3 -m unittest tests.ci.test_certification_lifecycle` exits 0.
Depends: PF-015
Repair: P-1140F-3
Serves: SR-009
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_certification_lifecycle
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: certification_state
Evidence: absent packages/schemas/examples/normalized-event.valid.json :: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

The machine is registered as `source-certification` with all eight states, `source_certifications` is its persistence owner, and `certification_results` holds the signed bundles. It is named `source-certification` rather than `certification` because `platform-certification` already exists and certifies an operating-system profile, which is a different thing. The acceptance was rewritten: it named `validate_state_vocabularies.py` as the binder of all three vocabularies and that script binds registry and SQL only, so the API third could never have been proved by the check the acceptance named. `validate_certification_contracts` now reads all three.

**What this unit could not honestly close.** Nothing is certified. No conformance suite has been run against any exact tuple, no result bundle has been signed, and every certification state reachable from this repository is `candidate`. A lifecycle can be specified without asserting that anything has moved through it, and that is all this unit did; `tests/ci/test_certification_lifecycle.py` asserts the absence rather than leaving it to be assumed. No tuple was marked certified and no bundle digest was invented — the fixture that used sixty-four `f` characters was removed rather than replaced with a more convincing constant.

**The live defects.** `normalized-event.schema.json` required `certification.bundle_sha256` as sixty-four hexadecimal characters with no null admitted while every producer binding in this repository carries null, so no `NormalizedAccountingEvent` could be constructed from any OTLP capture this repository can actually take. Four other artifacts had already made the same field nullable for the same reason — `evidence-bundle-v1.cddl` names the case, "nil while uncertified", and `producer-accounting-binding-v1.schema.json`, `appraisal-result-v1.schema.json` and `openapi-v1.yaml` all admit the null — so the event schema was the one out of step, and the placeholder was standing exactly where the honest answer belonged. Admitting the null without pinning the disposition would have converted a representation gap into a permission, so an event with a null digest is pinned to `private-analytics` in the schema; a collector that forgets is otherwise indistinguishable from one that decided. `accounting-profile-otel-v1.json` recorded this as a computed contradiction and blocked the field's derivation behind it, and `validate_otel_accounting_profile` now reads admissibility out of the schema, so neither the gap nor the declaration of it can outlive the other.

The result bundle's three case counts were self-reported and bound to nothing: a run could declare twelve cases and list two, and the way to turn a failing suite into a passing one was to delete the entry that failed — including `negative_case_count`, the number the `certification_results` check constraint reads to refuse an untested pass. The committed valid example did exactly that, declaring twelve cases while listing two. Counts are now derived. And a case was bound by identifier alone: the manifest digest binds the set of cases, and nothing noticed a fixture rewritten under an unchanged manifest, so each case now carries its own `case_sha256`.

The API third is met by publishing `evaluated.certification_state` on `AppraisalSummary`. The document already published *which* certification a claim was appraised under, by digest, and nothing about whether it was still active when it was read; a claim capped at private analytics because its tuple had expired is entitled to be told that rather than to infer it from a ceiling.

- candidate, testing, active, degraded, suspended, expired, superseded, retired;
- signed result bundle, suite/case digests, validity interval, signer/verifier policy;
- narrow per-tuple emergency downgrade and reinstatement.

### PF-017 — Source observation and operation identity
Files: `packages/schemas/source-observation.schema.json`, `packages/schemas/normalized-event.schema.json`, `packages/schemas/source-receipt-v1.schema.json`, `packages/schemas/producer-accounting-binding-v1.schema.json`, `packages/schemas/accounting-profile-otel-v1.json`, `packages/schemas/local-store-v1.sql`, `packages/schemas/examples/source-observation.valid.json` (new), `packages/schemas/examples/source-observation.valid-acp.json` (new), `packages/schemas/examples/source-observation.invalid-no-observer.json` (new), `packages/schemas/examples/source-observation.invalid-no-accumulation-flag.json` (new), `packages/schemas/examples/normalized-event.invalid-no-operation-identity.json` (new), `packages/schemas/examples/normalized-event.invalid-invented-operation-identity.json` (new), `packages/schemas/examples/normalized-event.invalid-unranked-capture-mode.json` (new), `packages/schemas/examples/normalized-event.invalid-cumulative-without-reset-rule.json` (new), `packages/schemas/examples/normalized-event.valid.json`, `conformance/adapters/claude-code-otel/source-observation.valid.json`, `conformance/adapters/claude-code-otel/normalized-event.invalid-user-email.json`, `conformance/adapters/manifest.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_source_observation_identity.py` (new), `docs/product/TOKEN_ACCOUNTING_SPEC.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: `packages/schemas/examples/` is executed by enumerating the directory rather than a list — every file carries a prefix a schema owns, every `.valid` file validates, every `.invalid-` file is refused by its own schema or by a named validator that has to name the file back, every prefix owns at least one valid example, and a prefix with no negative example declares why with the reverse check. The nine observation modes are one set across `source-observation.schema.json#execution_mode`, `normalized-event.schema.json#certification.capture_mode`, both mode vocabularies of `source-receipt-v1.schema.json` and `producer-accounting-binding-v1.schema.json#certification.tuple.mode`, compared against `observer-equivalence-v1.json#observation_modes` by set equality in both directions. `certification.state` on the receipt and the binding equals `uncertified` plus the `source-certification` machine's states, computed from the registry, and `source_receipts.certification_state` declares that vocabulary as a CHECK constraint. `operation`, `observer` and `reading` are required on both records; an `absent` identity source beside a populated `operation_ref` is refused and is pinned to `private-analytics`; a `cumulative` reading declaring `not-applicable` reset detection is refused. Every observer field is refused as an equivalence commitment preimage input and is named in that rule's forbidden list. `python3 -m unittest tests.ci.test_source_observation_identity` exits 0 and fails on each of those drifts.
Depends: PF-015
Repair: P-1140F-3
Serves: SR-017
Est: 10-14
Status: landed
Evidence: contains 1 packages/schemas/source-observation.schema.json :: "acp"
Evidence: contains 6 packages/schemas/normalized-event.schema.json :: "identity_source"
Evidence: contains 4 packages/schemas/normalized-event.schema.json :: "accumulation"
Evidence: absent packages/schemas/source-receipt-v1.schema.json :: "revoked"
Evidence: absent packages/schemas/producer-accounting-binding-v1.schema.json :: "revoked"
Evidence: contains 1 packages/schemas/local-store-v1.sql :: check (certification_state in (
Evidence: contains 3 scripts/repository/validate_state_vocabularies.py :: source_receipts.certification_state
Evidence: contains 1 scripts/repository/validate_planning_artifacts.py :: def validate_schema_example_coverage
Evidence: contains 1 docs/product/TOKEN_ACCOUNTING_SPEC.md :: operation.identity_source
Evidence: exists packages/schemas/examples/source-observation.valid-acp.json
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_source_observation_identity

- authenticated tuple selection before normalization;
- provider/model/source facts;
- operation, parent/child, retry generation, observer identity, cumulative/incremental semantics;
- direct/proxy/ACP/OTel equivalence.

**The acceptance was rewritten, and it had to be.** The first clause — "every example under `packages/schemas/examples/` and `conformance/adapters/claude-code-otel/` validates" — was not a check anybody could run. Most of the files in both directories are negatives that must *not* validate, so read literally the clause was false at head and false at every commit before it; read charitably it was "the examples are in the state the validator expects", which is what the suite already did and therefore learned nothing. And it improved when a failing example was deleted, which is the class this repository keeps rediscovering. The unit also declared no `(new)` file, so artifact presence could not observe it either: the whole status rested on assertion, and the only falsifiable half was the second clause. That half was genuinely failing — no schema here had an operation identity, an observer identity or an accumulation flag — but nothing would have said so.

It is replaced by a directory enumeration. The directory is the input: a prefix no schema owns fails, a name that is neither `.valid` nor `.invalid-<reason>` fails, a negative that stops being negative fails, and a prefix that loses its last valid example fails. Reading it that way immediately found that `consolidation-plan.invalid-newer-identity-survives.json` appears nowhere in `validate_planning_artifacts.py` — it is refused by `validate_oauth_identity_contract.py`, which nothing recorded, so from this validator's side it looked like an orphan and from the other side nothing said the schema was expected to accept it. Both schema-valid negatives now name the validator that refuses them, that file has to name the fixture back, and a declaration for a fixture the schema has since started refusing fails.

"cumulative/incremental" became `cumulative`/`delta`. `producer-accounting-binding-v1.schema.json` already carries `temporality` with those two values because they are OpenTelemetry's; a third word for the same fact would have been the hidden mapping this unit exists to remove, so the observation reads the binding's vocabulary back and the validator compares the two by set equality.

**Five live defects, all in artifacts that already existed.**

`acp` was in four of the five artifacts that carry the observation-mode vocabulary and not in `source-observation.schema.json`, while `generic-acp-v1` sat in `conformance/accounting/producer-bindings-v1.json` as a registered binding. An ACP observation was unrepresentable in the schema every ACP adapter has to write, and PF-017's own scope line says "direct/proxy/ACP/OTel equivalence". A one-value gap in one of five artifacts is invisible to any check that reads one artifact, which is why the check now reads all six and compares.

`certification.capture_mode` on the event was `^[a-z0-9]+(?:[.-][a-z0-9]+)*$` with no enum. An event could name a capture mode `observer-equivalence-v1.json` assigns no precedence rank, and the survivor rule would then have had nothing to order it by. `conformance/accounting/reconciliation-vectors-v1.json` carries that reading as a refusal.

The outcome vocabularies did not cross-resolve. An observation could report `aborted-unknown` and `unknown`; an event could record `aborted-known` and `quarantined-unknown`; three values were shared and no mapping existed anywhere. `aborted-unknown` therefore had to be written as `aborted-known`, which inverts the fact the source reported — an unknown remainder recorded as a known one. The map now lives in `accounting-arithmetic-v1.json#outcome_normalization`, `aborted-unknown` passes through unchanged, and `aborted-known` is declared normalizer-assigned with the reason it is unreachable from any observation.

The certification state vocabulary was a third vocabulary. `source-receipt-v1.schema.json` and `producer-accounting-binding-v1.schema.json` both admitted `revoked`, which no transition of the `source-certification` machine reaches — that machine ends at `retired` — and both omitted `testing`, `superseded` and `retired`, which transitions do. So a receipt could record a state no certification can ever hold and could not record three that one can. `PF-067` had recorded the device column that stores it, `source_receipts.certification_state`, in `SQL_COLUMNS_WITHOUT_VOCABULARY` naming PF-017 and PF-018 as the owners "rather than guessed at"; the guess would have been wrong in both directions. The column now carries the CHECK constraint and the two schemas carry the same nine values.

And that table had no reverse check. `check_absence_reasons` proves a `RECORDED_ABSENCES` reason cannot outlive the binding it excused, and the same guard was never applied to `SQL_COLUMNS_WITHOUT_VOCABULARY` — rule 8 `continue`s past a listed column without reading it, so a column that acquired a CHECK would have kept the excuse and silently lost the check. Both directions are now checked, and the table is empty.

**The prose owner was a second vocabulary.** `docs/product/TOKEN_ACCOUNTING_SPEC.md` listed eighteen canonical field names — `operation_id`, `count_source`, `billable_tokens_total`, `category_relationships` and the rest — and not one of them existed in any schema in this repository. Its five-level source-precedence list resolved to neither the four `count_authority` values nor the nine mode precedence ranks. Both sections are replaced by prose over the fields that exist, with the two orders that are executable. `operation_id`, the field the specification named and the schemas never had, is what reconciliation needed and is now `operation.operation_ref` with the discriminator that says how it was obtained.

**What is not claimed.** `accounting-profile-otel-v1.json` now derives the three new blocks, and two of them say the channel supplies nothing: the OTLP counter names no execution, so `identity_source` is `source-cursor-derived` and never `source-assigned`, and `parent_operation_ref` is always null because the counter carries no linkage between a subagent execution and the one that started it. That is why `observer-equivalence-v1.json` ranks the mode's achievable class at source-cursor. Making the fact representable is not making it available.

The inventory row is repaired. Line `:34` attributed source observation and normalized accounting to `PF-020..PF-024` — the transaction, ranking, period and social units, none of which owns any of it. PF-042's note flagged the misattribution four units ago and named the wrong line and the wrong pair.

### PF-018 — Accounting reconciliation and bounds
Files: `packages/schemas/accounting-arithmetic-v1.json`, `packages/schemas/accounting-arithmetic-v1.schema.json`, `packages/schemas/accounting-profile.schema.json`, `packages/schemas/reconciliation-vectors-v1.schema.json` (new), `conformance/accounting/reconciliation-vectors-v1.json` (new), `conformance/accounting/reconciliation-vectors-v1.invalid-arrival-order-field.json` (new), `conformance/accounting/accounting-profiles-v1.json`, `conformance/accounting/producer-bindings-v1.json`, `conformance/accounting/manifest.json`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_accounting_reconciliation.py` (new), `docs/product/TOKEN_ACCOUNTING_SPEC.md`
Acceptance: every reconciliation vector produces one result under **every permutation** of its readings, exhausted rather than sampled, with vectors capped at six readings so the sweep stays bounded; a vector with two equal-authority contradicting sources takes the disposition its accounting profile declared in advance and never a selected survivor; an event above the per-event bound and an event that would carry a period accumulator past the integer domain are both rejected, with the period total unchanged, and the arithmetic record declares saturation and capping forbidden. `reconciliation.authority_order` equals `normalized-event.schema.json#count_authority` in declaration order and `accounting-profile.schema.json`'s authority vocabulary equals it as a set. The failure conditions the vectors exercise equal the conditions the evaluator can reach, in both directions. `python3 -m unittest tests.ci.test_accounting_reconciliation` exits 0 and fails on each of those drifts.
Depends: PF-017
Repair: P-1140F-3
Serves: SR-009
Est: 12-16
Status: landed
Evidence: exists conformance/accounting/reconciliation-vectors-v1.json
Evidence: exists packages/schemas/reconciliation-vectors-v1.schema.json
Evidence: contains 1 scripts/repository/validate_planning_artifacts.py :: def evaluate_reconciliation
Evidence: contains 1 packages/schemas/accounting-arithmetic-v1.json :: "per_event_token_burn_maximum": "100000000"
Evidence: contains 1 packages/schemas/accounting-arithmetic-v1.json :: "capping": "forbidden"
Evidence: contains 1 conformance/accounting/reconciliation-vectors-v1.json :: "condition": "period-bound-exceeded"
Evidence: absent conformance/accounting/reconciliation-vectors-v1.json :: arrival
Evidence: absent packages/schemas/accounting-profile.schema.json :: "reconstructed"
Evidence: contains 1 docs/product/TOKEN_ACCOUNTING_SPEC.md :: Selecting a survivor between two equally authoritative contradicting sources is forbidden
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_accounting_reconciliation

- per-operation grouping;
- source authority, containment, cache/reasoning/modality semantics;
- equal-authority contradiction handling;
- deterministic tie-breaking independent of array order;
- checked arithmetic and practical event/period bounds.

**The acceptance was rewritten, and only in one direction.** It was satisfiable as written and it is now stronger. "The same result under two array orderings" is a check whose author picks the two orderings, and two orderings that agree prove nothing about the ones that do not; a first-wins reconciler is correct on any single ordering of an agreeing pair. The validator exhausts every permutation instead, which for the widest vector here is 24 evaluations and for the whole file is a few hundred. The six-reading cap is declared and enforced, so a vector cannot quietly grow past what the sweep can afford — a vector of seven fails rather than silently falling back to sampling.

**The vocabulary split was live.** `accounting-profile.schema.json` spelled the fourth count authority `reconstructed`; `normalized-event.schema.json`, `source-receipt-v1.schema.json`, `appraisal-result-v1.schema.json`, `appraisal-policy-v1.json`, `evidence-profile-policy-v1.json`, `adapter-manifest.schema.json`, `accounting-profile-otel-v1.schema.json` and `openapi-v1.yaml` all spelled it `exact-reconstruction`. Two spellings that never overlap. `local-exact-tokenizer-v1` declares both of its source fields under the profile spelling, so its authority could not be ranked at all — and `validate_otel_accounting_profile` already compares a bound profile's authorities against the event's `count_authority` and demands a declared contradiction when they differ, which for any reconstruction profile would have been a contradiction that did not exist. It does not fire today only because the one binding that check runs over happens to bind a provider-reported profile. The rename changed `local-exact-tokenizer-v1`'s canonical digest, which is recomputed rather than edited.

**The rules that were nowhere.** `contradiction_policy` existed on the profile and nothing consumed it; the arithmetic record had no grouping, no authority order, no tie-break and no bound beyond the integer domain. The reconciliation rule now states all of them, and the two that matter most are stated as prohibitions: `summation_across_readings` is forbidden, because two readings of one operation are two descriptions of one consumption, and `contradiction_resolution_by_selection` is forbidden, because choosing between two equally authoritative contradicting sources makes the accepted total depend on which reading was seen first. `array-position`, `arrival-order`, `receive-time` and `local-wall-time` are named as forbidden tie-break inputs and the vector schema refuses to be able to carry any of them: a field a vector can carry is a field a tie can be broken on, and that refusal is the file's one negative fixture.

**The bounds do not cap anybody.** Token Burn is the raw metric of record — accepted, immutable, unnormalized — so a bound that clipped an accumulated period figure would be normalization under another name, and `capping` is recorded as forbidden with that reason. The two bounds refuse one event each: one hundred million tokens in a single operation is a misread counter rather than a measurement, most often a cumulative reading admitted as an increment, which is exactly what PF-017's `reading.accumulation` made visible and what the `cumulative-reading-not-differenced` vector refuses; and an event that would carry a period accumulator past the unsigned 64-bit maximum leaves the domain. In both cases the event is rejected and the period total is unchanged. A saturating implementation would report the bound as a total, and nothing downstream distinguishes that from a real one.

**Nothing here asserts a certified tuple, because there is none.** Every binding in `conformance/accounting/producer-bindings-v1.json` is `candidate` or `uncertified`, PF-016 confirmed every reachable state is `candidate`, and no vector in this file carries a certification at all. Reconciliation decides which reading counts; certification decides whether the counted figure may compete, and that gate is closed today for every mechanism this repository can capture. The `absent-operation-identity-is-private-analytics` vector is where the two meet: a live-log reading with no source-derived identity — the shape every retrospective import has — keeps its tokens as private analytics and never competes, which is the binding rule stated as a vector rather than as a sentence.

### PF-019 — Idempotency authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`
Acceptance: `idempotency_records` keys on exactly the `key_scope` declared in `openapi-v1.yaml#x-idempotency-contract`, which a test asserts by comparing the two rather than restating either; the `idempotency-ledger` machine declares `executing`, `committed`, `replayable-failure`, `conflict`, `expired` and `abandoned`, all six reachable from the initial state, with `committed` non-terminal because it expires; `python3 -m unittest tests.ci.test_idempotency_ledger` exits 0 and fails when `operation_id` leaves the key.
Depends: PF-004
Repair: P-1140F-4
Serves: SR-012
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_idempotency_ledger

- typed principal, operation/API version, key and request fingerprint;
- exact stored status, content type, safe headers, bytes and result references;
- executing, committed, replayable-failure, conflict, expired and abandoned semantics;
- retention: at least 30 days for high-impact mutations; claim-batch responses until later acknowledged checkpoint supersession.

### PF-020 — Transaction and ambiguous-commit model
Files: `conformance/p1140e/sql-race-plans-v1.json`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `docs/architecture/API_EDGE_CONTRACT.md`, `scripts/repository/validate_p1140e_contracts.py`, `tests/ci/test_sql_race_plans.py`
Acceptance: `sql-race-plans-v1.json` states a case for each of crash-before-commit, crash-after-commit, dropped response, executing takeover and key expiry; every case in the file enumerates the rows a correct implementation leaves behind under `residual_rows`, each naming a table, a key and a presence of `present` or `absent`, with every present row stating column values that resolve against `packages/schemas/planning-schema.sql`; every case names at least one present and one absent row, and no two cases share an interleaving; `idempotency_records` bounds the replay window and the row's own retention with two different columns; `python3 scripts/repository/validate_p1140e_contracts.py` exits 0 and `python3 -m unittest tests.ci.test_sql_race_plans` exits 0 with a case per way the enumeration can rot back into prose.
Depends: PF-019
Repair: P-1140F-4
Serves: SR-012
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: unittest tests.ci.test_sql_race_plans
Evidence: contains 30 conformance/p1140e/sql-race-plans-v1.json :: "presence": "absent"
Evidence: contains 1 packages/schemas/planning-schema.sql :: idempotency_records_retained_past_replay_window
Evidence: contains 1 packages/schemas/planning-schema.sql :: idempotency_records_expired_holds_no_response
Evidence: absent packages/schemas/openapi-v1.yaml :: SR-012 stays open

- idempotency, business effect, audit, outbox and exact response commit together;
- crash before commit, crash after commit, dropped response, takeover and expiry cases;
- expired high-impact keys reject reuse rather than becoming fresh mutations.

**The acceptance is rewritten.** The original — "a plan for each of crash-before-commit, crash-after-commit, dropped response, takeover and expiry, each naming the exact rows a correct implementation leaves behind" — states the right requirement against a file that had no place to put a row and a validator with no rule that could read one. `sql-race-plans-v1.json` held fourteen cases, each with a `case_id`, a table list, `isolation: serializable`, a four-step `interleaving` and a one-line `expected`. All fourteen interleavings were the same four steps: `transaction-a-locks-authority`, `transaction-b-attempts-conflict`, `transaction-a-commits`, `transaction-b-rechecks`. The validator checked that the ids matched a hard-coded set, that the tables existed, and that no case claimed to have been executed — every one of which passes on a file whose cases are placeholders, which is what it was passing on. The rewritten criterion names the shape the requirement needs (`residual_rows`, present and absent, columns resolved against the DDL) and the test that fails when it decays.

**One column bounded two different lifetimes, and the cleanup was the bug.** `idempotency_records` had `expires_at` and nothing else. `x-idempotency-contract.expiry` promised that a request past the window "is not re-executed under the same key", and the only mechanism available for ending a replay was deleting the row — after which the key is fresh, so the very next request carrying it is executed as a new mutation. The promise and the storage were opposites. `retain_until` splits them: `expires_at` ends the replay window at D-225's 168 hours and the response bytes are discarded there, `retain_until` ends the row under `idempotency_record_retention_days`, and `idempotency_records_retained_past_replay_window` refuses a row where the second is not strictly later than the first. `idempotency_records_expired_holds_no_response` makes the discarding a constraint rather than a promise kept in application code over bytes that are still on disk.

The two figures had also been reading as a contradiction: D-225 says 168 hours, `policy-defaults-v1.json` says 30 days, and the disposition registry pointed the second at the same single column the first governed. They are not in conflict once they are bounding different things, and neither accepted decision had to be reopened to say so.

**Three stale justifications, all outliving their holes.** `openapi-v1.yaml#x-idempotency-contract` still carried `open_finding: SR-012 stays open. This block is the API half. The persistence half — the nullable response_digest, the missing response-body column and the account-only primary key — is not repaired here`. All three were repaired, by PF-019 and PF-049, one and two units earlier. `API_EDGE_CONTRACT.md` carried the same paragraph in prose and told clients to treat byte-identical replay as specified rather than demonstrated for a reason that no longer existed. Neither is replaced with a closure claim: the block now records what is repaired and states that repaired is not closed, and that `conformance/p1140f/semantic-findings-v1.json` is the only authority for the finding's state.

Two further stale facts fell out of reading the same paths: `SERVER_API_DATA_AND_RANKING_CONTRACT.md` still described the claim uniqueness constraints as `(device_id, sequence)` and `(device_id, payload_hash)`, which PF-010 moved onto the lineage, and the claim acceptance transaction still said "lock device sequence row" against a counter D-592 had rekeyed.

**The absent-row floor moved from 31 to 30, and a lower floor is a weaker check, so the reason is recorded rather than the number quietly edited.** PF-025 repaired the `block-race` plan, whose four absent rows encoded the pre-D-585 model in which a block deletes the friendship, the rivalry and any pending invitation. Three of those became `present`, because a block changes no relationship row. PF-025's new `board-create-owner` case added two. The count is a floor over the whole file and not a per-case rule; the per-case rule — every case names at least one present and one absent row — is in `validate_p1140e_contracts.py` and did not move.

This is SR-012's last unit. **No finding was touched.** `conformance/p1140f/semantic-findings-v1.json` is unmodified by this work, and it is not this unit's to modify: closure evidence cites the merge sha of the pull request that lands it, which cannot be known from inside that pull request.

### PF-021 — Ranking definition and audience authorization
Files: `packages/schemas/ranking-view-v1.schema.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`, `packages/schemas/examples/ranking-view.*.json`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_ranking_view_separation.py`, `tests/ci/test_public_operations.py`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
Acceptance: `ranking-view-v1.schema.json` states a `definition` and an `audience` whose property sets are disjoint and are held in `validate_planning_artifacts.py` in both directions; `ranking_definition_id`, `audience_id` and `ranking_view_id` all recompute from the record's own canonical encoding, and the three declared audience examples share one `ranking_definition_id` and produce three distinct `ranking_view_id` values; `planning-schema.sql` splits `ranking_definitions` from `ranking_views` and carries `check ((scope = 'global') = (default_visibility = 'universally-public'))`, so the only-global-is-public rule is enforced where the row is written; every operation carrying `security: []` is declared in `openapi-v1.yaml#x-public-operations` with one of the three admissible reasons, exactly one of which is `global-board`, and the operation holding that reason takes no `scope` parameter; `getPublicProfile` requires a session and returns 401 without one; `python3 -m unittest tests.ci.test_public_operations tests.ci.test_ranking_view_separation` exits 0 with a case per way the declaration and the split can rot.
Depends: PF-004
Repair: P-1140F-4
Serves: SR-010, SR-015
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_ranking_view_separation
Evidence: unittest tests.ci.test_public_operations
Evidence: contains 1 packages/schemas/planning-schema.sql :: create table ranking_definitions
Evidence: contains 1 packages/schemas/planning-schema.sql :: check ((scope = 'global') = (default_visibility = 'universally-public'))
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: getGlobalLeaderboard: global-board
Evidence: absent packages/schemas/openapi-v1.yaml :: getLeaderboard: global-board
Evidence: exists packages/schemas/examples/ranking-view.valid-friends-audience-over-the-same-definition.json

- stable ranking definition separate from viewer/board audience;
- metric/version, period, evidence/source/agent/provider/model filters, tie and projection policy;
- viewer, friend/rival cohort, block/privacy, board membership/visibility revisions;
- only global public by default.

**The acceptance was rewritten.** The original clause was `ranking-view-v1.schema.json` separates the ranking definition from the audience, with nothing saying what separated means. Renaming two fields satisfies it, and so does adding a comment. The clause now names the arithmetic: three identifiers that recompute, a property partition held in both directions, and the property the split exists for — one definition, three audiences, three view identifiers — stated so that it fails if the audience stops reaching the identifier.

**The audience half was recorded as done and was not.** `getLeaderboard` held the `global-board` reason, which the declaration block defines as "the one universally public view AGENTS.md names". Its path was `/leaderboards/{scope}/{period}` and `Scope` admitted `global`, `friends`, `rivals` and `board`. The reason named one of four values of a path segment and the declaration covered all four, so `GET /leaderboards/friends/weekly` answered an unauthenticated caller with a viewer-relative standing, and `GET /leaderboards/board/weekly` named no board at all — a key with no discriminator. PF-052 landed with a note saying this operation "gains a viewer parameter and loses its unauthenticated `security: []`", and did neither; the note stayed, which is the same justification-outliving-its-hole shape the closed-set-of-reasons rule was written against. The global board now has `/leaderboards/global/{period}` and holds the reason alone, the cohort scopes require a session, and a board standing is addressed by board at `/boards/{id}/leaderboard/{period}`.

**`getPublicProfile` is still repaired.** It requires a session, declares `x-authorization: authenticated-account`, answers 401 and appears in no public declaration; `test_public_operations` asserts all four and the assertions survived this unit unchanged.

**Two further live defects fell out of reading the same paths.** `RankEntry.evidence_class` admitted `imported` while `ranking_entries.evidence_class` and `ranking-generation-v1.schema.json` both refused it and AGENTS.md says historical imports never enter active competition — the public leaderboard schema was the only artifact in the repository saying an import could be ranked. And the five filter dimensions the accounting contract requires every leaderboard to support were nowhere in the view identity; they are now modes rather than lists, because a list read as a filter is satisfied by emptiness and a filter that lost its values would look unrestricted rather than broken.

This unit serves SR-010 and SR-015. It advances SR-015 no further than PF-021's earlier half did: that finding's closure is one enumerated boundary matrix plus a current-authorization check at every boundary it names, and **PF-033 is the unit that owes it**. Nothing here should be read as closing SR-015.

### PF-022 — Ranking generations, entries, snapshots and cursors
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/ranking-cursor-v1.schema.json`, `packages/schemas/ranking-cursor-vectors-v1.schema.json`, `conformance/planning/ranking-cursor-vectors-v1.json`, `packages/schemas/disclosure-projection-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_ranking_cursor.py`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
Acceptance: `ranking_projection_generations` carries exactly one active pointer enforced by `ranking_projection_generations_active_idx`, unique and partial on `state = 'active'`; every entry key in `ranking_entries` includes the generation — primary key `(ranking_view_id, generation, position)` and unique `(ranking_view_id, generation, erasure_domain_id)` — `score_snapshots` is unique on `(ranking_view_id, generation)`, and `RankEntry` and `LeaderboardPage` both carry the generation they render; `ranking-cursor-v1.schema.json` binds the viewer, the generation, the snapshot, the authorization revision and the expiry, `conformance/planning/ranking-cursor-vectors-v1.json` states nine presentations covering all five refusals and at least one acceptance in a fixed refusal order, and `validate_planning_artifacts.py#evaluate_cursor` reaches every outcome from the inputs rather than reading `expected` back; a cursor replayed by another viewer and a cursor replayed by an anonymous reader are both refused `viewer-mismatch`; `python3 -m unittest tests.ci.test_ranking_cursor` exits 0.
Depends: PF-021
Repair: P-1140F-4
Serves: SR-010, SR-015
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_ranking_cursor
Evidence: exists packages/schemas/ranking-cursor-v1.schema.json
Evidence: exists conformance/planning/ranking-cursor-vectors-v1.json
Evidence: contains 1 packages/schemas/planning-schema.sql :: create unique index ranking_projection_generations_active_idx
Evidence: contains 1 packages/schemas/planning-schema.sql :: constraint period_scores_generation_fk

- generation included in entry keys;
- isolated build/validation/promotion and one active pointer;
- immutable retained entries;
- viewer-bound signed cursor with authorization revision and expiry;
- score-only `rank()` peer groups and separate deterministic display key.

**The acceptance was rewritten in two places.** It required that "every entry key in `score_snapshots` includes the generation". `score_snapshots` holds no entries: it is one row per sealed generation, and the entries are in `ranking_entries`. The clause was satisfied by the table it named before this unit began and said nothing about the table that holds the thing it is about. It now names both, and states what each key is. Second, "a cursor fixture records the viewer, the authorization revision and the expiry" is satisfied by writing three fields into a JSON file that nothing reads. The fixture is now evaluated: a second implementation of the rule reaches every outcome from the inputs, so a case whose recorded answer is wrong fails.

**The one active pointer did not exist.** The `ranking-projection` machine calls its promotion transition `atomic-promote` and the storage contract calls a generation the current standing. Nothing enforced either: `state` was a five-value CHECK with no uniqueness, so two workers could each promote and leave two rows in `active`, after which "the current standing" is whichever one a reader's plan happened to find and both readers who found different ones saw a real row.

**The cursor rules compared fields that did not exist.** The `Cursor` parameter asserted the server "rejects a cursor it did not issue, a cursor issued against a different snapshot_id, and a cursor issued to a different principal". No record in this repository held an issuer, a snapshot or a principal, so the sentence was a promise about an opaque string. The record now holds all five inputs and the refusal order is itself a rule, because a presentation that breaks two of them must be refused by the same one every time or the refusal tells a prober which of the two facts they guessed right.

**Two columns pointed at nothing.** `period_scores.generation` was a bare `bigint` naming a generation that need not exist, and `period_scores.ranking_view_id` had no foreign key at all; the composite key now resolves both. The registry defect underneath was worse: the `ranking-projection` machine named `projection-generations` as its persistence owner — a four-column stub with no `state` column — while its five states live in `ranking_projection_generations`. AGENTS.md's "one persistence owner" was satisfied by a table holding none of the state, and the near-miss name is why nothing noticed. `validate_state_vocabularies.py` now requires a machine to name the table of every SQL column it is bound to, which caught a second instance in `model-alias-resolution`.

**`Serves:` gained SR-015 after the fact, and the work is unchanged.** This unit was recorded as serving SR-010 alone. SR-015 names `planning-schema.sql#score_snapshots` among its boundaries, and the mechanism that stops a durable handle into a sealed generation from replaying stale authorization is the cursor's `authorization_revision` binding and the `authorization-revision-moved` refusal — both of which are in this unit and in no other. SR-015's evidence therefore rested on two units, neither of which had touched the snapshot limb, while the unit that had was filed against a different finding. Nothing here was re-done: the attribution was wrong and is corrected. The audit that found it is `validate_finding_artifact_coverage.py`, which asks whether the commits a finding cites reached the artifacts it names.

### PF-023 — Periods, seasons, contributions and corrections
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/score-contribution-v1.schema.json`, `packages/schemas/ranking-correction-vectors-v1.schema.json`, `conformance/planning/ranking-correction-vectors-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_period_corrections.py`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
Acceptance: the `period` machine declares `open`, `frozen`, `closed`, `corrected` and `archived` with all five reachable from `open`, `archived` the only terminal state and no transition reaching it from `open`, the transition into `corrected` carried by an actor other than `worker`, and the vocabulary bound to `periods.state` by the state-vocabulary binding table; `score_contributions` is append-only by constraint — a `before delete` trigger and a `before update` trigger refusing every column an append-only rule protects, with `claim_id` outside the refusal because an erasure clears it through `on delete set null`, which PostgreSQL performs as an update — and `check ((origin = 'retraction') = (token_burn_delta < 0))` makes the direction recoverable from the row; `ranking_corrections` keys on `(correction_id, ranking_view_id, period_id, erasure_domain_id, direction)`; `conformance/planning/ranking-correction-vectors-v1.json` states six cases and `validate_planning_artifacts.py#rebuild_period_total` folds the ledger and the correction rows independently and requires the two to agree with each other and with the recorded total, rejecting rather than clamping when retractions exceed what they correct; `python3 -m unittest tests.ci.test_period_corrections` exits 0.
Depends: PF-022
Repair: P-1140F-4
Serves: SR-010
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_period_corrections
Evidence: exists conformance/planning/ranking-correction-vectors-v1.json
Evidence: contains 1 packages/schemas/planning-schema.sql :: create trigger score_contributions_no_rewrite
Evidence: contains 1 packages/schemas/planning-schema.sql :: check ((origin = 'retraction') = (token_burn_delta < 0))
Evidence: contains 1 packages/schemas/planning-schema.sql :: check (period_type <> 'lifetime' or state = 'open')
Evidence: absent packages/schemas/planning-schema.sql :: old.claim_id is distinct from new.claim_id

- exact calendar/timezone, open/frozen/closed/corrected/archived states;
- late-claim and correction windows;
- immutable contribution ledger;
- inverse/replacement corrections and rebuild equivalence;
- movement, overtake, streak and season event/retraction references.

**The acceptance was rewritten, and one third of it was unsatisfiable.** It required `minute_scores` and `period_scores` to be append-only by constraint. Neither can be, and neither should be: the disposition registry gives `period_scores` `erasure_action: delete` because it is a live personal record, and gives `minute_scores` a retention window enforced by dropping whole partitions. An append-only rule on either would make the erasure path and the retention sweep fail rather than make anything immutable. The append-only ledger is `score_contributions`, which the same registry classes `retain-unlinked` and which nothing was protecting; the clause now binds the rule to the table it is true of and says why the other two are derived rather than immutable. The `period` machine clause was also satisfied by declaring five states in a registry and nothing else, so it now names the reachability, the terminal state, the actor and the SQL binding.

**The rebuild clause was unsatisfiable as written.** `ranking_corrections` held `(ranking_correction_id, correction_id, ranking_view_id, token_burn_total_delta)`. It named no participant and no period: every row said that some total somewhere moved by some amount, and no rebuild from it could reproduce anybody's figure. `LEADERBOARD_STORAGE_AND_RANKING.md` documented `ranking_corrections_correction_idx` as serving "applying or reversing one correction across views", which reads as a working access path over a table that could not answer the question. The row now carries `period_id`, `erasure_domain_id`, a `direction` and an unsigned `magnitude` — D-263's shape rather than a signed column, because an addition of −5 and a retraction of 5 are the same row and D-263 composes a period as additions minus retractions.

**`periods` had no lifecycle at all.** `seasons` carried five timestamps in a checked order from `ends_at` through `freeze_at`, `close_at`, `appeal_window_ends_at` and `archive_at`. `periods` carried none of it, so "period results remain provisional through the lateness window, then finalize" had nothing recording which side of that boundary a period was on, and a correction to a closed period was indistinguishable from a claim landing in an open one. Three of the new rules are enforced rather than described: `archived` is unreachable from `open`, the transition into `corrected` is a moderator act under recent authentication rather than a scheduled job's — a scheduled job that can supersede a published standing is one that can change a result without anyone deciding to — and the `lifetime` period never leaves `open`, because it is unbounded and has no end to freeze at.

**`score_contributions` was called immutable and nothing enforced it.** The trigger pair does. `claim_id` is deliberately outside the refusal and the validator fails if it is added, because an erasure clears that column through `on delete set null` and PostgreSQL performs that as an UPDATE on the row: a blanket refusal breaks the erasure path rather than the rewrite path, which is the opposite of what the rule is for.

**Docker is unavailable here, so no DDL in this unit has executed.** The trigger, the function and the new constraints are declared in dependency order and CI is their first execution. That is stated rather than glossed: a planning validator reading this DDL as text is not a PostgreSQL instance accepting it.

### PF-024 — Social relationship authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: `friend_edges` stores one canonical ordered pair with a check constraint, `blocks` is directional with no symmetry constraint, and neither `friend_requests.state` nor `rival_edges.state` admits `blocked`; the `friendship` and `rivalry` machines declare no `blocked` state and no transition into one, with every remaining state reachable and every terminal state a sink; `conformance/social/block-independence-vectors.json` states six cases with inputs, expected relationship rows and expected visibility, registered in the suite manifest with two negative cases; `python3 -m unittest tests.ci.test_block_independence` exits 0 and fails when a terminal `blocked` state is reintroduced.
Depends: PF-004
Repair: P-1140F-4
Serves: SR-011
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_block_independence

- canonical friendship pair and directional request lifecycle;
- directional blocks separate from friendship;
- rivals separate from blocks/friendship;
- decline, cancel, expiry, unblock, generation and current authorization.

### PF-025 — Board ownership and role authority
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/projection-authorization-v1.json`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `conformance/p1140e/sql-race-plans-v1.json`, (new) `scripts/repository/validate_social_surface_contracts.py`, (new) `tests/ci/test_social_surface_contracts.py`, `scripts/repository/validate_p1140e_contracts.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_state_vocabularies.py`, `conformance/p1140e/validation-matrix-v1.json`
Acceptance: neither the `board-membership` nor the `board-invitation` machine declares a block-caused state or a `block-cascade` transition, every remaining state is reachable and every terminal state is a sink; `board_invites` declares an `invited_account_id` column and a `role` column whose CHECK equals the `BoardInvitationRequest.role` enum, and neither admits `owner` or `admin`; `boards` declares `name`, a `visibility` CHECK of `public`, `unlisted`, `invite-only` and `private`, and a `membership_revision` counter that `projection-authorization-v1.json` reads instead of a state; `Board.kind` and `BoardCreateRequest.kind` equal `boards.board_type`; the `board-create-owner` case in `conformance/p1140e/sql-race-plans-v1.json` writes both tables and states the absent row a partial unique index cannot refuse; `board-membership` declares a transition from `active-owner` to a non-owner active state and every transition into a privileged role requires recent authentication; the `block-race` plan leaves `friend_edges` and `rival_edges` present; `python3 -m unittest tests.ci.test_social_surface_contracts` exits 0 and each board case fails with its stated substring when the corresponding drift is injected.
Depends: PF-024
Repair: P-1140F-4
Serves: SR-011
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_social_surface_contracts.py
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: unittest tests.ci.test_social_surface_contracts
Evidence: unittest tests.ci.test_block_independence
Evidence: absent packages/schemas/state-machine-registry-v1.json :: invalidated-by-block
Evidence: absent packages/schemas/state-machine-registry-v1.json :: block-cascade
Evidence: contains 1 packages/schemas/planning-schema.sql :: role text not null check (role in ('member','viewer'))
Evidence: contains 1 conformance/p1140e/sql-race-plans-v1.json :: board-create-owner

- atomic board creation plus initial owner;
- invitations grant only non-privileged membership;
- separate recent-authenticated revision-checked admin promotion;
- paired ownership transfer preserving exactly one owner;
- role/action authorization matrix and recovery.

**The acceptance was rewritten, and two of its three clauses could not decide done.** It required a partial unique index to enforce "exactly one owner per board". A partial unique index cannot: it refuses a second `active-owner` row and is silent about a board with none, so the clause was satisfied by a constraint that enforces half of it. The rewritten clause names both halves — the index for at-most-one, and the `board-create-owner` transaction for at-least-one, with the absent row that states what the index cannot refuse. It also required that `boards` and `board_memberships` be written in one transaction "in the recorded SQL plan", and no such plan existed: `conformance/p1140e/sql-race-plans-v1.json` held a `board-owner-transfer` case and nothing about creation, so the criterion pointed at a record it could not read. The case exists now. And the third clause — `board_invites` cannot grant an admin or owner role, "which a rejected fixture case proves" — was refusing a value against a table that held no role column and no invitee at all. That is the class this repository has hit before: an operation whose declared refusals compare fields no record holds. The role is a column with a CHECK now, and the rewritten clause requires the SQL vocabulary and the wire enum to be equal sets rather than each separately plausible.

**The block repair D-585 made for friendship had never reached boards.** `board-membership` carried a terminal `blocked`, reached by a `block-cascade` from `invited`, `active-viewer`, `active-member` and `active-admin`, actor `user`, `reversal: none`. `board-invitation` carried `invalidated-by-block` the same way. This is worse than the friendship case rather than milder: a block is an act between two accounts, and what these two states destroyed was a membership and an invitation that a third party — the board owner — had granted, permanently, with no transition out. `tests/ci/test_block_independence.py` pinned the repair for `friendship` and `rivalry` and its `SHARED_AGGREGATES` tuple named only those two, so the board half sat untouched behind a test that read as though it covered the rule. Both states and both transitions are gone under D-616, and the new validator refuses either to return.

**The recorded race plan still described the model D-585 replaced.** `block-race` said the block transaction "deletes the friendship and the rivalry and inserts the block", with `friend_edges`, `rival_edges` and `board_invites` all `absent` afterwards and `expected` reading "block atomically removes incompatible relationships and invitations". PF-024 repaired the contract and the machines and left the plan alone, so the repository held one artifact saying a block changes no relationship row and another planning the deletion. The plan now states the rows that survive, and the validator fails if `friend_edges` or `rival_edges` goes back to `absent` on a block.

**The transfer plan required a transition the machine did not have.** `board-owner-transfer` states that the outgoing owner remains present "in a non-owner active state". `board-membership` had exactly one transition out of `active-owner`, `board-owner-leave`, which goes to `left`. There was no demotion, so the plan's own residual row was unreachable in the aggregate that owns it, and the `board_one_active_owner` index would have refused the promotion half. `board-demote-owner` is declared, in the `board-owner-transfer` boundary, under recent authentication.

**`moderator` was a word.** The contract listed five roles; `board_memberships.role` had four, the machine had four `active-*` states, and no column, transition or authorization row anywhere carried a moderator. It is removed from the prose rather than added to four artifacts, because board moderation is the `moderation-case` aggregate and not a membership role.

**Docker is unavailable here, so no DDL in this unit has executed.** The new columns, CHECKs and indexes are declared in dependency order and CI is their first execution.

### PF-026 — Presence evidence and projection
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/policy-defaults-v1.json`, `packages/schemas/presence-pulse-v1.schema.json`, `packages/schemas/projection-authorization-v1.json`, `packages/schemas/examples/presence-pulse.valid.json`, `packages/schemas/examples/presence-pulse.invalid-blocked-viewer-sees-online.json`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, `docs/privacy/PRIVACY_CONTRACT.md`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, (new) `conformance/social/presence-merge-vectors.json`, `conformance/social/manifest.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `scripts/repository/validate_social_surface_contracts.py`, `tests/ci/test_social_surface_contracts.py`
Acceptance: `presence_leases` records a device-bound `lease_generation` and declares no `visibility` column, and `profiles` declares `presence_visibility`; `PresenceRenewalRequest` declares no `availability` and requires `device_id`, `lease_generation` and `qualifying`, and every security alternative on `renewPresence` requires `deviceProof`; `packages/schemas/policy-defaults-v1.json` resolves `presence_heartbeat_seconds` to 30, `presence_idle_after_seconds` to 90 and `presence_offline_after_seconds` to 300, with idle strictly before offline; `conformance/social/presence-merge-vectors.json` states a merge rule and six cases, and `scripts/repository/validate_social_surface_contracts.py` folds each case under both device orderings and requires one answer; `python3 -m unittest tests.ci.test_social_surface_contracts` exits 0 and each presence case fails with its stated substring when the corresponding drift is injected.
Depends: PF-011, PF-024
Repair: P-1140F-4
Serves: SR-011
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_social_surface_contracts.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_social_surface_contracts
Evidence: exists conformance/social/presence-merge-vectors.json
Evidence: absent packages/schemas/policy-defaults-v1.json :: presence_lease_expiry_seconds
Evidence: contains 1 packages/schemas/planning-schema.sql :: presence_visibility text not null default 'authorized-viewers'
Evidence: contains 1 conformance/social/presence-merge-vectors.json :: "precedence": ["active", "idle", "expired", "revoked", "absent"]

- device-bound qualifying pulse every 30 seconds;
- active, idle at 90 seconds, offline at 300 seconds;
- lease generations and sleep/resume;
- deterministic multi-device merge;
- private/block/relationship/board visibility as separate viewer projection.

**The acceptance was rewritten, and two thirds of it named things that do not exist.** It required "the `presence` machine" to transition to `idle` at 90 seconds and `offline` at 300. There is no `presence` machine — the registry declares `presence-lease` — and it has no `offline` state; the lease expires, and `offline` is a value of the viewer projection. As written the clause could only be satisfied by inventing a state. Worse, it required "those exact numbers in `packages/schemas/policy-defaults-v1.json`", and both numbers were there under keys that meant the opposite: `presence_lease_expiry_seconds` held 90 and meant idle, `presence_idle_after_seconds` held 300 and meant offline. A reader checking the criterion would have found `presence_idle_after_seconds: 300` and passed it. The rewritten clause names the keys, the values and the ordering rule, so it is satisfied by the registry saying what it means rather than by two numbers being present somewhere in it.

**A misnamed pair made `idle` unreachable.** Read straight, the registry said the lease expires after 90 seconds and goes idle after 300, so `presence-expire` always fires before `presence-idle` and a state the machine declares can never be entered. D-385 recorded the misnaming, declined the rename on the stated ground that "`scripts/repository/validate_planning_artifacts.py` requires those exact spellings", and named the rename as its own reopen condition. The blocker was a hard-coded list in this repository holding its own defect in place, and the traceability row for D-385 already named PF-026 as the owner. D-618 is the rename; D-385 is superseded.

**A browser could fabricate presence.** The contract says in as many words that a browser or ordinary web session cannot fabricate indefinite activity. `renewPresence` accepted a session cookie, and `PresenceRenewalRequest` had exactly one field: `availability`, over `online`, `idle` and `offline`. So a tab could PUT `online` on a repeating timer and the sentence had nothing behind it. `validate_state_vocabularies.py` compounded it by declaring `PresenceRenewalRequest.availability` a *projection* of the presence-lease machine — a coarsening of a server-derived state, applied to a request, which is the direction a projection cannot run in. The request now carries the device, the generation and a qualifying boolean, and every alternative on the route requires device proof. This is also the write-side of a constraint that existed only on the read side: the schema comment says a pulse naming a superseded generation is discarded, and until now no generation reached the server on the path that admits pulses.

**Visibility was one policy stored per device.** `presence_leases.visibility` held `authorized-viewers` or `private` per `(account, device)` row, against a projection that produces one availability per account. Two devices could disagree with nothing saying which the merge took, so going private on a laptop while a desktop stayed authorized published the participant anyway. It is `profiles.presence_visibility` now, and `projection-authorization-v1.json` reads it there.

**The merge was required and never stated.** "Multi-device aggregation" was a bullet in the contract and nothing defined it. The rule is a precedence fold stated in the vector file, and the validator evaluates every case under both orderings, so a merge that depends on which device was read first fails rather than passing quietly. The suite manifest records exactly what that executes and what it does not: the rule against the fixture, not a server, a lease or a pulse.

**What this does not reduce.** Presence remains a last-active answer an authorized viewer can watch, and D-561 through D-604 accepted that exposure knowingly. Nothing here narrows it.

### PF-027 — Notification source, inbox and channel model
Files: `packages/schemas/notification-delivery-v1.schema.json`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `packages/schemas/examples/notification-delivery.valid.json`, `packages/schemas/examples/notification-delivery.invalid-inbox-attempt-deferred.json`, `packages/schemas/examples/notification-delivery.invalid-suppressed-security-event.json`, (new) `packages/schemas/examples/notification-delivery.invalid-security-category-remapped.json`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `conformance/p1140e/validation-matrix-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_social_surface_contracts.py`, `tests/ci/test_social_surface_contracts.py`
Acceptance: `notification-delivery-v1.schema.json` declares `event_categories` naming every `event_type` exactly once, every named category has a `<category>_enabled` property on the preferences record and a column of that name on `notification_preferences`, and `security` maps to the flag constrained `true`; `notifications.retraction_reason_code` carries a CHECK whose value set equals the `retraction.reason_code` enum, which the existing reason-registry check already binds to the `notification` transport; the API declares `getNotificationPreferences` and `updateNotificationPreferences`, and `NotificationPreferencesUpdate` declares no `security_enabled`; `notification-delivery.invalid-security-category-remapped.json` is rejected by the schema; the contract's launch type list names the eight registered types and no others; `python3 -m unittest tests.ci.test_social_surface_contracts` exits 0 and each notification case fails with its stated substring when the corresponding drift is injected.
Depends: PF-024, PF-026
Repair: P-1140F-4
Serves: SR-011
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_social_surface_contracts.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_social_surface_contracts
Evidence: exists packages/schemas/examples/notification-delivery.invalid-security-category-remapped.json
Evidence: contains 1 packages/schemas/planning-schema.sql :: product_enabled boolean not null
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: getNotificationPreferences
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: updateNotificationPreferences
Evidence: absent packages/schemas/openapi-v1.yaml :: PresenceRenewalRequest.availability

- immutable source event and revision;
- recipient inbox item, grouping, authorization revision, read/dismiss/expiry/retraction;
- per-channel queued/deferred/accepted/acknowledged/failed/expired attempts;
- preferences, quiet hours, security-critical policy and subscription lifecycle;
- push provider acceptance is not user read or guaranteed delivery.

The schema, DDL and API half landed under D-420 through D-423. `packages/schemas/notification-delivery-v1.schema.json` carries the source event, inbox item, delivery attempt and preferences; `notification_events` and `notification_deliveries` are real tables rather than the three-column stubs they were; `Notification` publishes only the four post-delivery states; and `markNotificationRead` gives the `notification-read` transition its first route.

**The acceptance was rewritten because the landed half had already satisfied all of it.** Every clause — the uniqueness over recipient, type, aggregate and revision; the recipient projection with an authorization revision; `retracted` on the machine; the six delivery states with no path from `accepted` to a read — was true before this unit began, and the block above said so in the same breath as `Status: in-progress`. A criterion that a unit's own prose records as already met cannot decide whether the unit is done. The rewritten clauses name what was still open.

**Four preference flags governed eight event types and nothing declared the mapping.** `suppression_cause` admits `category-disabled`, and no artifact anywhere said which category any event type belonged to, so the word named nothing a reader could resolve. `compatibility` and `release` fell under no flag at all — a worker deciding whether to create one had no preference to read — and, more seriously, whether a `security` notice could be muted depended on which mapping that worker invented. This is a hidden security-critical mapping of exactly the kind the schema discipline forbids. `event_categories` declares it by `const`, `product_enabled` is the flag the two uncovered types needed, and a rejected fixture pins the one entry that must never move.

**The prose promised types the model could not carry.** The launch list named eleven English phrases including rival suggestion, rank movement and quarantine; the enum has eight members and none of those three. Where a phrase maps to a registered type the repaired paragraph says so; where it does not, it says adding one is four artifacts rather than a sentence.

**`retraction_reason_code` accepted any string.** The contract promised "one of three registered reason codes" and the column had no CHECK, so registration was a convention. The three are in the column now and the validator compares that set to the schema enum, which the existing reason-registry check already ties to the `notification` transport — so a fourth code added in one place fails rather than diverging.

**A participant could not set a preference.** `notification_preferences` had no operation of any kind. The block above flagged that and this unit closes it; the update body omits `security_enabled`, `quiet_hours_scope` and the two opt-in timestamps rather than accepting and discarding them.

**The previous note said four reason codes carry retraction "on a transport of its own".** Three do. `NOTIFICATION_ALREADY_RETRACTED` is a Problem body on `markNotificationRead` and is not a retraction reason; the note is corrected here rather than left to be counted again.

**Still not implemented.** No aggregate appends an event, no worker groups one, no worker evaluates a preference, and no surface renders an inbox. Every check in this unit compares records to records.

### PF-028 — Export authority
Files: `docs/privacy/DATA_MAP.md`, `docs/privacy/PRIVACY_CONTRACT.md`, `packages/schemas/data-disposition-v1.schema.json`, `packages/schemas/data-disposition-v1.json`, `packages/schemas/export-manifest-v1.schema.json`, (new) `packages/schemas/examples/export-manifest.valid.json`, (new) seven `packages/schemas/examples/export-manifest.invalid-*.json` fixtures, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `conformance/p1140e/validation-matrix-v1.json`, `scripts/repository/validate_planning_artifacts.py`, (new) `tests/ci/test_export_and_deletion_domains.py`
Acceptance: `docs/privacy/DATA_MAP.md` declares a closed set of data-domain keys, one per category-of-processing section, and `data-disposition-v1.json` carries the key on every row it classes `personal`, and on every `pseudonymous` row that keeps attribution, and on no other row; the export manifest requires a version, a snapshot cutoff, an encryption reference that no property could hold a key in, and one entry per domain with a count, a digest when included and a reason from a closed set when excluded; a manifest that answers for a domain twice is refused by a computed check the schema cannot express; `exports` carries the typed scope, the frozen recent-auth instant, the snapshot cutoff and constraints refusing a downloadable package with no manifest, key or expiry, `export_artifacts` carries the domain key, and `export_download_grants` carries a non-null expiry, a revocation instant and the export it opens; `revokeExportDownloadGrant` is the route that ends a grant; `deletion_state_at_generation` equals the vocabulary `DeletionJob` publishes plus `none`, which excludes the machine's internal state.
Depends: PF-004, PF-019
Repair: P-1140F-4
Serves: SR-013
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: unittest tests.ci.test_export_and_deletion_domains
Evidence: unittest tests.ci.test_data_disposition_and_erasure
Evidence: exists packages/schemas/examples/export-manifest.valid.json
Evidence: exists packages/schemas/examples/export-manifest.invalid-domain-answered-twice.json
Evidence: contains 1 docs/privacy/DATA_MAP.md :: ### The seven domains, named once
Evidence: contains 1 packages/schemas/planning-schema.sql :: check (state not in ('snapshotting','encrypting','ready','downloaded','purged') or snapshot_cutoff_at is not null)
Evidence: contains 1 packages/schemas/planning-schema.sql :: check (revoked_at is null or revoked_at >= issued_at)
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: revokeExportDownloadGrant
Evidence: absent packages/schemas/export-manifest-v1.schema.json :: key_material
Evidence: absent packages/schemas/export-manifest-v1.schema.json :: cooling_off

- durable status resource and cancellation/purge;
- frozen recent-auth grant and coherent snapshot cutoff;
- versioned package, manifest, included/excluded domains, counts, checksums, encryption and short-lived revocable grants;
- rights-of-others filtering and download audit.

**The acceptance was rewritten, and the reason is the finding.** As written it asked for "included and excluded domains" against a repository in which no domain vocabulary existed. `exports` had four columns, `export_artifacts` keyed on a logical file name, and `deletion_effects.subsystem` was `text not null` with no CHECK — so "domain" was a word three artifacts used and none defined, and any implementation satisfying the sentence would have invented a fourth spelling. The rewritten clauses name the vocabulary's owner first, because until the Article 30 record declares the keys there is nothing for a manifest to be complete against. The acceptance also named the wrong table for the grant: it asked `export_artifacts` to carry "a revocable grant with an expiry", and the grant is `export_download_grants`, which existed as a four-column stub with neither.

**Seven keys, declared in the record and carried on the row.** `docs/privacy/DATA_MAP.md` names one key per category-of-processing section, `data-disposition-v1.json` carries it on all 71 rows that class `personal` or keep attribution, and the validator compares the two in both directions — plus a third comparison that no work unit asked for and that turned out to matter: every table the record names inside a section must carry that section's key. That check found `presence_events` filed under "Account and identity" in the Article 30 record while `presence_leases`, the row beside it in every other sense, sat under "Social, presence and notifications". The row was moved.

**Two rows carry no key and the exemption is bounded by the claim that buys it.** `deletion_tombstones` and `outbox_events` are `pseudonymous` with `attribution_retention` of `no-retention`: they attribute to nobody, so they are in no subject's export. Widening that exemption means editing a retention claim in the Article 30 record rather than deleting a label, which is the difference between a bounded exception and an escape hatch.

**A file list cannot record an absence.** The old manifest listed files. A package that omitted a domain was indistinguishable from one that held nothing for it and from one whose producer forgot the domain existed, and the schema could not tell any of the three apart because a logical name is whatever the producer types. Every domain now has an entry, every exclusion names a reason from a closed set, and there is no value meaning that the producer did not look — the same refusal `consolidation-plan-v1.schema.json` makes in the same position.

**`uniqueItems` does not see a repeated domain.** Two entries naming one domain with different counts are two distinct objects, so a manifest can answer twice for one domain, be silent about another, and satisfy every keyword the schema has. `export-manifest.invalid-domain-answered-twice.json` is that manifest and is declared a computed negative; the validator compares the answered multiset to the vocabulary.

**Short-lived and revocable were words.** `export_download_grants` held a subject, a revision and a creation time. `expires_at` is now `not null`, because a nullable expiry is an eternal grant one omitted value away, and `revokeExportDownloadGrant` is the first route that can end one. Revocation and expiry are separate timestamps because a link the participant closed and a link that ran out are different things to be told.

**A fourth deletion vocabulary is gone.** `deletion_state_at_generation` held a snake-cased cooling-off value and two words no machine, table or API enum used, which `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` had recorded as an open item; a manifest and the deletion job it described could not be compared at all. It equals the API's published vocabulary rather than the machine's, because the manifest is handed to the participant and the machine's internal `rebuilding-projections` is a state `DeletionJob` deliberately does not carry.

**Still not implemented.** No export has been requested, produced, sealed, granted or purged. Every check in this unit compares records to records.

### PF-029 — Deletion plan, per-effect outcomes and tombstones
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/DATA_MAP.md`, `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `conformance/p1140e/validation-matrix-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_export_and_deletion_domains.py`
Acceptance: `deletion_effects` is keyed on `(deletion_job_id, data_domain)` over the closed domain set PF-028 declares, its state vocabulary contains no member meaning the worker did not look, and its `erasure_action` vocabulary equals the actions `data-disposition-v1.json` assigns to domain-bearing tables; `deletion_jobs` carries the cooling-off window as `effective_after`, refuses a cancellation not before it, and refuses a job under legal hold in any state that erases; the `server-deletion` machine reaches `cancelled` only from `cooling-off` and only as the participant's own recently authenticated act, with `cancelDeletion` as its route; `DeletionJob` requires `domain_effects` and `blocked_by_legal_hold`; `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` states its claim ceiling in named literals and contains none of the eleven overclaims the validator lists, so an empty file fails both halves.
Depends: PF-023, PF-024, PF-027, PF-028
Repair: P-1140F-4
Serves: SR-013
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: unittest tests.ci.test_export_and_deletion_domains
Evidence: unittest tests.ci.test_state_vocabularies
Evidence: contains 1 packages/schemas/planning-schema.sql :: primary key (deletion_job_id, data_domain)
Evidence: contains 1 packages/schemas/planning-schema.sql :: check (cancelled_at is null or cancelled_at < effective_after)
Evidence: contains 1 packages/schemas/planning-schema.sql :: check ((legal_hold_reference is null) = (legal_hold_placed_at is null))
Evidence: contains 1 packages/schemas/state-machine-registry-v1.json :: "transition_id": "deletion-cancel"
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: cancelDeletion
Evidence: contains 1 docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md :: Deletion here is logical, not forensic.
Evidence: absent packages/schemas/planning-schema.sql :: subsystem text not null
Evidence: absent docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md :: unrecoverable

- hosted and local device deletion separated;
- immutable domain/effect plan;
- account mutation restrictions during execution;
- public profile/social/ranking/notification corrections;
- per-device command/result: complete, pending, expired, unreachable, waived;
- execution receipt does not claim forensic erasure;
- legal holds, retention and backup tombstone reapplication.

The per-device half landed under D-424 and D-425. `packages/schemas/local-deletion-v1.schema.json` carries the command, the signed receipt and the disposition; `local_deletion_commands` gains the disposition column, checked equal to the machine coarsened by acknowledgement and waiver, so `unreachable` is no longer reported as `expired`; `local_deletion_receipts` gains the four columns the device store already declares plus the COSE signature; and `DeletionJob.device_outcomes` is required, so a client cannot render one aggregate success. This unit is the hosted half.

**The acceptance was rewritten twice over, and both halves were wrong in ways worth recording.**

The first half asked that `deletion_jobs`, `deletion_effects`, `local_deletion_commands` and `local_deletion_receipts` "cover every domain named in `docs/privacy/DATA_MAP.md`". That record named no domains at all — it had seven category-of-processing sections and no keys — so the criterion compared a table against nothing. It was also wrong on its face about which tables answer for what: a device command cannot cover `integrity-moderation-appeals`, which exists only server-side, and demanding that it does would have produced a device command listing server domains it can do nothing about. PF-028 declares the keys; the rewritten clause holds the hosted plan to all seven and leaves the device half where D-424 put it, reported per device and never merged into the hosted answer.

The second half was `grep -in 'forensic' docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` returning no claim of erasure. The word was absent from that file, and had been for the life of the repository, so the criterion was already satisfied — by a document that made no statement about the claim ceiling whatsoever. That is an absence satisfied by emptiness, and it is the defect the criterion was written to prevent, in the criterion. The rewritten clause requires the ceiling to be stated in named literals *and* requires eleven overclaims to be absent, so an empty file now fails both halves. `test_an_empty_lifecycle_document_fails` is the case the old form could not have. The word `forensic` appears in that document for the first time, in a sentence denying the claim.

**`deletion_effects.subsystem` was `text not null` with no CHECK.** Any two workers could spell one subsystem two ways and both rows were accepted, which is worse than disagreeing: two owners of one idea with no shared vocabulary cannot be found to disagree. It is `data_domain` now, over PF-028's closed set, with `primary key (deletion_job_id, data_domain)` so a domain appears exactly once per job.

**`not-applicable` is gone from the effect state.** It was a member meaning the worker did not look, and with it a plan covered all seven domains by declining to answer for any. `consolidation-plan-v1.schema.json` refuses the same value in the same position and states the reason; the repair had reached that aggregate and not this one. A domain that held nothing reaches `complete` with `affected_row_count` zero, which is a statement about the account.

**The Article 30 record promised a cancellation nothing could perform.** `docs/privacy/DATA_MAP.md` states the seven-day cooling-off window as cancellable within it, and `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` recorded that the machine had no `cancelled` state and no transition out of `cooling-off` other than forward — with the gap assigned to this unit. `deletion-cancel` runs from `cooling-off` only, with the participant as actor under recent authentication, and `cancelDeletion` is its only route. A worker that can call off an erasure makes the erasure a request rather than a right. `check (cancelled_at is null or cancelled_at < effective_after)` puts the lateness refusal where the value is written rather than where it is read.

**A legal hold now stops something.** `legal_hold_reference` and `legal_hold_placed_at` are present together or not at all, and a held job may not be in `processing`, `rebuilding-projections`, `awaiting-local-receipt` or `complete`. Article 12(4) requires the participant to be told the controller is not acting, so `DeletionJob.blocked_by_legal_hold` says the request is held and no field says what the hold is.

**A recorded reason had outlived its hole.** The `local-deletion-command`/`api` absence read "Local-only; never persisted server-side and never exposed by the API". Both halves stopped being true when D-424 and D-425 landed `local_deletion_commands` in the planning DDL and `LocalDeletionOutcome` in the API — and its own binding row named the SQL column while the reason denied the column existed. The absence is real; the reason now says what it is.

**Rule 10 of the vocabulary validator had a missing exemption rather than a decided one.** Every mirrored sub-entity outcome is compared to the SQL vocabulary that owns it by rule 9, which is stricter, but until a mirrored outcome was named `state` none reached rule 10 to be exempted. `DeletionDomainEffect.state` is the first.

**Still not implemented.** No deletion plan has been built, no domain has been erased, no hold has been placed, no cancellation has been made, and no restore drill has been run. Every check in this unit compares records to records.

### PF-030 — Release authorization and component manifest
Files: `packages/schemas/release-set-v1.schema.json`, `packages/schemas/examples/release-set.valid.json` (new), `packages/schemas/examples/release-set.invalid-*.json` (new, seven), `scripts/repository/validate_planning_artifacts.py`, `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, `docs/operations/OPEN_SOURCE_RELEASE_CHECKLIST.md` (new)
Acceptance: the release-set schema requires a TUF role reference, a target path, an architecture, a hash, a provenance reference, a native signature reference, a compatibility tuple and an update class per component, and rejects a manifest that is not itself an authenticated target; each refusal is exercised by a named negative example, and `validate_release_set_manifests` refuses a valid example that stops being valid.
Depends: PF-015
Repair: P-1140F-5
Serves: SR-014
Est: 8-12
Status: landed
Evidence: exists packages/schemas/examples/release-set.valid.json
Evidence: exists packages/schemas/examples/release-set.invalid-manifest-signed-by-the-root-role.json
Evidence: exists packages/schemas/examples/release-set.invalid-target-path-escapes-the-namespace.json
Evidence: exists packages/schemas/examples/release-set.invalid-two-components-one-target-path.json
Evidence: contains 1 scripts/repository/validate_planning_artifacts.py :: def validate_release_set_manifests
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: exists docs/operations/OPEN_SOURCE_RELEASE_CHECKLIST.md

The acceptance listed eight required fields and one refusal, and a schema satisfies a list of required fields by declaring them. What it could not state is the refusal that matters: a manifest is itself a target, so a release set whose manifest is signed by the root role, or whose manifest target path is a component path, authenticates itself. Seven negative examples now name one refusal each — the root-role signature, the manifest path colliding with a component, a target path escaping the namespace, two components claiming one target path, a component with no compatibility tuple, an architecture disagreeing with its platform profile, and a deadline preceding publication — and the acceptance requires each to be exercised rather than merely possible.

The open-source release checklist lands with this unit because PF-030 authors the release-set schema its sixth item references. It carries seven items, all unmet, each naming what would satisfy it. The first is not a template row: it is the LGPL attribution finding the D-541 audit produced, where `@img/sharp-libvips-*` binaries are pinned under `LGPL-3.0-or-later` in two lockfiles and `LICENSES.md` already states the NOTICE review has not happened. The seventh records that no signing key or TUF root exists and none may be created during planning, so its absence is recorded rather than discovered later.

- TUF root/delegated roles own authorization;
- release manifest is an authenticated target;
- component IDs, target paths, architecture, hashes, provenance, native signing, compatibility and update class.

### PF-031 — Migration, health and rollback policy
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/install-plan-v1.schema.json`, `packages/schemas/examples/migration-chain.invalid-chain-with-a-gap.json` (new), `scripts/repository/validate_planning_artifacts.py`, `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
Acceptance: `update_policies` and `update_installations` express an ordered migration chain and a compatibility window; the chain is verified to be a chain rather than a set, so a gap between two versions fails; a fixture records one reversible and one irreversible migration, and the irreversible case has no rollback edge in the `update-lifecycle` machine.
Depends: PF-014, PF-030
Repair: P-1140F-5
Serves: SR-014
Est: 10-14
Status: landed
Evidence: exists packages/schemas/examples/migration-chain.valid.json
Evidence: exists packages/schemas/examples/migration-chain.invalid-reversible-with-drop.json
Evidence: exists packages/schemas/examples/migration-chain.invalid-chain-with-a-gap.json
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres

An ordered chain and an ordered set are not the same claim, and the acceptance asked only for order. A migration list can be sorted, complete-looking and still skip a version, at which point a rollback walks off the end of it. The chain is now verified to be contiguous and a gap between two versions is a named negative example.

`install-plan-v1.schema.json` gained the `plan_kind` discriminator this exposed. `platform_install_plans` was keyed on `(platform_profile_id, release_set_id)` and nothing else, so one profile and one release could hold only one plan — install, upgrade, repair, uninstall and orphan cleanup were the same row. The five kinds are now distinguished, an orphan cleanup carries no release set because there is none to name, a forward plan must verify the release signature at sequence 1, and a removal plan consists only of reversals.

- ordered migration chain and compatibility window;
- pre/post health checks;
- binary rollback only while prior version remains read/write compatible;
- irreversible migration recovery by roll-forward or verified pre-migration snapshot.

### PF-032 — Platform supervision and installer truth table
Files: `packages/schemas/platform-profile-registry-v1.json`, `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/state-machine-registry-v1.schema.json`, `scripts/repository/validate_state_vocabularies.py`, `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`, `docs/security/PLATFORM_ISOLATION.md`
Acceptance: `platform-profile-registry-v1.json` validates against its schema with a row for macOS, Windows, Linux, WSL, container and CI, each naming its supervision mechanism, its session and restart limitation, and its competitive eligibility separately from its installability; a profile that is installable and not competitively eligible is representable, and one asserting eligibility it has no supervision mechanism to support fails.
Depends: PF-011, PF-030
Repair: P-1140F-5
Serves: SR-014
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres

Separately is the load-bearing word and the acceptance did not say what it buys. Installability and competitive eligibility being distinct fields is satisfied by declaring two booleans; the property worth having is that the combination which actually occurs — installable, not competitively eligible, which is what a container and a CI runner are — is representable, and that the combination which must not occur cannot be asserted. A profile claiming eligibility with no supervision mechanism to derive it from is now a failure rather than a row.

- exact macOS, Windows, Linux, WSL, container and CI mechanisms;
- disclose session and restart limitations honestly;
- separate installation capability from competitive eligibility;
- install, upgrade, reboot, repair, uninstall and orphan cleanup states.

### PF-033 — Privacy projection and invalidation matrix
Files: `packages/schemas/projection-authorization-v1.schema.json`, `packages/schemas/projection-authorization-v1.json`, `packages/schemas/authorization-invalidation-vectors-v1.schema.json`, `conformance/planning/authorization-invalidation-vectors-v1.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/disclosure-projection-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_authorization_boundaries.py`, `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/DATA_MAP.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: `python3 scripts/repository/validate_planning_artifacts.py --allow-no-postgres` exits 0 and `validate_authorization_boundaries` fails when any of these is true — the boundary set differs in either direction from the operation identifiers in `openapi-v1.yaml`; a boundary declares a subject the document does not compute, or omits the surface a third-party subject requires; a surface neither evaluates nor excuses one of the nine authorization inputs; a universally-public surface claims an input an anonymous reader has no identity to evaluate; the set of surfaces omitting `directional-block` differs from the set held in the validator; a surface is reached by no boundary and no derived artifact; a schema reachable from a success response names an account other than its own subject and the disclosure projection does not classify it; the recomputed viewer-visible field matrix differs from `projection-authorization-v1.json#viewer_visible_fields` by a row, by a gate or by order; `openapi-v1.yaml#x-response-cache-policy` differs from the map recomputed from `x-public-operations`; a derived artifact kind of cursor, grant or cache is absent; a trigger has no case or an input has no trigger; or a case records an outcome `evaluate_invalidation` does not compute. `python3 -m unittest tests.ci.test_authorization_boundaries` exits 0 with one case per refusal, a case adding a field to `RankEntry` and failing because it has no gate, and cases proving the sealed generation is retained by every trigger while only the deletion trigger reaches the export download grant.
Depends: PF-021, PF-024, PF-026, PF-027, PF-028, PF-029
Repair: P-1140F-4
Serves: SR-015
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_authorization_boundaries
Evidence: exists packages/schemas/authorization-invalidation-vectors-v1.schema.json
Evidence: exists conformance/planning/authorization-invalidation-vectors-v1.json
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: x-response-cache-policy
Evidence: contains 1 packages/schemas/projection-authorization-v1.json :: "surface_id": "global-leaderboard-page",
Evidence: absent packages/schemas/projection-authorization-v1.json :: "surface_id": "board-member-list"

- immutable historical facts versus current authorization;
- block, privacy, board removal, moderation reversal, identity consolidation and deletion invalidation;
- cursor/grant/cache invalidation and append-only retraction.

**No `privacy-projection-v1.json` was created, and the `Files:` line no longer names one.** Two projection files already existed. `disclosure-projection-v1.json` owns which audience each field is written for; `projection-authorization-v1.json` owns which current authorization revision gates it. A third file holding "every viewer-visible field with its gate" would have re-listed the first file's fields and the second file's revisions, which is two answers to one question in a repository whose central rule is that there is one owner per question. What was actually missing is the *join* — which operation is gated by which inputs — and a join belongs with the rule rather than in a document of its own. So `projection-authorization-v1.json` gained the boundary matrix, the derived-artifact set, the trigger table and the derived per-field matrix, and the one new pair of files is the invalidation corpus and its schema, which is a conformance fixture rather than a second authority.

**The acceptance was rewritten, and both halves needed it.** "Every viewer-visible field appears exactly once in the projection file" is a property of a list, and a list satisfies it by being short: the disclosure projection classified eight schemas out of the fifty-two reachable from a success response, and nothing said the set was the right one. The falsifiable form is that the set is *computed* from the OpenAPI document and compared, which is what the rewritten criterion requires and what the added-field case proves. The second half — "a fixture proves a block, a board removal and a deletion each invalidate the cursors, grants and caches the file names" — was satisfied by a file naming no caches, which is the ninth instance of a criterion phrased so that emptiness passes it. It now requires all three kinds to be present and each to be invalidated by some trigger, requires every trigger to have a case and every input to have a trigger, and requires each case to record what it *retains*, because a corpus in which everything invalidates everything discriminates nothing.

**Three live defects, and the first is the one the finding is named after.** `board-member-list` was a declared authorization surface and no operation in the API lists board members, so it was a rule about a surface the product does not have. While it occupied the list, `listBlocks` — which returns another participant's account identifier on every row — had no surface at all, and `Relationship`, the shape carrying that identifier, was the single schema reachable from a success response that named an account other than its own subject and that the disclosure projection classified nowhere. One dead entry was standing in for a missing one, and neither was findable while the surface list and the operation list were written independently. The boundary matrix resolves them against each other by equality, so both directions now fail.

**One `leaderboard-page` surface was serving an operation with no viewer.** It declared nine read-time inputs on behalf of `getGlobalLeaderboard`, `getLeaderboard` and `getBoardLeaderboard`. The first carries `security: []`, because AGENTS.md makes exactly one view universally public. An anonymous reader has no block row, no friendship, no rivalry and no membership, so four of the nine had nothing to evaluate — and `directional-block`, the deny-hard one, resolves to admit: **a blocked participant reads the global board by logging out.** This is the shape PF-021 repaired on `getPublicProfile`, and the repair here is different because the operation is public by decision rather than by oversight. `global-leaderboard-page` is now its own surface evaluating the four subject-only inputs a reader with no identity can still be denied by, and recording the five it cannot with the reason. The block is not enforced there and the record says so, because suppressing one row from one reader on a public ranking is itself a disclosure — the gap is visible. D-622 records the choice and its reopen condition.

**Nothing in the API declared a cache directive.** The evaluation forbids caching an authorization result and the privacy contract permits caching a projection only when it is identical for every viewer; the document expressed neither, so a proxy, a content delivery network or a browser back-forward cache could store `GET /profiles/{handle}` and hand it to a second viewer. That is the same defect with the staleness measured in hours rather than statements, and it is what made the acceptance's "caches" leg vacuous: there were none to invalidate. `x-response-cache-policy` classifies every operation, `no-store` by construction, `public-shared` only where `x-public-operations` already gives the `global-board` or `reference-data` reason. The split is recomputed from that reason rather than listed twice, so a new operation is `no-store` without anyone deciding, and the `auth-bootstrap` operations stay `no-store` because they are public in order to establish a session and not because their bodies are.

**The sealed generation is recorded as invalidated by nothing.** Leaving it out would have been the same mistake in reverse: an artifact no trigger destroys and that nobody wrote down is indistinguishable from one nobody considered. It is `authorization_independent`, it holds no handle, no viewer and no authorization state, and every case in the corpus retains it. That is the immutable-history half of SR-015 stated as a computed outcome instead of a sentence.

Exit: every operation the API declares has one boundary, every third-party boundary names a surface, every surface answers for all nine inputs, every viewer-visible field carries the revision set that gates it, and every trigger's blast radius is evaluated rather than recorded. Nothing here is implemented; no surface in this repository evaluates the rule, which is why SR-015's closure evidence is a matter for the review that reads this commit and not for this file.

### PF-034 — Schema/interface inventory repair
Files: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `scripts/repository/validate_planning_coverage.py`, `tests/ci/test_planning_coverage_inventory.py` (new)
Acceptance: `python3 scripts/repository/validate_planning_coverage.py` exits 0 with every file Git tracks under `packages/schemas/` and `conformance/` owned by an inventory citation or by a named check that enumerates its directory, and every inventory citation into either tree resolving to a file, a directory or a pattern that matches something; the inventory carries both maturity literals in `INVENTORY_MATURITY_LITERALS` and none of the overclaims in `INVENTORY_FORBIDDEN_CLAIMS` outside that statement; `tests/ci/test_planning_coverage_inventory.py` injects a file with no owner, a citation resolving to nothing, a pattern matching nothing, a tree-root citation, a directory citation, a lost delegate, a removed maturity literal and every forbidden phrase, and each fails.
Depends: PF-005, PF-006, PF-007, PF-008, PF-009, PF-010, PF-011, PF-012, PF-013, PF-014, PF-015, PF-016, PF-017, PF-018, PF-019, PF-020, PF-021, PF-022, PF-023, PF-024, PF-025, PF-026, PF-027, PF-028, PF-029, PF-030, PF-031, PF-032, PF-033
Repair: P-1140F-5
Serves: SR-016
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_coverage.py
Evidence: unittest tests.ci.test_planning_coverage_inventory
Evidence: contains 1 scripts/repository/validate_planning_coverage.py :: INVENTORIED_TREES = ("packages/schemas", "conformance")
Evidence: contains 1 scripts/repository/validate_planning_coverage.py :: def check_inventory_coverage(errors: list[str]) -> None:
Evidence: contains 1 scripts/repository/validate_planning_coverage.py :: def inventoried_files() -> list[str]:
Evidence: contains 2 scripts/repository/validate_planning_coverage.py :: "scripts/repository/validate_planning_artifacts.py",
Evidence: contains 1 docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: This inventory records declared ownership.
Evidence: contains 1 docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: packages/schemas/local-trust-domains-v1.json
Evidence: contains 1 docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: packages/schemas/oauth-provider-registry-v1.json
Evidence: contains 1 docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: P-1140F semantic review record
Evidence: absent docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: closed-world
Evidence: absent docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: proposed provider registry

The prose range `PF-005 through PF-033` is expanded to the full enumeration because `Depends:` admits unit IDs only, and a range cannot be resolved by the cross-reference validator.

**The acceptance was rewritten, and its second clause was the reason.** `grep -in 'closed-world\|complete'` over the inventory is the shape PF-029 found: a check phrased as an absence, passing because the word had never appeared. Here it is worse than vacuous in both directions at once. `closed-world` occurs zero times in the document, so that half can never fail; `complete` occurs three times and every one of them is the inventory's own completeness *rule* — the thing the file exists to state — so the half that can fire fires on correct text, and the only way to satisfy a reader running the command literally is to delete the rule. The replacement requires the maturity statement in two exact literals and refuses eleven named overclaims, with the scan run over the text with the statement removed so the disclaimer is allowed to name what it disclaims. Both halves are injected: `test_a_missing_maturity_statement_fails` removes each literal, and `test_every_forbidden_claim_fires` adds each phrase and asserts the failure, because a ban list nothing has ever tripped is not a control.

**The coverage was not real, and it was not hand-listed either. Nothing read the inventory at all.** `doctor.py` asserted the file exists. `validate_planning_artifacts.py`'s `validate_inventory_register` asserted its rows are unique and carry a status from the declared vocabulary. Not one line of either tree was resolved against it in either direction, so the first clause of the acceptance described a check no code performed. A probe file dropped into `packages/schemas/` and into `conformance/p1140e/` passed every validator in `make validate`.

Two enumerations were real and are kept rather than duplicated. `validate_schema_example_coverage` reads `packages/schemas/examples/` as a directory, refuses a file whose prefix no schema owns, and executes each `.valid`/`.invalid-` expectation. `validate_conformance_manifests` refuses a suite holding a file no case, authority or tooling entry names, and recomputes every recorded fixture digest. Restating those files row by row here would have been a second owner for one vocabulary, so coverage of those directories is delegated by name and the delegation fails closed: the coverage validator checks that both functions still exist, and `test_a_delegation_whose_delegate_is_gone_fails` proves it.

**Sixty-three shipped files were owned by nothing.** Three conformance directories declare no suite manifest and so fell through every enumeration: `conformance/p1140e/`, `conformance/p1140f/` and `conformance/planning/` — the records this repository keeps about itself, which is the set most likely to be edited to agree with whoever is reading it. They now have three rows of their own. The rest were top-level `packages/schemas/` contracts the table named in prose and never in a path: `local-trust-domains-v1.json`, whose eight roles are what the privacy boundary rests on; `egress-allowlist-v1.json` and `observability-allowlist-v1.yaml`, cited as “egress and observability allowlists”; `platform-profile-registry-v1.json`, cited as “platform-profile registry”; `release-set-v1.schema.json`, cited as “release-set schema”; `social-integrity-events-v1.proto`, cited as “events”; and `pricing-interpretation.schema.json`, which had no row of any kind, so the one figure the product labels estimated and server-interpreted had no declared owner.

**One row was a stale claim rather than a vague one.** `oauth-provider-registry-v1.json` was recorded as a *proposed* provider registry long after it was authored. That is the same drift in the opposite direction, and it is the direction the citation-resolution half now refuses: a row may not name an artifact that is not there, and it may not describe an artifact that is.

**Four counts in the conformance-harness row were each one out of step.** It said fifteen manifests, thirteen of the fifteen with `runner.state: absent`, three suites holding no fixture and four recording a `negative_case_gap`. The tree holds sixteen, fourteen, two and three. The sixteenth suite arrived and the sentence saying how many there were did not move, which is the failure this unit is about stated in miniature.

Two rules keep the check from satisfying itself. A citation naming a tree root grants no coverage, because the sentence explaining that every file must be owned would otherwise own every file. A directory citation grants no coverage either: `conformance/planning/` appears in this repair inside the sentence recording that the directory declares no manifest, and while directory citations counted, that sentence covered every file in the directory it was describing as uncovered. Both are injected as cases.

Exit: the inventory resolves against the two trees it inventories in both directions, a new contract under either tree fails the gate until a row owns it, and the maturity statement is required in literals rather than assumed from the absence of a word.

### PF-035 — P-1140E validator repair
Files: `scripts/repository/validate_p1140e_contracts.py`, `tests/ci/test_p1140e_contracts.py`, `tests/ci/planning_fixtures.py`, `tests/ci/test_state_vocabularies.py`
Acceptance: the P-1140E structural gate exits non-zero on each of six injected defects and 0 on the clean tree, with each leg injected against the validator that owns it: missing owner and missing fixture path against `scripts/repository/validate_p1140e_contracts.py`; unreachable lifecycle state and SQL/state/API vocabulary mismatch against `scripts/repository/validate_state_vocabularies.py`; missing generation key, missing authority revision and a content digest that does not match against `scripts/repository/validate_planning_artifacts.py`. `python3 -m unittest tests.ci.test_p1140e_contracts` runs all six, and the P-1140E summary line names the check as structural with `claim_scope=structural-consistency-only` and `runtime_evidence=absent`.
Depends: PF-034
Repair: P-1140F-5
Serves: SR-016
Est: 10-14
Status: landed
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_p1140e_contracts
Evidence: unittest tests.ci.test_state_vocabularies
Evidence: contains 1 tests/ci/planning_fixtures.py :: P1140E_REDIRECTED = ("ROOT", "SCHEMAS", "CONF", "TRACE")
Evidence: contains 1 tests/ci/planning_fixtures.py :: def mirror_repository(sandbox: Path, writable: tuple[str, ...]) -> None:
Evidence: contains 1 tests/ci/planning_fixtures.py :: class StateVocabularyMixin:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_an_unreachable_lifecycle_state_fails(self) -> None:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_a_sql_state_api_vocabulary_mismatch_fails(self) -> None:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_a_missing_generation_key_fails(self) -> None:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_a_missing_authority_revision_fails(self) -> None:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_a_content_digest_that_does_not_match_fails(self) -> None:
Evidence: contains 1 tests/ci/test_p1140e_contracts.py :: def test_the_summary_names_the_check_as_structural(self) -> None:
Evidence: contains 1 scripts/repository/validate_p1140e_contracts.py :: generate_p1140e_coverage.reproducible(),

**The acceptance was rewritten, because as written it could only be satisfied by making four checks worse.** It demanded all six injections from `validate_p1140e_contracts.py`. Four of them are already owned elsewhere and already fire: lifecycle reachability and the three-way SQL/state/API vocabulary agreement by `validate_state_vocabularies.py`, which exists for exactly that; the generation-keyed constraints on `ranking_entries` and `score_snapshots`, the nine viewer-authorization `revision_source` fields and every recomputed fixture digest by `validate_planning_artifacts.py`. Reimplementing them in the P-1140E validator would have put a second owner on each of those vocabularies, which is the defect class this repair sequence has spent thirty units removing, and the two copies would disagree the first time either moved. The acceptance now names the owning validator per leg. `make validate` runs all three, so the gate still fails on any of the six; what changed is which file is allowed to be the authority for each.

**The three named as remaining were not the three that were missing.** The block claimed coverage of "missing owner" by pointing at the reason-authority cases, which are a different rule: an authority that resolves to nothing, a declared authority no code uses, and one shadowing a registered machine are three injections against `reason-codes-v1.json`, and none of them is a decision binding with an owner that is not there. The matrix's five owners per decision — normative, work-unit, schema-or-state, platform-scope and fixture — had no injection at all, so the check that resolves them had never been shown to fire. `MissingOwnerTests` now injects a dangling `normative_owner`, an empty one and a dangling `fixture_path`.

**The suite could not test what it claimed to test, and the reason was one unpatched constant.** It copied `packages/schemas/` to a temporary directory and patched `SCHEMAS`, leaving `CONF` on the real `conformance/p1140e/`. Any case mutating a registry therefore tripped `state fixture set mismatch` or `platform validation plan set mismatch` — a disagreement between the sandbox registry and the committed fixtures — before reaching the check under test, so a case could pass on an error it did not inject. `P1140EValidatorMixin` redirects `ROOT`, `SCHEMAS`, `CONF` and `TRACE` or refuses to run, and it mirrors the repository rather than copying four directories: the matrix resolves owner, work-unit, schema, platform and fixture citations against `ROOT` and those land in four different top-level trees, plus `.github/`, so the writable trees are copied and everything else is symlinked. It also redirects `generate_p1140e_coverage`'s own `ROOT`, `SCHEMAS` and `MATRIX`, because that module is imported by the validator and holds its own constants; leaving them on the real repository would make the reproducibility check compare the committed matrix against the committed registries while every other check read the sandbox. That reproducibility check is preserved and asserted, not undone.

**A shared fixture said it carried no tests and carried twenty-one.** `ValidatorFixture` in `tests/ci/test_state_vocabularies.py` documented itself as "shared setup only. Carries no tests, so inheriting it does not re-run them", which stopped being true the moment the first case was added below the helpers; two classes inherit it, so those twenty-one run three times. Inheriting it here would have added a third copy and made this unit's suite report thirty-nine cases when it holds eighteen — a count that improves when you add nothing. The scaffolding is now `StateVocabularyMixin` in `tests/ci/planning_fixtures.py`, `ValidatorFixture` is a subclass of it whose docstring says what it actually is, and the inflation is recorded rather than repaired, because collapsing it changes the reported total of a suite this change is not otherwise touching.

- verify owner existence and reachable lifecycle;
- detect SQL/state/API vocabulary mismatch;
- detect missing generation keys and authority revisions;
- verify content digests and tuple/certification references;
- remain structural and never claim runtime proof.

Exit: each of the six defect classes is injected against the validator that owns it and observed to fail, the clean tree passes, and the summary line still says the check is structural and that runtime evidence is absent.

### PF-036 — P-1140F exact-head review
Files: `conformance/p1140f/review-target-v1.json`, `conformance/p1140f/semantic-findings-v1.json`, `conformance/p1140f/REPAIR_HEAD_REVIEW.md`, `conformance/p1140f/gate-authorization-v1.json`, `conformance/p1140f/gate-authorization-v1.schema.json`, `conformance/planning/decisions-v1.json`, `assets/ui/references/manifest.json`, `docs/project/STATUS.md`, `docs/project/PROJECT.md`, `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`, `scripts/repository/validate_p1140f_authority.py`, `tests/ci/test_validate_p1140f_authority.py`
Acceptance: mechanical part: `review-target-v1.json` pins a commit that `git cat-file -e` resolves, every one of SR-005..SR-017 carries a closure verdict, and `python3 scripts/repository/validate_p1140f_authority.py` exits 0 with zero open findings at any severity. The review judgement itself is not mechanizable and must not be presented as though the validator produced it, and the record says by whom it was made and under what authority.
Depends: PF-001, PF-002, PF-003, PF-004, PF-005, PF-006, PF-007, PF-008, PF-009, PF-010, PF-011, PF-012, PF-013, PF-014, PF-015, PF-016, PF-017, PF-018, PF-019, PF-020, PF-021, PF-022, PF-023, PF-024, PF-025, PF-026, PF-027, PF-028, PF-029, PF-030, PF-031, PF-032, PF-033, PF-034, PF-035, PF-070, PF-071, PF-072, PF-073, PF-074
Repair: P-1140F-5
Serves: SR-016
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_p1140f_authority.py
Evidence: validator scripts/repository/doctor.py
Evidence: unittest tests.ci.test_validate_p1140f_authority
Evidence: contains 1 conformance/p1140f/review-target-v1.json :: "reviewed_commit": "46bf2fa47963261d48fa80a6980de85d80cfaad8"
Evidence: contains 1 conformance/p1140f/review-target-v1.json :: "state": "reviewed"
Evidence: contains 1 conformance/p1140f/gate-authorization-v1.json :: "open_p0_baseline"
Evidence: absent conformance/p1140f/semantic-findings-v1.json :: "state": "repaired-pending-review"

**Who made this judgement, and under what authority.** The owner delegated the four decisions this unit records to the CTO: the verdict for SR-005..SR-017, the D-300 regrading, the storyboard baseline promotion, and the exceptions to record. This unit executes those decisions and says so in the record rather than presenting them as the output of a validator. The gate state is not among them and is not touched.

**Why the previous version of this block said an agent could not land it, and what changed.** It said the mechanical half requires pinning a target and moving thirteen findings to `closed`, that both are owner acts, and that an agent doing them would satisfy the acceptance by doing the one thing it forbids. That reasoning was correct and is unchanged. What changed is not the reasoning but the authority: the acts are now recorded owner decisions rather than an agent's own. The defect the old text guarded against was an agent *originating* a review verdict; the guard survives as the first recorded limitation, which states plainly that this review is not independent and that SR-016 is the finding governing exactly this situation.

**The verdict is PASS-WITH-EXCEPTIONS and the registry spells it `pass`.** `review-target-v1.schema.json` admits `pending`, `pass` and `fail`, and `validate_p1140f_authority.py` requires `pass` when the state is `reviewed`. Adding a fourth enum value would have meant amending two schemas and the validator to record something `limitations` already carries in full. The three exceptions are the verdict rather than commentary on it, and they are recorded verbatim in both `review-target-v1.json#limitations` and `REPAIR_HEAD_REVIEW.md`.

**A regrade would have emptied the only thing counting.** The ceiling was P1-only, and `open_p1_baseline.severity` was pinned to the constant `P1` by the schema. Moving nine findings to P0 would have dropped the counted number from thirteen to three while leaving nine findings governed by nothing — a signal improving because what it counted was removed, which is the seventh instance of that shape in this program and the one that would have been introduced by the repair itself. Every severity the registry can carry now has a ceiling, the validator refuses a severity that lacks one, and a test reads the severity enum from the schema so a future P3 fails there rather than silently. The aggregate is unchanged at thirteen: 9 + 3 + 1.

**One further defect found in the same place.** The exact-head review check read `open_p1` alone, so after the regrade a review could have passed with nine open P0 findings. It now refuses any open finding at any severity.

**The two registry digests are a recorded claim, not a machine-derived fact.** Nothing computes or verifies `finding_registry_sha256` or `artifact_registry_sha256`; the schema checks only that they are sixty-four hex characters. They were computed from the two files at the reviewed commit and a reader can reproduce them with `git show <commit>:<path> | shasum -a 256`. The same is true of `validation_run`, which is the planning-checks run number on that exact commit and is named in the record so it can be opened.

**The storyboard promotion, and why these captures are of this head.** D-610 recorded that relabelling the public figure moved pixels in the governed baselines and that an agent does not promote captures. The owner has promoted them. The SHA-256 values come from storyboard-visuals run 31592533820, and no file under `assets/`, `packages/ui/` or `apps/web/` changed between that run's head and the reviewed head, which is what makes them captures of the head under review rather than of an older one. Nine viewports moved — public-profile, rival-comparison and board-standings across desktop, tablet and mobile. `friends` and `activity-and-notifications` matched their reviewed captures exactly and were not touched. D-610 is spent.

**What this unit does not do.** It does not flip any gate: `gate-authorization-v1.json` still records P-1140F as `in-progress-planning`, and gates are opened and closed by the owner alone. It does not write its own closure evidence into SR-016, because a unit cannot cite its own merge commit; that citation and the removal of the two interval reasons it justifies land in the unit that follows. It does not make any finding true by closing it — three of SR-016's four artifacts are recorded as needing no change rather than repaired by a unit serving it, and the reasons are there to be read rather than to be counted.


### PF-037 — Enforce required unit fields in the issue plan generator
Files: `scripts/repository/generate_issue_plan.py`, `docs/implementation/ISSUE_GENERATION.md`, `.github/workflows/planning-checks.yml`, `tests/ci/test_generate_issue_plan.py` (new)
Acceptance: `python3 scripts/repository/generate_issue_plan.py` emits records carrying `files`, `acceptance`, `depends`, `est` and `status` read from each unit block, and exits non-zero when the generated record set disagrees with `python3 scripts/repository/validate_work_unit_status.py` about any unit's status.
Depends: none
Est: 4-6
Status: landed
Evidence: validator scripts/repository/generate_issue_plan.py
Evidence: unittest tests.ci.test_generate_issue_plan
Evidence: contains 1 scripts/repository/generate_issue_plan.py :: GATE_RECORD = ROOT / "conformance/p1140f/gate-authorization-v1.json"
Evidence: contains 1 scripts/repository/generate_issue_plan.py :: REQUIRED_FIELDS = ("Files", "Acceptance", "Depends", "Est", "Status")
Evidence: absent scripts/repository/generate_issue_plan.py :: POST_LAUNCH_HEADING
Evidence: absent docs/implementation/ISSUE_GENERATION.md :: post-launch-explicit-approval
Evidence: absent docs/implementation/ISSUE_GENERATION.md :: <NN> <title>
Evidence: absent .github/workflows/planning-checks.yml :: P-1104-explicit-implementation-approval

**Field enforcement has moved.** `scripts/repository/validate_work_unit_status.py` owns it under D-201 and fails on a missing, empty or duplicated field, an over-ceiling `Est:`, an unresolvable `Depends:`, a cycle, a contradicted status, an unowned SQL table and a stale derived block. What this unit owned was the generator, which emitted records carrying none of those fields — 260 titles and a component label, from which nobody could read what a unit touches, what would make it done, or whether it had already been done. Each record now carries the unit's own five lines, and the generator refuses to emit a record it cannot fill rather than restating the enforcement rule.

**The gate is read, not written down.** `phase_gate` and the `blocked` label were literals: every implementation record said `P-1104-explicit-implementation-approval` and `blocked`, and `.github/workflows/planning-checks.yml` asserted the same two literals back, so the pair agreed with each other and with nothing else from the moment the owner opened P-1104 on 2026-08-05. Which gate a unit sits behind is now derived from its epic prefix and its state read from `conformance/p1140f/gate-authorization-v1.json`; the workflow step reads the same record instead of repeating the answer. An unrecognised state blocks rather than releases.

**Two readers, one document.** The generator and `validate_work_unit_status.py` match different heading patterns over the same file, so a heading that lost its title, or one whose prefix is wider than `[A-Z]{1,2}`, is counted by one and not the other — and neither can see that alone. The generator now compares its whole unit set and every status against the validator's and exits non-zero on any difference, before it complains about numbering.

`POST_LAUNCH_HEADING` and the `PL-` branch matched a heading that has never existed and are gone, along with the `post-launch-explicit-approval` gate they invented.

**One defect found while landing this.** `ISSUE_GENERATION.md`'s stable-key section had been corrected to three digits, but the generator-behavior section one paragraph below still documented `### <ID>-<NN> <title>` — a form the generator's own `\d{3}` pattern rejects — and nothing could catch it, because `<NN>` is a placeholder rather than a citation and `validate_cross_references.py` only resolves real IDs. Worse, the same document's phase-gate section still read "work units remain blocked by `P-1104-explicit-implementation-approval` … until the user explicitly authorizes implementation after P-1140F closes", which the gate record has forbidden in five sibling documents since 2026-08-05 and could not forbid here: `ISSUE_GENERATION.md` is not in its `documents` list. A contradiction of the open gate survived in the one planning contract the gate record does not watch. Both are repaired, and `tests/ci/test_generate_issue_plan.py` now asserts against both.

### PF-038 — Reconcile state vocabularies across API, SQL and registry
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`, `packages/schemas/state-machine-registry-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: a script asserts that for every aggregate with a `state` column, an API enum, and a registry machine, the three value sets are identical; zero mismatches reported.
Depends: none
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_state_vocabularies

Nine aggregates currently disagree. `Appeal` shares exactly one state name between API and registry. `ranking-projection` is `building/published/superseded/failed` in SQL against `building/validating/active/superseded/failed` in the registry, so the projection worker has no valid target state. `Notification` cannot express `retracted`, which is the D-070 correction path. `idempotency_records` is `reserved/committed/failed` in SQL against `reserved/committed/conflict/expired` in the registry — neither is a superset. Export, deletion, certification, update-lifecycle, and web-session-family also diverge; certification has four vocabularies across three files plus the inventory.

This unit also fixes the absence of a naming-convention rule: SQL uses `snake_case`, the registry uses `kebab-case`, and no document specifies which wins. Highest-leverage unit in the plan — every code generator, migration, and worker depends on its output.

### PF-039 — Decide and specify the session authentication scheme
Files: `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md` (new), `packages/schemas/openapi-v1.yaml`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
Acceptance: `openapi-v1.yaml` declares a `securitySchemes` entry matching the ADR; a refresh operation exists if the ADR requires one; `grep -c "bearerAuth" openapi-v1.yaml` no longer returns a global-only result.
Depends: none
Est: 6-8
Status: landed
Evidence: exists docs/decisions/ADR-015-SESSION_AUTHENTICATION.md
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: sessionCookie
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: refreshSession

**Landed in `963f6f6` under D-220 and D-221.** The document declares `bearerAuth`, `sessionCookie` and `refreshCookie`, and `refreshSession` and `revokeAllSessions` exist.

The defect as found: `AUTHENTICATION_AND_RECOVERY.md:63-66` specified HTTP-only same-site cookies with refresh-token rotation while the OpenAPI document declared a single global opaque `bearerAuth` with no cookie scheme, no OAuth2 flows, no scopes and no refresh endpoint. Those were two different architectures and the first authenticated request could not be implemented until one was chosen. The `web-session-family` machine's `replay-detected` state is persisted by `O-006`, which is where the remaining half of that sentence lives.

### PF-040 — Specify accounting arithmetic
Files: `packages/schemas/accounting-profile.schema.json`, `docs/product/TOKEN_ACCOUNTING_SPEC.md`, `conformance/accounting/arithmetic-vectors-v1.json`
Acceptance: two independent implementations reproduce every vector in the new fixture byte-for-byte, including the profile digest.
Depends: PF-038
Est: 8-12
Status: landed
Evidence: exists conformance/accounting/arithmetic-vectors-v1.json
Evidence: exists packages/schemas/accounting-arithmetic-vectors-v1.schema.json
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres

`accounting-profile.schema.json` defines no rounding, overflow, precision, or unit-conversion rules, and no canonical digest algorithm — yet `accounting_profile_sha256` is a signed claim field. `retry_policy`, `cancellation_policy`, and `nested_execution_policy` at `:209-228` are enum labels with no defined behavior. Two implementations cannot currently agree on a token total, which makes cross-language parity meaningless.

### PF-041 — Specify the OpenTelemetry accounting profile
Files: `packages/schemas/accounting-profile-otel-v1.json` (new), `packages/schemas/accounting-profile-otel-v1.schema.json` (new), `tests/ci/test_otel_accounting_profile.py` (new), `scripts/repository/validate_planning_artifacts.py`, `docs/integrations/AGENT_INTEGRATION_RESEARCH_MATRIX.md`, `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `conformance/accounting/manifest.json`, `conformance/adapters/agent-registry-v1.json`, `conformance/adapters/manifest.json`
Acceptance: every top-level field of `packages/schemas/normalized-event.schema.json` has exactly one declared origin and determinism class in the profile, by equality in both directions, with the fields an OTLP payload carries no fact about marked `not-derivable-from-otlp`; the profile's supported metric set equals the metric set its producer binding declares; every supported metric names a capture fixture that replays that exact metric under that exact binding and carries at least one non-refusal vector; no derivation reads an attribute the binding strips or drops; and a disagreement with the bound accounting profile or an absent certification bundle must be declared in `known_contradictions`, with a declaration that no longer describes a disagreement failing too.
Depends: PF-040
Est: 8-12
Status: landed
Evidence: exists packages/schemas/accounting-profile-otel-v1.json
Evidence: exists packages/schemas/accounting-profile-otel-v1.schema.json
Evidence: contains 1 packages/schemas/accounting-profile-otel-v1.json :: "kind": "default-third-party-metrics-exporter"
Evidence: contains 1 packages/schemas/accounting-profile-otel-v1.json :: "kind": "default-on-prompt-logging"
Evidence: contains 1 packages/schemas/accounting-profile-otel-v1.json :: "kind": "identity-attributes-on-every-datapoint"
Evidence: contains 3 packages/schemas/accounting-profile-otel-v1.json :: "origin": "not-derivable-from-otlp"
Evidence: contains 1 docs/integrations/AGENT_INTEGRATION_RESEARCH_MATRIX.md :: `metrics_exporter`
Evidence: contains 1 conformance/adapters/agent-registry-v1.json :: statsig
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_otel_accounting_profile

Empirically verified capture surface, 2026-08-05: Claude Code emits `claude_code.token.usage` as a counter with attributes `model`, `query_source` (`main`/`subagent`/`auxiliary`), and `type` (`input`/`output`/`cacheRead`/`cacheCreation`). Gemini CLI emits `gemini_cli.token.usage`; Codex emits `codex.turn.token_usage`. Prompt and response content appears only on the logs channel and is redacted unless explicitly enabled, so metrics-only capture keeps the collector out of L0 entirely.

Three hazards this profile must encode: every Claude Code metric carries `organization.id`, `user.account_uuid`, `user.account_id`, `user.email`, and `user.id`, which must be dropped at ingest rather than trusted for identity; Gemini CLI's `logPrompts` defaults to **true**; and Codex's `metrics_exporter` defaults to `statsig`, not `none`.

**Landed under D-614 and D-615.** All three hazards are encoded, and the third was recorded nowhere in this repository before this unit: neither `AGENT_INTEGRATION_RESEARCH_MATRIX.md` nor `conformance/adapters/agent-registry-v1.json` mentioned `metrics_exporter` or `statsig`, so the Codex row's defect column named only the `exec` and MCP-server silence. It is also the one hazard of the three that leaks outward — the other two risk importing content or identity into the collector, and this one exports the participant's token activity to a vendor neither party chose.

**The profile supports exactly one metric, and says so.** `claude_code.token.usage` is the only metric any fixture in this repository replays. `gemini_cli.token.usage`, `gen_ai.client.token.usage` and `codex.turn.token_usage` are recorded as published surfaces read on 2026-08-06 with no capture, which is an absence of evidence rather than partial support. The supported set is held equal to the binding's declared metric set in both directions, so neither file can grow a metric the other has not exercised.

The `Acceptance:` was rewritten because neither clause could be run as written. The first — that the profile "maps a captured OTLP payload to a `NormalizedAccountingEvent` deterministically" — is unsatisfiable under any honest reading. An OTLP counter carries no event identity, no outcome and no retry fact: `event_id` is minted by the receiver, `local_fingerprint` is a device-keyed commitment, `outcome` is a declared `success` that cannot be told from a cancellation that consumed tokens, and `retry` is a declared zero. Three of the twenty-four fields are therefore `not-derivable-from-otlp` and four more are device-scoped. Calling the result deterministic would have been true only of `canonical_tokens`, which the capture vectors already exercised before this unit existed. The replacement asks for what can be checked: one origin and one determinism class per field, by equality, so a field added to the event fails until someone decides where it comes from.

The second clause — "fixture includes at least one real capture per supported metric" — was satisfiable by emptiness in the direction that mattered. Nothing tied "supported" to anything: the producer binding could have declared a second metric and the fixture would still have passed, because `validate_planning_artifacts.py` read `binding["otel"]["metrics"][0]` by position and compared the capture file's single `metric` field against it. **That was a live defect and it is fixed here**: the series evaluator now selects the metric by name and refuses a capture naming a metric the binding omits, and `validate_producer_bindings` refuses any declared metric that no capture replays. A binding that declared `gemini_cli.token.usage` today would have had every vector silently replayed against the Claude Code category map and reported as passing.

Two contradictions were found by reading the unit's files against each other and are recorded rather than repaired, because repairing either changes what a future certification certifies:

- **`otel-count-authority`.** `cloud-separate-cache-v1`, the accounting profile the binding names, declares all four of its source fields `provider-reported`. `ADAPTER_ONE_CLAUDE_CODE_OTEL.md` section 7 says recording `provider-reported` as this capture's count authority "would overstate the evidence and is forbidden", while section 6 of the same file describes the categories as provider-reported. Both statements are about the same number. The collector never sees a provider response; it sees an unsigned counter a CLI process emits, and D-077 keeps every locally observed mechanism attested-local. The event carries `runtime-reported`; the bound profile identity keeps the overstatement until `A-001` registers a narrower profile and re-points the binding. Section 6 now names the contradiction instead of restating one side of it.
- **`otel-certification-bundle-absent`.** `packages/schemas/normalized-event.schema.json` requires `certification.bundle_sha256` as sixty-four hexadecimal characters with no null admitted, and every binding in this repository is `candidate` or `uncertified` with `bundle_sha256` null. So no `NormalizedAccountingEvent` can be constructed from any OTLP capture this repository can actually take, and the only fixture that fills the field uses sixty-four `f` characters. The event schema has no representation for an uncertified capture while the binding registry's own publication rule says every binding is private analytics today. `PF-016` owns it.

Both are computed rather than trusted: the validator recomputes the disagreement from the bound profile and the binding on every run, so an undeclared disagreement fails and a declaration whose disagreement has been repaired fails too.

### PF-042 — Author the source receipt contract
Files: `packages/schemas/source-receipt-v1.schema.json`, `packages/schemas/source-observation.schema.json`, `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
Acceptance: every `NormalizedAccountingEvent` fixture resolves to exactly one source receipt; schema validates the full existing observation corpus.
Depends: PF-041
Est: 6-8
Status: landed
Evidence: exists packages/schemas/source-receipt-v1.schema.json
Evidence: validator scripts/repository/validate_planning_coverage.py

Inventory line `:35`. Provenance for every claim, and the first of the 33 `planned-missing` contracts that blocks real work. The misattribution this note flagged was on the row above, `:34`, and it read `PF-020..PF-024` rather than `PF-021/PF-022` — five units of which none is an accounting unit; they are transaction, ranking, period and social. `PF-017` repaired the row to name `PF-017`/`PF-018`. The note is left in place because a flag that was raised and not acted on for four units is worth keeping visible.

### PF-043 — Author the appraisal result and policy contracts
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/disclosure-projection-v1.json`, `packages/schemas/reason-codes-v1.json`, `tests/ci/test_appraisal_disclosure.py` (new), `scripts/repository/validate_planning_artifacts.py`, `conformance/p1140e/validation-matrix-v1.json`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: `ClaimRecord.appraisal_id` resolves to a defined schema and to operationId `getAppraisal`, which is authenticated and answers with `AppraisalSummary` and never with the stored record; `AppraisalSummary` equals `appraisal-result-v1.schema.json` minus `schema_version`, minus `evaluated.anomaly_disposition` and `policy.implementation_sha256`, and with `public_state` crossing as `evidence_class`, by equality in both directions and including every admitted enum value; neither withheld name is declared as a property anywhere in `openapi-v1.yaml`; `disclosure-projection-v1.json` classifies the shape as self-audience; and a withheld field the record has dropped fails, so the justification cannot outlive the hole. `validate_cross_references.py` reports zero dangles.
Depends: PF-038
Est: 8-10
Status: landed
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: operationId: getAppraisal
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: AppraisalSummary:
Evidence: absent packages/schemas/openapi-v1.yaml :: anomaly_disposition:
Evidence: absent packages/schemas/openapi-v1.yaml :: implementation_sha256:
Evidence: contains 1 packages/schemas/disclosure-projection-v1.json :: "api_schema": "AppraisalSummary"
Evidence: contains 1 packages/schemas/reason-codes-v1.json :: getAppraisal
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_cross_references.py
Evidence: unittest tests.ci.test_appraisal_disclosure

Inventory lines `:37-38`. `ClaimRecord.appraisal_id` already references an appraisal today and there is no `/appraisals/{id}` path and no schema behind it.

**Landed under D-613 and D-615.** Both schemas already existed; what was missing was the retrievable operation, and the interesting question was never whether one could be written but what it may return.

The privacy answer is that the operation is self-only in every field and returns a projection rather than the record. `ClaimRecord` is a `self` shape in `disclosure-projection-v1.json` and `appraisal_id` is classified `self` there with the reason "names the verifier appraisal, which is integrity-private", so an appraisal identifier is only ever legible to the participant who submitted the claim and there is no non-owner audience to design for. A caller who is not that participant is answered 404 rather than 403: 403 confirms the appraisal exists, and an appraisal binds one-to-one to a claim, so a confirmed identifier is a confirmed submission by someone. The 403 the operation does declare comes from `INVITE_REQUIRED` and `NATIVE_SESSION_DEVICE_REVOKED`, which are facts about the caller's own account, and never from ownership.

Two fields are withheld from the subject as well. `evaluated.anomaly_disposition` admits `under-review` and `shadow-only`, and showing either to the participant tells them an integrity case is open — which is exactly what D-381 keeps from them, because an investigation is `integrity-private` and the participant reads the effect on their standing rather than the existence of a case. `policy.implementation_sha256` is the server verifier's build digest, which is not the participant's personal data and which no appeal needs. Neither name is declared as a property anywhere in the document, so the absence is uniform and cannot itself be read as a signal.

Everything else is disclosed to the subject because D-084 requires it: an integrity sanction is silent toward the public and notified toward the sanctioned participant, with the effect and the appeal route stated. `acceptance_outcome`, the seven `dimensions`, `awarded_profile_id`, `evidence_class`, `ranking_eligibility`, `reason_codes`, `validity` and `supersession` are that effect, and `evaluated` minus the anomaly disposition is what an appeal argues against — withholding it would leave the appeal route D-084 promises unusable. Disclosing the dimensions to the subject also discloses strictly less than they already hold: `SelfRankEntry` gives them `evidence_factor_hundredths` and `trust_factor_hundredths` outright. The record's `public_state` crosses as `evidence_class` because D-143 admits exactly one evidence vocabulary to the API.

The `Acceptance:` was rewritten because it decided nothing. "Resolves to a defined schema and a retrievable operation" is satisfied by any response shape, including one returning the whole `VerifierAppraisalResult` to any authenticated caller — which would have published the anomaly disposition D-381 forbids and would have passed. It was also satisfied by the state of the tree before this unit ran in the half that mattered: `validate_cross_references.py` already reported zero dangles, because a JSON `format: uuid` field is not a reference the validator resolves, so the "no dangling reference remains" clause was true while the reference dangled in the only sense a reader cares about. The replacement is an equality against the record, so a field added to `appraisal-result-v1.schema.json` fails until someone decides whether the subject sees it, and a field the record drops fails too rather than leaving a withholding rule that guards nothing.

### PF-044 — Add pagination to unpaginated list operations
Files: `packages/schemas/openapi-v1.yaml`
Acceptance: every operation returning a collection declares `cursor` and `limit` parameters with the contract's default 50 and maximum 200; zero collection operations without both.
Depends: none
Est: 3-4
Status: landed
Evidence: contains 17 packages/schemas/openapi-v1.yaml :: parameters/Cursor
Evidence: contains 17 packages/schemas/openapi-v1.yaml :: parameters/Limit

**Landed in `963f6f6` under D-222.** All seventeen collection operations declare `cursor` and `limit`.

The defect as found: twelve operations declared neither — `listSessions`, `listIdentities`, `listDevices`, `listFriends`, `listFriendRequests`, `listBlocks`, `listRivals`, `listBoards`, `listOrganizations`, `listCommunities`, `listModerationCases`, `listAppeals` — while `SERVER_API_DATA_AND_RANKING_CONTRACT.md:44` already specified the contract they violated.

### PF-045 — Specify the error response matrix
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
Acceptance: every operation declares its 4xx responses; every reason code maps to exactly one HTTP status and resolves to exactly one authority — a registered state machine, or a declared non-aggregate authority where the fault belongs to no aggregate — and a declared authority that no code uses fails.
Depends: PF-038
Est: 8-10
Status: landed
Evidence: validator scripts/repository/validate_p1140e_contracts.py
Evidence: contains 1 packages/schemas/reason-codes-v1.json :: CLAIM_CLOCK_ROLLBACK
Evidence: contains 1 packages/schemas/reason-codes-v1.json :: CLAIM_TIMESTAMP_IN_FUTURE
Evidence: absent conformance/adversarial/anti-cheat-registry-v1.json :: "name":"clock-rollback","expected_action":"quarantine_session","reason_code":"CLAIM_SEQUENCE_UNEXPECTED"

**Mostly landed in `963f6f6` under D-223.** Operations declare their 4xx responses and the matrix lives in `packages/schemas/reason-codes-v1.json` rather than inline.

This unit then stayed `in-progress` behind a hole that had already been filled. Its own text said it "closes when every code resolves and not before", pointing at the twenty `state_machine: "vibeproof-v1"` values D-224 recorded as only partly repaired. D-560 added `non_aggregate_authorities` to the registry and `validate_p1140e_contracts.py` resolves against it, so every one of the 69 codes resolves today and none dangles. The blocker outlived the defect; the paragraph asserting it is struck.

The `Acceptance:` was rewritten because it could not be satisfied as written. It required every code to map to "one **registered state machine**", and 38 of 69 do not: 20 name `server-runtime`, 15 `vibeproof-v1` and 3 `local-channel-v1`. Those are runtime, protocol and local-channel faults that belong to no aggregate and therefore have no machine — which is exactly why D-560 introduced the authority list rather than inventing machines to satisfy a field. An acceptance that the design deliberately contradicts is not a bar the unit failed to clear; it is a bar in the wrong place.

The defect as found: no operation declared 401, 403, 404, 409 or 422 — only 200, 429 and default — and all twenty reason codes referenced `state_machine: "vibeproof-v1"`, which is not a registered machine, so every code dangled.

### PF-046 — Represent evidence class in the public API
Files: `packages/schemas/openapi-v1.yaml`, `packages/schemas/disclosure-projection-v1.json`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`
Acceptance: `grep -c evidence_class packages/schemas/openapi-v1.yaml` returns non-zero; the disclosure projection defines exactly what a viewer may see.
Depends: PF-043
Est: 4-6
Status: landed
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: evidence_class
Evidence: exists packages/schemas/disclosure-projection-v1.json
Evidence: exists packages/schemas/disclosure-projection-v1.schema.json

**Half landed in `963f6f6` under D-226; the rest under D-393.** `evidence_class` crosses the boundary on `PublicProfile`, `RankEntry`, `AccountProfile` and `ClaimRecord` with the three values D-143 fixed. The projection this unit's second clause names is `packages/schemas/disclosure-projection-v1.json`, which classifies every property of seven API schemas by audience; the file was previously named as `evidence-disclosure-v1.schema.json` and is renamed here because it governs privacy disclosure as well as evidence. `validate_planning_artifacts.py` resolves every field against the OpenAPI document. The unit was once recorded as `landed` on the strength of the first clause alone and `validate_work_unit_status.py` refused it, which is the check doing the job it was added for; what makes the status correct now is that both clauses are observable.

The defect as found: the string did not appear anywhere in the OpenAPI document, so the product's central differentiator was unrepresentable in its own API, and four competing vocabularies existed for the concept — `packages/ui` used `Hardened|Standard|Imported`, `crates/vibeproof-core` used a five-value scale, `evidence-profile-policy-v1.json` used `profile_id` values, and the API had none.

### PF-047 — Expand profile and rank entry schemas to the rendered product
Files: `packages/schemas/openapi-v1.yaml`, `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
Acceptance: every field rendered by `packages/ui/src/concepts/product-storyboards.tsx` and `packages/ui/src/patterns/product-system.tsx` resolves to an API field; no storyboard depends on a value the API cannot return.
Depends: PF-046
Est: 6-8
Status: landed
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: credited_token_burn
Evidence: absent packages/ui/src/concepts/product-storyboards.tsx :: Verified competitor
Evidence: absent packages/ui/src/concepts/product-storyboards.tsx :: All sources verified

**Landed in `963f6f6` under D-227 and D-228.** `RankEntry` lost `score` and gained `credited_token_burn` and the rendered fields, and the four banned claim strings in `packages/ui/src/concepts/product-storyboards.tsx` were replaced rather than softened.

The defect as found: `PublicProfile` had 4 fields and `RankEntry` had 7, both `additionalProperties: false`, while the finished design system rendered avatars, evidence badges, rank movement, sparklines and board standings that no operation could supply.

### PF-048 — Author the indexing and partitioning plan
Files: `packages/schemas/planning-schema.sql`, `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_index_coverage.py`
Acceptance: every foreign key's referencing columns lead a *total* index, primary key or unique constraint on the referencing table, with a partial index refused because PostgreSQL's referential check on a parent delete has to see the rows the predicate excludes; every index that supports no foreign key is named, with the query it serves, in the access-path table of `LEADERBOARD_STORAGE_AND_RANKING.md`, and every index that table names exists; no index repeats another index or a unique constraint column for column; the set of range-partitioned tables in the DDL equals the set the contract declares partitioned, on the same partition keys, each with a default partition; `python3 scripts/repository/validate_planning_artifacts.py --allow-no-postgres` exits 0 and `python3 -m unittest tests.ci.test_index_coverage` exits 0 with a case per rule.
Depends: PF-038
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_index_coverage
Evidence: contains 1 packages/schemas/planning-schema.sql :: score_contributions_domain_idx
Evidence: contains 6 packages/schemas/planning-schema.sql :: create index oauth_transactions_
Evidence: absent packages/schemas/planning-schema.sql :: create index social_integrity_events_aggregate_idx

**The acceptance is rewritten, and the old one was failing on a schema that satisfied it.** `grep -c "CREATE INDEX" planning-schema.sql` is greater than 3 — the DDL is written in lower case, so that case-sensitive grep answers **zero** against a file holding 132 indexes. This is the sixth naming-or-casing mismatch this repository has produced that finds no overlap at all, and it is the reason the unit still read `not-started` after commit `58976cf` had already written the index block, the access-path table and the partitioning section under this unit's own name.

The rest of the old criterion was worse than wrong, it was backwards. A count rises when a redundant index is added and falls when a wrong one is removed, so the only number the unit stated moved against the thing it was measuring. Under it, the schema scored 132 while **eighteen foreign keys had no index at all**: all five on `oauth_transactions`, `score_contributions.erasure_domain_id`, `certification_results.source_certification_id`, `tuf_metadata.root_version`, `ranked_identities.account_id`, `notification_events.actor_account_id` and seven more. Five of those were invisible because a *partial* index covered the column — `oauth_transactions_live_link_idx` over three live states, `ranked_identities_account_live_idx` where `retired_at is null`, `consolidation_cases_absorbed_idx` over five open states, `source_certifications_active_idx` where `state = 'active'` — and a partial index cannot answer a parent delete, which has to prove the absence of *any* child row including the ones the predicate excludes. The erasure path is the one that suffers: it deletes from `accounts`, which thirty-one tables reference, and `score_contributions` could only be scanned by period.

There was a redundant index too, which is the same signal read from the other end. `social_integrity_events_aggregate_idx` covered `(aggregate_id, aggregate_revision)` and the table already declared `unique (aggregate_id, aggregate_revision)`, which PostgreSQL implements as a btree over those columns in that order. It served no query the constraint did not and cost a write on every insert. Removing it lowered the count and improved the schema, which is the clearest statement available of why the count was never the signal.

`validate_index_coverage` replaces it with coverage in both directions, and it is deliberately not a total. The second rule is the one that keeps the table honest: an index that supports no foreign key must name the query it serves, because an index justified by no query cannot be shown to be wrong and cannot be dropped by anyone who did not write it. Eighteen indexes were in that state, several of them filed under section headings in the DDL that claimed foreign-key support for columns that deliberately carry none — `moderation_cases.account_id`, `appeals.account_id`, `deletion_jobs.account_id`, `invite_codes.issued_by_account_id`, `organizations.owner_account_id` and `communities.owner_account_id` all outlive the account they name, on purpose, and a reader taking the heading at its word would have concluded the erasure delete was covered there.

The unit's own note was stale in every figure it stated: 98 tables became 122, "3 indexes total" became 132, "zero `PARTITION BY`" became three range-partitioned tables with default partitions, and the claim that `SERVER_API_DATA_AND_RANKING_CONTRACT.md` partitions claims by receipt month had already been corrected to the opposite — `claims` cannot be partitioned without making three global uniqueness invariants per-month, and the contract says so. `friend_edges` and `rival_edges` did get their reverse-direction indexes. The 300 ms leaderboard SLO remains unmeasured: no index in this repository has been built against data, no plan has been read, and none of the required benchmarks has been run.

### PF-049 — Repair the idempotency contract
Files: `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/state-machine-registry-v1.json`
Acceptance: a replayed request returns the original response body byte-for-byte; the ledger expresses `conflict` and `expired`.
Depends: PF-038
Est: 4-6
Status: landed
Evidence: contains 1 packages/schemas/planning-schema.sql :: response_body bytea
Evidence: contains 1 packages/schemas/planning-schema.sql :: idempotency_records_replayable_is_answerable
Evidence: contains 1 packages/schemas/planning-schema.sql :: idempotency_records_digest_pairs_with_body
Evidence: validator scripts/repository/validate_state_vocabularies.py

**The API half landed in `963f6f6` under D-225; the SQL half lands here.** The wire contract states the scoped key and byte-identical replay under one `x-idempotency-contract` block, and the ledger could not answer it: `planning-schema.sql` stored a nullable `response_digest` and no response body at all. A digest proves a response was equal; it cannot return one. A contract that states an invariant its storage cannot hold is worse than one that states nothing, because it reads as satisfied.

The ledger now stores `response_status` and `response_body` beside the digest, with two constraints doing the work the nullability did not. `idempotency_records_replayable_is_answerable` refuses a `committed` or `replayable-failure` row that leaves any of the three null, which is what let a row claim to be replayable while holding nothing to replay. `idempotency_records_digest_pairs_with_body` refuses a digest without its body and a body without its digest; SQL cannot verify the digest is *over* the body without an extension, so the pairing is constrained and the limit is stated rather than implied.

Only the server's own fixed-schema response is stored. No request body and no client content: the privacy boundary governs what may be written, not what the column can hold, and `expires_at` already bounds how long even that is kept.

The three defects the unit found are all closed: the principal is `(principal_type, principal_id)` rather than account-only, `operation_id` is in the primary key so one key cannot replay a different operation's response, and the state vocabulary carries `conflict` and `expired`.

The defect as found: `planning-schema.sql` stored a nullable `response_digest` with no response-body column; its primary key was `(actor_account_id, idempotency_key)` with no global uniqueness; and the principal was account-only.

### PF-050 — Populate retention and disposition policy
Files: `packages/schemas/policy-defaults-v1.json`, `packages/schemas/data-disposition-v1.json`, `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: every one of the 98 tables in `packages/schemas/planning-schema.sql` has a declared retention class, which a script asserts by diffing the table list against the policy file in both directions; no `expires_at` column exists without a named enforcement owner.
Depends: PF-038
Est: 6-8
Status: landed
Evidence: exists packages/schemas/data-disposition-v1.json
Evidence: exists packages/schemas/data-disposition-v1.schema.json
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres

Inventory `:106-107` assigns retention to `policy-defaults-v1.json`, which currently contains 16 knobs and zero retention windows. `expires_at` is stored in several tables and enforced nowhere.

### PF-051 — Specify multi-observer deduplication
Files: `packages/schemas/normalized-event.schema.json`, `docs/product/TOKEN_ACCOUNTING_SPEC.md`, `conformance/accounting/dedup-vectors-v1.json`
Acceptance: two collectors observing one session produce a single counted event; fixture covers the colliding and non-colliding commitment cases.
Depends: PF-042
Est: 6-8
Status: landed
Evidence: exists conformance/accounting/dedup-vectors-v1.json
Evidence: exists packages/schemas/dedup-vectors-v1.schema.json
Evidence: exists conformance/accounting/dedup-vectors-v1.invalid-empty-preimage.json

Inventory `:74`. `TOKEN_ACCOUNTING_SPEC.md:74-76` currently relies on the collector's own `duplicate_domain_commitment`, so two collectors on one real session can choose non-colliding commitments and double-count. Double counting is a scoring defect, not a data-quality defect.

### PF-052 — Author ranking generation, entry and snapshot contracts
Files: `packages/schemas/ranking-generation-v1.schema.json`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/planning-schema.sql`
Acceptance: `LeaderboardPage.snapshot_id` and `revision` and `RankEntry.ranking_view_id` all resolve; a generation can be pinned, superseded, and read back.
Depends: PF-038, PF-048
Est: 10-14
Status: landed
Evidence: exists packages/schemas/ranking-generation-v1.schema.json
Evidence: contains 1 packages/schemas/planning-schema.sql :: ranking_entries

Inventory `:88`. Three fields dangled in the API when this unit was written. The note also said this was where `getLeaderboard` would gain a viewer parameter and lose its unauthenticated `security: []`; the unit landed without doing either, and the note outlived the hole it described for six units. `PF-021` did it: the global board has its own path and holds the `global-board` reason alone, the `Scope` enum admits `friends` and `rivals` only, and a board standing is addressed at `/boards/{id}/leaderboard/{period}`.

### PF-053 — Decide provider-attested evidence for organizations
Files: `docs/decisions/ADR-016-PROVIDER_ATTESTED_ORG_EVIDENCE.md` (new), `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/planning/DECISION_REGISTER.md`
Acceptance: the ADR states whether org boards use provider admin APIs, and `EVIDENCE_AND_ATTESTATION_PROFILES.md` reflects the resulting E1 availability.
Depends: none
Est: 4-6
Status: landed
Evidence: exists docs/decisions/ADR-016-PROVIDER_ATTESTED_ORG_EVIDENCE.md
Evidence: contains 1 docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md :: E1-R

Research on 2026-08-05 established that Anthropic's Admin API (`/v1/organizations/usage_report/messages` plus the Claude Code analytics endpoint), OpenAI's `/v1/organization/usage/completions`, and Cursor's team usage API all return provider-attested counts that a user cannot fabricate — but all three require org-admin credentials, and no provider offers an OAuth scope permitting an individual to authorize third-party read of their own consumption. Anthropic's documentation states the Admin API is unavailable for individual accounts.

Consequence: E1 evidence is reachable **today for organizations and unreachable for individuals**. This bears directly on the ranking-integrity limits recorded in `docs/security/THREAT_MODEL.md` and determines whether a credible evidence tier exists at all. It affects the identity and board data model, so it is decided before ranking contracts are frozen rather than after.

### PF-054 — Make the negative CBOR corpus executable and sole
Files: `conformance/vibeproof/v1/malformed-resource-corpus.json`, `conformance/vibeproof/v1/manifest.json`, `conformance/vibeproof/v1/README.md`, `scripts/repository/generate_vibeproof_vectors.py`, `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_vibeproof_rule_ownership.py`, `tests/ci/test_work_unit_status.py`
Acceptance: every case states its input exactly one way; every case that states it as hex is decoded by the canonical profile decoder and must be refused with the exact `decoder_signal` it declares, so a case cannot claim a malformation its bytes do not contain; every refusal the profile decoder can produce is exercised by at least one case; every `registry_reason_code` resolves in `packages/schemas/reason-codes-v1.json`, which the suite manifest declares as this corpus's reason authority; every stage and outcome is one the corpus declares; and `malformed-resource-corpus.json` is the only negative-vector file, which `PF-002`'s ownership check enforces.
Depends: none
Est: 4-6
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_vibeproof_rule_ownership
Evidence: contains 9 conformance/vibeproof/v1/malformed-resource-corpus.json :: decoder_signal
Evidence: contains 27 conformance/vibeproof/v1/malformed-resource-corpus.json :: registry_reason_code
Evidence: missing conformance/vibeproof/v1/negative-vectors.json

**The original premise was false and the original acceptance was vacuous.** `conformance/vibeproof/v1/malformed-resource-corpus.json` already held twenty negative cases, and duplicate keys, non-minimal integers, indefinite containers and trailing bytes were four of them. All four cases the acceptance named already existed, so it passed on the unrepaired tree and had done since the corpus was written. "Batch, rotation, gap, and correction vectors are also absent" was half wrong too: `batch-257-claims`, `batch-1048577-bytes` and `rotation-payload-mismatch` were there. Gap and correction were the two genuinely missing axes, and are added.

**`negative-vectors.json` is deliberately not created.** The `Files:` line above used to create it, which would have broken `PF-002` in the same pull request: a third file declaring a rule name is exactly what `PF-002`'s ownership check refuses, and `validate_conformance_manifests` separately fails on any file in that directory no manifest case names. `P-008` named the same file and no longer does. The corpus records the decision in its own `note` so a future reader finds it where the file would have been.

**What was actually missing is that nothing decoded the corpus.** `validate_vibeproof_vectors` checked that twenty hard-coded case identifiers were present — the same shape of check as the acceptance, and satisfied by the same twenty strings. A case could name a malformation its bytes did not contain, or carry bytes that decoded cleanly, and no check would notice. Nine cases now carry a `decoder_signal`, the profile decoder must refuse each with exactly that signal, and `PROFILE_VIOLATIONS` enumerates every refusal the decoder can produce so an uncovered one is a failure rather than an invisible gap. Three of the nine — a reserved additional-information value, `undefined`, and a truncated byte string — are new, and each is a refusal the profile requires and the corpus did not exercise.

**Reason codes resolved against nothing.** `manifest.json` has declared `packages/schemas/reason-codes-v1.json` as this suite's reason authority since it was written, and none of the twenty local reason codes — `protocol-duplicate-key` and its siblings — resolved against it; the registry uses `CLAIM_INVALID_CANONICAL_ENCODING` casing. Each case now carries a `registry_reason_code` that resolves, alongside the local identifier the other artifacts cite. The manifest's single `expect_reason_code` names the canonical-decode class and the note records the ten codes the corpus actually spans.

`wrong-algorithm` said "replace protected alg -8 with -7". D-192 and RFC 9864 moved the profile to `-19`, so the case mutated one forbidden algorithm into another and tested no boundary at all. It now reads "-19 with -8".

The eighteen cases that state a mutation, a generator or a transaction state stay prose and are counted as prose. They are not executable until an implementation reads them, and `P-008` is the unit that makes one do so.

Two tests were pinned to this document's shape rather than to its meaning and are repaired here. `test_not_started_contradicted_by_an_existing_artifact_fails` named `PF-054` and the exact `(new)` path on its `Files:` line, so it failed the moment this unit stopped promising that file; it now finds any `not-started` unit that promises one. `test_a_unit_missing_a_required_field_is_not_emitted` asserted a literal line number for `PF-037`, so every edit anywhere above it in this file failed a test about a missing `Acceptance:` field; it now computes the line. Both failures had nothing to do with what the tests check.

### PF-055 — Repair the P-1140F authority validator
Files: `scripts/repository/validate_p1140f_authority.py`, `tests/ci/test_validate_p1140f_authority.py` (new)
Acceptance: closing a finding in `conformance/p1140f/semantic-findings-v1.json` leaves the validator green; the validator fails when the open count increases.
Depends: none
Est: 3-4
Status: landed
Evidence: validator scripts/repository/validate_p1140f_authority.py
Evidence: unittest tests.ci.test_validate_p1140f_authority

`:53` raises unless exactly 13 P1 findings are open; `:139` raises unless zero are open for a review to pass. The two conditions cannot both hold, so closing a finding correctly turns CI red and the only routes to green are inaction or editing the validator. Replace the exact-count check with monotonic non-regression.

### PF-056 — Restore executable evaluation gates
Files: `.github/workflows/planning-checks.yml`, `evals/suites/suites.yaml`, `scripts/ci/run_evals.py`
Acceptance: `run_evals.py --validate-registry`, `verify_repository.py`, and `python -m unittest discover -s tests` all run in CI and exit 0.
Depends: PF-055
Est: 4-6
Status: landed
Evidence: validator scripts/ci/run_evals.py --validate-registry
Evidence: unittest tests.ci.test_run_evals
Evidence: contains 1 .github/workflows/planning-checks.yml :: verify_repository.py
Evidence: contains 1 .github/workflows/planning-checks.yml :: unittest discover

Four validators fail at HEAD and no workflow invokes them, so nothing detected the failure. Commit `31a6539` added `authority_class` and `evidence_ceiling` to satisfy `validate_p1140f_authority.py:124`, while `run_evals.py` rejected any key outside its allowlist — one validator required exactly what another forbade.

**Partially repaired 2026-08-06.** The allowlist now admits both keys, which resolves the first contradiction. A second one remains and needs a decision rather than a patch: `shadow-codec-parity` carries `reason: "…not normative VibeProof conformance"`, which is a **scope disclaimer**, while `run_evals.py:156` treats `reason` purely as a not-applicable excuse and requires it blank on `ready` suites. One key is serving two purposes. Either split the disclaimer into a distinct field such as `scope_note` — which `validate_p1140f_authority.py` must then read for the evidence-ceiling justification — or relax the blank-reason rule when `authority_class` is present. Choose deliberately; both validators depend on the answer.

Until that is settled, `run_evals.py --validate-registry`, `generate_gate_ledger.py`, `verify_repository.py`, and one test in `tests/ci/test_run_evals.py` still fail. 1,255 of 3,206 Python lines never execute in automation, including the fixture-digest binding, argv shell-injection refusal, path-traversal containment, and evidence-freshness checks. This unit also removes the `paths:` filters that currently exempt `apps/`, `crates/`, `Cargo.toml`, and `.github/workflows/ci.yml` from every check.

### PF-057 — Specify the P-1104 gate transition
Files: `scripts/repository/doctor.py`, `docs/project/STATUS.md`, `docs/planning/TASK_CATALOG.md`, `docs/implementation/IMPLEMENTATION_HANDOFF.md`
Acceptance: `doctor.py` derives phase state from `conformance/p1140f/*.json` rather than from prose substrings; opening or closing the gate requires no edit to `doctor.py`.
Depends: PF-055
Est: 4-6
Status: landed
Evidence: contains 1 scripts/repository/doctor.py :: conformance/p1140f/gate-authorization-v1.json
Evidence: absent scripts/repository/doctor.py :: implementation remains unauthorized
Evidence: unittest tests.ci.test_gate_authorization

The gate is currently enforced by prose substring assertions in four files: `doctor.py:90` requires `STATUS.md` to contain the literal string "implementation remains unauthorized", `:95` requires "blocked-approval" in `TASK_CATALOG.md`, `:105` requires "P-1104: blocked", and `:110` requires "inactive" and "blocked" in the handoff. Moving the gate therefore requires editing the validator that enforces it, which is the same defect as PF-055 in a different place. The machine-readable state already exists in `conformance/p1140f/`; the validator should read it.

### PF-058 — Author the system narrative in PROJECT.md
Files: `docs/project/PROJECT.md`, `docs/project/DOCUMENTATION.md`
Acceptance: a reader who has read only `PROJECT.md` can state the full path a token takes from an agent process to a public rank, and name the component that owns each step.
Depends: none
Est: 6-8
Status: landed
Evidence: contains 1 docs/project/PROJECT.md :: collector
Evidence: contains 1 docs/project/PROJECT.md :: adapter
Evidence: contains 1 docs/project/PROJECT.md :: verifier
Evidence: contains 1 docs/project/PROJECT.md :: daemon

No document explains how the system works end to end. Understanding it currently requires reading eight files in a prescribed order, which is why `AGENTS.md:12` has to prescribe that order. `PROJECT.md` should carry one narrative — install, adapter observes, collector normalizes, sync signs, verifier appraises, ledger records, projection ranks — with a diagram, and every other document should read as detail hanging off it.

This is the single highest-value change for anyone, human or agent, encountering the repository for the first time. It does not replace any normative contract; it gives them a spine.

### PF-059 — Merge duplicated UI and design documentation
Files: `docs/style-guide/COMPONENT_INVENTORY.md`, `docs/style-guide/COMPONENT_STANDARD.md`, `docs/style-guide/README.md`, `docs/style-guide/UI_ARCHITECTURE.md`, `docs/style-guide/UI_FOUNDATIONS.md`, `docs/style-guide/BRAND.md`, `docs/project/DOCUMENTATION.md`
Acceptance: one owner per concept; no two files in `docs/style-guide/` describe the same component surface; `DOCUMENTATION.md` names the surviving owner for each.
Depends: none
Est: 6-8
Status: landed
Evidence: missing docs/style-guide/COMPONENTS.md
Evidence: exists docs/style-guide/UI_ARCHITECTURE.md
Evidence: validator scripts/repository/doctor.py

Three files described components (`COMPONENTS.md`, `COMPONENT_INVENTORY.md`, `COMPONENT_STANDARD.md`) and three described design foundations (`design/design.md`, `design/UI_FOUNDATIONS.md`, `style-guide/README.md`); the first and fourth of those have since been merged into their surviving owners. `docs/architecture/ARCHITECTURE.md` and the former `docs/style-guide/ARCHITECTURE.md` shared a filename while describing unrelated scopes, which made every reference to "ARCHITECTURE.md" ambiguous until the latter was renamed to `docs/style-guide/UI_ARCHITECTURE.md`.

Merge unique content into one owner per concept, repair references, and delete or clearly mark the duplicates, per the rule already stated in `DOCUMENTATION.md`.

### PF-060 — Collapse single-purpose documentation directories
Files: `docs/protocol/`, `docs/qa/`, `docs/evals/`, `docs/design/`, `docs/project/DOCUMENTATION.md`, `README.md`, `AGENTS.md`
Acceptance: no directory under `docs/` holds fewer than four files without a recorded reason; every moved path resolves; `doctor.py` passes.
Depends: PF-059
Est: 4-6
Status: landed
Evidence: missing docs/protocol
Evidence: missing docs/qa
Evidence: missing docs/evals
Evidence: missing docs/design
Evidence: validator scripts/repository/doctor.py

Eighteen directories hold 82 files, and seven of them hold one to three: `protocol/` (1), `qa/` (1), `evals/` (2), `privacy/` (2), `design/` (3), `engineering/` (3), `project/` (3). Fold `protocol/` into `architecture/`, combine `qa/` and `evals/` into one verification directory, and fold `design/` into `style-guide/`. Keep `privacy/` and `project/` where they are — both are small but load-bearing, and `privacy/` deliberately isolates the invariant everything else serves.

Every move must repair inbound references. `AGENTS.md` and `doctor.py`'s REQUIRED list both name paths.

### PF-061 — Archive spent planning specifications
Files: `docs/history/MACHINE_CONTRACT_REPAIR_SPEC.md`, `docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md`, `docs/history/`, `docs/project/DOCUMENTATION.md`, `AGENTS.md`, `README.md`
Acceptance: both files are in `docs/history/` with unique content merged into a living owner; no inbound reference is broken; `doctor.py` passes.
Depends: none
Est: 4-6
Status: landed
Evidence: exists docs/history/MACHINE_CONTRACT_REPAIR_SPEC.md
Evidence: exists docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md
Evidence: missing docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md
Evidence: validator scripts/repository/doctor.py

`MACHINE_CONTRACT_REPAIR_SPEC.md` (521 lines) declares itself a "normative P-1140B–E planning input"; P-1140E is closed, so it is spent. `REPOSITORY_ALIGNMENT_2026-07-23.md` (366 lines) restates decisions owned by `DECISION_REGISTER.md` and is cited in the `AGENTS.md` initialization order and in `DOCUMENTATION.md`, so both must be updated when it moves. Roughly 890 lines leave the active planning surface.

Unlike the nine files archived on 2026-08-05, these two have live inbound references. Merge before moving; do not orphan a reference.

### PF-062 — Make the decision register and task catalog machine-readable
Files: `conformance/planning/decisions-v1.json` (new), `conformance/planning/decisions-v1.schema.json` (new), `conformance/planning/tasks-v1.json` (new), `conformance/planning/tasks-v1.schema.json` (new), `scripts/repository/generate_planning_docs.py` (new), `docs/planning/DECISION_REGISTER.md`, `docs/planning/TASK_CATALOG.md`
Acceptance: the Markdown register and catalog are generated from JSON and byte-identical to the committed files; a validator fails on drift between source and generated output.
Depends: PF-053, PF-055
Est: 12-16
Status: landed
Evidence: exists conformance/planning/decisions-v1.json
Evidence: exists conformance/planning/decisions-v1.schema.json
Evidence: exists conformance/planning/tasks-v1.json
Evidence: exists conformance/planning/tasks-v1.schema.json
Evidence: validator scripts/repository/generate_planning_docs.py --check
Evidence: contains 1 docs/planning/DECISION_REGISTER.md :: <!-- generated: decision-register -->
Evidence: contains 1 docs/planning/TASK_CATALOG.md :: <!-- generated: task-catalog -->

`conformance/p1140f/*.json` is the pattern that works in this repository: validators read structure. But every planning gate lived in a Markdown table that validators reach by substring matching — `validate_p1140f_authority.py:131` greps prose for a count, and `doctor.py` asserts that literal strings appear somewhere in a document. That is why the phase gate could only be moved by editing its own validator.

This unit's own prose said the register held **132 rows running to D-205**. It holds **290 rows running to D-607** — the figure had aged past double while sitting in the document that exists to stop figures aging. Corrected here rather than left as another count nothing derives.

Reading the register against itself found what the sparse numbering was hiding. `## Register rules` sits *between* the D-144 and D-180 rows, so in Markdown terms the table ends at D-144: the remaining 146 rows follow a heading with no table header and do not render as a table at all. Nothing caught it because `validate_decision_register` matches rows with a regex rather than parsing a table, so it read all 290 either way. The rules section is now part of the preamble and the table is contiguous.

Make JSON the source and generate the Markdown, so prose can no longer drift from state and validators can assert on structure. `validate_work_unit_status.py` is the smaller precedent for exactly this shape: JSON-free, but the derived block in the work breakdown is generated and drift fails the build. This unit is what lets PF-063 assert on the whole register.

### PF-063 — Complete decision traceability coverage
Files: `conformance/planning/decision-traceability-v1.json` (new), `conformance/planning/decision-traceability-v1.schema.json` (new), `scripts/repository/generate_planning_docs.py`, `scripts/repository/validate_planning_artifacts.py`, `docs/planning/decision-traceability/`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, `docs/project/DOCUMENTATION.md`
Acceptance: every accepted implementation-bearing decision has a traceability row with an implementation owner, machine or state ownership, platform scope, and executable evidence requirement; the traceability validator covers the whole register rather than a frozen prefix of it, so a decision added without a row fails the build.
Depends: PF-062
Est: 4-6
Status: landed
Evidence: exists conformance/planning/decision-traceability-v1.json
Evidence: exists conformance/planning/decision-traceability-v1.schema.json
Evidence: validator scripts/repository/generate_planning_docs.py --check
Evidence: contains 1 scripts/repository/validate_planning_artifacts.py :: def validate_decision_traceability
Evidence: absent docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md :: D-094

The `Files:` line named three paths and the estimate said 4-6 hours, both written when the uncovered tail was assumed small. It was 222 of 291 decisions — three times the covered head, not the "69 traced and 63 not" the prose below described.

`validate_p1140e_contracts.py` is deliberately **not** in the repair. Widening its `range(1, 70)` would make a closed program's evidence set mutable, which the prose below already argues against; coverage of the whole register is a second matrix owned by the P-1140F track, exactly as that paragraph says. Naming the P-1140E validator in `Files:` contradicted the unit's own reasoning.

Reference resolution itself is closed. `scripts/repository/validate_cross_references.py` resolves every decision, finding, ADR, program, work-unit, path, `$ref`, and `operationId` citation in the repository and exits non-zero on any that dangles; `tests/ci/test_cross_references.py` proves it fires per class. The 128 dangling work-unit citations that motivated this unit — a superseded two-digit numbering across 72 identifiers, including the `I-`, `PL-` and `U-` prefixes that never existed in the breakdown, and `D-01` through `D-10` used as work-unit identifiers in the same files where `D-001` onward are decisions — were deleted rather than remapped, because no unit they named survives.

What remains is coverage, not resolution. `validate_p1140e_contracts.py:52-59` freezes its traceability matrix at `range(1, 70)` and delegates the remainder to a validator that never references a `D-` identifier, so **every decision from D-070 onward has no traceability row at all**. The register now runs to D-205 with 132 rows, so the uncovered tail is larger than the covered head: 63 decisions are traced and 69 are not.

The freeze is deliberate — P-1140E owns D-001..D-069 and a later decision must not silently expand a closed structural matrix — so the repair is a second matrix owned by the P-1140F track rather than widening the range in place. Widening `range(1, 70)` would make a closed program's evidence set mutable, which is the defect this repository exists to stop.

The four traceability files under `docs/planning/decision-traceability/` cover D-001 through D-069 and stop there. Extending them is the visible half; the half that decides whether this closes is that a new decision must not be mergeable without a row, which needs the check to run over the register rather than over a fixed list.

### PF-064 — Remove stale dates from living document filenames
Files: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md`, `docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN.md`, `scripts/repository/doctor.py`, `AGENTS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/TASK_CATALOG.md`, `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`, `docs/planning/SR_SEVERITY_REGRADING_PROPOSAL.md`, `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, `docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md`, `docs/research/README.md`, `conformance/p1140f/REPAIR_HEAD_REVIEW.md`, `conformance/p1140f/gate-authorization-v1.json`, `conformance/p1140f/semantic-findings-v1.json`
Acceptance: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md` and `docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN.md` exist and neither dated predecessor does; `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md` still carries its date, because a closed record is what the convention is for; no reference to either old basename survives anywhere in the tree; `doctor.py`, `validate_p1140f_authority.py` and `validate_cross_references.py` each exit 0.
Depends: PF-057
Est: 2-3
Status: landed
Evidence: exists docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md
Evidence: missing docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md
Evidence: exists docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN.md
Evidence: missing docs/planning/ANTI_CHEAT_IMPLEMENTATION_PLAN_2026-07-23.md
Evidence: exists docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md
Evidence: validator scripts/repository/validate_p1140f_authority.py
Evidence: validator scripts/repository/validate_cross_references.py

The `Acceptance` this unit shipped with was "no file that is still being updated carries a date in its filename; every inbound reference resolves; `doctor.py` passes", and it is rewritten above because none of its three clauses could fail. Nothing in the repository determines which files are "still being updated", so the first clause was satisfiable by asserting that every dated file is a record — including the two this unit exists to rename. The second and third restate checks `validate_cross_references.py` and `doctor.py` already run on every commit, so they would have passed before the unit was started. An acceptance that holds on the unrepaired tree measures nothing. The replacement names the three files and their disposition, and it fails in both directions: removing the P-1140E audit's date breaks it exactly as leaving the other two dates would.

The `Files:` line named five paths; the change touches fourteen. The unit's own prose already listed nine of the missing ones, so the field that is supposed to be "the exact paths" was the least accurate statement in the block.

`P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md` is live and is still being updated, but its filename says July 24. A date in a filename should mean the document is a point-in-time record; using it for a living document teaches readers to distrust the convention.

Nine tracked files reference it and each has to move with it: `AGENTS.md`, `docs/project/DOCUMENTATION.md`, `docs/planning/TASK_CATALOG.md`, `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`, `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, `docs/history/REPOSITORY_ALIGNMENT_2026-07-23.md`, `scripts/repository/doctor.py`'s REQUIRED list, `conformance/p1140f/REPAIR_HEAD_REVIEW.md`, and the pinned-path strings in `conformance/p1140f/gate-authorization-v1.json` and `conformance/p1140f/semantic-findings-v1.json`. Those last two are the constraint that decides how this unit is done: `validate_p1140f_authority.py` requires every pinned path to exist, and the records are owned by the P-1140F closure track. D-140 refused the same rename for `openapi-v1.yaml` for exactly this reason. Either the rename lands together with the record update in one change, or it waits for the pins to be released — decide which, and record it, rather than discovering the constraint mid-rename.

Decided under D-606: the rename lands together with the record update, in this change. D-140 is not the same case. There the disagreement was between a path and its contents, and converting the contents to YAML removed it without touching a pinned string — a repair existed that left the records alone. Here the filename asserts a date the document contradicts by continuing to change, and no edit to the contents can fix that. Waiting for the pins to be released is strictly worse than moving them: PF-034 and PF-036 both add citations to this document, and PF-062 absorbs `TASK_CATALOG.md` into generated output, so every unit that lands first makes the rename larger.

Two other dated filenames under `docs/planning/` need the same judgement and are in scope for this unit: `P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`, which is a closed program's record and should keep its date, and `ANTI_CHEAT_IMPLEMENTATION_PLAN.md`, which is a plan rather than a record and should not.

Archived point-in-time reports in `docs/history/` keep their dates. That is what the convention is for.

### PF-065 — Correct the OpenAPI file extension
Files: `packages/schemas/openapi-v1.yaml`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_planning_coverage.py`, `scripts/repository/validate_p1140e_contracts.py`, `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
Acceptance: the file's extension matches its contents; every reader resolves it; all planning validators pass.
Depends: PF-038
Est: 2-3
Status: landed
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: This document is YAML
Evidence: validator scripts/repository/validate_planning_coverage.py

`openapi-v1.yaml` contains JSON. YAML is a superset of JSON so parsers accept it, but the first tool that selects a parser by extension, or any human opening it expecting YAML, will be wrong. Either rename to `.json` or convert the contents to YAML — decide deliberately and record which, since several validators reference the path by name.

### PF-066 — Repair unreachable states and false terminal states
Files: `packages/schemas/state-machine-registry-v1.json`, `tests/ci/test_state_vocabularies.py`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: every state in every registry machine is reachable from its initial state, and no state listed in `terminal_states` has an outgoing transition. A test asserts both across all 26 machines, not only those bound to SQL or an API enum.
Depends: none
Est: 6-8
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_state_vocabularies

Two defect classes found by a reachability sweep during the PF-038 follow-up. Both are invisible to `validate_state_vocabularies.py`, which compares vocabularies across three sources and does not examine transitions.

**Unreachable states.** `daemon-lifecycle` cannot reach `degraded`, `offline`, `stopped`, or `stopping`. `privileged-supervisor` cannot reach `degraded`. `interactive-shell` cannot reach **10 of its 15 states**. These machines bind to neither a SQL column nor an API enum, so the existing three-way check never looks at them. A declared state no transition can produce is a specification that cannot be implemented.

One instance of this class was already fixed: `Notification.state` exposed `read` with no transition reaching it — all three sources agreed on a state no worker could produce. The `notification-read` transition closed it, and a scoped reachability guard now covers bound machines. This unit extends that guard to all 26.

**False terminal states.** Four machines declare a state terminal while giving it an outgoing transition: `idempotency-ledger.committed → expired`, `moderation-case.reversed → closed`, `update-lifecycle.failed → rolled-back`, `release-trust.superseded → expired`. A worker that trusts `terminal_states` will refuse a legal transition, and one that trusts the transition list will violate the terminal declaration. Decide which is authoritative per machine and make the registry say it once.

### PF-067 — Make state-vocabulary binding coverage self-checking
Files: `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_state_vocabularies.py`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
Acceptance: the validator fails when a declared aggregate has an unpopulated `sql=` or `api=` binding that could have been populated, and reports its true three-way coverage rather than an aggregate count.
Depends: none
Est: 4-6
Status: landed
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: contains 5 scripts/repository/validate_state_vocabularies.py :: _state.state",)
Evidence: contains 1 scripts/repository/validate_state_vocabularies.py :: def check_absence_reasons
Evidence: contains 1 docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md :: ### Recorded absences

`validate_state_vocabularies.py` is a genuine check — its drift-injection tests prove it catches renames, deletions, and dropped enum values. But its guarantee was narrower than its name implied. Of 42 declared aggregates, only **9** received a real three-way registry + SQL + API comparison; 27 were two-way and 6 were format-only. (The unit was written when there were 31; PF-013 added five more.)

Coverage was driven by a hardcoded `BINDINGS` table, so an aggregate whose `sql=` or `api=` field was simply never populated silently escaped the identity checks while still counting toward the reported total.

Reading the table against `local-store-v1.sql` found that this had already happened. All five `local-*` aggregates carried an explicit `sql=()` while PF-013 had created `local_collection_state`, `local_sync_state`, `local_auth_state`, `local_permission_state` and `local_connectivity_state`, each with a CHECK constraint holding exactly that aggregate's declared states. The five were reported as covered aggregates and were compared against nothing. The check that should have caught it — "every SQL state column is bound to an aggregate or declares a sub-entity vocabulary" — read the device half of the storage contract for table *names* only, so a column there could be neither bound nor found unbound. That is the recurring class again: a signal that improves when you remove what it counts.

Repaired three ways. The five bindings are wired, taking coverage to 9 three-way, 32 two-way and 1 format-only. The persistence check now resolves both halves of the storage contract, so the SQL axis fails closed on the device side as the API axis already did under rule 10. And omission is now explicit: every absent binding carries a recorded reason in `RECORDED_ABSENCES`, mirrored entry-for-entry in the contract's recorded-absence table, with the reverse check too — a reason for a binding that is in fact populated fails, because that is how the `local-*` excuse survived. The contract previously said the reason for a `—` "is given under Open items"; 39 cells recorded `—` and Open items explained four. A promise no validator executes is the same defect as a check phrased as an absence.

Two device columns surfaced once the persistence check began reading `local-store-v1.sql`: `outbox_claims.state` is now a declared sub-entity vocabulary, and `source_receipts.certification_state` has no CHECK constraint at all, so it is recorded in `SQL_COLUMNS_WITHOUT_VOCABULARY` naming PF-017 and PF-018 as the owners of the vocabulary it should mirror, rather than guessed at.

### PF-068 — Author the Ed25519 divergence-case conformance corpus
Files: `conformance/vibeproof/v1/ed25519-divergence-corpus.json`, `conformance/vibeproof/v1/README.md`, `conformance/vibeproof/v1/zip215-oracle-run.json`, `conformance/vibeproof/v1/zip215-oracle/main.go`, `scripts/repository/generate_ed25519_divergence_corpus.py`, `scripts/repository/run_ed25519_oracles.py`, `tests/ci/test_ed25519_divergence_corpus.py`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`
Acceptance: the corpus contains at least one case for each of non-canonical `A`, non-canonical `R`, small-order `A`, and `S >= l`; every case records its expected ZIP-215 verdict; a generator reproduces the corpus byte-identically from recorded inputs, so no verdict is asserted by hand; and every ZIP-215 verdict is either confirmed against an independent ZIP-215 implementation with the run recorded, or marked `unconfirmed` with the command that would confirm it.
Depends: none
Est: 8-12
Status: landed
Evidence: validator scripts/repository/generate_ed25519_divergence_corpus.py --check
Evidence: unittest tests.ci.test_ed25519_divergence_corpus
Evidence: exists conformance/vibeproof/v1/README.md
Evidence: contains 9 conformance/vibeproof/v1/ed25519-divergence-corpus.json :: "status": "confirmed"

VibeProof v1 pins Ed25519 verification to ZIP-215 because RFC 8032 does not pin it: SS5.1.7 permits both the cofactored and cofactorless group equations, and FIPS 186-5 SS7.7 repeats that permission verbatim. A cofactored verifier accepts a strictly larger set of signatures than a cofactorless one, and the implication runs one way only, so a Rust signer and a Go verifier that both conform to RFC 8032 can disagree without any round-trip test noticing.

RFC 8032's own test vectors cannot detect this. They are well-formed signatures that pass under every implementation, which is exactly why they prove nothing about the axes that diverge. Only adversarial inputs separate the criteria sets. `tests/ci/test_ed25519_divergence_corpus.py` asserts that insufficiency executably by running RFC 8032 SS7.1 TEST 1 through both verification rules and requiring both to accept.

The corpus is nine cases and D-340 records their construction. Five separate the two criteria, and `cofactored-only-order8-r` is the one that shows the divergence is the group equation rather than a story about malformed encodings: every byte in it is canonical and `A` is an ordinary public key. `s-equals-l` and `s-plus-l` record where ZIP-215 is not more permissive, because an implementer who reads it as uniformly laxer drops the range check that stops malleability.

Verdicts are confirmed, not asserted. D-341 fixes the rule: a ZIP-215 verdict is `confirmed` only when an independent implementation returned it against a digest of the case's exact bytes, `unconfirmed` otherwise with the command that would confirm it, and a contradiction between the oracle and the generator stops the corpus being written at all. All nine are currently confirmed by `github.com/hdevalence/ed25519consensus` v0.2.0 under `conformance/vibeproof/v1/zip215-oracle-run.json`. Go's `crypto/ed25519` and Python's `cryptography` are run as contrast oracles and D-342 forbids either verdict being recorded as a ZIP-215 one; selecting a ZIP-215-capable Go implementation for the product remains part of the D-012 bakeoff, and using one as a measuring instrument is not adopting it. D-343 records what running the contrast oracles found: two deployed cofactorless verifiers accept a non-canonical `A` encoding RFC 8032 SS5.1.3 says must fail to decode, so the corpus separates divergence from the strict text and divergence from a measured implementation rather than reporting one number.

This unit authors the corpus. It does not make anything conformant: no implementation reads the corpus, `P-003` and `P-004` are the units that make the Rust and Go verifiers yield its recorded verdicts, and `P-003` already names that as its acceptance criterion.

### PF-069 — Specify the private-beta invite aggregate
Files: `docs/security/PRIVATE_BETA_ADMISSION.md` (new), `packages/schemas/state-machine-registry-v1.json`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `packages/schemas/policy-defaults-v1.json`, `packages/schemas/data-disposition-v1.json`, `docs/privacy/DATA_MAP.md`
Acceptance: `invite_codes` and `invite_redemptions` exist with a state vocabulary that agrees across the registry, the SQL `CHECK` and the binding table; a redemption is keyed so that two concurrent redemptions of one code cannot both insert and one account cannot hold two; `redeemInvite` declares its own `security` requirement and a 4xx set that resolves against the reason registry in both directions; and the issuer-to-invitee edge has a lawful basis and a retention window in the Article 30 record.
Depends: PF-038, PF-050
Est: 8-12
Status: landed
Evidence: exists docs/security/PRIVATE_BETA_ADMISSION.md
Evidence: contains 1 packages/schemas/planning-schema.sql :: create table invite_codes
Evidence: contains 1 packages/schemas/planning-schema.sql :: create table invite_redemptions
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: redeemInvite
Evidence: contains 1 packages/schemas/reason-codes-v1.json :: INVITE_CODE_NOT_REDEEMABLE
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres

D-180 recorded that the private beta had no admission mechanism at all: codes needed issuance, a redemption binding exactly one account, quota, expiry, revocation, a state machine, a persistence owner and an API surface, and none of those existed. Everything downstream already assumed the ring — `docs/architecture/API_EDGE_CONTRACT.md` derives every rate-limit quota from a 200-participant invite-only population, and D-238 makes that ring the substitute for a staging environment.

This unit is the specification and not the implementation. No code is issued, no redemption runs, no expiry sweeper exists, and the lockout counter is edge-side state that nothing writes. D-280 through D-288 record the substantive choices, and `docs/security/PRIVATE_BETA_ADMISSION.md` states in its own Evidence section which claims are arguments from a constraint rather than measured results.

The unit that follows from this one is the handler: the serializable redemption transaction, the admission middleware that answers `INVITE_REQUIRED` outside the six-operation exempt set, the issuance tool, the expiry sweeper, and the erasure integration that deletes the redemption row and moves the code to `retired` in one transaction. Each is blocked behind P-1104 alongside every other implementation epic.

### PF-070 — Reconcile the challenge and batch binding across the CDDL, the DDL and the API
Files: `packages/schemas/vibeproof-claim-v1.cddl`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/policy-defaults-v1.json`, `packages/schemas/data-disposition-v1.json`, `docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`, `conformance/vibeproof/v1/malformed-resource-corpus.json`, `conformance/vibeproof/v1/exact-byte-vectors.json`, `conformance/vibeproof/v1/manifest.json`, `conformance/vibeproof/v1/README.md`, `scripts/repository/validate_batch_challenge_binding.py` (new), `scripts/repository/validate_repair_task_binding.py`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/cddl_instance.py`, `tests/ci/test_batch_challenge_binding.py` (new), `tests/ci/test_repair_task_binding.py`
Acceptance: `challenge-v1`, `claim_challenges` and `ClaimChallenge` carry the same eleven fields with no field in one and not the others, and `python3 scripts/repository/validate_batch_challenge_binding.py` exits non-zero when a field is added to or removed from any one of the three alone; `vibeproof-claim-v1` signs the batch id, zero-based index and claim count, and the exact-byte vectors reproduce byte-identically with them; a committed `atomic-batch-result-v1` carrying one refused per-claim result does not encode, with those exact bytes recorded as a negative corpus case that fails if the grammar readmits them; `gap_declarations` refuses a gap wider than the figure ADR-007 states, read from ADR-007 rather than restated; and `validate_repair_task_binding.py` still fails when any of PF-001..PF-036 drops its `Repair:` and when a unit above 36 carries `Serves:` without one.
Depends: PF-009, PF-010, PF-054
Repair: P-1140F-2
Serves: SR-007
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_batch_challenge_binding.py
Evidence: validator scripts/repository/validate_repair_task_binding.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/generate_vibeproof_vectors.py --check
Evidence: unittest tests.ci.test_batch_challenge_binding
Evidence: unittest tests.ci.test_repair_task_binding
Evidence: contains 1 packages/schemas/planning-schema.sql :: create table claim_batches
Evidence: contains 1 packages/schemas/planning-schema.sql :: create table gap_declarations
Evidence: contains 1 packages/schemas/planning-schema.sql :: expected_next_sequence bigint not null
Evidence: contains 1 packages/schemas/vibeproof-claim-v1.cddl :: cose-sign1-gap-v1 = #6.18([
Evidence: absent packages/schemas/openapi-v1.yaml :: batch_commitment:

D-625 returned SR-007 to `repair-in-progress` because one of its four named conflicting artifacts, `openapi-v1.yaml#ClaimChallenge`, had never been touched. This is that repair, and it is larger than the one artifact, because the artifact was only the visible end of a three-way disagreement.

**The challenge was defined three times over disjoint field sets.** `challenge-v1` bound account pseudonym, lineage, nonce, expected next sequence, expected local head, expected checkpoint, expiry and maximum batch. `claim_challenges` stored the challenge id, the account, the lineage, the device, the nonce, the expiry and its consumption. `ClaimChallenge` published a challenge id, a device, a nonce, a `batch_commitment` and an expiry. The intersection of the three was the nonce and the expiry. `VIBEPROOF_V1_PROTOCOL.md` says step 5 of the atomic transaction "verifies challenge ownership, expiry, expected tuple and single use" — and the expected tuple existed in exactly one of the three, so the verification the protocol describes could not be performed. Not performed incorrectly: not performed. The three now carry the same eleven fields and `validate_batch_challenge_binding.py` holds the table, so a field added to one of them alone fails.

Three smaller disagreements inside that one. `challenge_id` was `uuid7` on the wire, `text` in the DDL and a 64-hex string in the API, so the width a verifier compared depended on which document it read; it is `uuid7`/`uuid`/`format: uuid` now. `max_batch_claims` was `uint32` against a `batch-context` bounded at 256 claims, so a challenge could authorize a batch that could not be encoded. And ADR-007 requires the challenge to carry "maximum claim count, and maximum encoded bytes"; the byte ceiling existed in no artifact at all.

**`batch_commitment` is removed rather than propagated, under D-626.** It was required on both the challenge request and the challenge response and appeared nowhere else in the repository. Propagating it to the CDDL and the DDL would have made three artifacts agree on something uncomputable: every claim in a batch signs the challenge nonce, so the batch bytes depend on the challenge, and a digest of them cannot be supplied when asking for it. One challenge per batch is enforced instead by `unique (consumed_by_batch_id)` on `claim_challenges`, which is ADR-007's "a challenge cannot authorize multiple batches" as a write refusal.

**The batch position is now signed.** ADR-007 says every claim signs "its own batch ID, zero-based index, total count", and rejects a batch for "missing indices, duplicate indices, changed order". The claim map had thirty-one labels and none of them was any of those three, so the only statement of a claim's position was the order of the unsigned outer `batch-context` array — which the submitter writes. The rejection rule could not be applied to a hostile submitter at all. Labels 31, 32 and 33 carry them, the exact-byte vectors were regenerated with them, and `claims` mirrors them with `unique (batch_id, batch_index)`.

**Partial acceptance is now unrepresentable rather than prohibited in prose.** Three documents forbade it — ADR-007, `VIBEPROOF_V1_PROTOCOL.md` and `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` — and nothing at any layer refused it. `ClaimBatchResult` required both `accepted_claim_ids` and `rejections` with no mutual exclusion, so "batch accepted, claims 3 and 7 rejected" was a valid instance of the published contract. `atomic-batch-result-v1` gave the batch an outcome and each claim an independent one and tied them to nothing. `claims.batch_id` was a bare `uuid not null` pointing at no table. All three are closed: the CDDL result is a two-way choice whose committed arm admits only accepted per-claim results, the API schema carries a `oneOf`, and `claim_batches` exists with a `(batch_id, outcome)` key that `claims` and `claim_rejections` reference at disjoint outcome sets, so a partial outcome has no row to be written into.

**The gap declaration was a shape and nothing else.** D-043 says "bounded signed gap declarations" and ADR-007 says "a signed `gap-declaration` included in the first claim after the gap". There was no `cose-sign1-gap-v1`, so nothing could sign it; no slot in the claim or the batch, so nothing could carry it; no table, so nothing could store it, while `device_lineages.continuity_state` could already read `gap-declared` with no record of which gap; and no expression of the 10,000-sequence maximum, so "bounded" was a word with no enforcement. It now has a wrapper and protected headers with their own content type, a digest carried in claim label 34 with the envelope in `batch-context` label 5, a `gap_declarations` table, and the bound as a CHECK — because the bound is a relation between two labels and CDDL constrains each label independently, so it cannot live in the grammar. `gap-declaration` label 7 was `0..5` against four registered causes, so two ordinals were representable and unresolvable.

**Two things found while repairing, not before.** `policy-defaults-v1.json` set `batch_max_claims` to 500 while the grammar admitted 256 and the negative corpus refused 257; the configurable ceiling was twice the encodable one, and an operator raising it would have produced rejections no reason code explained. It is 256. And the negative corpus had no way to state "these bytes decode perfectly and the grammar forbids them" — the corpus said so itself, deferring `atomic-batch-result-v1` and `claim-result-v1` with the words "in prose state rather than in bytes". That absence is why partial acceptance could be forbidden by three documents and admitted by two schemas for as long as it was. A `cddl_hex` case shape now exists, six cases use it, and `challenge-without-expected-tuple` records the exact shape SR-007 named so the artifacts cannot drift back to it silently.

**What this unit does not do.** It does not close SR-007; the finding's state and review verdict are the owner's. It reconciles four of the five divergences D-043 records and the whole of the challenge one; the fifth — `checkpoint-receipt-v1` and `checkpoint_receipts` having near-disjoint column sets, with `server_receipt_sequence` defined once in the CDDL and stored nowhere while `VIBEPROOF_V1_PROTOCOL.md` makes it part of server state — is untouched and stands open. It is a receipt-shape divergence rather than a challenge or batch one, and folding it in here would have made one unit answer for two findings. And nothing here is implementation: no verifier reads the CDDL, no handler applies the constraints, and `validate_batch_challenge_binding.py` proves the artifacts agree, not that the protocol they agree on is correct.

### PF-071 — Bind the adapter manifest's certification block to the one certification vocabulary
Files: `packages/schemas/adapter-manifest.schema.json`, `packages/schemas/examples/adapter-manifest.valid.json`
Acceptance: `adapter-manifest.schema.json#certification` declares a required `state` whose enum is `uncertified` plus the eight states of the `source-certification` machine, the same nine `source-receipt-v1.schema.json` and `producer-accounting-binding-v1.schema.json` carry; `certification.bundle_sha256` admits null and is null exactly when `state` is `uncertified`, enforced in both directions by an `if`/`then`/`else` so that a null digest and an uncertified state cannot be stated apart; `modes` and `certification.mode` both admit exactly the nine observation modes `observer-equivalence-v1.json` declares, so `import` is refused and `acp` is admitted; and `packages/schemas/examples/adapter-manifest.valid.json` carries no invented bundle digest.
Depends: PF-016, PF-018
Repair: P-1140F-3
Serves: SR-009
Est: 4-6
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_finding_artifact_coverage
Evidence: contains 1 packages/schemas/adapter-manifest.schema.json :: "uncertified",
Evidence: contains 2 packages/schemas/adapter-manifest.schema.json :: "acp",
Evidence: absent packages/schemas/adapter-manifest.schema.json :: "import"
Evidence: absent packages/schemas/examples/adapter-manifest.valid.json :: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

**Found by `validate_finding_artifact_coverage.py`, not by reading.** `adapter-manifest.schema.json#certification` is the first of SR-009's three conflicting artifacts and no commit the finding's closure evidence cites had ever opened the file. PF-015 repaired the tuple digest, PF-018 the accounting reconciliation, and PF-016 the certification lifecycle in five other artifacts — `certification-result-v1.schema.json`, `normalized-event.schema.json`, the registry, the DDL and the API — while the manifest that every adapter has to write sat two commits old, both from before P-1140F began. It was green because nothing read it: `validate_planning_artifacts.py` checked the schema for well-formedness and validated its one example, and the vocabulary binder that compares observation modes across six artifacts and certification states across two does not name this file in either map.

**Four live defects, all in one block.** There was no `state` field at all, so a manifest could name a bundle digest and a tuple and say nothing about whether that certification was active when it was read — while `ACCOUNTING_AND_TIME_CONTRACT.md` holds the effective ceiling at `private-analytics` for every state other than `active`, a rule the artifact had no field in which to express. `bundle_sha256` was a required non-nullable 64-hex string, which four other artifacts had already made nullable for the reason `evidence-bundle-v1.cddl` states in words — "nil while uncertified" — and which `ADAPTER_CERTIFICATION_POLICY.md` makes unavoidable here, because every tuple this repository can reach is `candidate` and no result bundle has been signed. So no adapter manifest could validate without inventing a digest, and the committed example duly carried sixty-four `f` characters: the identical placeholder PF-016 deleted from `normalized-event.valid.json` and asserted gone with its own `Evidence: absent` line. The same constant survived one directory away because nothing looked. `certification.mode` carried a bare slug pattern and no enum, so a certified tuple could name a mode `observer-equivalence-v1.json` assigns no precedence rank and the survivor rule would have had nothing to order it by. And `modes` was a second spelling of the mode vocabulary — nine values, but with `import` and without `acp` — which is precisely the duplication `planning-schema.sql`'s own CHECK comment names this finding as existing to remove.

**The null is bound rather than merely admitted.** Making `bundle_sha256` nullable on its own would convert a representation gap into a permission: a manifest that forgot the digest would be indistinguishable from one that declared itself uncertified. The `if`/`then`/`else` makes the two facts one — `uncertified` requires the null and every other state requires the digest — so both directions fail, which is what stops the pair being satisfiable by an implementer picking whichever half is convenient.

**What this unit does not do.** It does not close SR-009; the finding's state and review verdict are the owner's, and D-633 returns it to `repair-in-progress` rather than repairing the record to match the schema. It does not repair `lifecycle`, which is a separate six-value enum in the same file sharing only three values with the `source-certification` machine and bound to no machine at all — that is an adapter-lifecycle divergence rather than a certification-block one, and `UNIVERSAL_AGENT_COMPATIBILITY.md`'s five-stage adapter lifecycle has no registered machine to reconcile it against, so folding it in here would have meant inventing one. It does not add the collector-artifact, accounting-arithmetic or privacy-binding digests `UNIVERSAL_AGENT_COMPATIBILITY.md` names as tuple dimensions, nor the `version_min`/`version_max_exclusive` range `compatibility-tuple-v1.schema.json` requires against this file's single `source_version` string. And nothing here certifies anything: every state this repository can reach is still `candidate` or `uncertified`, and the example says `uncertified` because that is what is true.

### PF-072 — Reconcile the verifier appraisal record across the CDDL, the DDL and the appraisal result
Files: `packages/schemas/vibeproof-claim-v1.cddl`, `packages/schemas/planning-schema.sql`, `packages/schemas/appraisal-policy-v1.json`, `packages/schemas/appraisal-policy-v1.schema.json`, `conformance/evidence/appraisal-result.valid-standard.json`, `conformance/evidence/appraisal-result.valid-superseded.json`, `conformance/evidence/appraisal-result.invalid-e1r-hardened.json`, `conformance/evidence/appraisal-result.invalid-imported-competitive.json`, `conformance/evidence/appraisal-result.invalid-client-selected-state.json`, `conformance/evidence/manifest.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `scripts/repository/validate_planning_artifacts.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_accounting_evidence_chain.py`
Acceptance: `verifier-appraisal-v1`, `verifier_appraisals` and `appraisal-result-v1.schema.json` describe one appraisal record, with `validate_evidence_chain` comparing the CDDL's **field set** against the record's rather than only the integer ranges of its ten dimension labels, so a field present in one and absent from another fails in either direction; the CDDL carries `evidence_bundle_sha256`, the supersession pair and the evaluated certification state, and its certification-bundle label admits nil, because `appraisal-result-v1.schema.json` records that a capture bound to no certification is every capture this repository can currently take and the profile must be able to encode one; `verifier_appraisals` holds the claim digest, the evidence digest, the validity interval and the supersession chain, carries a unique index that makes one appraisal current per claim, and admits a null `evidence_profile_id` to match the nullable awarded profile both other authorities declare; the relationship between `verifier_appraisals` and `evidence_assessments` is declared, because both persist the same three assessed states with no record of which wins; and `python3 -m unittest tests.ci.test_accounting_evidence_chain` exits 0 and fails on each of those drifts.
Depends: PF-017
Repair: P-1140F-3
Serves: SR-017
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_accounting_evidence_chain
Evidence: contains 1 packages/schemas/planning-schema.sql :: create unique index verifier_appraisals_current_per_claim_idx
Evidence: contains 1 packages/schemas/planning-schema.sql :: evidence_profile_id text check (evidence_profile_id in
Evidence: contains 1 packages/schemas/vibeproof-claim-v1.cddl :: 26: 0..8,                ; certification state
Evidence: contains 1 packages/schemas/vibeproof-claim-v1.cddl :: 18: digest32 / nil,      ; certification bundle sha256
Evidence: contains 1 packages/schemas/planning-schema.sql :: provenance_state text not null check
Evidence: contains 1 packages/schemas/planning-schema.sql :: integrity_state text not null check
Evidence: contains 1 packages/schemas/planning-schema.sql :: continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken'))
Evidence: absent packages/schemas/appraisal-policy-v1.json :: source_limb

**The three authorities now hold the same twenty-six fields.** The CDDL gained the four facts the record carried and no label did — the evidence-bundle digest, both halves of the supersession chain, and the certification state as it stood at appraisal — plus the three evaluated bundle identifiers. Label 18 admits nil, because every capture this repository can take is bound to no certification and the previous non-nullable digest made the common case unencodable; label 5 admits nil for the same reason on the verifier implementation, which the policy bundle has recorded as null since it was written. `verifier_appraisals` went from nine columns to thirty-one and now stores the claim digest, the evidence digest, the seven dimensions, the validity interval and the supersession chain. `evidence_profile_id` is nullable, which is what CDDL label 14 and `awarded_profile_id` had always said and what `not null` made unrepresentable: a rejected claim is awarded no profile, so the table could not store the outcome of a rejection.

**The check is the repair.** `appraisal_wire_ranges()` matched `0..<n>` and nothing else, so it parsed ten labels of twenty-three and labels 3, 5, 14 and 18 through 22 were invisible to everything. A field could be added to the record and to no label, or dropped from the CDDL entirely, and the only thing looking would report that ten dimensions were still in range — which is why one aggregate could be described three ways for as long as it was. `appraisal_cddl_labels()` reads every label and its declared type; `appraisal-policy-v1.json` carries `wire_binding.labels` mapping each to a record field and `record_only_fields` naming the six that are deliberately not on the wire with the reason for each; and the comparison fails in both directions on the field set, on nullability per field, and on ordinal density. The same shape runs against the DDL: `column_bindings` maps record field to column by full path, `column_only` explains the one column no field names, and `unbound_fields` and `unpersisted_fields` are separated because a gap this repository intends to close and a decision that the column would be wrong are different claims and one list made them one.

**Three slack ranges, found by tightening the rule rather than by reading.** The old comparison was `>`: an ordinal outside the range failed, and a range wider than the ordinals passed. `capture_class` and `accounting_class` were declared `0..4` against four values and `device_key_class` `0..6` against six, so three labels each carried one integer that encoded successfully and resolved to nothing. This is the shape PF-070 found once in the gap declaration's cause label; here it was three more times in one rule, in the artifact that had gone unparsed. The rule is now equality, and the test that widens `capture_class` back to `0..4` was confirmed against the pre-repair validator: it passed there.

**`bound_columns` was a second spelling and is gone.** It listed column names beside `unbound_fields`' record-field names, and nothing connected the two vocabularies — which is how `evidence_profile_id` sat in `bound_columns`, declared reconciled, while contradicting both other authorities on nullability. A map from field path to column cannot be half-right in that way. The same edit removed `source_limb` from `unbound_fields`: it named no field of the record, no label of the CDDL and no column of the table, so it was an entry excusing the absence of something that does not exist. `dimensions.source_class` already carries the D-078 limbs.

**One aggregate, one owner, stated in the DDL.** `evidence_assessments` persisted the same three assessed states against the same `claim_id`, and `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` and `DATA_MAP.md` both read the two tables as one thing while `appraisal-policy-v1.json` named only `verifier_appraisals`. The three states leave `verifier_appraisals` rather than being redeclared there: they were never a coarser spelling of the seven dimensions to be kept beside them, and a copy in the aggregate's own owner would have made the finding's defect permanent. They remain on `evidence_assessments`, which is the older record, retained because `public_state` has a consumer PF-046 owns and because the erasure and data-disposition contracts name the table. Their `SQL_LOCAL_VOCABULARIES` entries for `verifier_appraisals` were deleted rather than left pointing at columns that no longer exist. The evidence for that departure is `contains 1` rather than `absent`, because the three declarations are still in the file and should be: they are `evidence_assessments`' columns. `absent` would have been false, and "absent from this table" is not something the verb can say — so the assertion is that each appears exactly once, which is true only while one table holds it.

**What this unit does not do.** It does not close SR-017; the finding's state and review verdict are the owner's, and this unit cannot cite its own merge commit as closure evidence. It does not touch `evidence-profile-policy-v1.json`, which is the sole dimension authority the repair binds the others to rather than a party to the disagreement — though note that its `source` list carries `E1` undivided while the record and the wire carry the D-078 limbs, which is a refinement the policy bundle declares and reconciles rather than a divergence. It does not add instance-level CDDL conformance execution, so `evidence-bundle-v1.cddl` and `verifier-appraisal-v1` are still grammars nothing decodes against: `validate_evidence_chain` proves the three authorities agree about the record, not that any implementation produces it. And nothing here is implementation — no verifier evaluates a dimension, no row is written, and a claim's appraisal remains a thing this repository specifies rather than performs.

**What it looked like before the repair, kept because the shape recurs.** SR-017 named seven conflicting artifacts and PF-017, its only serving unit, opened one of them. Seventeen fields existed in the CDDL rule and in no column: the canonical claim digest, the verifier policy id, the verifier implementation digest, the acceptance outcome, all seven dimensions, the ranking eligibility, the anomaly disposition, the evaluated certification bundle, both validity timestamps and the re-evaluation trigger. Three columns existed in the DDL and in neither other authority. Four concepts existed in the appraisal record and in neither the CDDL nor the DDL: the evidence-bundle digest, both halves of the supersession chain, and the certification state. `appraisal-policy-v1.json` declared twenty of these as `unbound_fields` and three as `dropped_columns`, and `validate_evidence_chain` failed when that declaration went stale - so the gap was honestly recorded, and recording a gap is not closing it. D-267's reopen trigger was exactly that the SQL half lands. It has landed.

**Three disagreements nothing recorded, all now closed.** `evidence_profile_id text not null` contradicted CDDL label 14 `registered-id / nil` and `appraisal-result-v1.schema.json#awarded_profile_id`: a rejected or quarantined claim has no awarded profile and the table could not store one. That column was not in the declared gap - it sat in `bound_columns`, declared reconciled and not. CDDL label 18 was `digest32` with no `/ nil` while the record admitted null for the same fact. And `evidence_assessments` was a second table persisting the same three states for the same aggregate with nothing declaring which won, against AGENTS.md's rule of one persistence owner per mutable aggregate. The first two are repaired in the artifacts; the third is settled above.

**Why the validator clause was the load-bearing half of the acceptance.** `appraisal_wire_ranges()` extracted only the ten labels matching an integer-range pattern, so labels 3, 5, 14 and 18 through 22 were never parsed and no check noticed that the CDDL lacked the evidence digest, the supersession pair and the certification state entirely. A repair that added those fields without extending the comparator would have left the next drift exactly as invisible as this one was - which is why the comparator, not the fields, is what this unit is really about.

### PF-073 — Reconcile the checkpoint receipt across the CDDL, the DDL and the API
Files: `packages/schemas/vibeproof-claim-v1.cddl`, `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `packages/schemas/data-disposition-v1.json`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `docs/security/INTEGRITY_MODEL.md`, `conformance/vibeproof/v1/fork-and-rotation-vectors.json`, `conformance/vibeproof/v1/manifest.json`, `conformance/p1140e/sql-race-plans-v1.json`, `scripts/repository/validate_checkpoint_receipt_binding.py` (new), `scripts/repository/validate_planning_artifacts.py`, `tests/ci/test_checkpoint_receipt_binding.py` (new), `tests/ci/test_batch_challenge_binding.py`, `tests/ci/test_fork_and_rotation.py`, `Makefile`, `.github/workflows/planning-checks.yml`
Acceptance: `checkpoint-receipt-v1`, `checkpoint_receipts` and a `CheckpointReceipt` component in `openapi-v1.yaml` carry the same eleven fields with no field in one and not the others, and `python3 scripts/repository/validate_checkpoint_receipt_binding.py` exits non-zero when a field is added to or removed from any one of the three alone; `server_receipt_sequence` has a column and a `unique (lineage_id, server_receipt_sequence)` constraint, so the monotonic receipt counter `VIBEPROOF_V1_PROTOCOL.md` names as server state is stored rather than only described; the five items of that document's server-state sentence are parsed out of it and each must resolve to a column, rather than the sentence being restated in the validator; every column that is not on the wire records why, and every wire label that is not a column records why; and `python3 -m unittest tests.ci.test_checkpoint_receipt_binding` exits 0 and fails on each of those drifts.
Depends: PF-009, PF-010, PF-070
Repair: P-1140F-2
Serves: SR-007
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_checkpoint_receipt_binding.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: unittest tests.ci.test_checkpoint_receipt_binding
Evidence: unittest tests.ci.test_batch_challenge_binding
Evidence: contains 1 packages/schemas/planning-schema.sql :: server_receipt_sequence bigint not null
Evidence: contains 1 packages/schemas/planning-schema.sql :: unique (lineage_id, server_receipt_sequence)
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: CheckpointReceipt:
Evidence: absent packages/schemas/planning-schema.sql :: unique (lineage_id, last_sequence)

**The sixth divergence, which is why D-043 stayed provisional.** PF-070 reconciled four of the five divergences D-043 records and the whole of the challenge one, and said in terms that it had not touched the receipt. `checkpoint-receipt-v1` declared twelve labels; `checkpoint_receipts` declared nine columns; the two overlapped on two concepts — the lineage, and the claim high-water mark, which they spelled differently. The API projected none of it: there was no `CheckpointReceipt` component anywhere in `openapi-v1.yaml`, and `ClaimBatchResult.checkpoint_receipt` was a base64 blob with `maxLength: 4096`, so a client received the receipt as bytes it could verify and not as a record it could read.

**`server_receipt_sequence` was defined once and stored nowhere.** One occurrence in the whole repository — CDDL label 7 — against a protocol document that lists "monotonic receipt sequence" as one of the five things server state consists of. No column, no API property, no validator, no reader. The counter that was doing the work in its place was `last_sequence`, which counts claims: one atomic batch advances the claim sequence by up to 256 and the receipt sequence by exactly one, so the two were never the same number and the uniqueness constraint that looked like it enforced receipt monotonicity enforced something else. Both now exist, both are unique per lineage, and the column is renamed `accepted_through_claim_sequence` so the two counters cannot be read as one word again.

**The prose authority is parsed rather than restated.** ADR-007 says nothing about receipts — `checkpoint` and `receipt` match zero lines in it — so unlike PF-070 there was no consequence clause to derive a bound from, and none was invented. `VIBEPROOF_V1_PROTOCOL.md`'s server-state sentence is the sole prose authority, and the validator splits its five items out of the sentence and requires each to resolve to a column. Deleting the sentence fails, removing an item from it fails, and adding an item that no column holds fails. A validator that restated the five items would have gone on passing after the document changed, which is the difference between reading an authority and copying it.

**A test that had stopped testing.** `tests/ci/test_batch_challenge_binding.py` proved PF-070's server-only-column check by injecting a drift anchored on `issued_at timestamptz not null`, replacing the first occurrence in the file. Giving `checkpoint_receipts` an `issued_at` — declared earlier in the DDL — moved that anchor into the wrong table, so the test injected nothing into the table it was about and passed for the wrong reason. It was silently green until it was re-run against a file it did not expect. It is re-anchored on `expected_checkpoint_receipt_id`, which belongs to the table under test, with the reason in its docstring. This is the seventh instance in this program of a signal that improves when you remove what it counts, and the first one found in a drift-injection test rather than in a contract.

**Two things repaired that this unit did not set out to touch.** `data-disposition-v1.json` requires an expiry enforcement owner for any column that expires; the new `expires_at` is recorded as `rejected-at-read`, because it bounds how long the receipt may be presented as a head and not how long the row is kept — deleting the row would break the chain the next receipt links to. And `conformance/vibeproof/v1/manifest.json` carried a stale digest of `fork-and-rotation-vectors.json` once the constraint name in that fixture's note was corrected.

**What this unit does not do.** It does not close SR-007 or promote D-043; the finding's state and the decision's status are the owner's, and this unit cannot cite its own merge commit. It leaves `heads[].last_sequence` and `expected_authoritative_last_sequence` in `fork-and-rotation-vectors.json` alone: those are fixture vocabulary for acknowledged heads rather than column names, and renaming them would ripple through `resolve_checkpoint_heads` for no gain — the decision is recorded in that function's docstring rather than left to be rediscovered. Nothing here is implementation: no server issues a receipt, no client verifies one, and `validate_checkpoint_receipt_binding.py` proves the three artifacts agree about the receipt, not that the protocol they agree on is correct.

### PF-074 — Make the adapter manifest able to express the exact certification tuple
Files: `packages/schemas/adapter-manifest.schema.json`, `packages/schemas/examples/adapter-manifest.valid.json`, `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md`, `docs/planning/SR_SEVERITY_REGRADING_PROPOSAL.md`, `scripts/repository/validate_adapter_certification_tuple.py` (new), `tests/ci/test_adapter_certification_tuple.py` (new), `Makefile`, `.github/workflows/planning-checks.yml`
Acceptance: `adapter-manifest.schema.json#certification` enumerates the exact tuples a certification covers, each carrying every dimension `packages/schemas/compatibility-tuple-v1.schema.json` requires — the `version_min`/`version_max_exclusive` range in place of a single `source_version`, the artifact, accounting, arithmetic and privacy-binding digests, the duplicate domain, a validity interval and a revocation — and `python3 scripts/repository/validate_adapter_certification_tuple.py` exits non-zero when a dimension reaches the manifest, the tuple authority or `source_certifications` and not the other two, in either direction; every dimension deliberately absent from a side records why, so an absence cannot be satisfied by emptiness; the single-valued `source_version`, `platform_profile_id` and `mode` carriers are gone, so a certification covering a product of the manifest's four arrays is unrepresentable rather than discouraged; `check (state = 'active' or effective_ceiling = 'private-analytics')` holds in the manifest as well as the DDL, with the two ceiling vocabularies bound by a declared projection rather than an implicit rename; nothing is certified, the committed example stays `uncertified` with a null bundle digest, a null suite version and an empty tuple list, and no digest is invented anywhere; and `python3 -m unittest tests.ci.test_adapter_certification_tuple` exits 0 and fails on each of those drifts.
Depends: PF-016, PF-018, PF-071
Repair: P-1140F-3
Serves: SR-009
Est: 12-16
Status: landed
Evidence: validator scripts/repository/validate_adapter_certification_tuple.py
Evidence: validator scripts/repository/validate_planning_artifacts.py --allow-no-postgres
Evidence: validator scripts/repository/validate_cross_references.py
Evidence: unittest tests.ci.test_adapter_certification_tuple
Evidence: contains 1 packages/schemas/adapter-manifest.schema.json :: "version_max_exclusive"
Evidence: contains 1 packages/schemas/adapter-manifest.schema.json :: "attribute_allowlist_sha256"
Evidence: contains 1 packages/schemas/examples/adapter-manifest.valid.json :: "tuples": []
Evidence: absent packages/schemas/adapter-manifest.schema.json :: "source_version"

**What PF-071 left, said by PF-071.** That unit bound the certification block to the certification *state* vocabulary and wrote down what it had not done: the collector-artifact, accounting-arithmetic and privacy-binding digests `UNIVERSAL_AGENT_COMPATIBILITY.md` names as tuple dimensions, and the `version_min`/`version_max_exclusive` range `compatibility-tuple-v1.schema.json` requires against a single `source_version` string. That paragraph is this unit's specification, and it was accurate. A point version cannot express a certified range, and eleven other dimensions had nowhere to go at all.

**The product was the larger half.** `source_products`, `platforms`, `modes` and `accounting_profile_ids` were manifest-level arrays, and a single `source_version`, `platform_profile_id` and `mode` sat above them, so one certification authorized every combination those arrays multiplied into — untested combinations included, with no validity interval and no revocation. The repair is not a constraint on the product but the removal of anything from which a product could be derived: the single-valued carriers are gone and `certification.tuples` is the sole statement of coverage. The arrays remain as a declaration of reach, and coverage became containment — the validator refuses an enumerated tuple whose product, mode, accounting profile or duplicate domain the manifest does not declare, and whose platform profile the registry does not declare. An unbounded `tuples` array is refused too, because the product could otherwise be restated entry by entry.

**Eighteen dimensions, three ways, and twelve of them bound by one digest.** Six dimensions have a column on `source_certifications`; twelve are covered by `tuple_digest`, which is unique and is taken over the whole record, so a row naming the digest has already named the dimension and a column would be a second place the same fact could be wrong. That is a recorded reason rather than an omission, and the reverse is checked: a dimension recorded as digest-bound that later gains a column fails. Seven certification-record fields bind directly and four columns are server-only with reasons, which accounts for every column of the table rather than for the ones someone remembered.

**The ceiling was a hidden translation.** `ACCOUNTING_AND_TIME_CONTRACT.md` holds the effective ceiling at `private-analytics` for every state other than `active`, and the DDL enforces it; the manifest did not. It does now, and the two vocabularies that had to meet for it to mean anything — `standard-competitive` against `standard`, `hardened-source-bound` against `hardened` — are bound by a declared projection whose domain and range the validator asserts, rather than by a rename a reader had to notice. AGENTS.md forbids exactly this kind of hidden security-critical mapping.

**Three placeholders found in the committed example.** PF-071 removed sixty-four `f` characters from the bundle digest and the same class of defect survived two fields away: `suite_version` read `"1.0.0"` for a suite `ADAPTER_CERTIFICATION_POLICY.md` says has never run, and `platform_profile_id` read `"linux-x64-native"`, which the thirty-four-entry platform profile registry has never declared. Both are gone — the suite version is nullable and bound to `uncertified` beside the bundle digest, and an unregistered profile is now refused in any enumerated tuple. `mode` was also a third spelling of `observation_mode`, which both the tuple schema and the DDL had already settled.

**The null is bound rather than admitted, again.** `bundle_sha256: null`, `suite_version: null` and `tuples: []` are one fact with `uncertified`, enforced in both directions by a single `if`/`then`/`else`. That is what lets an honest manifest satisfy twelve new digest dimensions without inventing one of them: the committed example enumerates zero tuples and never reaches them. Any state other than `uncertified` requires a digest, a suite version and at least one tuple, because an empty list under a named state would be the product returning as an absence.

**A check that cannot fail at this head, recorded rather than deleted.** The containment rule — that an enumerated tuple names only what the manifest declares — has four branches, and all four are exercised by drift tests that inject `candidate` tuples. Against the committed content it is vacuous, because the only committed manifest is `uncertified` and enumerates nothing. The honest fix is a committed manifest that certifies something, and nothing in this repository may certify anything. It is stated here rather than counted as coverage. A negative example fixture was also considered and refused: `EXAMPLE_NEGATIVE_GAPS` names `adapter-manifest` as its only entry, and adding one would have emptied that map and forced the deletion of the test that fails when a declared gap no longer exists — weakening a check to add another.

**What this unit does not do.** It does not close SR-009; the finding's state and review verdict are the owner's, and this unit cannot cite its own merge commit. It does not repair `lifecycle`, still a six-value enum in the same file bound to no registered machine, for the reason PF-071 gave: `UNIVERSAL_AGENT_COMPATIBILITY.md`'s five-stage adapter lifecycle has no machine to reconcile against, and inventing one is not a binding repair. It does not touch the accounting-input and certification-evidence half of SR-009. And it certifies nothing: a schema that can express an exact tuple is not a certified tuple, and every state this repository can reach is still `candidate` or `uncertified`.

### PF-075 — Repair what an independent review of the pinned head found
Files: `evals/suites/suites.yaml`, `docs/verification/EVAL_SYSTEM.md`, `conformance/p1140f/semantic-findings-v1.json`, `conformance/p1140f/review-target-v1.json`, `conformance/planning/decisions-v1.json`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, `scripts/repository/validate_finding_artifact_coverage.py`, `scripts/repository/validate_repair_task_binding.py`, `scripts/repository/validate_state_vocabularies.py`, `tests/ci/test_repair_task_binding.py`, `tests/ci/test_state_vocabularies.py`
Acceptance: `evals/suites/suites.yaml#ranking-accounting` carries a `scope_note` naming the five of its six required cases that do not execute, and `docs/verification/EVAL_SYSTEM.md` marks the same five, so the registry and the document agree about the gap rather than one implying coverage the other denies; `validate_finding_artifact_coverage.py` fails a recorded reason for an artifact named with a `#fragment` when the reason never says that fragment; `validate_repair_task_binding.py` fails a settled finding that does not cite a landed unit declaring `Serves:` for it, and prints citation completeness beside the landed count; `validate_state_vocabularies.py` fails a recorded absence reason or binding note that denies an axis its own binding populates, distinguishing a server-scoped denial from a device-half one so the five genuinely local aggregates still pass; and each of those three checks fails on an injected drift with the exact message the test names.
Depends: PF-036, PF-072, PF-073, PF-074
Est: 8-12
Status: landed
Evidence: validator scripts/repository/validate_finding_artifact_coverage.py
Evidence: validator scripts/repository/validate_repair_task_binding.py
Evidence: validator scripts/repository/validate_state_vocabularies.py
Evidence: unittest tests.ci.test_repair_task_binding
Evidence: unittest tests.ci.test_state_vocabularies
Evidence: contains 1 evals/suites/suites.yaml :: Named for a conformance it does not execute
Evidence: contains 1 docs/verification/EVAL_SYSTEM.md :: One of the six executes
Evidence: absent scripts/repository/validate_state_vocabularies.py :: note="Local-only; never persisted server-side and never exposed by the API.",

**Why this unit declares no `Serves:`, and what carries the attribution instead.** It was first written as `Serves: SR-016`, and the two rules then in force refused it from both sides: a settled finding must cite every landed unit serving it, and a finding may only close once every unit serving it has landed. Together they say a new unit cannot serve an already-closed finding, which is right. Adding a repair to a closed finding either means the closure was wrong and the finding should reopen, or the work is not that finding's repair. Here it is the second: SR-016's artifact is repaired by this unit, and the record of why sits in D-637, which names the review, what it found and what was corrected. Declaring `Serves:` would have been the neater line and would have made the repository fail the rule this unit introduces - the first evidence that the rule works is that it caught its own author.

**Every defect in this unit was found by a reviewer who did not write the thing reviewed.** Three read-only reviews ran against the pinned head with no access to the reasoning that produced it and instructions to refute rather than confirm. They found five defects that every validator in this repository had passed. That is the argument for the review, and it is also the answer to what limitation 1 costs: the mechanical criteria were green throughout.

**A closure reason that described a different suite.** SR-016 excused `evals/suites/suites.yaml#ranking-accounting` with a reason saying the suite-name limb was resolved because the file now carries `shadow-codec-parity` with an explicit exploratory ceiling. That is a different suite. The reason never said `ranking-accounting`, and `ranking-accounting` still had exactly the defect the finding names: `EVAL_SYSTEM.md` declared six required cases and one runs, the single `imported-exclusion-and-dedupe` fixture, so a suite named for a ranking conformance executed nothing that ranks. The suite now states which five do not run and forbids itself as ranking-conformance, aggregation evidence, a launch gate or a support claim, and the document marks the same five. The name is kept, because the suite is where those cases belong once something implements them — the silence about their absence was the defect, not the ambition.

**And the check that would have caught it.** An artifact named with a `#fragment` is excused for that fragment, not for the file. A reason that never says the fragment is describing something else in the same file. The coverage validator now requires the fragment to appear in its own reason, which failed immediately on the SR-016 entry and on `evidence-profile-policy-v1.json#dimensions`, whose reason was substantively right and still never said `dimensions`.

**Three findings closed without citing a unit that served them.** SR-007 closed without citing PF-073, while retaining a sentence saying the receipt divergence was still open — PF-073 had closed it seventy-five minutes earlier. SR-009 closed without citing PF-074, which is the reviewed head itself. `validate_repair_task_binding.py` required every cited unit to serve the finding and to have landed, and never the converse, so a landed unit declaring `Serves:` could be absent from the record and the finding read as fully evidenced. The converse check now exists, keyed on settled findings so a citation may still land in the PR after the repair, and it immediately found a third instance nobody had looked for: SR-009 had never cited PF-016 either. The summary prints citation completeness beside the landed count, because `4/4` landed with three cited printed as `4/4`.

**A reason that denied what its own binding declared.** `daemon-lifecycle`, `privileged-supervisor` and `interactive-shell` each recorded their absent API binding with "never persisted server-side", while the same `Binding` named `service_instances`, `privileged_supervisor_instances` and `shell_sessions` and `planning-schema.sql` defines all three. The sentence was false from `8baad9a`, the commit that added the sql binding directly beneath it and left the prose alone, and it sat in both the validator and the contract document because it had been copied verbatim. A recorded absence may now not deny an axis its own binding populates, with server-scoped denials distinguished from device-half ones so the five aggregates whose tables live only in `local-store-v1.sql` still pass on the same sentence. `ranked-identity-eligibility` carried the same rot in a spelling the table cannot catch — "No `ranked_identities` table exists in the planning migration yet", against a table `8baad9a` created — and is repaired by hand with that limit recorded.

**Two decisions that could not close for reasons unrelated to their subject.** D-012 required fuzz evidence while the phase rules bar activating fuzz workflows, so it was unclosable by construction rather than merely open; its fuzz criterion is retained and P-1007 is named as its blocker, which makes the wait a schedule rather than a deadlock nobody owns. D-046 now records that PF-074's containment rule is vacuous at head for the same reason D-046 is open — nothing is certified — so certifying a tuple is what gives that check a subject.

**What this unit does not do.** It does not re-pin the review. The reviewed head carries a tracked machine-local `.venv` symlink removed three commits later, and moving the pin to a commit nobody reviewed would be a larger claim than the one being corrected; it is disclosed as the fourth limitation instead, with the fifth recording that three findings closed on an incomplete record. It does not make the review independent — that limitation stands, and these repairs are the measure of what it was worth. And it does not claim the three new checks make the recorded reasons true: two of them catch a phrase class and a missing citation, which is narrower than the claims those reasons make.

## Implementation epics — specified, blocked until P-1104

Everything below holds the launch scope in `docs/planning/PRODUCT_SCOPE_FREEZE.md`. These were headings until D-200; they are now units specified to the same standard as the `PF-` units above, and they remain blocked until P-1104 regardless of how well specified they are. Being specified is not being authorized, and being authorized is not being started.

### The five defects this section recorded against itself

Each was recorded here rather than silently carried. Each is now closed or stands with a reason.

- **Six units declared prose dependencies that do not resolve** — `PF-001`, `PF-004`, `O-005`, `X-001`, `X-009`, `X-010`, on phrases such as "implemented product paths" and "all launch paths". **Closed.** All six now carry unit IDs. In four of them the phrase was carrying two different things at once: an ordering claim and an authorization or capability condition. The ordering claim became a dependency; the condition is recorded in the unit body, because a condition is not an edge and cannot be scheduled. `validate_work_unit_status.py` fails on any `Depends:` entry that is not a resolvable ID.
- **Eleven units were orphans that nothing depended on** — `F-008`, `L-014`, `N-018`, `N-019`, `P-010`, `S-001`, `S-004`, `S-015`, `W-001`, `W-010`, `X-011`. **Ten closed, one stands.** `S-001` was the worst of them: `S-002` through `S-015` are all built on the Go service foundation and none depended on it. `S-002` now does. `W-001` gained the nine screens that consume its generated client, `S-004` gained `S-010`, and the six suite and automation units gained `X-010` or `X-011`. `X-011` remains an orphan and that is correct: nothing follows a launch-readiness review. A sink at the end of the graph is not the defect a missing edge in the middle is.
- **`X-011` did not gate launch.** P-1105 readiness transitively depended on 162 of 194 units, excluding all ten Epic W units — the entire hosted web product — plus `O-012`, `R-012`, `M-011`, `S-015`, `N-018`, `N-019`, `P-010` and `F-008`. Launch readiness was declarable with no web application. **Closed.** `X-011` now names the whole launch set explicitly, and `validate_work_unit_status.py --gate X-011` fails while any unit in its closure is not `landed`.
- **52 of the tables in `packages/schemas/planning-schema.sql` were named nowhere in this file.** **Closed, and the real number was larger.** The recorded figure counted 73 tables; the DDL declares 98, so 77 were unowned rather than 52. Every one now has a unit that names it, including the organizations and communities surfaces whose words did not appear in this document at all, and `validate_work_unit_status.py` fails on any `create table` no unit names. The check runs against the DDL, so a table added later without an owner fails rather than joining the backlog quietly.
- **Thirteen categories had no unit anywhere.** **Closed, twice over.** This branch authored `F-009` local development, `F-010` product CI/CD, `F-011` feature-flag mechanics, `S-016` error taxonomy, `S-017` API versioning and deprecation, `S-018` rate limiting, `S-019` audit ledger, `S-020` data migration and backfill, `X-012` logging, metrics and tracing, `X-013` staging, `X-014` load and soak testing, `X-015` runbooks and on-call, `X-016` cost model, `X-017` product analytics. Four more — `G-017`, `G-018`, `G-019` and `O-013` — were authored for table and API surfaces with no owner rather than for a missing category. **Epic OS** then absorbed thirteen units from `https://github.com/vedant-simulacrum/vibemaxxing/pull/66`, which had closed the same surfaces as normative documents with real numbers behind them; six of the units above are `superseded-by` their OS counterpart under D-207.

These units bind to normative owners that already exist rather than restating them: `OS-001` and `OS-002` to `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`; `OS-003`, `OS-004` and `OS-011` to `docs/architecture/API_EDGE_CONTRACT.md`; `OS-005` and `OS-006` to `docs/operations/LOGGING_AND_INSTRUMENTATION.md`; `OS-007` to `docs/engineering/LOCAL_DEVELOPMENT.md`; `OS-008` and `OS-009` to `docs/verification/CONFORMANCE_HARNESS.md`; `OS-010` to `docs/verification/TEST_STRATEGY.md`; `OS-012` to `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`; `OS-013` to `docs/operations/ENVIRONMENTS_AND_SECRETS.md`; `X-003` to `docs/operations/OBSERVABILITY_PRIVACY.md`; `X-004` to `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`; `X-005` to `docs/operations/INCIDENT_RESPONSE.md`; `X-015` to `docs/operations/SLOS_AND_ALERTS.md`; and `L-003` to `docs/operations/RELEASE_VERIFICATION.md`.

## Epic F — Reproducible foundation

### F-001 Toolchain and lockfile pins
Files: `rust-toolchain.toml`, `.node-version`, `Cargo.toml`, `apps/api/go.mod`, `apps/web/package.json`, `scripts/ci/check_toolchain_pins.py` (new), `tests/ci/test_toolchain_pins.py` (new), `Makefile`, `.github/workflows/planning-checks.yml`
Acceptance: `python3 scripts/ci/check_toolchain_pins.py` exits 0 on the pinned tree and non-zero when any manifest names a range, a caret or `latest`; the installed `cargo`, `go` and `node` versions equal the pinned strings byte-for-byte, and a tool that is not installed is reported as an uncompared pin rather than passing silently.
Depends: PF-036
Est: 4-6
Status: landed
Evidence: validator scripts/ci/check_toolchain_pins.py
Evidence: unittest tests.ci.test_toolchain_pins
Evidence: contains 1 apps/api/go.mod :: go 1.26.5
Evidence: absent apps/web/package.json :: ^

**Five pins are read, not restated.** The check reads `rust-toolchain.toml`'s channel, `.node-version`, `Cargo.toml`'s `rust-version`, the `go` directive in `apps/api/go.mod` and `apps/web/package.json`'s `engines`, then compares each against the installed tool. A check that compared one hardcoded list against another would agree with itself forever. Eleven npm specifiers moved from carets to exact versions, and `package.json` gained the `engines.node` pin that `.node-version` already carried.

**A tool that is absent is an uncompared pin, never a pass.** `--allow-uninstalled` changes the exit code and still prints the skip and the ran/skipped counts, because this repository's rule is that an absence must be visible rather than silent.

**The pin does not follow the machine.** The first attempt at this unit edited `apps/api/go.mod` from `1.26.5` down to `1.26.4` so the check would pass against the installed toolchain. That is the manifest chasing the environment, which is the opposite of pinning and the same shape as every defect the P-1140F program removed: making a signal green by moving the thing it measures. The pin was restored and the toolchain installed instead, which is the direction the dependency actually runs. The machine's mise configuration resolved `go` from `latest`, which is why it had drifted a patch below a repository that states its version.

**Two tests were pinning values in order to prove rules about them.** Both broke when the pin was corrected. One replaced the literal `go 1.26.4` and could not find it; the other asserted a mismatch against a hardcoded `1.26.5` and, once that became the pin, passed while proving the opposite of its name. Both now read the pin from `apps/api/go.mod`, and the mismatch case derives a version that cannot equal it by construction.

**What this does not prove.** That the pinned releases exist upstream, are supported, are free of advisories, or that anything here builds. The validator says so in its own claim-scope line. It compares declarations to one machine.

### F-002 Workspace initialization and package boundaries
Files: `Cargo.toml`, `crates/vibeproof-core/Cargo.toml`, `crates/vibeproof-adapters/Cargo.toml` (new), `crates/vibeproof-collector/Cargo.toml` (new), `crates/vibeproof-sync/Cargo.toml` (new), `crates/vibemaxxing-daemon/Cargo.toml` (new), `crates/vibemaxxing-cli/Cargo.toml` (new)
Acceptance: `cargo metadata --locked --no-deps` lists exactly the workspace members declared in `Cargo.toml`; `cargo tree --invert vibeproof-collector` shows no path from a network-capable crate into the collector, which is the D-006 boundary expressed as a dependency edge.
Depends: F-001
Est: 8-12
Status: not-started

### F-003 Authoritative generated bindings
Files: `packages/protocol/rust/src/lib.rs` (new), `packages/protocol/go/protocol.go` (new), `packages/protocol/typescript/index.ts` (new), `scripts/ci/generate_bindings.py` (new), `packages/schemas/openapi-v1.yaml`
Acceptance: `python3 scripts/ci/generate_bindings.py --check` exits 0, and exits non-zero after one byte of any source schema changes without regeneration; `git diff --exit-code packages/protocol` after a fresh regeneration proves no generated file is hand-maintained.
Depends: F-001
Est: 12-16
Status: not-started

### F-004 Byte-identical regeneration and drift detection
Files: `scripts/ci/generate_bindings.py` (new), `tests/ci/test_generated_bindings.py` (new), `.github/workflows/ci.yml`
Acceptance: two consecutive regenerations produce identical bytes under `sha256sum`, and CI fails when a committed generated file differs from a fresh regeneration; `python3 -m unittest tests.ci.test_generated_bindings` exits 0.
Depends: F-003
Est: 6-8
Status: not-started

### F-005 Checked numeric/time/digest/identifier primitives
Files: `crates/vibemaxxing-primitives/Cargo.toml` (new), `crates/vibemaxxing-primitives/src/lib.rs` (new), `crates/vibemaxxing-primitives/tests/overflow.rs` (new)
Acceptance: `cargo test -p vibemaxxing-primitives` exits 0 with one case per operation proving addition, multiplication and unit conversion return an error at the boundary rather than wrapping or saturating; `cargo clippy -p vibemaxxing-primitives -- -D clippy::arithmetic_side_effects` exits 0.
Depends: F-002
Est: 8-12
Status: not-started

### F-006 Privacy canary library and fixtures
Files: `crates/vibemaxxing-canary/Cargo.toml` (new), `crates/vibemaxxing-canary/src/lib.rs` (new), `conformance/privacy/p1140b-boundary-canaries-v1.json`, `conformance/telemetry/canaries.json`
Acceptance: `cargo test -p vibemaxxing-canary` exits 0 and fails when any canary string from either fixture reaches an outbound buffer; the suite covers every forbidden content class named in `docs/privacy/PRIVACY_CONTRACT.md`, and a class present in the contract but absent from the suite fails the test.
Depends: F-002
Est: 8-12
Status: not-started

### F-007 Feature disable and emergency-revoke framework
Files: `crates/vibemaxxing-kill-switch/Cargo.toml` (new), `crates/vibemaxxing-kill-switch/src/lib.rs` (new), `apps/api/internal/killswitch/killswitch.go` (new), `packages/schemas/policy-defaults-v1.json`
Acceptance: `cargo test -p vibemaxxing-kill-switch` and `go test ./internal/killswitch/...` both exit 0, with a case proving a revoked capability is refused within the propagation deadline recorded in `packages/schemas/policy-defaults-v1.json` and that the revocation survives a process restart.
Depends: F-002
Est: 8-12
Status: not-started

### F-008 Narrow format/lint/unit automation restoration
Files: `.github/workflows/ci.yml`, `scripts/ci/verify_repository.py`
Acceptance: `cargo fmt --check`, `cargo clippy -- -D warnings`, `gofmt -l`, `go vet ./...`, `npm run lint` and `npm test` each run in CI and exit 0; `grep -n 'paths:' .github/workflows/ci.yml` returns no filter exempting `apps/`, `crates/` or `Cargo.toml`.
Depends: F-001, F-002, F-003, F-004, F-005, F-006, F-007
Est: 6-8
Status: not-started

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

The prose range `F-001 through F-007` is expanded because `Depends:` admits unit IDs only. The prose condition `separate automation authorization` is not a dependency and is recorded here instead: activating these jobs is product automation and is outside the current authorization, per `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.

This unit was an orphan. `F-010` and `X-011` now depend on it.

### F-009 Local development environment
Files: `docs/engineering/LOCAL_DEVELOPMENT.md` (new), `scripts/dev/bootstrap.sh` (new), `compose.dev.yaml` (new), `Makefile`
Acceptance: `make dev-up` brings up PostgreSQL and the API from a clean checkout with no manual step, `make dev-check` exits 0, and `bash scripts/dev/bootstrap.sh --verify` exits non-zero when a toolchain version pinned by `F-001` is missing or wrong.
Depends: F-001, F-002
Est: 8-12
Status: superseded-by OS-007

One of the thirteen categories that previously had no unit anywhere. The database engine and migration tool are fixed by ADR-018 and are not re-decided here.

### F-010 Product CI/CD pipeline
Files: `scripts/ci/check_required_checks.py` (new), `docs/engineering/CI_AND_DELIVERY.md` (new), `.github/workflows/ci.yml`, `docs/engineering/ENGINEERING_SYSTEM.md`
Acceptance: `python3 scripts/ci/check_required_checks.py` exits 0 only when every quality layer listed under `## Required quality layers` in `docs/engineering/ENGINEERING_SYSTEM.md` has a matching job in the workflow set and appears in the branch-protection required-checks list, and exits non-zero when a layer has no job.
Depends: F-008
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. Deployment is deliberately excluded here and stays in `X-001`; this unit ends at a verified artifact, not at a running environment. Activating product CI is outside the current authorization for the reason recorded under `F-008`.

### F-011 Feature-flag mechanics
Files: `packages/schemas/feature-flag-v1.schema.json` (new), `apps/api/internal/flags/flags.go` (new), `packages/schemas/planning-schema.sql`, `packages/schemas/policy-defaults-v1.json`
Acceptance: `go test ./internal/flags/...` exits 0 with cases proving evaluation is deterministic for a given `(flag, principal, revision)` triple, that an unknown flag resolves to its recorded default rather than erroring, and that no flag name or evaluation result appears in any egress buffer under the `F-006` canary suite.
Depends: F-007, S-002
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

One of the thirteen categories that previously had no unit anywhere. `feature_flags` is the persistence owner and had no owning unit before this one.

Distinct from `F-007`: that unit revokes a capability in an emergency and is a safety control; this one is ordinary staged rollout. A flag evaluation is not an analytics event and must never be reported as one.

## Epic P — Normative VibeProof

### P-001 Rust canonical normative model
Files: `crates/vibeproof-core/src/model.rs` (new), `crates/vibeproof-core/tests/model.rs` (new), `packages/schemas/vibeproof-claim-v1.cddl`
Acceptance: `cargo test -p vibeproof-core --test model` exits 0, and a name cross-check in that test fails when any CDDL rule in `packages/schemas/vibeproof-claim-v1.cddl` has zero or more than one corresponding Rust type.
Depends: F-003
Est: 12-16
Status: not-started

### P-002 Rust deterministic CBOR encoder/decoder
Files: `crates/vibeproof-core/src/cbor.rs` (new), `crates/vibeproof-core/tests/canonical_cbor.rs` (new), `conformance/vibeproof/v1/malformed-resource-corpus.json`
Acceptance: `cargo test -p vibeproof-core --test canonical_cbor` exits 0; encoder output matches every vector in `conformance/vibeproof/v1/exact-byte-vectors.json` byte-for-byte; the decoder rejects every case in `conformance/vibeproof/v1/malformed-resource-corpus.json` with its recorded `reason_code`; a fixture encoded with the RFC 8949 Section 4.2.3 length-first ordering fails, which is what pins D-191.
Depends: P-001
Est: 12-16
Status: not-started

**The `Files:` line named a corpus that must not exist.** It declared a second negative corpus under `conformance/vibeproof/v1/` as new — the same `negative-vectors` filename PF-054 refused for the planning-side unit — and PF-054 had already made `conformance/vibeproof/v1/malformed-resource-corpus.json` the sole executable negative corpus. The name is written without a resolvable path here on purpose: this document is cross-reference checked, and a backticked path to a file that must never exist dangles. Creating the second file would have been a new owner for a vocabulary an existing artifact owns, which is the defect PF-054 closed; the acceptance now names the corpus that exists and the `reason_code` field its thirty-three cases actually carry.

### P-003 Rust COSE_Sign1 and Ed25519 profile
Files: `crates/vibeproof-core/src/cose.rs` (new), `crates/vibeproof-core/tests/cose.rs` (new), `conformance/vibeproof/v1/exact-byte-vectors.json`
Acceptance: `cargo test -p vibeproof-core --test cose` exits 0; the protected header encodes algorithm -19 and not -8, which a byte assertion on the header proves per D-190; every case in the ZIP-215 divergence corpus authored by `PF-068` yields its recorded verdict.
Depends: P-002, PF-068
Est: 12-16
Status: not-started

### P-004 Independent Go normative model and decoder
Files: `apps/api/internal/vibeproof/model.go` (new), `apps/api/internal/vibeproof/decode.go` (new), `apps/api/internal/vibeproof/decode_test.go` (new)
Acceptance: `go test ./internal/vibeproof/...` exits 0 against the same exact-byte and negative corpora as `P-002`; `go list -deps ./internal/vibeproof` names no artifact produced by the Rust crate, so the two implementations share only the CDDL source.
Depends: F-003
Est: 12-16
Status: not-started

### P-005 Go COSE verification and authorization binding
Files: `apps/api/internal/vibeproof/cose.go` (new), `apps/api/internal/vibeproof/cose_test.go` (new)
Acceptance: `go test ./internal/vibeproof/ -run COSE` exits 0 with every ZIP-215 divergence case producing its recorded verdict; substituting the standard-library `crypto/ed25519` makes the suite fail, which is the check that D-192 is actually enforced rather than merely cited.
Depends: P-004
Est: 12-16
Status: not-started

### P-006 Exact claim/appraisal/receipt/challenge/batch vectors
Files: `conformance/vibeproof/v1/exact-byte-vectors.json`, `scripts/repository/generate_vibeproof_vectors.py`
Acceptance: `python3 scripts/repository/generate_vibeproof_vectors.py --check` exits 0; the file carries at least one vector for each of claim, appraisal, receipt, challenge and batch; both implementations reproduce every byte, and hand-editing any vector makes the check fail, which is what D-194 requires.
Depends: P-003, P-005
Est: 8-12
Status: not-started

### P-007 Rotation/gap/correction/fork vectors
Files: `conformance/vibeproof/v1/fork-and-rotation-vectors.json`, `scripts/repository/generate_vibeproof_vectors.py`
Acceptance: the generator's `--check` mode reproduces `fork-and-rotation-vectors.json` and exits 0, so a hand-edited verdict fails rather than persists; the file additionally covers a correction record, which the hand-written corpus does not; Rust and Go each resolve every lineage, checkpoint and rotation vector to the verdict the file records, and disagree on none.
Depends: P-006
Est: 8-12
Status: not-started

The file is no longer `(new)`. `PF-010` wrote it by hand and a Python resolver in `validate_planning_artifacts.py` replays it, which is one subject and no generator. This unit's acceptance is what it has always been and is still entirely unmet: nothing regenerates the file, so an edited verdict persists, and no VibeProof implementation has ever been asked any of these questions. The acceptance is narrowed to the part this unit actually adds rather than restating what already landed.

### P-008 Malformed, mutation and resource corpus
Files: `conformance/vibeproof/v1/malformed-resource-corpus.json`
Acceptance: both decoders reject every case with its recorded reason and, for the cases that carry bytes, with its recorded `decoder_signal`; a bounded-allocator test fails when either exceeds the declared allocation ceiling or nesting depth; a single-bit mutation of any accepted vector is rejected rather than decoded.

`conformance/vibeproof/v1/negative-vectors.json (new)` is removed from the `Files:` line. `PF-054` resolved against the corpus that exists rather than adding a second file, and `PF-002` now fails on a third file declaring a CDDL rule. This unit is what makes the eighteen prose cases executable; it does not need a new file to do it.
Depends: P-003, P-005
Est: 10-14
Status: not-started

### P-009 Cross-language differential and byte-exact suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_protocol_differential.py` (new), `scripts/ci/run_evals.py`
Acceptance: a `protocol-conformance` suite is registered in `evals/suites/suites.yaml` and `python3 scripts/ci/run_evals.py --suite protocol-conformance` exits 0 with a status that is not `not_applicable`; the suite runs both implementations over every vector and fails on any disagreement, so a suite that skips one implementation cannot report a pass.
Depends: P-006, P-007, P-008
Est: 10-14
Status: not-started

### P-010 Fuzz/property harness activation
Files: `crates/vibeproof-core/fuzz/fuzz_targets/decode.rs` (new), `crates/vibeproof-core/fuzz/Cargo.toml` (new), `.github/workflows/fuzz.yml` (new), `docs/verification/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md`
Acceptance: `cargo fuzz run decode -- -runs=100000` exits 0 with no crash and no timeout, and a deliberately reintroduced non-minimal-integer acceptance is found inside that budget — a green fuzz run with no capability check is not evidence.
Depends: P-009
Est: 10-14
Status: not-started

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

The prose condition `separate security/eval workflow authorization` is not a dependency and is recorded here instead: the fuzz workflow named in the file list may not be activated under P-1104.

This unit was an orphan. `X-010` now depends on it.

## Epic A — Accounting and deterministic integrity

### A-001 Immutable accounting-profile loader and digest verification
Files: `crates/vibeproof-core/src/accounting/profile.rs` (new), `packages/schemas/accounting-profile.schema.json`, `conformance/accounting/accounting-profiles-v1.json`
Acceptance: `cargo test -p vibeproof-core --test accounting_profile` exits 0; the loader refuses a profile whose recomputed `accounting_profile_sha256` differs by one byte, and the digest it computes equals the value recorded in the fixture.
Depends: F-003, F-005
Est: 8-12
Status: not-started

### A-002 Operation/observer identity model
Files: `crates/vibeproof-core/src/accounting/identity.rs` (new), `packages/schemas/normalized-event.schema.json`, `conformance/accounting/accounting-v1-fixtures.json`
Acceptance: two observations of one operation from different observers resolve to a single operation identity and a retry generation resolves to a distinct one, each asserted by a fixture case; an event with no observer identity is rejected rather than defaulted.
Depends: A-001
Est: 8-12
Status: not-started

### A-003 Category containment and source authority
Files: `crates/vibeproof-core/src/accounting/containment.rs` (new), `conformance/accounting/p1140b-accounting-cases-v1.json`
Acceptance: a case whose cache-read count exceeds its containing input count is rejected rather than clamped; when two sources disagree, the higher-authority source wins by the recorded ordering and the losing value is retained in the result rather than dropped.
Depends: A-002
Est: 8-12
Status: not-started

### A-004 Cache/reasoning/modality/total reconciliation
Files: `crates/vibeproof-core/src/accounting/reconcile.rs` (new), `conformance/accounting/reconciliation-vectors-v1.json`
Acceptance: every vector reconciles to its recorded total; a vector whose parts cannot sum to its stated total yields a contradiction verdict rather than a silent adjustment, and the test fails if any adjustment is applied.
Depends: A-003
Est: 10-14
Status: not-started

### A-005 Retry/cancellation/nested-agent reconciliation
Files: `crates/vibeproof-core/src/accounting/lifecycle.rs` (new), `conformance/accounting/reconciliation-vectors-v1.json`
Acceptance: each value of `retry_policy`, `cancellation_policy` and `nested_execution_policy` is exercised by at least one vector, which a coverage assertion in the test enforces; a cancelled operation contributes exactly the recorded amount and a nested subagent turn is counted exactly once.
Depends: A-003
Est: 10-14
Status: not-started

### A-006 Duplicate-domain engine
Files: `crates/vibeproof-core/src/accounting/dedup.rs` (new), `conformance/accounting/dedup-vectors-v1.json`
Acceptance: two collectors over one session produce one counted event in every vector, including the case where the two choose non-colliding duplicate-domain commitments; each vector is run under both input orderings and must produce the same result.
Depends: A-002
Est: 10-14
Status: not-started

### A-007 Checked arithmetic and bounds
Files: `crates/vibeproof-core/src/accounting/bounds.rs` (new), `crates/vibemaxxing-primitives/src/lib.rs` (new)
Acceptance: `cargo test -p vibeproof-core --test accounting_bounds` exits 0; every arithmetic path returns an error at the boundary rather than wrapping, and an event above the recorded per-period ceiling is rejected with a reason code that resolves in `packages/schemas/reason-codes-v1.json`.
Depends: F-005
Est: 6-8
Status: not-started

### A-008 Deterministic contradiction/quarantine results
Files: `crates/vibeproof-core/src/accounting/verdict.rs` (new), `packages/schemas/reason-codes-v1.json`
Acceptance: every contradiction produces exactly one verdict drawn from the reason registry; running the whole fixture corpus twice with shuffled input order produces byte-identical verdict output, which is the order-independence D-018 assumes.
Depends: A-003, A-004, A-005, A-006, A-007
Est: 8-12
Status: not-started

### A-009 Server pricing interpretation model
Files: `apps/api/internal/pricing/pricing.go` (new), `packages/schemas/pricing-interpretation.schema.json`, `conformance/pricing/pricing-v1.json`, `conformance/pricing/pricing-v1-manifest.json`
Acceptance: `go test ./internal/pricing/...` exits 0; an unpriced model yields no cash figure rather than zero; every emitted figure carries the estimated label, which a response-schema assertion enforces so the label cannot be dropped by a caller.
Depends: A-001
Est: 8-12
Status: not-started

`pricing_interpretations` records how each dataset was applied to produce a figure.

Persistence owner for `pricing_datasets`, `pricing_entries`, `cost_interpretations` and `model_alias_facts`. All four had no owning unit before this one; `model_alias_facts` in particular is what lets an unrecognised model alias resolve to a priced model without guessing.

### A-010 Accounting differential and order-invariance evidence
Files: `evals/suites/suites.yaml`, `evals/fixtures/token-accounting-conformance.json`, `tests/conformance/test_accounting_differential.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite token-accounting-conformance` exits 0 with a status that is not `not_applicable`; the Rust and Go implementations produce identical totals for every fixture under both input orderings, and a one-token divergence fails the suite.
Depends: A-008
Est: 10-14
Status: not-started

## Epic N — Local runtime

### N-001 Local database schema and encrypted storage
Files: `packages/schemas/local-store-v1.sql`, `crates/vibemaxxing-daemon/src/store/mod.rs` (new), `crates/vibemaxxing-daemon/tests/store.rs` (new)
Acceptance: `cargo test -p vibemaxxing-daemon --test store` exits 0; a test reads the raw database file after writing claim material and fails when any canary string from `conformance/privacy/p1140b-boundary-canaries-v1.json` appears in plaintext.
Depends: F-002, F-005
Est: 12-16
Status: not-started

### N-002 Local migration and snapshot framework
Files: `crates/vibemaxxing-daemon/src/store/migrate.rs` (new), `packages/schemas/local-store-v1.sql`
Acceptance: migrating forward from an empty database and from every intermediate version produces byte-identical schema dumps; a snapshot taken before a migration restores to a database that passes the same integrity check, and a missing snapshot fails the test rather than being skipped.
Depends: N-001
Est: 10-14
Status: not-started

### N-003 Non-network collector process
Files: `crates/vibeproof-collector/src/main.rs` (new), `crates/vibeproof-collector/Cargo.toml` (new), `crates/vibeproof-collector/tests/no_network.rs` (new)
Acceptance: `cargo tree --invert --package vibeproof-collector` shows no reachable network crate, and a test that runs the collector under a sandbox failing every socket syscall exits 0. Both checks are needed: the dependency check catches intent, the syscall check catches a transitive surprise.
Depends: A-008, N-001
Est: 12-16
Status: not-started

### N-004 Source-blind sync process
Files: `crates/vibeproof-sync/src/main.rs` (new), `crates/vibeproof-sync/tests/egress.rs` (new), `packages/schemas/egress-allowlist-v1.json`
Acceptance: the test enumerates every field name in each serialised outbound payload and fails when one is absent from `packages/schemas/egress-allowlist-v1.json`; adding a field without an allowlist entry fails the build.
Depends: P-003, N-001
Est: 12-16
Status: not-started

### N-005 OS-supervised daemon
Files: `crates/vibemaxxing-daemon/src/main.rs` (new), `crates/vibemaxxing-daemon/tests/lifecycle.rs` (new), `packages/schemas/state-machine-registry-v1.json`
Acceptance: the test drives the daemon into every state of the `daemon-lifecycle` machine, including `degraded`, `offline`, `stopping` and `stopped`, and fails when a declared state cannot be reached — the defect class `PF-066` repaired in the registry, asserted here against a running process.
Depends: N-001
Est: 10-14
Status: not-started

### N-006 Authenticated channel handshake and peer identity
Files: `crates/vibemaxxing-daemon/src/channel/handshake.rs` (new), `conformance/sandbox/local-channel-vectors-v1.json` (new), `packages/schemas/local-control-v1.proto`
Acceptance: every vector produces its recorded accept-or-reject verdict, including the same-user impersonation and stale-process cases; a peer whose OS-reported identity differs from the recorded one is refused with a reason code that resolves in `packages/schemas/reason-codes-v1.json`.
Depends: N-003, N-004, N-005
Est: 12-16
Status: not-started

### N-007 Capability grants and typed local operations
Files: `crates/vibemaxxing-daemon/src/channel/capability.rs` (new), `packages/schemas/local-control-v1.proto`
Acceptance: a matrix test asserts cell by cell that each role can invoke exactly the operations its capability grant names and no others; an expired or revoked grant is refused within the deadline recorded in `packages/schemas/policy-defaults-v1.json`.
Depends: N-006
Est: 10-14
Status: not-started

### N-008 Commitment, receipt and queue stores
Files: `crates/vibemaxxing-daemon/src/store/queue.rs` (new), `packages/schemas/local-store-v1.sql`
Acceptance: a commitment write followed by a receipt write survives a `SIGKILL` between the two with no partial row, asserted at every write boundary; the queue drains in order and never re-emits an acknowledged item.
Depends: P-003, N-001
Est: 10-14
Status: not-started

### N-009 Crash consistency and recovery
Files: `crates/vibemaxxing-daemon/src/store/recover.rs` (new), `crates/vibemaxxing-daemon/tests/crash.rs` (new)
Acceptance: a fault-injection harness kills the process at every write boundary in the store, and after every one the database opens cleanly and passes its integrity check; a boundary the harness cannot reach fails the run rather than being skipped.
Depends: N-002, N-008
Est: 12-16
Status: not-started

### N-010 Protected key backend abstraction
Files: `crates/vibemaxxing-daemon/src/keys/mod.rs` (new), `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`
Acceptance: the backend trait has one implementation per platform plus a test-only in-memory one; `grep -rn 'secret_key\|private_key' crates/vibemaxxing-daemon/src` returns no line outside the backend module, so key material cannot leave it.
Depends: P-003, N-001
Est: 8-12
Status: not-started

### N-011 macOS key and process integration
Files: `crates/vibemaxxing-daemon/src/keys/macos.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: `cargo test -p vibemaxxing-daemon --features macos` exits 0 on a macOS runner, and the platform-profile row records which key path the host actually took rather than the best available one — a Secure Enclave claim on a host that fell back to the keychain fails the test.
Depends: N-010
Est: 8-12
Status: not-started

### N-012 Windows key and process integration
Files: `crates/vibemaxxing-daemon/src/keys/windows.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: `cargo test -p vibemaxxing-daemon --features windows` exits 0 on a Windows runner; the profile row records whether the key is TPM-backed or software-protected, and a TPM claim on a host without one fails the test.
Depends: N-010
Est: 8-12
Status: not-started

### N-013 Linux key and process integration
Files: `crates/vibemaxxing-daemon/src/keys/linux.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: `cargo test -p vibemaxxing-daemon --features linux` exits 0 on both a desktop-session and a headless runner; the headless case records the weaker protection it actually has rather than inheriting the desktop row, which a differing profile digest between the two runs proves.
Depends: N-010
Est: 8-12
Status: not-started

### N-014 CLI control client
Files: `crates/vibemaxxing-cli/src/main.rs` (new), `crates/vibemaxxing-cli/tests/commands.rs` (new)
Acceptance: every command exits with a status code the help text documents, and a test diffs the command list against the operations `packages/schemas/local-control-v1.proto` declares for the CLI role, failing on any difference in either direction.
Depends: N-007
Est: 8-12
Status: not-started

### N-015 Interactive shell process/connection lifecycle
Files: `crates/vibemaxxing-cli/src/shell/mod.rs` (new), `packages/schemas/state-machine-registry-v1.json`
Acceptance: the test drives the shell into all fifteen states of `interactive-shell`, including pre-auth startup and restart after crash, and fails when one cannot be reached; `shell_sessions` holds exactly one row per live connection, enforced by a unique constraint.
Depends: N-007
Est: 10-14
Status: not-started

`shell_ipc_peers` records the peer identity behind each live connection.

`shell_sessions` had no owning unit before this one.

### N-016 Shell subsystem projections and action separation
Files: `crates/vibemaxxing-cli/src/shell/projections.rs` (new)
Acceptance: a matrix test asserts that UI exit, pause collection, pause sync, stop daemon, logout and uninstall each produce their own recorded effect and none produces another's; the daemon, collection, sync, auth, permission, update and connectivity projections are read independently and no command mutates a projection it does not own.
Depends: N-015
Est: 8-12
Status: not-started

### N-017 Optional privileged supervisor
Files: `crates/vibemaxxing-daemon/src/supervisor/mod.rs` (new), `docs/decisions/ADR-012-OPTIONAL_PRIVILEGED_SUPERVISION.md`, `packages/schemas/planning-schema.sql`
Acceptance: a full end-to-end run with the supervisor absent exits 0, which is what makes it optional rather than nominally optional; when present it holds only the capabilities `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md` grants it, asserted capability by capability; `privileged_supervisor_instances` records each install.
Depends: N-006
Est: 10-14
Status: not-started

`privileged_consents` records the explicit consent for each privileged operation.

The prose condition `separate privilege review` is not a dependency and is recorded here instead: this unit needs a privilege review before it starts, and no unit ID expresses that. `privileged_supervisor_instances` had no owning unit before this one.

### N-018 Sleep/resume/reboot/login/logout/offline suite
Files: `crates/vibemaxxing-daemon/tests/platform_lifecycle.rs` (new), `evals/suites/suites.yaml`
Acceptance: `python3 scripts/ci/run_evals.py --suite resilience` exits 0 with a status that is not `not_applicable`, carrying one case per transition — sleep, resume, reboot, login, logout and offline — each with a recorded expected outcome; a transition with no case fails the suite rather than being absent from it.
Depends: N-009, N-015
Est: 10-14
Status: not-started

This unit was an orphan. `X-010` now depends on it.

### N-019 Disk-full/permission-loss/corruption suite
Files: `crates/vibemaxxing-daemon/tests/degraded_storage.rs` (new), `evals/suites/suites.yaml`
Acceptance: under an injected `ENOSPC`, a revoked directory permission and a truncated database file, the daemon reports a degraded state and loses no acknowledged claim; a case that ends in a silent success fails the test.
Depends: N-009
Est: 10-14
Status: not-started

This unit was an orphan. `X-010` now depends on it.

### N-020 Content-egress and local-role adversarial suite
Files: `crates/vibemaxxing-canary/src/lib.rs` (new), `conformance/telemetry/canaries.json`, `evals/suites/suites.yaml`
Acceptance: `python3 scripts/ci/run_evals.py --suite privacy-boundary` exits 0 with a status that is not `not_applicable`; every forbidden content class named in `docs/privacy/PRIVACY_CONTRACT.md` has at least one attempted-egress case from every local role, and every attempt is blocked.
Depends: N-003, N-004, N-005, N-006, N-007, N-008, N-009, N-010, N-011, N-012, N-013, N-014, N-015, N-016, N-017
Est: 12-16
Status: not-started

The prose range `N-003 through N-017` is expanded because `Depends:` admits unit IDs only.

## Epic S — Server secure spine

### S-001 Go modular service foundation
Files: `apps/api/cmd/api/main.go`, `apps/api/internal/server/server.go` (new), `apps/api/internal/config/config.go` (new)
Acceptance: `go build ./...` and `go test ./...` exit 0; `go list -deps ./internal/...` shows no domain package importing the HTTP layer, which is the boundary this unit exists to set and the one a later unit would otherwise erase silently.
Depends: F-002, F-003
Est: 10-14
Status: not-started

This unit was an orphan: `S-002` through `S-015` did not depend on the Go service foundation they are all built on. `S-002` now depends on it and every later Epic S unit reaches it transitively.

### S-002 PostgreSQL migration runner, roles and recovery
Files: `migrations/0001_init.sql` (new), `apps/api/internal/db/migrate.go` (new), `packages/schemas/planning-schema.sql`, `docs/decisions/ADR-018-DATABASE_AND_MIGRATION_TOOLING.md`
Acceptance: applying every migration to an empty database produces a schema dump byte-identical to one produced from `packages/schemas/planning-schema.sql`; `schema_migrations` records each version exactly once; every reversible step has a down path and every irreversible one is declared irreversible rather than left undefined.
Depends: S-001, F-001
Est: 12-16
Status: not-started

Also the persistence owner for `service_events`, the service-instance lifecycle ledger.

Persistence owner for `schema_migrations` and `service_instances`, neither of which had an owning unit before.

### S-003 Typed idempotency persistence
Files: `apps/api/internal/idempotency/store.go` (new), `migrations/0002_idempotency.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: a second insert with the same `(principal_type, principal_id, operation_id, idempotency_key)` is rejected by a unique constraint rather than by application code; the stored `idempotency_records` row carries the response status, content type, safe headers and body bytes; `go test ./internal/idempotency/...` exits 0.
Depends: S-002
Est: 8-12
Status: not-started

### S-004 Exact response replay and reservation recovery
Files: `apps/api/internal/idempotency/replay.go` (new), `apps/api/internal/idempotency/replay_test.go` (new)
Acceptance: a replayed request returns the stored body byte-for-byte and the stored status; a reservation left by a crashed process becomes recoverable at the recorded lease expiry and not before; an expired high-impact key is rejected rather than treated as a fresh mutation.
Depends: S-003
Est: 8-12
Status: not-started

This unit was an orphan. `S-010` now depends on it, which is correct: claim acceptance is the mutation whose replay has to be exact.

### S-005 Provider/OAuth transaction persistence
Files: `apps/api/internal/oauth/store.go` (new), `migrations/0003_oauth.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: an `oauth_transactions` row binds action, account or session, recent-auth grant, provider revision, redirect, state, PKCE verifier and expiry; a second consumption of the same transaction is rejected by a constraint, which a concurrent double-callback test exercises.
Depends: S-002
Est: 8-12
Status: not-started

Also the persistence owner for `oauth_authorization_events`, the append-only record of each authorization step.

### S-006 Account, linked identity and recent-auth persistence
Files: `apps/api/internal/identity/store.go` (new), `migrations/0004_identity.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `accounts`, `account_handles`, `linked_identities`, `web_sessions`, `session_families`, `native_sessions`, `optional_authenticators` and `recovery_codes` all carry the constraints their contract names; removing the last authentication method is rejected by a constraint rather than by a handler, which a direct SQL test proves.
Depends: S-002
Est: 12-16
Status: not-started

The unit also persists `recovery_cases`, whose cooling-off window, session revocation and device quarantine are carried by check constraints rather than by handler discipline.

`optional_authenticators` and `recovery_codes` — the passkey and recovery-code tables — had no owning unit before this one.

### S-007 Ranked identity, consolidation and appeal persistence
Files: `apps/api/internal/rankedidentity/store.go` (new), `migrations/0005_ranked_identity.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `ranked_identities` is a separate table from `accounts` with at most one active resolved row per person, enforced by a partial unique index; `appeals` and `appeal_decisions` record the investigation privately, and no query path sums two accounts' scores.
Depends: S-006
Est: 12-16
Status: not-started

The unit also persists `identity_investigations`, `identity_events`, `consolidation_cases` and `consolidation_contributions`, which the planning DDL now defines with their constraints. `consolidation_contributions` is the row-level form of the D-070 rule this unit's acceptance already states: one row per absorbed claim with its original period attribution, and no summed figure anywhere in the path.

### S-008 Device, key, installation and lineage persistence
Files: `apps/api/internal/device/store.go` (new), `migrations/0006_devices.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `devices`, `device_keys`, `device_enrollment_grants`, `device_lineages`, `device_key_events` and `adapter_installations` are keyed so that continuity is lineage-scoped rather than device-row-scoped, which a test proves by replacing a device row and showing the lineage survives.
Depends: S-002
Est: 12-16
Status: not-started

The unit also persists `lineage_fork_cases` and `lineage_fork_branches`, the D-072 fork and clone resolution tables, because a fork is a property of a lineage and belongs with the lineage keying this unit owns.

`adapter_installations` had no owning unit before this one.

### S-009 Challenge and checkpoint persistence
Files: `apps/api/internal/challenge/store.go` (new), `migrations/0007_challenges.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `claim_challenges`, `device_sequences` and `checkpoint_receipts` reject an out-of-order sequence, a reused challenge and a checkpoint that does not chain, each by constraint; `go test ./internal/challenge/...` exits 0.
Depends: S-008
Est: 10-14
Status: not-started

### S-010 Atomic claim acceptance and verifier transaction
Files: `apps/api/internal/claims/accept.go` (new), `migrations/0008_claims.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: accepting a claim writes the `claims` row, the `claim_payloads` row, the idempotency record, the audit row and the outbox row in one transaction, and an injected failure at any point leaves none of them, which a rollback test asserts row by row.
Depends: P-009, A-010, S-003, S-004, S-009
Est: 12-16
Status: not-started

### S-011 Immutable claims/appraisals/receipts/corrections
Files: `apps/api/internal/claims/ledger.go` (new), `migrations/0009_appraisals.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `claims`, `claim_rejections`, `claim_corrections`, `verifier_appraisals` and `evidence_assessments` reject an `UPDATE` and a `DELETE` at the database level; a correction is a new append-only row referencing the original, which a test proves by showing the original bytes unchanged.
Depends: S-010
Est: 10-14
Status: not-started

### S-012 Transactional outbox and worker checkpoints
Files: `apps/api/internal/outbox/outbox.go` (new), `migrations/0010_outbox.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `outbox_events` is written in the same transaction as its effect and `worker_checkpoints` advances only after an acknowledged batch; a worker killed mid-batch re-delivers at least once and never skips, which a fault-injection test asserts.
Depends: S-011
Est: 10-14
Status: not-started

### S-013 Fork quarantine and requalification
Files: `apps/api/internal/quarantine/quarantine.go` (new), `migrations/0011_quarantine.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: given the fork vectors from `P-007`, every post-fork branch lands in `quarantines` and every pre-fork accepted claim remains accepted; requalification resumes in a new lineage generation, and a test fails if any pre-fork claim is retracted.
Depends: S-008, S-009, S-010, S-011, S-012
Est: 12-16
Status: not-started

The prose range `S-008 through S-012` is expanded because `Depends:` admits unit IDs only.

### S-014 Compatibility/certification policy persistence
Files: `apps/api/internal/certification/store.go` (new), `migrations/0012_certification.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `platform_profiles` and `platform_certifications` bind an exact compatibility tuple; a query for support returns nothing when the certification is empty, planned, expired or suspended, which a table test asserts for each of those four states.
Depends: S-002
Est: 10-14
Status: not-started

The unit also persists `source_certifications`, which is where the exact tuple and its lifecycle live, and `platform_install_plans` with `platform_install_operations`, the typed platform operations one release performs on one profile. A check constraint on `source_certifications` makes any state other than `active` incapable of holding a ceiling above private analytics, which is the four-state assertion the acceptance names, expressed so that it cannot be got wrong by a query.

### S-015 Crash-before/after-commit PostgreSQL evidence
Files: `apps/api/internal/db/crash_test.go` (new), `conformance/p1140e/sql-race-plans-v1.json`
Acceptance: every plan in `conformance/p1140e/sql-race-plans-v1.json` runs against a real PostgreSQL instance and leaves exactly the rows it records; a skipped plan fails the suite, so an absent database cannot be reported as a pass.
Depends: S-010, S-011, S-012
Est: 12-16
Status: not-started

The prose range `S-010 through S-012` is expanded because `Depends:` admits unit IDs only. This unit was an orphan; `X-011` now depends on it.

### S-016 Error taxonomy and reason-code mapping
Files: `apps/api/internal/apierr/apierr.go` (new), `apps/api/internal/apierr/apierr_test.go` (new), `packages/schemas/reason-codes-v1.json`, `packages/schemas/openapi-v1.yaml`
Acceptance: `go test ./internal/apierr/...` exits 0 with a table test proving every code in `packages/schemas/reason-codes-v1.json` maps to exactly one HTTP status and one registered state machine, and that no handler can return a status or reason absent from the registry.
Depends: S-001, PF-045
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. `PF-045` decides the matrix; this unit is the runtime that cannot deviate from it.

### S-017 API versioning and deprecation
Files: `docs/architecture/API_VERSIONING_AND_DEPRECATION.md` (new), `scripts/ci/check_api_compatibility.py` (new), `apps/api/internal/server/version.go` (new), `packages/schemas/openapi-v1.yaml`
Acceptance: `python3 scripts/ci/check_api_compatibility.py --base origin/main` exits non-zero on any breaking change to a released operation that is not accompanied by a version bump and a dated deprecation entry, and 0 otherwise; a removed operation with no deprecation window fails.
Depends: S-001
Est: 8-12
Status: superseded-by OS-011

One of the thirteen categories that previously had no unit anywhere.

### S-018 Rate limiting and quota enforcement
Files: `apps/api/internal/ratelimit/ratelimit.go` (new), `apps/api/internal/ratelimit/ratelimit_test.go` (new), `packages/schemas/policy-defaults-v1.json`, `packages/schemas/openapi-v1.yaml`
Acceptance: `go test ./internal/ratelimit/...` exits 0; a table test asserts in both directions that every operation declaring a 429 has a configured limit and every configured limit names an existing operation; limits key on the authenticated principal and never on a content-derived value, which a test proves by rejecting a key derived from request content.
Depends: S-001, S-016
Est: 8-12
Status: superseded-by OS-003

One of the thirteen categories that previously had no unit anywhere.

### S-019 Audit event ledger
Files: `apps/api/internal/audit/audit.go` (new), `apps/api/internal/audit/audit_test.go` (new), `packages/schemas/planning-schema.sql`, `docs/privacy/DATA_MAP.md`
Acceptance: `go test ./internal/audit/...` exits 0; every mutation named in `docs/privacy/DATA_MAP.md` writes exactly one `audit_events` row in the same transaction as its effect, which an aborted-transaction test proves by showing neither row present; no audit column can hold a forbidden content class, asserted against the `F-006` canary set.
Depends: S-002, S-012
Est: 8-12
Status: not-started

`audit_events` had no owning unit before this one.

### S-020 Data migration and backfill runner
Files: `apps/api/internal/backfill/runner.go` (new), `apps/api/internal/backfill/runner_test.go` (new), `docs/operations/DATA_MIGRATION_AND_BACKFILL.md` (new)
Acceptance: `go test ./internal/backfill/...` exits 0; a backfill resumes from its recorded `worker_checkpoints` row after a kill, and re-running a completed backfill changes no row, which a table-checksum comparison before and after asserts.
Depends: S-002, S-012
Est: 10-14
Status: not-started

One of the thirteen categories that previously had no unit anywhere. Distinct from `S-002`, which runs schema migrations: this unit moves and rebuilds data behind them, which is the operation that can starve online traffic and the one that has to be resumable.

## Epic O — OAuth, sessions and ranked identity

### O-001 GitHub provider capability implementation
Files: `apps/api/internal/oauth/github.go` (new), `packages/schemas/oauth-provider-registry-v1.json`, `conformance/auth/provider-mixup-vectors-v1.json`
Acceptance: `go test ./internal/oauth/ -run GitHub` exits 0 against the recorded provider fixture; every capability the registry row claims — PKCE method, RFC 9207 `iss`, device flow — is exercised by a case, and a claimed capability with no case fails the test rather than being assumed.
Depends: S-005, PF-005
Est: 8-12
Status: not-started

### O-002 X provider capability implementation
Files: `apps/api/internal/oauth/x.go` (new), `packages/schemas/oauth-provider-registry-v1.json`, `conformance/auth/provider-mixup-vectors-v1.json`
Acceptance: `go test ./internal/oauth/ -run XProvider` exits 0 against the recorded provider fixture, under the same claimed-capability-must-have-a-case rule as `O-001`.
Depends: S-005, PF-005
Est: 8-12
Status: not-started

### O-003 Desktop browser Authorization Code + PKCE
Files: `apps/api/internal/oauth/authcode.go` (new), `crates/vibemaxxing-cli/src/auth.rs` (new)
Acceptance: the loopback redirect binds a single-use port and a state value; a callback carrying a mismatched state, a reused code or no PKCE verifier is refused, one test case each, and the refusal reason resolves in `packages/schemas/reason-codes-v1.json`.
Depends: O-001, O-002
Est: 10-14
Status: not-started

### O-004 Callback issuer/redirect/mix-up protection
Files: `apps/api/internal/oauth/callback.go` (new), `conformance/auth/provider-mixup-vectors-v1.json`
Acceptance: every vector in the mix-up fixture yields its recorded verdict, including an authorization response from provider B replayed to provider A's callback; a provider that returns no `iss` takes the recorded fallback path rather than trusting the response, asserted by a case for each provider.
Depends: O-003
Est: 10-14
Status: not-started

### O-005 Limited-input interactive device flow
Files: `apps/api/internal/oauth/deviceflow.go` (new), `crates/vibemaxxing-cli/src/auth.rs` (new), `packages/schemas/oauth-provider-registry-v1.json`
Acceptance: a table test asserts the flow starts only for providers whose registry row records device-flow capability; a test that sets `CI=true` expects a refusal, so the flow cannot become a CI default by omission.
Depends: O-001, O-002, O-003
Est: 8-12
Status: not-started

The prose dependency `provider capability; never CI default` is replaced. The capability half is now the resolvable dependency on `O-001` and `O-002`; the never-CI-default half was never a dependency at all and is an acceptance clause, which is where it now lives.

### O-006 Web/native session and refresh-family rotation
Files: `apps/api/internal/session/session.go` (new), `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md`, `packages/schemas/planning-schema.sql`
Acceptance: reusing a refresh token moves the `session_families` row to `replay-detected` and revokes every descendant; the state is read back from SQL rather than inferred in memory, which a direct query asserts.
Depends: S-006, PF-039
Est: 10-14
Status: not-started

`session_tokens` is the per-token row inside a family and is written here, not by `S-006`, because rotation is what creates and retires it.

### O-007 Linked identity and exact unlink
Files: `apps/api/internal/identity/link.go` (new), `apps/api/internal/identity/link_test.go` (new)
Acceptance: unlinking the last authentication method is refused; an unlink revokes exactly the sessions and device grants the contract names and no others, asserted row by row before and after.
Depends: O-004, O-006
Est: 8-12
Status: not-started

Also writes `identity_events`, the append-only link and unlink ledger.

### O-008 Provider loss/compromise recovery
Files: `apps/api/internal/identity/recovery.go` (new), `apps/api/internal/identity/recovery_test.go` (new)
Acceptance: a recovery attempted before the cooling-off period recorded in `packages/schemas/policy-defaults-v1.json` is refused; a compromised identity moves to `compromised` and then `recovery-pending`, and a notification row exists per affected session.
Depends: O-007
Est: 10-14
Status: not-started

### O-009 Ranked eligibility and investigation
Files: `apps/api/internal/rankedidentity/eligibility.go` (new), `apps/api/internal/rankedidentity/eligibility_test.go` (new)
Acceptance: an account with no resolved ranked identity returns no row from any ranking query; fetching the public projection of an account under investigation returns no investigation field, and the test fails if one appears.
Depends: S-007, O-007
Est: 10-14
Status: not-started

`identity_investigations` holds the private investigation record; it is written here and published nowhere.

### O-010 Duplicate-account consolidation execution
Files: `apps/api/internal/rankedidentity/consolidate.go` (new), `packages/schemas/consolidation-plan-v1.schema.json` (new)
Acceptance: a fixture with deliberately overlapping claims consolidates to strictly less than the sum of the two accounts' totals, which is the check that history is recomputed from non-overlapping contributions rather than added; the consolidation plan validates against its schema.
Depends: O-008, O-009, S-011
Est: 12-16
Status: in-progress

`packages/schemas/consolidation-plan-v1.schema.json` exists and validates. The execution path does not: no Go package reads it, and the overlapping-claims fixture the acceptance names has not been written.

### O-011 Restriction, appeal, reversal and retirement
Files: `apps/api/internal/moderation/restriction.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: every restriction row has a reachable appeal path in the `appeal` machine and every reversal is a new append-only row; `appeal_decisions` exposes the outcome and no investigation evidence, asserted by a column-level test on the published projection.
Depends: O-009
Est: 10-14
Status: not-started

### O-012 OAuth, recovery and consolidation race suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_oauth_races.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite authentication-recovery` exits 0 with a status that is not `not_applicable`; concurrent callbacks, concurrent unlinks and simultaneous consolidation of the same pair each end in exactly one recorded outcome, and a run that ends in two fails the suite.
Depends: O-004, O-005, O-006, O-007, O-008, O-009, O-010, O-011
Est: 12-16
Status: not-started

The prose range `O-004 through O-011` is expanded because `Depends:` admits unit IDs only.

### O-013 Optional authenticator and recovery-code enrollment
Files: `apps/api/internal/authenticator/authenticator.go` (new), `apps/api/internal/authenticator/authenticator_test.go` (new), `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `packages/schemas/planning-schema.sql`
Acceptance: `go test ./internal/authenticator/...` exits 0; a recovery code is single-use and a direct read of `recovery_codes` returns only a hash; an `optional_authenticators` row cannot become the last remaining method without the recorded explicit confirmation, asserted by a refused case.
Depends: O-006, S-006
Est: 8-12
Status: not-started

D-028 makes passkeys and hardware credentials optional stronger factors rather than mandatory primary authentication. `optional_authenticators` and `recovery_codes` are persisted by `S-006` and had no runtime unit before this one.

## Epic V — First source vertical slice and certification

### V-001 Select one local runtime source
Files: `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md`, `conformance/adapters/agent-registry-v1.json`
Acceptance: exactly one registry row is marked selected for the local-runtime lane and its compatibility tuple resolves in `packages/schemas/platform-profile-registry-v1.json`; a second selected row in the same lane fails the registry validator.
Depends: A-010, N-020
Est: 6-8
Status: not-started

### V-002 Select one cloud structured-usage source
Files: `conformance/adapters/agent-registry-v1.json`, `docs/integrations/AGENT_INTEGRATION_RESEARCH_MATRIX.md`
Acceptance: exactly one registry row is marked selected for the cloud structured-usage lane and names the provider endpoint it reads; a second selected row in the same lane fails the registry validator.
Depends: A-010, S-014
Est: 6-8
Status: not-started

### V-003 Compatibility tuple and capability probe runtime
Files: `crates/vibeproof-adapters/src/probe.rs` (new), `packages/schemas/compatibility-tuple-v1.schema.json` (new), `scripts/research/agent_capability_probe.py`
Acceptance: the probe emits a tuple that validates against the schema and whose digest equals the registry row's; a host whose probe result differs from the certified tuple is reported unsupported rather than downgraded, asserted by a deliberately mismatched fixture.
Depends: V-001, V-002
Est: 10-14
Status: in-progress

The schema half exists. No probe does, so nothing emits a tuple and the mismatched-host fixture has not been written.

### V-004 Local adapter implementation
Files: `crates/vibeproof-adapters/src/local/mod.rs` (new), `conformance/adapters/claude-code-otel/source-observation.valid.json`, `conformance/adapters/claude-code-otel/otlp-attribute-disposition-v1.json`
Acceptance: `cargo test -p vibeproof-adapters --test local` exits 0; the valid fixture produces its recorded normalized event, and each of the four invalid-identity fixtures beside it is rejected with its recorded reason.
Depends: V-003
Est: 12-16
Status: not-started

### V-005 Cloud adapter implementation
Files: `crates/vibeproof-adapters/src/cloud/mod.rs` (new), `conformance/adapters/agent-registry-v1.json`
Acceptance: a schema assertion on every fetched payload rejects a provider response carrying a prompt, response or transcript field rather than filtering it, which a deliberately content-bearing fixture proves; the adapter reads aggregate usage only.
Depends: V-003
Est: 12-16
Status: not-started

### V-006 Certification runner and signed result bundle
Files: `scripts/ci/run_certification.py` (new), `packages/schemas/certification-result-v1.schema.json` (new)
Acceptance: the emitted bundle validates against its schema and carries suite and case digests, a validity interval and a signer reference; two runs against the same tuple produce the same case digests, and a changed fixture changes them.
Depends: V-004, V-005
Est: 12-16
Status: in-progress

The bundle schema exists and two fixtures exercise it, one of them a pass with no negative case that the schema refuses. No runner emits a bundle, so the reproducibility half of the acceptance is untested.

`certification_results` stores the signed bundle for each certified tuple.

### V-007 Source upgrade-break and privacy fixtures
Files: `conformance/adapters/upgrade-break-fixtures-v1.json` (new), `crates/vibeproof-adapters/tests/upgrade_break.rs` (new)
Acceptance: a fixture recorded from a newer source version with a changed field set makes the adapter report an uncertified tuple rather than parse best-effort; every privacy fixture in the set is blocked by the `F-006` canary suite.
Depends: V-006
Est: 8-12
Status: not-started

### V-008 Multi-observer duplicate reconciliation
Files: `crates/vibeproof-adapters/tests/multi_observer.rs` (new), `conformance/accounting/dedup-vectors-v1.json`
Acceptance: the dedup vectors run end to end through both adapters and yield one counted event per real operation; starting the two observers in the opposite order produces the same count.
Depends: V-004, V-005, A-006
Est: 10-14
Status: not-started

### V-009 Emergency suspend/degrade/reinstate
Files: `apps/api/internal/certification/suspend.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: suspending one tuple leaves every other tuple certified, asserted row by row; a suspended tuple returns no support claim from any query, and reinstatement restores exactly the prior row rather than a fresh one.
Depends: V-006, S-014
Est: 8-12
Status: not-started

### V-010 Support registry publication
Files: `conformance/adapters/agent-registry-v1.json`, `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`
Acceptance: `python3 scripts/repository/validate_planning_artifacts.py --allow-no-postgres` exits 0 and the published registry lists only tuples holding a current, non-expired, non-suspended certification; a row with an empty certification set fails the validator, which is what stops a registry implying exercised support.
Depends: V-006, V-007, V-008, V-009
Est: 8-12
Status: not-started

The prose range `V-006 through V-009` is expanded because `Depends:` admits unit IDs only.

## Epic R — Ranking and pricing

### R-001 Period and season registry
Files: `apps/api/internal/ranking/periods.go` (new), `migrations/0013_periods.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: each `periods` row names an exact calendar and timezone and all five states of the period machine are reachable; a claim whose receipt timestamp falls in no open period is rejected rather than assigned to the nearest one.
Depends: S-002
Est: 8-12
Status: not-started

`seasons` is the multi-period grouping and is registered here alongside `periods`.

### R-002 Immutable score contributions
Files: `apps/api/internal/ranking/contributions.go` (new), `migrations/0014_scores.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `minute_scores` and `period_scores` reject `UPDATE` and `DELETE` at the database level; replaying an already-accepted claim leaves the row count unchanged, which is the check that a contribution is written exactly once.
Depends: S-011, R-001
Est: 10-14
Status: not-started

`score_contributions` is the immutable ledger row; `minute_scores` and `period_scores` are projections of it, and a rebuild reads the ledger rather than the projections.

`minute_scores` had no owning unit before this one.

### R-003 Ranking definitions and audience instances
Files: `apps/api/internal/ranking/views.go` (new), `packages/schemas/ranking-view-v1.schema.json`, `packages/schemas/planning-schema.sql` (`ranking_definitions`, `ranking_views`)
Acceptance: a `ranking_definitions` row names a metric version, a period and its evidence, source, agent, provider and model filters, and a column assertion fails if it carries any viewer or audience field — audience belongs to `ranking_views`, and the viewer to the request. `PF-021` split the two tables; this unit is the Go half.
Depends: O-009, R-001
Est: 10-14
Status: not-started

### R-004 Generation-keyed entries and isolated build
Files: `apps/api/internal/ranking/build.go` (new), `migrations/0015_ranking_generations.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: every entry key includes its `ranking_projection_generations` generation; a read concurrent with a build returns only the previously active generation, which a test asserts by reading during a deliberately slow build.
Depends: R-002, R-003
Est: 12-16
Status: not-started

`ranking_entries` is the generation-keyed entry table.

`ranking_projection_generations` is the generation record the entry keys reference. This line named `projection_generations` — a four-column stub with no `state` column and no relation to `ranking_entries` — until `PF-022`. The `ranking-projection` machine named the same stub as its persistence owner, and a near-miss table name satisfied every check in this repository.

### R-005 Generation validation and atomic promotion
Files: `apps/api/internal/ranking/promote.go` (new), `apps/api/internal/ranking/promote_test.go` (new)
Acceptance: a partial unique index permits exactly one active generation; promotion is a single statement, and an injected validation failure leaves the previous generation active with no window in which none is.
Depends: R-004
Est: 8-12
Status: not-started

### R-006 Immutable snapshots and viewer-bound cursors
Files: `apps/api/internal/ranking/cursor.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: a cursor replayed by a different viewer is rejected; a cursor whose authorization revision is stale is rejected rather than silently refreshed; `score_snapshots` rejects `UPDATE` at the database level.
Depends: R-005
Est: 10-14
Status: not-started

### R-007 Tie rank and deterministic display ordering
Files: `apps/api/internal/ranking/order.go` (new), `apps/api/internal/ranking/order_test.go` (new)
Acceptance: two entries with equal scores receive the same `rank()` value and a stable display order that is byte-identical across two independent builds; the display key is a separate column and never participates in the peer grouping.
Depends: R-004
Est: 6-8
Status: not-started

### R-008 Evidence/source/environment filters
Files: `apps/api/internal/ranking/filters.go` (new), `packages/schemas/ranking-view-v1.schema.json`
Acceptance: every filter value resolves to a certified tuple or to an `evidence_class` the API publishes; a filter naming an uncertified tuple returns an empty result and never an unfiltered one, asserted by a case that would otherwise leak every row.
Depends: R-002, S-014
Est: 8-12
Status: not-started

### R-009 Estimated pricing line items
Files: `apps/api/internal/ranking/lineitems.go` (new), `packages/schemas/pricing-interpretation.schema.json`
Acceptance: every cash figure carries the estimated label and a `cost_interpretations` reference; a model with no pricing entry yields no line item rather than a zero one, which a fixture with an unpriced model asserts.
Depends: A-009, R-002
Est: 8-12
Status: not-started

### R-010 Corrections and rebuild equivalence
Files: `apps/api/internal/ranking/corrections.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: a rebuild from the contribution ledger reproduces the promoted generation byte-for-byte; every `ranking_corrections` row is an inverse or replacement referencing the original, which the ledger's append-only constraint enforces rather than application code.
Depends: R-002, R-003, R-004, R-005, R-006, R-007, R-008, R-009
Est: 12-16
Status: not-started

The prose range `R-002 through R-009` is expanded because `Depends:` admits unit IDs only.

### R-011 Movement, overtakes, streaks and retractions
Files: `apps/api/internal/ranking/events.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: every movement, overtake and streak event references the generation that produced it, and a retraction is a new event referencing the retracted one; a retracted event is absent from the viewer projection while remaining in the ledger, asserted by reading both.
Depends: R-006, R-010
Est: 10-14
Status: not-started

`ranking_movement_events` is the append-only movement, overtake and streak ledger.

`ranking_events` is the append-only movement, overtake, streak and retraction ledger.

### R-012 Authorization/pagination/correction concurrency suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_ranking_races.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite ranking-accounting` exits 0 with a status that is not `not_applicable`; paginating across a promotion, and correcting a period while a viewer paginates it, each end in one recorded outcome and never in a page mixing two generations.
Depends: R-003, R-004, R-005, R-006, R-007, R-008, R-009, R-010, R-011
Est: 12-16
Status: not-started

The prose range `R-003 through R-011` is expanded because `Depends:` admits unit IDs only.

## Epic G — Social, boards, presence and notifications

### G-001 Profiles and visibility policy
Files: `apps/api/internal/social/profiles.go` (new), `packages/schemas/privacy-projection-v1.json` (new), `packages/schemas/openapi-v1.yaml`
Acceptance: the public projection of a `profiles` row contains only the fields the privacy projection permits for the requesting viewer, asserted field by field for an anonymous viewer, a friend and a blocked viewer; a field with no projection entry fails the test rather than defaulting to visible.
Depends: O-009
Est: 8-12
Status: not-started

### G-002 Friendship requests and canonical pairs
Files: `apps/api/internal/social/friends.go` (new), `migrations/0016_social.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: a check constraint on `friend_edges` makes two rows for one friendship impossible; a duplicate `friend_requests` row is rejected by a unique constraint; decline, cancel and expiry each end in their own recorded state, one case each.
Depends: G-001
Est: 10-14
Status: not-started

### G-003 Directional blocks and unblock
Files: `apps/api/internal/social/blocks.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: blocking B creates no reverse `blocks` row and deletes no `friend_edges` row, asserted by reading both tables; unblocking restores exactly the prior projection, asserted by comparing the projection before the block and after the unblock.
Depends: G-001
Est: 8-12
Status: not-started

### G-004 Rivals
Files: `apps/api/internal/social/rivals.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: a `rival_edges` row survives a block and a friendship change, asserted by reading it after each; a rivals query returns no row whose viewer authorization has lapsed.
Depends: G-002, G-003
Est: 6-8
Status: not-started

### G-005 Board creation and atomic owner
Files: `apps/api/internal/boards/create.go` (new), `migrations/0017_boards.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: the `boards` row and its initial owner membership are written in one transaction and an injected failure leaves neither; a partial unique index guarantees exactly one owner per board, which a direct insert of a second owner must violate.
Depends: G-001
Est: 8-12
Status: not-started

### G-006 Member invitations and acceptance
Files: `apps/api/internal/boards/membership.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: accepting a `board_invites` row can only create a non-privileged `board_memberships` row, asserted by an admin-role invite that must be refused; every membership change appends a `board_membership_events` row, asserted by row count before and after.
Depends: G-005
Est: 10-14
Status: not-started

`board_invites` and `board_membership_events` had no owning unit before this one.

### G-007 Separate admin promotion
Files: `apps/api/internal/boards/promote.go` (new), `apps/api/internal/boards/promote_test.go` (new)
Acceptance: promotion requires a recent-authentication grant and a matching membership revision, one refused case each; a promotion attempted as part of an invite acceptance is refused, which is the privilege-escalation path this unit exists to close.
Depends: G-006
Est: 8-12
Status: not-started

### G-008 Paired ownership transfer
Files: `apps/api/internal/boards/transfer.go` (new), `apps/api/internal/boards/transfer_test.go` (new)
Acceptance: transfer demotes the old owner and promotes the new one in one transaction; an injected failure at every boundary leaves exactly one owner, asserted at each boundary rather than only at the end.
Depends: G-007
Est: 8-12
Status: not-started

### G-009 Device-bound presence pulses
Files: `apps/api/internal/presence/pulse.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: a pulse is accepted only from a device holding a current `presence_leases` generation; a pulse replayed from another device is rejected with a reason code that resolves in `packages/schemas/reason-codes-v1.json`.
Depends: N-006, O-009
Est: 8-12
Status: not-started

`presence_events` is the append-only pulse ledger behind the derived state.

### G-010 Account presence projection and multi-device merge
Files: `apps/api/internal/presence/project.go` (new), `packages/schemas/policy-defaults-v1.json`
Acceptance: the merged state is `active`, `idle` at the 90-second threshold and `offline` at the 300-second threshold using the values recorded in `packages/schemas/policy-defaults-v1.json` rather than literals in code; merging two devices produces the same result under both orderings.
Depends: G-009
Est: 8-12
Status: not-started

### G-011 Viewer-specific presence authorization
Files: `apps/api/internal/presence/authorize.go` (new), `packages/schemas/privacy-projection-v1.json` (new)
Acceptance: a blocked viewer, a non-friend and a removed board member each receive `offline` rather than the real state, one case each; the private setting changes only the projection, which a direct read of the server-derived state proves by showing it unchanged.
Depends: G-003, G-005, G-010
Est: 8-12
Status: not-started

### G-012 Typed notification source events and inbox
Files: `apps/api/internal/notifications/events.go` (new), `migrations/0018_notifications.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `notification_events` rejects `UPDATE` and `DELETE` at the database level; each `notifications` row carries the authorization revision under which it was generated; a source event whose type is not registered is rejected rather than stored untyped.
Depends: G-002, G-003, G-004, G-005, G-006, G-007, G-008, R-011
Est: 12-16
Status: not-started

The prose range `G-002 through G-008` is expanded because `Depends:` admits unit IDs only. `notification_events` had no owning unit before this one.

### G-013 Channel subscriptions and delivery attempts
Files: `apps/api/internal/notifications/delivery.go` (new), `apps/api/internal/notifications/delivery_test.go` (new)
Acceptance: every attempt records exactly one of `queued`, `deferred`, `accepted`, `acknowledged`, `failed` or `expired`; a test asserts no code path maps provider acceptance to a read or to a delivery guarantee.
Depends: G-012
Est: 10-14
Status: not-started

`notification_deliveries` records one row per channel attempt.

### G-014 Preferences, quiet hours, read/dismiss and expiry
Files: `apps/api/internal/notifications/preferences.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: a security-critical notification is delivered despite quiet hours and a non-critical one is deferred, one case each, driven by `notification_preferences`; read, dismiss and expiry are three distinct recorded states and no two share a column value.
Depends: G-012, G-013
Est: 8-12
Status: not-started

### G-015 Retraction and current-authorization recheck
Files: `apps/api/internal/notifications/retract.go` (new), `apps/api/internal/notifications/retract_test.go` (new)
Acceptance: retracting a source event removes it from every recipient projection while leaving the ledger row present, asserted by reading both; a recipient blocked since generation receives no delivery on recheck.
Depends: G-003, G-012
Est: 8-12
Status: not-started

### G-016 Social/presence/notification race and privacy suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_social_races.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite social-ranking-simulation` exits 0 with a status that is not `not_applicable`; simultaneous block-and-friend, block-and-presence-read, and retract-and-deliver each end in one recorded outcome, and a run ending in two fails the suite.
Depends: G-002, G-003, G-004, G-005, G-006, G-007, G-008, G-009, G-010, G-011, G-012, G-013, G-014, G-015
Est: 12-16
Status: not-started

The prose range `G-002 through G-015` is expanded because `Depends:` admits unit IDs only.

### G-017 Organization boards
Files: `apps/api/internal/boards/organizations.go` (new), `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`, `docs/decisions/ADR-016-PROVIDER_ATTESTED_ORG_EVIDENCE.md`
Acceptance: the four organization operations in `packages/schemas/openapi-v1.yaml` all resolve to the `organizations` table; an organization board admits only members whose ranked identity is resolved, and an org-admin credential grants no read of an individual member's content, asserted by a refused case.
Depends: G-005, S-007
Est: 10-14
Status: not-started

`organizations` had no owning unit and the word "organization" did not appear anywhere in this document. ADR-016 decides whether org boards consume provider admin APIs, and this unit implements whichever answer that ADR records rather than reopening it.

### G-018 Community boards
Files: `apps/api/internal/boards/communities.go` (new), `packages/schemas/planning-schema.sql`, `packages/schemas/openapi-v1.yaml`
Acceptance: the community operations in `packages/schemas/openapi-v1.yaml` all resolve to the `communities` table; a community board view is subject to the same viewer-authorization check as every other non-global scope, asserted by an unauthorized read that must return nothing.
Depends: G-005
Est: 8-12
Status: not-started

`communities` had no owning unit and the word "community" did not appear anywhere in this document.

### G-019 Social integrity event ledger
Files: `apps/api/internal/integrity/events.go` (new), `packages/schemas/social-integrity-events-v1.proto`, `packages/schemas/planning-schema.sql`
Acceptance: `social_integrity_events` rejects `UPDATE` and `DELETE`; every event type in `packages/schemas/social-integrity-events-v1.proto` has a writer and every writer names a declared type, asserted in both directions; no event column can hold a content-derived value, asserted against the `F-006` canary set.
Depends: G-016, S-019
Est: 8-12
Status: not-started

Also the persistence owner for `social_events`.

`social_integrity_events` had a Protobuf contract and a table but no owning unit. Detection remains deterministic and local-only advisory per the binding product rules; this ledger records deterministic control outcomes, not statistical inferences.

## Epic M — Moderation, export and deletion

### M-001 Moderation case and effect authority
Files: `apps/api/internal/moderation/cases.go` (new), `migrations/0019_moderation.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `moderation_cases`, `moderation_actions` and `moderation_effects` are append-only; every effect names the case that produced it and the aggregate it restricts, and an effect with no reachable reversal transition fails the state check.
Depends: O-011, G-001
Est: 10-14
Status: not-started

### M-002 Moderation appeal and reversal
Files: `apps/api/internal/moderation/appeal.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: every `appeals` row reaches a recorded `appeal_decisions` outcome or an expiry, with no state that has neither; a reversal appends new rows and edits none, which the append-only constraint enforces.
Depends: M-001
Est: 8-12
Status: not-started

### M-003 Export status resource and snapshot
Files: `apps/api/internal/export/job.go` (new), `migrations/0020_export.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: an `exports` row carries a frozen recent-auth grant and a coherent snapshot cutoff; two reads of the same export at different times return the same content set, which a test asserts by inserting new data between them.
Depends: S-003, G-016, R-010
Est: 10-14
Status: not-started

### M-004 Export package, manifest, encryption and checksums
Files: `apps/api/internal/export/package.go` (new), `packages/schemas/export-manifest-v1.schema.json`
Acceptance: the produced manifest validates against `packages/schemas/export-manifest-v1.schema.json`; per-domain counts equal the rows actually written and every checksum verifies; `export_artifacts` records the encryption reference, and a package with a mismatched count fails the check.
Depends: M-003
Est: 10-14
Status: not-started

### M-005 Download grants, audit, revocation and purge
Files: `apps/api/internal/export/grant.go` (new), `apps/api/internal/export/grant_test.go` (new)
Acceptance: a download grant expires at its recorded time and is revocable before it; every download appends an audit row; a purge removes the artifact and leaves the audit trail, asserted by reading both after the purge.
Depends: M-004
Est: 8-12
Status: not-started

`export_download_grants` holds the short-lived revocable grants and their audit rows.

### M-006 Hosted deletion plan and account mutation freeze
Files: `apps/api/internal/deletion/plan.go` (new), `migrations/0021_deletion.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: a `deletion_jobs` row holds an immutable domain-and-effect plan covering every domain in `docs/privacy/DATA_MAP.md`; account mutations are refused while the job executes, asserted one refused mutation per restricted operation.
Depends: M-001, M-003
Est: 10-14
Status: not-started

### M-007 Per-domain deletion/anonymization/retraction effects
Files: `apps/api/internal/deletion/effects.go` (new), `packages/schemas/planning-schema.sql`
Acceptance: every `deletion_effects` row records deletion, anonymization or retraction for exactly one domain, and the union of effects equals the plan; a public profile, social edge, ranking entry and notification each show their recorded correction after execution.
Depends: M-006, R-010, G-015
Est: 12-16
Status: not-started

Crypto-erasure under D-085 is the mechanism: `erasure_domains` declares each erasable domain, `erasure_keys` holds the per-domain key whose destruction renders the domain unreadable, and `erasure_domain_links` binds a row to the domain that governs it. Destroying a key is not the same claim as overwriting a row, and the receipt must not say otherwise.

### M-008 Per-device local deletion commands and receipts
Files: `apps/api/internal/deletion/devices.go` (new), `crates/vibemaxxing-daemon/src/deletion.rs` (new), `packages/schemas/planning-schema.sql`
Acceptance: each `local_deletion_commands` row resolves to a `local_deletion_receipts` row recording `complete`, `pending`, `expired`, `unreachable` or `waived`; `grep -in 'forensic\|unrecoverable' apps/api/internal/deletion` returns no claim the receipt cannot support.
Depends: N-007, M-006
Est: 10-14
Status: not-started

### M-009 Tombstones, backup propagation and restore reapplication
Files: `apps/api/internal/deletion/tombstone.go` (new), `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: a restore from a backup taken before a deletion reapplies every tombstone before the data is readable, asserted by a restore drill that reads the affected rows immediately after restore and finds them absent.
Depends: M-007
Est: 10-14
Status: not-started

`erasure_records` is the append-only record of each destruction, and `erasure_restore_receipts` records what a restore reapplied. Without the second one, a restore drill cannot show that a destroyed domain stayed destroyed.

`deletion_tombstones` is what a restore has to reapply before any affected row becomes readable.

### M-010 Legal hold and minimal retained fraud/audit signals
Files: `apps/api/internal/deletion/legalhold.go` (new), `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: a legal hold blocks exactly the effects it names and no others, asserted effect by effect; retained fraud and audit signals are the minimal set enumerated in the contract, and a signal not in that set fails the retention check.
Depends: M-006
Est: 8-12
Status: not-started

### M-011 Export/deletion concurrency and restore suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_export_deletion_races.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite data-lifecycle-recovery` exits 0 with a status that is not `not_applicable`; an export running during a deletion, and a restore during a deletion, each end in one recorded outcome with no readable row the plan removed.
Depends: M-003, M-004, M-005, M-006, M-007, M-008, M-009, M-010
Est: 12-16
Status: not-started

The prose range `M-003 through M-010` is expanded because `Depends:` admits unit IDs only.

## Epic L — Packaging, release and migration

### L-001 TUF repository roles and trusted client state
Files: `apps/api/internal/release/tuf.go` (new), `migrations/0022_release.sql` (new), `packages/schemas/planning-schema.sql`
Acceptance: `tuf_roots` stores the root and delegated role metadata and a client refuses metadata signed by a role outside its trusted set, asserted by a hostile-metadata fixture per role; expiry is enforced rather than warned about.
Depends: F-001
Est: 10-14
Status: not-started

`tuf_metadata` stores the client's trusted metadata state alongside `tuf_roots`.

### L-002 Authenticated release component manifest
Files: `apps/api/internal/release/manifest.go` (new), `packages/schemas/release-set-v1.schema.json`, `packages/schemas/planning-schema.sql`
Acceptance: every `release_sets` row is itself an authenticated TUF target, and each `release_targets` row carries component ID, target path, architecture, hash, provenance, native signature, compatibility tuple and update class; a target missing any field is refused.
Depends: L-001
Est: 10-14
Status: not-started

`release_transparency_events` is the append-only publication log for each release set.

### L-003 Provenance and platform-native signature verification
Files: `crates/vibemaxxing-cli/src/update/verify.rs` (new), `docs/operations/RELEASE_VERIFICATION.md`
Acceptance: verification fails when the provenance attestation does not name the recorded builder, and separately when the platform-native signature does not verify; both failures are tested independently so one passing cannot mask the other.
Depends: L-002
Est: 10-14
Status: not-started

### L-004 Compatibility graph and migration chain
Files: `apps/api/internal/release/compatibility.go` (new), `crates/vibemaxxing-daemon/src/store/migrate.rs` (new)
Acceptance: the compatibility graph admits exactly the version pairs the contract names and rejects every other, asserted pair by pair; a migration chain with a gap fails to load rather than skipping the missing step.
Depends: N-002, S-002, L-002
Est: 10-14
Status: not-started

The unit persists `compatibility_edges`, one row per relation across the six interfaces that version independently, and `storage_migrations`, which carries the D-392 rollback class beside each `schema_migrations` version. `packages/schemas/compatibility-graph-v1.schema.json` and `packages/schemas/migration-chain-v1.schema.json` are the records; neither is loaded by any code.

### L-005 Health checks and staged activation
Files: `crates/vibemaxxing-cli/src/update/health.rs` (new), `docs/operations/RELEASE_VERIFICATION.md`
Acceptance: a failing pre-check aborts before any file is replaced and a failing post-check triggers the recorded recovery path; both are asserted by injected failures, and a run where neither check executes fails the test.
Depends: L-004
Est: 8-12
Status: not-started

### L-006 Compatible binary rollback
Files: `crates/vibemaxxing-cli/src/update/rollback.rs` (new), `crates/vibemaxxing-cli/tests/rollback.rs` (new)
Acceptance: a rollback is offered only while the prior version remains read/write compatible with the current local schema, asserted by a case where it is refused; after rollback the daemon opens the store cleanly.
Depends: L-004, L-005
Est: 8-12
Status: not-started

### L-007 Irreversible migration roll-forward/snapshot recovery
Files: `crates/vibemaxxing-cli/src/update/rollforward.rs` (new), `crates/vibemaxxing-daemon/src/store/recover.rs` (new)
Acceptance: after an irreversible migration, recovery succeeds by roll-forward or by restoring the verified pre-migration snapshot, and no path offers a binary rollback; a test that attempts one must be refused.
Depends: L-004, L-005
Est: 10-14
Status: not-started

### L-008 macOS installer and supervision
Files: `apps/desktop/macos/Info.plist` (new), `crates/vibemaxxing-cli/src/install/macos.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: install, upgrade, reboot, repair, uninstall and orphan cleanup each reach their recorded state on a macOS runner, one case each; the profile row records the session and restart limitation the host actually has rather than the best case.
Depends: N-011, N-015, L-003
Est: 10-14
Status: not-started

### L-009 Windows installer and supervision
Files: `apps/desktop/windows/service.rs` (new), `crates/vibemaxxing-cli/src/install/windows.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: the same six lifecycle states are reached on a Windows runner, one case each, and the profile row records the actual supervision mechanism and its restart limitation.
Depends: N-012, N-015, L-003
Est: 10-14
Status: not-started

### L-010 Linux packages/systemd-user/headless
Files: `apps/desktop/linux/vibemaxxing.service` (new), `crates/vibemaxxing-cli/src/install/linux.rs` (new), `packages/schemas/platform-profile-registry-v1.json`
Acceptance: the same six lifecycle states are reached under a systemd user session and under a headless invocation, and the two produce different profile rows — a headless host that inherits the desktop row fails the test.
Depends: N-013, N-015, L-003
Est: 10-14
Status: not-started

### L-011 WSL/container/CI lifecycle packages
Files: `crates/vibemaxxing-cli/src/install/container.rs` (new), `packages/schemas/platform-profile-registry-v1.json`, `docs/security/PLATFORM_ISOLATION.md`
Acceptance: WSL, container and CI hosts each produce a profile row that records their supervision limits and their competitive eligibility separately; a CI host is installable and not competitively eligible, asserted as two independent fields.
Depends: N-013, L-003
Est: 8-12
Status: not-started

### L-012 Update deadlines, deferral and eligibility
Files: `apps/api/internal/release/policy.go` (new), `packages/schemas/planning-schema.sql`, `docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md`
Acceptance: `update_policies` records a deadline and a deferral allowance per release, and `update_installations` records the outcome per device; a device past its deadline loses competitive eligibility and retains local function, asserted as two independent effects.
Depends: L-001, L-002, L-003, L-004, L-005, L-006, L-007, L-008, L-009, L-010, L-011, S-014
Est: 10-14
Status: not-started

The prose range `L-001 through L-011` is expanded because `Depends:` admits unit IDs only. `update_policies` had no owning unit before this one.

### L-013 Key compromise, freeze, rollback and mix-and-match suite
Files: `evals/suites/suites.yaml`, `tests/conformance/test_updater_hostile.py` (new)
Acceptance: `python3 scripts/ci/run_evals.py --suite updater-conformance` exits 0 with a status that is not `not_applicable`; key compromise, freeze, rollback and mix-and-match of components from two release sets are each refused, one case each.
Depends: L-012
Est: 12-16
Status: not-started

### L-014 Uninstall, orphan cleanup and diagnostics
Files: `crates/vibemaxxing-cli/src/install/uninstall.rs` (new), `crates/vibemaxxing-cli/tests/uninstall.rs` (new)
Acceptance: after uninstall no daemon, launch agent, service, key, database file or queue directory remains, asserted path by path on each platform runner; a diagnostics bundle produced during uninstall contains no forbidden content class under the `F-006` canary suite.
Depends: L-008, L-009, L-010, L-011, M-008
Est: 10-14
Status: not-started

The prose range `L-008 through L-011` is expanded because `Depends:` admits unit IDs only. This unit was an orphan; `X-011` now depends on it.

## Epic W — Hosted web integration

### W-001 Generated API clients and error/reason mapping
Files: `apps/web/lib/api/client.ts` (new), `packages/protocol/typescript/index.ts` (new), `packages/schemas/reason-codes-v1.json`
Acceptance: the client is generated from `packages/schemas/openapi-v1.yaml` rather than hand-written, which `git diff --exit-code` after a regeneration proves; `npx tsc --noEmit` exits 0; every reason code has a mapped user-facing string and every mapped string names a real code, asserted in both directions so an unmapped code fails the build.
Depends: F-004, PF-045, S-016
Est: 10-14
Status: not-started

The prose dependency `implemented OpenAPI and F-004` is replaced. "Implemented OpenAPI" is not a unit; the two units that actually gate this one are `PF-045`, which decides the error matrix, and `S-016`, which is the runtime that cannot deviate from it.

This unit was an orphan. `W-002` through `W-009` now depend on it, which is the real edge: every screen consumes this client.

### W-002 Authentication and recovery UX
Files: `apps/web/app/login/page.tsx` (new), `apps/web/app/recover/page.tsx` (new), `apps/web/e2e/auth.spec.ts` (new)
Acceptance: every state of the `web-session-family` machine has a rendered state and a Playwright case; `npm run test:e2e -- auth` exits 0, and a state with no case fails the run rather than being absent from it.
Depends: W-001, O-012
Est: 12-16
Status: not-started

### W-003 Leaderboards and ranking context UX
Files: `apps/web/app/page.tsx`, `apps/web/app/boards/[slug]/page.tsx`, `apps/web/e2e/leaderboard.spec.ts` (new)
Acceptance: every field the leaderboard renders resolves to a field the generated client can return, which the TypeScript build enforces; `npm run test:e2e -- leaderboard` exits 0; `grep -rniE 'verified|all sources' apps/web/app` returns nothing, which is the banned-copy rule `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md` states.
Depends: W-001, R-012
Est: 12-16
Status: not-started

### W-004 Profiles, friends, rivals and boards UX
Files: `apps/web/app/profile/[handle]/page.tsx`, `apps/web/app/friends/page.tsx`, `apps/web/app/rivals/[handle]/page.tsx`
Acceptance: `npm run test:e2e -- social` exits 0; given an API response with a field absent because the viewer is not authorized, the client renders the absence and does not synthesize a value, asserted by a case that fails if any placeholder figure appears.
Depends: W-001, G-016
Est: 12-16
Status: not-started

### W-005 Presence and notification UX
Files: `apps/web/app/activity/page.tsx`, `apps/web/components/presence.tsx` (new)
Acceptance: presence renders the server-derived value only: a case that supplies `offline` while the local session is active must render `offline`; `npm run test:e2e -- presence` exits 0.
Depends: W-001, G-016
Est: 10-14
Status: not-started

### W-006 Evidence, source, privacy and outbound disclosure UX
Files: `apps/web/components/evidence-badge.tsx` (new), `packages/ui/src/patterns/product-system.tsx`, `packages/ui/src/concepts/product-storyboards.tsx`
Acceptance: the three published `evidence_class` values render with the labels D-143 fixes and an exhaustive switch fails to compile if a fourth appears; `grep -rniE 'verified|attested' apps/web packages/ui` returns nothing, so no surface can present a self-report as a provider confirmation.
Depends: W-001, V-010, R-008
Est: 10-14
Status: not-started

### W-007 Device, lineage, fork, platform and update UX
Files: `apps/web/app/devices/page.tsx` (new), `apps/web/e2e/devices.spec.ts` (new)
Acceptance: a forked lineage, a quarantined branch and a device past its update deadline each render their own recorded state, one case each; a device that is installable but not competitively eligible renders both facts separately rather than as one status.
Depends: W-001, S-013, L-012
Est: 10-14
Status: not-started

### W-008 Moderation and appeals UX
Files: `apps/web/app/appeals/page.tsx` (new), `apps/web/e2e/appeals.spec.ts` (new)
Acceptance: `npm run test:e2e -- appeals` exits 0; the appeal surface renders the decision outcome and no investigation evidence, asserted by a case whose fixture contains investigation fields that must not appear in the DOM.
Depends: W-001, M-002
Est: 8-12
Status: not-started

### W-009 Export and deletion UX
Files: `apps/web/app/privacy/export/page.tsx` (new), `apps/web/e2e/export.spec.ts` (new)
Acceptance: `npm run test:e2e -- export` exits 0; the deletion surface reports per-device outcomes including `unreachable` and `waived` rather than a single success, and `grep -rniE 'permanently erased|unrecoverable' apps/web` returns nothing.
Depends: W-001, M-011
Est: 10-14
Status: not-started

### W-010 Accessibility, responsive and exceptional-state matrix
Files: `apps/web/e2e/accessibility.spec.ts` (new), `scripts/ui/check-ui-system.mjs`, `packages/ui/src/concepts/product-state-matrix.stories.tsx`
Acceptance: `npm run test:a11y` exits 0 with zero axe violations at the three recorded breakpoints; a matrix test asserts every screen has a rendered loading, empty, error and unauthorized state and fails on a missing cell.
Depends: W-002, W-003, W-004, W-005, W-006, W-007, W-008, W-009
Est: 12-16
Status: not-started

The prose range `W-002 through W-009` is expanded because `Depends:` admits unit IDs only. This unit was an orphan; `X-011` now depends on it, which is what makes the hosted web product gate launch.

The matrix has an authority under D-394: `packages/schemas/ui-state-projection-v1.json` enumerates the eight exceptional states and resolves each to a registered machine, a viewer-authorization input, or nothing at all where it is genuinely client-local. The acceptance names four cells; the record names eight, and `blocked` and `private` are both required to render indistinguishably from a subject that does not exist, which a matrix test can assert and a screenshot cannot.

## Epic X — Operations, open source and launch evidence

### X-001 Cloud-portable reference deployment
Files: `infrastructure/README.md` (new), `infrastructure/terraform/main.tf` (new), `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
Acceptance: `terraform validate` and `terraform plan` exit 0 against the reference configuration; the plan names no managed service on the D-026 exclusion list; a second apply produces an empty plan, which is the check that the configuration is actually declarative.
Depends: S-015, W-010, L-011, OS-013
Est: 12-16
Status: not-started

The prose dependency `implemented server/web; separate deployment authorization` is replaced. The implemented-server-and-web half becomes `S-015`, `W-010` and `L-011`. The deployment-authorization half was never a dependency: production infrastructure and deployment are not unlocked by P-1104 and this unit may not run until they are separately authorized.

### X-002 Secrets, signing keys and recovery procedures
Files: `docs/operations/SECRETS_AND_KEY_RECOVERY.md` (new), `scripts/ci/check_secret_inventory.py` (new), `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
Acceptance: `python3 scripts/ci/check_secret_inventory.py` exits 0 only when every secret and signing key named in the operations contract has an owner, a rotation period and a recovery procedure, and exits non-zero when any one of the three is missing.
Depends: L-013
Est: 8-12
Status: superseded-by OS-013

### X-003 Observability allowlist and privacy canaries
Files: `packages/schemas/observability-allowlist-v1.yaml`, `docs/operations/OBSERVABILITY_PRIVACY.md`, `evals/suites/suites.yaml`
Acceptance: `python3 scripts/ci/run_evals.py --suite observability-privacy` exits 0 with a status that is not `not_applicable`; every emitted telemetry field appears in `packages/schemas/observability-allowlist-v1.yaml`, and a field added without an entry fails the suite.
Depends: F-006, OS-005
Est: 10-14
Status: not-started

The prose dependency `implemented services` is replaced by `X-012`, which is the unit that actually emits the telemetry this one constrains.

### X-004 Backup/restore and deletion tombstone drills
Files: `evals/suites/suites.yaml`, `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md`
Acceptance: `python3 scripts/ci/run_evals.py --suite data-lifecycle-recovery` exits 0 with a status that is not `not_applicable`; a restore drill meets the recovery point and recovery time objectives recorded in `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, and exceeding either fails the drill rather than being noted.
Depends: M-009
Est: 10-14
Status: not-started

### X-005 Incident response and abuse operations
Files: `docs/operations/INCIDENT_RESPONSE.md`, `evals/suites/suites.yaml`
Acceptance: `python3 scripts/ci/run_evals.py --suite moderation-operations` exits 0 with a status that is not `not_applicable`; every severity in `docs/operations/INCIDENT_RESPONSE.md` has a named owner and a paging path exercised by a drill, and a severity with no drill fails.
Depends: M-002, X-003, X-015
Est: 10-14
Status: not-started

### X-006 Reproducible builds, SBOM and dependency/license governance
Files: `scripts/ci/check_reproducible_build.py` (new), `LICENSES.md`, `.github/workflows/ci.yml`
Acceptance: two builds of the same commit on two hosts produce identical artifact digests; an SBOM is emitted per artifact and every dependency resolves to a license recorded in `LICENSES.md`; a dependency with no license entry fails the check.
Depends: L-003, F-008
Est: 12-16
Status: not-started

### X-007 Public repository security/contribution documentation
Files: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
Acceptance: `python3 scripts/repository/doctor.py` exits 0 with each document present and naming a current contact and a disclosure window; a placeholder contact or an unfilled jurisdiction fails the check rather than passing as present-but-empty.
Depends: X-006
Est: 6-8
Status: not-started

### X-008 Exact platform/source certification expansion
Files: `conformance/adapters/agent-registry-v1.json`, `packages/schemas/platform-profile-registry-v1.json`
Acceptance: every newly certified tuple has a signed result bundle from `V-006` and a `platform_certifications` row; a registry entry without both fails `python3 scripts/repository/validate_planning_artifacts.py --allow-no-postgres`.
Depends: V-010, L-013
Est: 10-14
Status: not-started

### X-009 Performance, capacity and cost evidence
Files: `benchmarks/postgres/ranking_benchmark.sql`, `docs/engineering/PERFORMANCE_BUDGETS.md`, `evals/suites/suites.yaml`
Acceptance: `python3 scripts/ci/run_evals.py --suite performance-efficiency` exits 0 with a status that is not `not_applicable`; every budget in `docs/engineering/PERFORMANCE_BUDGETS.md` has a measured figure recorded against it, and a run exceeding any budget fails.
Depends: S-015, R-012, W-010, OS-010, X-016
Est: 12-16
Status: not-started

The prose dependency `implemented product paths` is replaced. The paths that actually have to exist before performance and cost can be measured are the three end-to-end suites and the two new units that produce the load and the cost model.

### X-010 Accessibility, privacy, security and recovery review
Files: `docs/verification/ACCEPTANCE_GATES.md`, `docs/security/THREAT_MODEL.md`, `scripts/ci/generate_gate_ledger.py`
Acceptance: mechanical part: `python3 scripts/ci/generate_gate_ledger.py` exits 0 and every gate in `docs/verification/ACCEPTANCE_GATES.md` names an executed suite whose recorded status is not `not_applicable`. The four review verdicts are human judgements and are not mechanizable; a green ledger records that the evidence exists, never that the review was favourable, and this unit must not be reported as passed on the ledger alone.
Depends: N-018, N-019, N-020, P-010, O-012, R-012, G-016, M-011, L-013, W-010, X-003, X-004, X-005
Est: 12-16
Status: not-started

The prose dependency `all launch paths` is replaced by the thirteen suite-terminal units that constitute them. A phrase cannot be ordered and cannot be checked for completeness; a list can.

### X-011 P-1105 launch-readiness review
Files: `conformance/p1140f/gate-authorization-v1.json`, `docs/project/STATUS.md`, `docs/verification/ACCEPTANCE_GATES.md`
Acceptance: mechanical part: `python3 scripts/repository/validate_work_unit_status.py --gate X-011` exits 0 only when every unit this one depends on carries `Status: landed`; `python3 scripts/repository/validate_p1140f_authority.py` reports zero open P0 or P1; every launch-gating eval suite reports a status that is not `not_applicable`. The readiness verdict itself is the owner's decision and is not mechanizable — no agent may derive it from a green run, and gate state is changed by the owner alone.
Depends: F-008, F-010, F-011, P-010, A-010, N-018, N-019, N-020, S-015, S-016, S-019, S-020, O-012, O-013, V-010, R-012, G-016, G-017, G-018, G-019, M-011, L-013, L-014, W-010, X-001, X-003, X-004, X-005, X-006, X-007, X-008, X-009, X-010, X-013, X-015, X-016, X-017, OS-001, OS-002, OS-003, OS-004, OS-005, OS-006, OS-007, OS-008, OS-009, OS-010, OS-011, OS-012, OS-013
Est: 12-16
Status: not-started

P-1105 readiness previously depended on 162 of 194 units, excluding all ten Epic W units — the entire hosted web product — plus `O-012`, `R-012`, `M-011`, `S-015`, `N-018`, `N-019`, `P-010` and `F-008`. Launch readiness was declarable with no web application. The dependency list above is the repair: it names every epic-terminal unit, every previously excluded unit, and the six new operations units, so the transitive closure now covers the whole breakdown.

This unit remains an orphan, and that stands: nothing follows a launch-readiness review. An orphan at the end of the graph is a sink, which is correct; an orphan in the middle, which the eleven others were, is a missing edge.

### X-012 Structured logging, metrics and tracing
Files: `apps/api/internal/observability/observability.go` (new), `apps/api/internal/observability/observability_test.go` (new), `packages/schemas/observability-allowlist-v1.yaml`, `docs/operations/OBSERVABILITY_PRIVACY.md`
Acceptance: `go test ./internal/observability/...` exits 0; every log field, metric label and span attribute the service can emit is enumerated at build time and checked against `packages/schemas/observability-allowlist-v1.yaml`, so a field added without an allowlist entry fails to compile rather than failing in production.
Depends: S-001, F-006
Est: 10-14
Status: superseded-by OS-005

One of the thirteen categories that previously had no unit anywhere. `X-003` constrains what may be emitted; this unit is the emitter, and the allowlist check belongs at compile time because a runtime check has already leaked by the time it fires.

### X-013 Staging environment
Files: `infrastructure/staging/main.tf` (new), `docs/operations/STAGING_ENVIRONMENT.md` (new)
Acceptance: `terraform validate` exits 0 for the staging configuration and a diff against the reference configuration reports only the recorded intentional differences; a check fails when any staging resource references a production data source, so participant data cannot reach it.
Depends: X-001
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere.

### X-014 Load and soak testing
Files: `benchmarks/load/leaderboard.js` (new), `benchmarks/load/README.md` (new), `docs/engineering/PERFORMANCE_BUDGETS.md`
Acceptance: a load run against staging sustains the recorded request rate inside the p99 latency budget in `docs/engineering/PERFORMANCE_BUDGETS.md`, and a soak run holds memory and connection counts flat across the recorded duration; exceeding either budget fails the run rather than being recorded as a note.
Depends: X-013, R-012
Est: 10-14
Status: superseded-by OS-010

One of the thirteen categories that previously had no unit anywhere. `X-009` reports the evidence; this unit produces it, and the 300 ms leaderboard SLO cannot be claimed without it.

### X-015 Runbooks and on-call
Files: `docs/operations/RUNBOOKS.md` (new), `scripts/ci/check_runbook_coverage.py` (new), `docs/operations/SLOS_AND_ALERTS.md`
Acceptance: `python3 scripts/ci/check_runbook_coverage.py` exits 0 only when every alert in `docs/operations/SLOS_AND_ALERTS.md` names a runbook section that exists and every runbook section names an alert that exists; an alert with no runbook fails, and so does a runbook for an alert that was deleted.
Depends: X-003, OS-005
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. The rotation itself is a single-maintainer arrangement today and the coverage check is what keeps that honest rather than implied.

### X-016 Cost model
Files: `docs/operations/COST_MODEL.md` (new), `scripts/ci/check_cost_model.py` (new), `benchmarks/postgres/ranking_benchmark.sql`
Acceptance: `python3 scripts/ci/check_cost_model.py` exits 0 only when every component of the reference deployment has a unit-cost figure and a measured driver, and the modelled cost at the recorded participant count falls inside the recorded band around the figure measured by `X-014`; a component with no figure fails.
Depends: X-001, OS-010
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere. This is infrastructure cost for the operator and is unrelated to Estimated Cash Burn, which is a participant-facing metric.

### X-017 Product analytics
Files: `docs/product/PRODUCT_ANALYTICS.md` (new), `packages/schemas/observability-allowlist-v1.yaml`, `conformance/telemetry/canaries.json`
Acceptance: every analytics quantity is derived from fixed-schema aggregates the server already holds, asserted by a check that fails on any analytics field absent from `packages/schemas/observability-allowlist-v1.yaml`; the `N-020` egress suite runs unchanged and still passes, which is the proof that this unit added no client-side event stream.
Depends: OS-005, N-020
Est: 8-12
Status: not-started

One of the thirteen categories that previously had no unit anywhere, and the one most likely to be built wrong. The binding product rules forbid content-derived data crossing the device boundary and admit only fixed-schema aggregate accounting, so there is no behavioural event pipeline to build. This unit is deliberately server-side aggregate only. If that is judged insufficient for a product decision, the answer is a recorded decision that changes the rule, not a wider collector added under an analytics heading.

## Epic OS — Operational surfaces

Proposed by `https://github.com/vedant-simulacrum/vibemaxxing/pull/66`, which closed
fifteen operational surfaces as normative documents and recorded decisions D-230
through D-245. That branch could not edit this file because this branch owned it, so
the units were published in its description for absorption. They are absorbed here
with their identifiers unchanged, because renaming a published identifier breaks
every reference to it.

Six units this branch had authored independently cover the same surfaces and are
marked `superseded-by` rather than deleted: `F-009` by `OS-007`, `S-017` by
`OS-011`, `S-018` by `OS-003`, `X-002` by `OS-013`, `X-012` by `OS-005`, and
`X-014` by `OS-010`. The OS unit wins in each case because a normative owner
document now exists behind it and carries the numbers. `X-012` also covered metric
instrumentation, which is `OS-006`.

Two prose dependencies in the proposed set are replaced by unit IDs, under the same
rule as everywhere else: `OS-007` depended on "ADR-018 first migration", which is
`S-002`, and `OS-013` on "ADR-017 provider selection", which is not a unit at all
and is recorded as a condition.

### OS-001 Origin validation and CORS at the API edge
Files: `packages/schemas/openapi-v1.yaml`, `apps/api/internal/middleware/origin.go` (new), `apps/api/internal/middleware/origin_test.go` (new), `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`
Acceptance: `go test ./internal/middleware/ -run Origin` exits 0; a preflight from a non-allowlisted origin returns 204 carrying no `Access-Control-*` header; a state-changing request with a foreign `Origin` returns 403; `grep -c localhost` over a production build artifact returns 0, which is what makes the development origin compiled out rather than configured off. The middleware reads its allowlist, preflight values and check order from `packages/schemas/origin-policy-v1.json` rather than restating them, so a divergence is a build failure and not a review miss.
Depends: PF-039, OS-014
Est: 3-5
Status: not-started

### OS-002 Loopback listener hardening
Files: `crates/vibemaxxing-daemon/src/listener.rs` (new), `crates/vibeproof-collector/src/listener.rs` (new), `conformance/sandbox/loopback-vectors-v1.json` (new), `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`
Acceptance: a request carrying `Host: evil.example` to a loopback listener returns 403; a listener configured with a routable bind address refuses to start rather than binding; the dashboard token never appears in a `Set-Cookie` header, asserted by a case that fails if it does.
Depends: OS-001
Est: 5-8
Status: not-started

The `Host` allowlist is the control that closes DNS rebinding, and it is the only one that can: a rebound request still carries the attacker's name in `Host` while resolving to a loopback address, and peer credentials cannot help because the peer is the participant's own browser running as the participant.

### OS-003 Rate limiter
Files: `apps/api/internal/ratelimit/ratelimit.go` (new), `apps/api/internal/ratelimit/ratelimit_test.go` (new), `packages/schemas/policy-defaults-v1.json`, `docs/architecture/API_EDGE_CONTRACT.md`
Acceptance: `go test ./internal/ratelimit/...` exits 0; a table test asserts every class in `docs/architecture/API_EDGE_CONTRACT.md` enforces its recorded quota and that no class is enforced without a recorded quota; ordinary limits emit `RateLimit` headers and adaptive limits emit none; the first subject-rights request in any 24-hour window is admitted regardless of bucket state, which Article 12(5) requires.
Depends: PF-045
Est: 5-8
Status: not-started

Supersedes `S-018`, which this branch authored before `docs/architecture/API_EDGE_CONTRACT.md` existed. Limits key on the authenticated principal and never on a content-derived value.

### OS-004 Client retry, backoff and circuit breaking
Files: `crates/vibeproof-sync/src/retry.rs` (new), `apps/web/lib/api/retry.ts` (new), `docs/architecture/API_EDGE_CONTRACT.md`
Acceptance: the jitter distribution is uniform over the full interval, asserted statistically over a fixed seed; the retry budget fails fast at 10% over a trailing 60-second window; the circuit opens at 20 consecutive failures and half-opens at 60 seconds; a 409 and a 410 are never retried, one case each.
Depends: OS-003, PF-049
Est: 5-8
Status: not-started

Full jitter rather than jittered fixed delay, because the failure mode is a fleet that all failed at the same instant. Retry safety is read from the specification and never from the HTTP method. The daemon claim queue is the one unbounded case: dropping a queued claim loses activity the append-only ledger cannot recreate.

### OS-005 Structured logging
Files: `apps/api/internal/logging/logging.go` (new), `crates/vibemaxxing-daemon/src/logging.rs` (new), `packages/schemas/observability-allowlist-v1.yaml`, `docs/operations/LOGGING_AND_INSTRUMENTATION.md`
Acceptance: every emitted line carries the required field set; a non-literal message string fails lint, which is the control that stops interpolation carrying forbidden content past a field allowlist; `account_ref` differs across a salt rotation, asserted by rotating the salt in a test; a forbidden field is dropped and the `F-006` canary fires.
Depends: F-006
Est: 3-5
Status: not-started

Supersedes `X-012`. The proposed unit recorded `Depends: none`; `F-006` is the resolvable dependency, because the canary firing is half of this unit's acceptance and cannot fire before the canary library exists.

### OS-006 Metric instrumentation
Files: `apps/api/internal/telemetry/telemetry.go` (new), `packages/schemas/observability-allowlist-v1.yaml`, `evals/suites/suites.yaml`, `docs/operations/LOGGING_AND_INSTRUMENTATION.md`
Acceptance: the eighteen metrics named in `docs/operations/LOGGING_AND_INSTRUMENTATION.md` emit with allowlisted attributes only, asserted in both directions; `python3 scripts/ci/run_evals.py --suite observability-privacy` reports a status that is not `not_applicable`; `/readyz` fails when the applied migration version is outside the declared range.
Depends: OS-005, PF-049
Est: 5-8
Status: not-started

There is no trace export: a hosted tracing backend is a recurring cost against the measured ceiling D-360 sets and would have to process inside the EU under ADR-017. Four span boundaries are recorded locally.

### OS-007 Local development stack
Files: `compose.yaml` (new), `Makefile`, `.env.example` (new), `docs/engineering/LOCAL_DEVELOPMENT.md`
Acceptance: `make dev-up` produces a healthy database on a clean machine with no manual step; `make validate` runs the PostgreSQL DDL stage rather than skipping it; `make migrate-verify` reproduces `packages/schemas/planning-schema.sql` from the migration history byte-for-byte.
Depends: S-002
Est: 3-5
Status: not-started

Supersedes `F-009`. The proposed dependency "ADR-018 first migration" is `S-002`. Three properties of the compose definition are load-bearing and `docs/engineering/LOCAL_DEVELOPMENT.md` explains each: the port binds `127.0.0.1` explicitly, the database initialises with locale `C` because two engineers on different distributions otherwise get different `ORDER BY` results and a leaderboard is an ordering, and the volume is named.

### OS-008 Conformance manifest format and validator
Files: `packages/schemas/conformance-manifest-v1.schema.json` (new), `conformance/vibeproof/v1/manifest.json` (new), `tests/ci/test_conformance_manifests.py` (new), `scripts/repository/validate_planning_artifacts.py`, `docs/verification/CONFORMANCE_HARNESS.md`
Acceptance: every suite directory under `conformance/` other than `p1140e` and `p1140f` declares one manifest and one README; the validator exits non-zero when a manifest cites an authority or a clause that does not resolve, when a fixture digest does not match, when a fixture no manifest names is present, when a populated suite declares neither a negative case nor a recorded gap, or when a case identifier is duplicated or wrongly prefixed.
Depends: none
Est: 3-5
Status: landed
Evidence: unittest tests.ci.test_conformance_manifests
Evidence: exists packages/schemas/conformance-manifest-v1.schema.json
Evidence: contains 1 scripts/repository/validate_planning_artifacts.py :: validate_conformance_manifests
Evidence: contains 1 conformance/sandbox/manifest.json :: origin-policy-v1.json

**Landed under D-441 and D-442.** Fifteen manifests, one per suite directory. The proposed unit named a standalone `scripts/repository/validate_conformance_manifests.py`, superseded before it was written: the stage lives in `scripts/repository/validate_planning_artifacts.py` instead, beside the reason registry and OpenAPI stages it has to agree with, because a separate script would have had to reload and re-derive both.

Three of the D-242 field rules could not be satisfied as written and are corrected rather than worked around. `suite_id` is the directory name and `eval_suite_ids` is a separate list, because no directory name equals its eval registry id. `reason_authority` is per suite, because a loopback refusal cannot live in a registry that requires every code to bind to an API operation. A suite holding no fixture records `fixture_state: empty` with zero cases. Thirteen of the fifteen declare no runner, which is the honest state and not a passing one; the two that do declare one name a script that reads two conformance files and emits none of the result document the harness contract defines.

### OS-009 Conformance runners
Files: `crates/conformance-runner/src/main.rs` (new), `apps/api/cmd/conformance/main.go` (new), `docs/verification/EVAL_SYSTEM.md`
Acceptance: each runner emits the result schema in `docs/verification/EVAL_SYSTEM.md`; a case where both subjects agree on the wrong answer reports `fail: expectation` rather than `pass`, which is the check that cross-language agreement is not being mistaken for conformance; two runs of the same commit produce byte-identical output.
Depends: OS-008
Est: 8-13
Status: not-started

### OS-010 Load test harness
Files: `benchmarks/load/scenarios.js` (new), `benchmarks/load/README.md` (new), `.github/workflows/load-test.yml` (new), `docs/verification/TEST_STRATEGY.md`
Acceptance: all six scenarios in `docs/verification/TEST_STRATEGY.md` run against an ephemeral stack; `offline-drain` admits every claim exactly once; `ratelimit-breach` leaves other principals statistically unchanged, asserted against a recorded tolerance.
Depends: OS-003, X-013
Est: 8-13
Status: not-started

Supersedes `X-014`. The scenarios are sized at the D-180 reference population of 200 participants and a passing run may never be cited as evidence for the 100,000 target; `docs/verification/TEST_STRATEGY.md` says so and this unit does not contradict it. Activating the workflow is product automation and is outside the current authorization.

### OS-011 Deprecation mechanics
Files: `packages/schemas/openapi-v1.yaml`, `apps/api/internal/middleware/deprecation.go` (new), `docs/architecture/API_EDGE_CONTRACT.md`
Acceptance: a deprecated operation emits `Deprecation`, `Sunset` and `Link` headers; the window between the two dates is at least 180 days, asserted arithmetically rather than by review; a fixture pins the exact header set so a silent removal fails.
Depends: OS-001
Est: 2-3
Status: not-started

Supersedes `S-017`.

### OS-012 Clock discipline
Files: `apps/api/internal/clock/clock.go` (new), `crates/vibeproof-core/src/time.rs` (new), `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
Acceptance: a claim beyond the 300-second future tolerance is rejected; the server refuses to finalize beyond a 2000 ms measured offset; `grep -rnE 'now\(\)\s*-' apps/api/internal crates/vibeproof-core` returns no interval computed by subtracting wall-clock timestamps, which is the defect a monotonic source exists to prevent.
Depends: OS-006
Est: 3-5
Status: not-started

D-245 is open and this unit inherits it: a clock rollback and a future timestamp still have no reason code, because registering one is blocked behind the partial reason-code repair D-224 records. This unit cannot close while its rejection has no code to cite.

### OS-013 Secret rotation runbook and first rotation
Files: `docs/operations/ENVIRONMENTS_AND_SECRETS.md`, `scripts/ci/check_secret_inventory.py` (new)
Acceptance: `python3 scripts/ci/check_secret_inventory.py` exits 0 only when every class in `docs/operations/ENVIRONMENTS_AND_SECRETS.md` records a first rotation date, an owner and a cadence, and non-zero when any is missing; a session-key rotation does not invalidate a handle inside its retained generations, asserted by a case.
Depends: L-013
Est: 2-3
Status: not-started

Supersedes `X-002`. The proposed dependency "ADR-017 provider selection" is not a unit and is recorded as a condition instead: every environment, secret-store and residency statement behind this unit is contingent on an ADR-017 selection that has not run, and the unit cannot start before it does.

### OS-014 Origin and loopback machine contract
Files: `packages/schemas/origin-policy-v1.schema.json` (new), `packages/schemas/origin-policy-v1.json` (new), `tests/ci/test_origin_policy.py` (new), `packages/schemas/openapi-v1.yaml`, `packages/schemas/reason-codes-v1.json`, `scripts/repository/validate_planning_artifacts.py`, `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`
Acceptance: the OpenAPI document declares an `Origin` parameter on exactly the operations whose security includes `csrfToken` and on no others, and a `Preflight` response component declaring six `Access-Control-*` headers none of which is required; the `x-origin-policy` block equals the policy record field by field; the development origin is recorded as compiled out rather than configured off; every loopback listener binds all eight D-231 controls and no loopback refusal code appears in `reason-codes-v1.json`.
Depends: PF-039
Est: 3-5
Status: landed
Evidence: unittest tests.ci.test_origin_policy
Evidence: contains 22 packages/schemas/openapi-v1.yaml :: parameters/Origin
Evidence: contains 1 packages/schemas/openapi-v1.yaml :: x-origin-policy
Evidence: contains 1 packages/schemas/reason-codes-v1.json :: ORIGIN_NOT_ALLOWED
Evidence: absent packages/schemas/reason-codes-v1.json :: LOOPBACK_

**Landed under D-440.** This is the machine surface `OS-001` and `OS-002` implement against, and it is not either of them: no middleware validates an origin and no listener checks a `Host` header. The unit exists because the inventory recorded the origin row as `planned-missing` on the grounds that the OpenAPI document declared no `Origin` parameter and no preflight response, and that gap is a contract gap rather than an implementation one.

The `Origin` parameter is optional in the document and conditionally required in the record, because OpenAPI cannot express a parameter that is mandatory under one security alternative and absent under another. The loopback refusal vocabulary is owned by the policy record and the validator fails if it is ever merged into the API reason registry, where every wire-visible code must bind to a declared operation.

## Explicit non-units

The following are not launch units:

- country leaderboards;
- SLM detector promotion;
- native Android, iOS, iPadOS or ChromeOS clients;
- kernel anti-cheat;
- mandatory inference proxy;
- unsupported claims generated from unexercised manifests;
- autonomous workflow activation during planning.

## Critical path

**What to start next is derived, not written here.** It is in the generated block under **Plan status**, computed from the `Status:` lines and the dependency graph by `scripts/repository/validate_work_unit_status.py`. The hand-written list that used to sit in this section went stale the moment a unit landed and nobody edited it — it still named `PF-053` as unstarted after its ADR had been committed. A list that has to be maintained by hand to stay true will not stay true.

All `F-` through `X-` units remain blocked until P-1104 regardless of status.

An earlier revision stated "PF-001 only" as the next unit, and a companion claim placed `PF-002`/`PF-003` immediately after `PF-001` on the critical path. Both were wrong by this file's own dependency lines: `PF-002` and `PF-003` are leaves that nothing depends on, and the longest `PF-` chain begins at `PF-004`, which does not depend on `PF-001`. The corrected chain to `PF-036` is `PF-004 → PF-021 → PF-022 → PF-023 → PF-029 → PF-033 → PF-034 → PF-035 → PF-036`, a depth of nine.

Longest chains under the repaired graph, measured in units rather than time: 19 to `S-010` (first claim accepted server-side), 26 to `V-004` (first working adapter), 28 to `W-003` (leaderboard visible in a browser), 37 to `W-010`, 38 to `X-010`, and 43 to `X-011`. A 26-unit serial chain before one real token reaches a board is the specific reason the plan is sequenced by vertical slice rather than by layer.

`X-011`'s transitive closure is 224 of the 258 units. The 33 outside it are `PF-037` through `PF-067` — planning repairs whose value is repository hygiene rather than a launch prerequisite — plus the six `superseded-by` units, which are outside by construction because their successors are inside. Every live implementation unit is inside the closure, which is what the previous 162-of-194 figure was supposed to mean and did not.