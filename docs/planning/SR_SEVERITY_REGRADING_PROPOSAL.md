# Proposed severity regrading for the P-1140F semantic findings

Status: **proposal, awaiting owner decision.** Nothing in this document has been applied.
Proposed: 2026-08-06
Register row: D-300
Authority: none. `conformance/p1140f/semantic-findings-v1.json` holds the live severity of every finding and `conformance/p1140f/gate-authorization-v1.json` holds the gate state. Both are unchanged by this document and neither may be edited to match it without an owner decision.

## What this is

All thirteen P-1140F semantic findings, SR-005 through SR-017, carry the same severity. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md` says that uniformity "is not a graded judgement and must not be read as one: severity here means only 'open and blocking this gate'", and refers the grading to the owner because changing it changes the count pinned in the gate record.

This document is that referred judgement, written out so the owner can approve, amend or reject it row by row. It proposes a severity for each finding, argues the proposal from what the finding would cost if it shipped unfixed, and separates two things severity does not carry: whether the finding blocks launch, and whether it can be falsified today.

## What this is not

- It is not a decision. No finding is closed, deferred, downgraded or waived by it. All thirteen remain open at their recorded severity until the owner says otherwise.
- It is not evidence. A grade is an opinion about cost, not a verdict about correctness, and grading a finding does not advance its repair.
- It is not a second finding registry. The registry is `conformance/p1140f/semantic-findings-v1.json`; this document cites it and never restates it as authority.
- It is not a statement about live risk. Nothing in this repository is implemented. Every cost below is conditional on shipping the contract as currently written, and a P0 here is a planning-severity judgement, not a production incident.

## The test used

Severity answers one question: **what does this cost if the product ships with the contract as written?** It deliberately says nothing about how hard the repair is. A finding that silently corrupts an accepted claim outranks one that makes a document inconsistent, however much longer the second one takes to fix.

Three grades are available, because `conformance/p1140f/semantic-findings-v1.schema.json` admits exactly `P0`, `P1` and `P2`.

- **P0** — shipping it unfixed admits an outcome that cannot be detected or reversed after the fact: an accepted claim is silently corrupted, personal data is published to someone not authorized to see it, or a participant's standing is set by someone other than the server verifier.
- **P1** — shipping it unfixed produces a wrong outcome that the product can see and correct: a double count that leaves two ledger rows, a spoofed presence state, an escalation the owner can reverse. The append-only correction path exists and is sufficient.
- **P2** — shipping it unfixed harms no participant and alters no claim. What breaks is the repository's account of itself.

Two further axes are recorded separately for every finding, because collapsing them into severity is what produced the uniform grade in the first place.

**Launch-blocking** is not severity. A finding blocks launch when a contract on the launch path cannot be implemented around it — which can be true of a low-severity finding, and false of a high-severity one whose path nothing reaches at beta scale. One finding below is graded P2 and is still gate-blocking, which is a third thing again: it blocks P-1140F from being called closed without touching anything a participant uses.

**Falsifiable today** records whether the finding can be closed by evidence that exists now. Several close only once behaviour exists, and saying so is more useful than a grade, because it tells the owner which of these the implementation track will resolve on its own and which need a document written first.

## Proposed grading

| Finding | Subject | Recorded | Proposed | Launch-blocking | Falsifiable today |
|---|---|---|---|---|---|
| SR-005 | Protocol authority and executable drift | P1 | **P0** | yes | yes |
| SR-006 | OAuth, linked identity, recovery, ranked identity | P1 | **P0** | yes | contradiction half only |
| SR-007 | Device lineage, challenge, replay, checkpoint | P1 | **P0** | yes | yes |
| SR-008 | Local daemon, shell, IPC, platform supervision | P1 | **P1** (unchanged) | yes | contradiction half only |
| SR-009 | Adapter certification and deterministic accounting | P1 | **P0** | yes | yes |
| SR-010 | Ranking authorization, generations, periods, corrections | P1 | **P0** | yes | yes |
| SR-011 | Social relationships, boards, presence, notifications | P1 | **P1** (unchanged) | yes | partly |
| SR-012 | Idempotency and ambiguous commit recovery | P1 | **P1** (unchanged) | yes | yes |
| SR-013 | Export, deletion, retention, backup tombstones | P1 | **P0** | yes | yes |
| SR-014 | Release authorization, compatibility, migration, rollback | P1 | **P0** | yes | partly |
| SR-015 | Current-authorization recheck at every boundary | P1 | **P0** | yes | no |
| SR-016 | Review-record integrity | P1 | **P2** | no, but gate-blocking | yes |
| SR-017 | Source-bound evidence and verifier appraisal authority | P1 | **P0** | yes | yes |

Nine P0, three P1, one P2. That distribution is not a failure of the test: eleven of the thirteen findings sit on a path that carries either an accepted claim or personal data, and the two that do not are exactly the ones that separate out. If the owner reads nine P0 as too flat to be useful, the ordering within the P0 band that this document argues is, worst first: SR-014, SR-005, SR-007, SR-006, SR-015, SR-013, SR-010, SR-017, SR-009.

## Per-finding argument

### SR-005 — Protocol authority and executable drift → P0

**What breaks if it ships.** The normative authority is a deterministic 31-field CBOR payload under a mandatory COSE_Sign1 profile. The prototype and `conformance/protocol/vibeproof-v1-vectors.json` implement an unsigned 11-field profile carrying client-selected evidence and `billable` values. Ship the second and every accepted claim is unsigned and self-graded: the client states its own evidence level and its own billable quantity, and the server has no signature to re-check afterwards. That violates the binding rule that public evidence status and competitive eligibility are assigned by the server verifier and never selected by the client, and it violates it in the one direction that leaves no trace — an unsigned claim cannot be shown later to have been forged, because there was never anything to verify.

**Who is harmed.** Every honest participant, continuously and invisibly. The ranking is the product; a forgeable claim makes the whole ordering meaningless, and no correction can distinguish the forged rows from the real ones after the fact.

**Launch-blocking.** Yes. D-090 and D-183 put deterministic CBOR, CDDL and COSE with Ed25519 on the launch critical path rather than deferring them, on the grounds that the evidence architecture is the product.

**Falsifiable today.** Yes, and it is the most falsifiable finding in the set. Two committed corpora disagree byte for byte, D-096 already names the closure — rewrite both implementations against `packages/schemas/vibeproof-claim-v1.cddl` and the vectors under `conformance/vibeproof/v1/`, retire the shadow corpus — and D-190 through D-194 have since fixed the algorithm identifier, the map ordering, the verification rule, the float ban and the vector generator that closure depends on. It is the only finding already in `repair-in-progress`.

### SR-006 — OAuth, linked identity, recovery, and ranked identity → P0

**What breaks if it ships.** The API carries a raw authorization-code mutation detached from its OAuth transaction, and the transaction binds neither the target account, nor the session, nor the recent-auth grant, nor the exact provider configuration, nor the result. An authorization code that reaches the wrong endpoint therefore attaches a provider identity to an account that is not the one that started the flow. Around it, provider loss, compromise, recovery, consolidation, canonical ranked identity, retirement and appeal have no executable authority at all.

**Who is harmed.** The participant whose ranked identity is grafted onto someone else's account, and everyone below them on a board. Three separate launch controls read the provider link and all three fail with it: the D-081 90-day account-age gate, the D-286 invite admission record, and the D-054 one-active-ranked-identity rule. Under D-070 a consolidation combines historical claim contributions under a surviving identity, so a wrongly linked identity is not cleanly reversible once consolidation has run.

**Launch-blocking.** Yes. Authentication is the first surface a beta participant touches and there is no path around it; D-288 makes an authenticated pre-admission session a real state the product must serve.

**Falsifiable today.** The contradiction half is: `packages/schemas/openapi-v1.yaml` and `packages/schemas/planning-schema.sql` disagree today about what an identity mutation binds, and that is checkable now. The recovery, consolidation, ranked-identity and investigation aggregates are recorded `planned-missing` in `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, so that half is a design task and closes when the schemas are authored, not when a contradiction is resolved.

### SR-007 — Device lineage, challenge, replay, checkpoint, and recovery → P0

**What breaks if it ships.** `device_sequences` is keyed on `device_id` and holds the continuity head per device row, while the protocol claims lineage-wide authority and the binding product rule states that continuity is lineage-scoped rather than device-row-scoped. Ship the DDL as written and a copied device store produces two rows that are each internally continuous, so the fork the D-072 quarantine exists to catch is invisible to the mechanism that is supposed to catch it. Separately, CDDL, OpenAPI and PostgreSQL describe incompatible challenge objects and identifier types, so a challenge issued by one boundary is not the object another boundary validates.

**Who is harmed.** Every participant who did not clone their device. Fork detection is the only structural control against one person running N copies of a lineage, and this defect removes it silently: nothing is logged, nothing is quarantined, and the inflated totals are accepted claims that the immutability rule then protects.

**Launch-blocking.** Yes. There is no version of the product where continuity is optional, and D-072's quarantine is unimplementable against a per-device row.

**Falsifiable today.** Yes. Both authorities are committed, they disagree about the key, and the disagreement is visible by reading two files.

### SR-008 — Local daemon, shell, IPC, and platform supervision → P1, unchanged

**What breaks if it ships.** `packages/schemas/local-control-v1.proto` puts `sender_role` in the envelope as a field the sender fills in. A process therefore declares its own trust domain, and the protocol structurally permits cross-role messages: there is no daemon-assigned role, no process generation, no capability grant and no handshake that would refuse one. Any process running as the same user can present itself as the daemon, submit source observations, or drive lifecycle operations.

**Why P1 and not P0.** This is the grade most likely to be argued with, so the reasoning is written out. Every failure mode this finding enables against a participant's *own* account is one that D-100 already concedes is unpreventable: no provider offers an individual-account attestation path, no claim is self-evidencing, and the integrity load is carried by the ADR-020 confidence weight rather than by source attestation. A participant who wants to fabricate their own figures does not need this defect. What the defect genuinely adds is cross-process rather than cross-person: malware, another user's process under the D-067 privileged supervision profile, or a shared CI runner made competitive by D-065 can act as the daemon on a machine that is not solely theirs. That is a real harm and it is narrower, and the D-265 source receipt records which observations were seen and which one counted, so the outcome is both detectable and correctable through the append-only path. Detectable and correctable is the P1 line.

**Launch-blocking.** Yes. The daemon is the collector; there is no product without it, and the shell lifecycle it drives is a launch surface. Note that the state-machine half of this finding has already been repaired elsewhere: D-196 removed the unreachable states, the sinks and the false terminals across every machine including `interactive-shell` and `daemon-lifecycle`. What remains is the trust-domain half.

**Falsifiable today.** The Protobuf contradiction is. OS peer identity, daemon-assigned roles, capability grants and local persistence are `planned-missing`, and their correctness is a runtime property that closes only once the daemon exists.

### SR-009 — Universal adapter certification and deterministic accounting → P0

**What breaks if it ships.** `packages/schemas/adapter-manifest.schema.json` carries one `certification` object per manifest, holding `bundle_sha256`, `suite_version`, `source_version`, `platform_profile_id` and `mode`. The manifest above it lists `source_products`, `platforms`, `modes` and `accounting_profile_ids` as arrays. One certification therefore authorizes every combination of those arrays, including combinations nothing has ever exercised, and it carries no validity interval and no revocation. This is the finding the brief singles out: `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` specifies one exact tuple in prose — `claude-code-otel` over loopback OTLP, ceiling `standard-competitive`, attested-local under D-077 — and the manifest schema had no field that could express it.

Note that the representation half of this paragraph has since been repaired, which narrows the finding rather than closing it. PF-071 gave the block a certification state and a nullable bundle digest; PF-074 replaced the single-valued `source_version`, `platform_profile_id` and `mode` with an enumerated `certification.tuples` list carrying the version range, the artifact, accounting, arithmetic and privacy-binding digests, the duplicate domain, a validity interval and a revocation, so coverage is containment in a stated list rather than a product over the four arrays. `scripts/repository/validate_adapter_certification_tuple.py` fails when a dimension reaches the manifest, `packages/schemas/compatibility-tuple-v1.schema.json` or `source_certifications` and not the other two. What remains of this finding is the accounting-input and certification-evidence half, and the grade below is unchanged: a schema that can now express an exact tuple is not a certified tuple, and every state this repository can reach is still `candidate` or `uncertified`.

**Who is harmed.** Everyone else on the board, which is what makes this worse than a self-farming defect. D-098 measured the Claude Code session JSONL substrate at roughly 174 times undercount on input, 91 times overcount on subagents, and an 11% retroactive decrease within 16 hours, and capped it at private analytics for exactly that reason. A manifest-wide certificate cannot express that cap: certify the OTLP tuple and the JSONL tuple is certified with it. Figures wrong by two orders of magnitude then compete at full weight, and every honest participant's position moves. It violates the binding rule that generic OpenTelemetry, proxy, wrapper and unknown-version integrations remain private analytics until an exact tuple is certified, and the rule that registries may not imply exercised support.

**Launch-blocking.** Yes. D-089 makes Claude Code adapter number one and the first integration certified end to end, and the artifact that must record that certification cannot represent it.

**Falsifiable today.** Yes, by schema inspection alone. Note that the accounting-input half is materially narrower than it was: D-264 introduced `packages/schemas/producer-accounting-binding-v1.schema.json`, which pins the producer surface, scope, shape, attribute disposition, profile and certification state and forces `effective_ceiling` to private analytics for every state other than active, and every binding in `conformance/accounting/producer-bindings-v1.json` is currently below active. D-269 closed multi-observer deduplication by fixing the commitment preimage to source-derived facts only. What is left is the certification tuple itself.

### SR-010 — Ranking authorization, immutable generations, periods, and corrections → P0

**What breaks if it ships.** One public route structurally serves global, friends, rivals and board leaderboards with no viewer identity and no board identity in the request. Ship it and a private board's standings are retrievable by anyone who can name the board, which directly violates the binding rule that only global leaderboard views are universally public by default and that friend, rival, private and unlisted board views require current viewer authorization.

**Who is harmed.** Every member of a non-global board, and the harm is a disclosure, so it is irreversible the moment it happens. D-088 puts all six board scopes across all six periods in launch scope, so the exposed surface is the majority of the product's boards rather than an edge case.

**Launch-blocking.** Yes, for the same reason.

**Falsifiable today.** Yes. The route and its response shape are committed and carry no audience parameter.

**Scope note, because it changes what closing this means.** The storage half of this finding has largely landed. D-211 sealed the generation and froze its aggregates, D-212 replaced the cursor with a `(ranking_view_id, generation, position)` anchor carrying no subject identifier, and `ranking_projection_generations`, `score_snapshots` and `score_contributions` now exist with the correction path D-263 defines. The ADR-020 `score` limb has also moved: D-218 renamed `minute_scores.score` and `period_scores.score` to `token_burn_total` and the credited fields, and D-227 and D-144 removed `RankEntry.score` in favour of `credited_token_burn`. What still carries the banned word is three *table* names, which D-218 recorded as a deliberate stop because `packages/schemas/state-machine-registry-v1.json` names `period-scores` and `score-snapshots` as persistence owners and that registry belongs to this closure track. That residue is cosmetic and harms nobody; the authorization half is the P0.

### SR-011 — Social relationships, boards, presence, and notifications → P1, unchanged

**What breaks if it ships.** Board invitation, membership, ownership, friendship, directional block, rivalry, presence and notification lifecycles are not coherently separated. Presence may be client-declared, which contradicts the binding rule that presence is server-derived from qualifying device activity, and `presence_leases` does not even carry the `offline` state D-073 defines. `blocks` is a bare pair of account identifiers with no timestamp and no revision, so a block cannot be ordered against anything that was served before it. Notification inbox, transport, read, suppression, expiry and retraction use incompatible authorities against a binding rule that makes the server inbox the notification authority.

**Why P1.** Each outcome here is visible to the product and reversible by it. A spoofed presence state is wrong and correctable. An invitation that grants more than the non-privileged membership D-071 allows is an escalation the board owner can undo. A notification delivered twice or not retracted is an inbox defect. None of it alters an accepted claim and none of it publishes a figure to an unauthorized viewer — the case where a stale block leaves a participant visible to someone they blocked is real, but it is the boundary recheck, which is SR-015's aggregate rather than this one's. The restated SR-015 says exactly this: those findings own their aggregates, SR-015 owns the boundary.

**Launch-blocking.** Yes. D-184 binds the private beta to the full scope freeze — friends, rivals, presence, notifications, moderation and appeals ship together — so none of these lifecycles can be deferred past the beta ring.

**Falsifiable today.** Partly. Presence, blocks and rivalry are checkable against the committed DDL now. Notification source-event, inbox, delivery-attempt and preference schemas are `planned-missing`, and D-086 has since narrowed that surface by making the server inbox the only launch transport.

### SR-012 — Idempotency and ambiguous commit recovery → P1, unchanged

**What breaks if it ships.** `idempotency_records` has primary key `(actor_account_id, idempotency_key)` and a nullable `response_digest`, and holds no response body. Two consequences follow. The key is scoped to the account rather than to the operation, so one participant reusing a key across two different operations receives the first operation's stored outcome for the second. And a claim-batch submission whose commit is ambiguous can be retried into a second commit, because a nullable digest cannot decide replay against conflict.

**Who is harmed.** The participant whose batch double-counts, and everyone they outrank as a result. D-233 already records this consequence in the client contract rather than hiding it: a keyed-mutation retry is currently safe against duplicate side effects and is not safe against receiving a different response body.

**Why P1 and not P0.** A double commit leaves two rows in an append-only ledger. It is visible to the product, and D-263 makes the correction path a directed append that rebuilds the period into a new generation rather than editing a total. Detectable and reversible is the P1 line, and the distance to closure is unusually short: D-142 and D-225 already accepted the exact contract — key scoped to `(principal_id, operation_id, idempotency_key)`, a SHA-256 request digest deciding replay, a byte-identical stored response under an `Idempotency-Replayed` header, `409` and `410` for conflict and expiry, a 168-hour window — and both decisions state in terms that they do not close this finding because the persistence half is untouched. This is the cleanest example in the set of a finding whose severity should not be read off its repair cost.

**Launch-blocking.** Yes. Claim ingestion is keyed and the daemon retries by design.

**Falsifiable today.** Yes, entirely. Two accepted decisions and one committed DDL disagree, and PF-049 is the unit that resolves it.

### SR-013 — Export, deletion, retention, and backup tombstones → P0

**What breaks if it ships.** The deletion half of this finding has closed in substance. What has not is export. `exports` holds an identifier, an account, a state and an `expires_at`; `export_artifacts` holds a digest, a size and a record count. There is no export snapshot binding, no manifest authority, no encryption, no download grant and no purge schedule anywhere in the DDL, while `docs/privacy/DATA_MAP.md` states real windows in prose — bundles purged seven days after they become ready, short-lived revocable download grants — that nothing enforces.

**Who is harmed.** The participant who exercised Article 20 and got back the single most concentrated personal record the product holds. Ship it as written and that bundle has no purge and its download grant has no revocation, so the disclosure is unbounded in time and irreversible once it happens. D-108 makes portability a live obligation because the lawful basis is consent, and D-288 puts `requestExport` among the six operations reachable before invite redemption, so this is on the first path a beta participant can walk rather than a late surface.

**Launch-blocking.** Yes, and legally as well as technically.

**Falsifiable today.** Yes. D-216 requires `packages/schemas/data-disposition-v1.json` to hold one row per persistence owner with a retention window and an enforcement actor, and the export tables cannot satisfy it because the columns the window would attach to do not exist. PF-050 is the unit.

**Scope note.** The deletion, retention and backup-tombstone limbs landed under D-210 through D-216: the erasure record, key destruction, the `erasure_keys` presence-or-destruction constraint, the out-of-backup journal, the restore receipt, partition-drop retention and the disposition registry. If the owner wants the register to reflect what is actually left, the honest statement is that SR-013 is now an export finding wearing a four-part title.

### SR-014 — Release authorization, compatibility, migration, and rollback → P0

**What breaks if it ships.** `tuf_roots` and `release_sets` exist, but the release set has no proper external trust envelope and no component or path model, and TUF client state, the compatibility graph, migration chains, rollback classes and verified installation plans are all `planned-missing`. D-068 and ADR-013 make automatic updates mandatory for competitive profiles. Ship a mandatory automatic updater whose trust envelope is incomplete and the failure mode is arbitrary code execution on every participant's machine, delivered by the product itself, at the moment the product decides.

**Who is harmed.** Everyone who installed it, simultaneously. This is the largest blast radius in the finding set by a wide margin, and it is the reason this document orders SR-014 first within the P0 band.

**Launch-blocking.** Yes. D-183 keeps the signing primitives on the critical path, and the workflows that would exercise a release are disabled under `P-1007` regardless of P-1104, so there is no route by which this gets exercised early and quietly.

**Falsifiable today.** Partly, and this is the finding where the honest answer matters most. The trust-envelope and component-model contradiction is checkable against `packages/schemas/release-set-v1.schema.json` now. TUF client state, the compatibility graph and the D-074 rollback classes are `planned-missing`, so they close when authored. Whether the updater actually refuses hostile metadata is a runtime property that closes only when an update runs against an adversarial corpus, which D-024 already requires and which cannot happen in this phase.

### SR-015 — Current-authorization recheck at every display and delivery boundary → P0

**What breaks if it ships.** This finding was restated on 2026-08-06 from a repairable cluster that owned no artifacts into the invariant it actually asserts: every display and delivery boundary rechecks current authorization instead of replaying a historical snapshot. Ship without it and a block, a privacy change, a board removal, a moderation reversal or a consolidation does not take effect where the participant expects it to. Concretely, `score_snapshots` seals a generation and D-212 makes cursors durable into it, and `blocks` carries no timestamp — so a viewer holding a cursor into a sealed generation keeps receiving entries for a participant who has since blocked them or gone private, and nothing in the cursor contract knows the block happened.

**Who is harmed.** The participant who took an action specifically to stop being seen, and reasonably believes it worked. That is worse than an ordinary disclosure because it recurs on every page fetch and because the product has told them it is fixed. It violates the binding rule that non-global board views require *current* viewer authorization, with the emphasis where the finding puts it.

**Launch-blocking.** Yes. It spans the leaderboard, public-profile, presence, notification and export operations, which is most of the read surface.

**Falsifiable today.** No, not as a whole, and this is the finding where the grade matters least and the falsifiability note matters most. What is checkable now is the absence: no boundary matrix exists, and the five cited operations in `packages/schemas/openapi-v1.yaml` declare no authorization recheck. What cannot be checked now is the invariant itself, because "rechecks current authorization at every boundary" is a runtime property of code that does not exist. The closure criterion the restatement records — one enumerated boundary matrix, plus a check at every boundary in it — is deliberately split for that reason: the matrix is authorable today and the checks are not.

**One limb is already closed and should be credited.** The erasure case works: D-211 makes an erased entry render nothing at all rather than a placeholder, and D-212 removes the subject identifier from the cursor so a stale cursor cannot resurrect one. What is open is block, privacy change, board removal and moderation reversal.

### SR-016 — Review-record integrity: reviewed head, evidence class, and named owners → P2

**What breaks if it ships.** Nothing ships. This finding is about what the repository claims about itself, and after its restatement it is about three strings that disagree: `conformance/p1140f/REPAIR_HEAD_REVIEW.md` pins one commit, the semantic review document states a different review base, and `conformance/p1140f/review-target-v1.json` is `not-pinned` with a null commit and a pending verdict. No participant is harmed by any of that, no claim is altered, and nothing is published.

**Why P2 rather than P1.** The test is cost if shipped, and the cost of this one shipping is zero. That is the whole argument, and it is what the brief means by a finding that makes a document inconsistent ranking below one that corrupts a claim. Its other two limbs have also been repaired by adjacent work, which narrows it further: D-195 made every persistence owner in `packages/schemas/state-machine-registry-v1.json` resolve to a table in `packages/schemas/planning-schema.sql` and made a validator fail when one does not, closing the 19-of-26 gap the finding cites; and the suite-name limb has moved, since `evals/suites/suites.yaml` now carries `shadow-codec-parity` with an explicit exploratory ceiling rather than a suite named for a conformance it does not execute.

**Launch-blocking.** No. Nothing on the participant path reads any of these records.

**Gate-blocking.** Yes, and this is the reason P2 must not be read as "ignore it". Closure criterion 8 of P-1140F requires the exact repaired head to receive independent manual review with zero open semantic findings, and `review-target-v1.json` is the record that would hold that verdict. P-1140F cannot honestly be called closed while the pin does not exist, whatever severity this row carries. A P2 that gates a program is an unusual shape and it is stated here explicitly so the grade is not mistaken for permission.

**Falsifiable today.** Yes, completely, and it is the only finding in the set that is closeable by evidence that exists right now: pin the target, record the verdict, make the prose head claims equal to it.

### SR-017 — Source-bound evidence and verifier appraisal authority → P0

**What breaks if it ships.** The contradiction half is live and cited. One appraisal aggregate is described three ways: `packages/schemas/vibeproof-claim-v1.cddl` carries seven classification dimensions, `packages/schemas/evidence-profile-policy-v1.json` enumerates the same seven as server-verifier authority, and `verifier_appraisals` in `packages/schemas/planning-schema.sql` persists only provenance, continuity and integrity state — no claim digest, no evidence digest, no validity interval, no supersession. Ship that and two things follow. A ranking contribution cannot be pinned to the exact appraisal that produced it, so it references a mutable current tier and a later policy change silently re-scores accepted history. And without supersession there is no way to express a reappraisal, so a claim admitted under an adapter that is later revoked, or a key that is later found compromised, keeps its awarded evidence class permanently.

**Who is harmed.** Every participant whose historical periods are rewritten by a policy edit they never saw, which violates the binding rule that accepted claims and historical facts remain immutable and that corrections are append-only. The second failure mode harms everyone else instead: revoked evidence that cannot be revoked is a permanent unearned weight in the ranking, and under D-100 the ADR-020 confidence weight is the only integrity control the product has, so an appraisal that cannot be superseded disables it.

**Launch-blocking.** Yes, for that last reason specifically.

**Falsifiable today.** Yes, and considerably more so than when the finding was restated. The design half has largely landed: D-265 authored the source receipt, D-266 the evidence bundle, D-267 the appraisal result, and D-268 the appraisal policy bundle, and all four files now exist. D-267 went further and made the remaining distance machine-visible by naming the three-state columns as dropped and every field the table cannot hold as unbound, both checked against the DDL. The remaining work is the SQL binding, and a validator already fails until it lands.

## What adopting this proposal would mechanically require

This section exists so the owner can price the decision. None of it has been done and none of it may be done by an agent.

1. **Thirteen `severity` edits in `conformance/p1140f/semantic-findings-v1.json`.** Nine to `P0`, one to `P2`, three unchanged.

2. **Three prose counts must move in the same commit.** `scripts/repository/doctor.py` requires every open-P1 count stated in a registry summary document to equal the live registry count exactly, and reports the number the document states when it does not. `docs/project/STATUS.md`, `docs/planning/TASK_CATALOG.md` and `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING.md` each state thirteen. After the regrade the live P1 count is three, and all three documents fail until they say three.

3. **One prose statement becomes false.** The semantic review document states that semantic P0 findings open is zero. Under this proposal it is nine. That line is not matched by any recorded claim pattern, so no validator would catch it — which is precisely why it is listed here.

4. **The non-regression ceiling stops covering nine findings, and cannot be extended without a schema change.** `open_p1_baseline.count` is 13 and the rule fails only when the active count *exceeds* it, so dropping to three keeps validation green with no edit to the gate record. That is the trap: nine findings would move out of the only ceiling the repository has, and nothing would report it. `conformance/p1140f/gate-authorization-v1.schema.json` sets `additionalProperties: false` at the top level and pins `open_p1_baseline.severity` to the constant `P1`, so recording a P0 ceiling requires editing the schema as well as the record. **If the owner adopts any part of this proposal, adding a P0 baseline in the same change is the load-bearing half.**

5. **`docs/project/DOCUMENTATION.md` gains this file** in the `planning/` row of the complete file map. That registration is included in this branch; nothing else in this list is.

6. **Nothing about gate state changes.** P-1140F stays `in-progress-planning`, P-1104 stays `authorized-open`, and no finding changes `state`. A regrade is a judgement about the same thirteen open findings, not a step toward closing any of them.

## Observations recorded while grading, not repaired here

Three drifts surfaced during this review. None is a semantic finding, none is repaired in this branch, and each is stated so it is visible rather than carried silently.

- **SR-017 carries no `planned_artifacts` field**, while both the semantic review document and the finding's own restatement rationale say the design half is carried there. The explanation is benign and is that the four artifacts have since been authored, so they correctly sit in `conflicting_artifacts` instead; the prose in both places is stale rather than the registry being wrong. `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` already records the source receipt as present rather than planned-missing.
- **The SR-010 paragraph of the semantic review names four artifacts that still carry `score`**, one of which no longer does: `RankEntry` lost the field under D-227 and D-144, and the columns in `minute_scores` and `period_scores` were renamed under D-218. What remains is three table names, which D-218 recorded as a deliberate stop pending this track.
- **The `docs/project/DOCUMENTATION.md` complete file map has duplicated rows** for `decisions/`, `architecture/`, `privacy/` and `security/`, and two contradictory paragraphs under "Small directories, with reasons" giving different file counts for `privacy/`, `engineering/` and `verification/`. That is a merge artifact in the index rather than a finding.
