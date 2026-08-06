# Schema and Interface Inventory

Status: authoritative planning inventory; all entries remain blocked by P-1140F unless explicitly marked otherwise
Updated: 2026-08-06

## Purpose

This file is the canonical inventory of technical specifications, machine-readable contracts, planned implementation owners, and evidence requirements. A technical concept is incomplete unless it appears here with:

1. one normative owner;
2. one machine-readable owner or an explicit planned path;
3. one persistence or runtime owner where mutable;
4. one planning-repair owner;
5. one implementation work-unit dependency;
6. one executable-evidence requirement.

Syntax validity, schema parsing, fixture loading, symbolic race plans, prototypes, or generated types do not establish semantic correctness or implementation readiness.

## Maturity labels

- **present-blocked** — owner exists but P-1140F identifies semantic defects.
- **present-provisional** — owner exists but a decision, version, or evidence choice remains provisional.
- **planned-missing** — required technical specification does not yet exist at the listed canonical path.
- **prototype-only** — executable material exists but is not the normative implementation.
- **post-launch** — intentionally not a launch dependency.

## Authority and protocol specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| VibeProof claim, challenge, batch, gap, checkpoint, rotation, recovery, correction | `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` | `packages/schemas/vibeproof-claim-v1.cddl`; `conformance/vibeproof/v1/` | present-blocked | SR-005, SR-007; PF-001..PF-006; P epic |
| Deterministic CBOR/COSE/Ed25519 profile | VibeProof protocol | exact vectors and malformed/resource corpus | present-blocked | shadow protocol must be quarantined; independent Rust/Go codecs after P-1104 |
| Rust/Go shadow protocol | none; non-authoritative | `crates/vibeproof-core/`, `apps/api/cmd/api/`, `conformance/protocol/` | prototype-only | remove from normative/product paths under PF-001 |
| Source observation and normalized accounting | `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`; `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md` | `source-observation.schema.json`; `normalized-event.schema.json`; accounting registries | present-blocked | SR-009; PF-020..PF-024; A/V epics |
| Source receipt | `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`; `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md` | `packages/schemas/source-receipt-v1.schema.json`; `conformance/evidence/source-receipt.*.json` | present-provisional | SR-017; D-265; PF-042. Device-local, one per accounting event, records every observation and which one counted; carries no attestation under D-100. Local persistence owner remains planned-missing |
| Evidence bundle | evidence and integrity contracts | `packages/schemas/evidence-bundle-v1.cddl` | present-provisional | SR-017; D-266. At-rest and device-local; binds claim bytes, receipt, profile and arithmetic digests, provenance, privacy and equivalence. No instance-level CDDL conformance checking exists in this repository |
| Verifier appraisal result | `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`; integrity model | `packages/schemas/appraisal-result-v1.schema.json`; `conformance/evidence/appraisal-result.*.json` | present-blocked | SR-017; D-267; PF-043. Seven named dimensions, claim and bundle digests, validity and supersession. Blocked while `packages/schemas/planning-schema.sql#verifier_appraisals` holds three states the record does not use and lacks twenty fields it carries |
| Appraisal policy bundle | evidence contract | `packages/schemas/appraisal-policy-v1.schema.json`; `packages/schemas/appraisal-policy-v1.json` | present-provisional | SR-017; D-268; PF-043. Binds `evidence-profile-policy-v1.json` by digest, adds wire ordinals, the D-078 E1 limb refinement, validity, supersession and the SQL binding. Provisional until a verifier implementation digest exists to pin |

## Identity, authentication, device and continuity specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Provider capability and OAuth transactions | `docs/security/AUTHENTICATION_AND_RECOVERY.md` | OpenAPI, PostgreSQL, state registry; proposed provider registry | present-blocked | SR-006; PF-007..PF-010; O epic |
| Linked identity lifecycle | authentication contract | OpenAPI/PostgreSQL/state registry | present-blocked | exact identity targeting, loss, compromise and unlink safety |
| Account recovery | authentication contract | `packages/schemas/recovery-case-v1.schema.json`; `planning-schema.sql` `recovery_cases`; `recovery-case` machine | present-provisional | SR-006; D-320. Cooling-off, session revocation and device quarantine are check constraints; one live case per account is a partial unique index. Provisional because no API operation exposes the case, so a participant has no route to open one |
| Ranked identity and investigation | `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` | `packages/schemas/ranked-identity-v1.schema.json`; `planning-schema.sql` `ranked_identities`, `identity_investigations`, `identity_events`; `identity-investigation` machine | present-provisional | SR-006; D-321. One non-retired identity per account is enforced; one active resolved identity per person is not, and is reached through appealable cases rather than claimed as a constraint |
| Account consolidation | authentication/ranked-identity contracts; D-070 | `packages/schemas/consolidation-plan-v1.schema.json`; `planning-schema.sql` `consolidation_cases`, `consolidation_contributions`; `account-consolidation` machine | present-provisional | D-322. Claim-level contributions with original period attribution; the result object carries no combined total and the validator refuses the field name. Provisional until the ranking rebuild that consumes the contributions exists |
| Device installation, key and lineage | device/evidence contracts | `device-lineage.schema.json`; OpenAPI; SQL; state registry | present-blocked | SR-007; PF-011..PF-016; D epic |
| Challenge and continuity | VibeProof protocol | CDDL/OpenAPI/SQL | present-blocked | one lineage-scoped authority and identifier vocabulary |
| Fork/clone resolution | integrity/threat models; D-072 | `packages/schemas/fork-resolution-v1.schema.json`; `planning-schema.sql` `lineage_fork_cases`, `lineage_fork_branches`; `lineage-fork-case` machine | present-provisional | D-323. Every branch is recorded, a resumed generation is strictly later than the fork generation, one survivor per case is a partial unique index, and `unresolved` stays appealable. Provisional because no detector produces a case |
| Exact mutation idempotency | authoritative state contract; D-075 | OpenAPI/SQL/state/reason/policy | present-blocked | SR-012; PF-025..PF-027; S epic |

## Native runtime and local trust specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Daemon, collector, sync, shell and CLI boundaries | native runtime contracts; ADR-010/012/013 | `local-control-v1.proto`; platform/state registries | present-blocked | SR-008; PF-017..PF-019; N epic |
| Interactive shell lifecycle | native client/daemon contract | state registry | present-blocked | lifecycle must contain process/connection only; subsystem states are projections |
| Local IPC handshake and capabilities | native runtime contract | `local-control-v1.proto` | present-blocked | OS peer, artifact identity, generation, daemon-assigned role, nonce/sequence and revocation |
| Local persistence | native runtime/storage contract | `packages/schemas/local-store-v1.sql` | present-provisional | D-324. SQLite with WAL and full synchronous durability, one writer, no key column anywhere, commitment before offer, outbox, acknowledged checkpoints and a per-device deletion receipt that records residual risk. Provisional because the migration profile is stated in prose and no migration file exists |
| Platform supervision | ADR-010/011/012 | platform-profile registry | present-blocked | exact OS mechanisms, restart guarantees and honest weaker-profile labels |
| Presence pulse and visibility | product/privacy contracts; D-073 | `packages/schemas/presence-pulse-v1.schema.json`; `planning-schema.sql` `presence_leases`, `presence_events` | present-provisional | D-325. Native-only qualifying pulses, a lease generation that stops a resumed process reviving an expired lease, visibility as a policy rather than a state, and the three thresholds bound to policy keys by value. Provisional because two of those policy keys are misnamed and are not renamed here |

## Adapter, accounting and certification specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Adapter capability manifest | universal compatibility contract | adapter manifest schema and registry | present-blocked | capability declaration must not imply certification |
| Per-adapter integration contract | `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` for `claude-code-otel`; one file per adapter thereafter | agent registry `capability` block; `conformance/adapters/claude-code-otel/` fixtures | present-blocked | receive surface, environment, attribute allowlist and D-099 strip list, stage mapping, degraded-fallback bounds and certification tuple; binds `cloud-separate-cache-v1` until PF-041 registers a narrower profile |
| Atomic compatibility tuple | universal compatibility/evidence contracts | `packages/schemas/compatibility-tuple-v1.schema.json`; `planning-schema.sql` `source_certifications` | present-provisional | D-327. Artifact digest, bounded source version range, observation mode taken from the equivalence rule rather than respelled, platform profile, accounting digests and privacy binding. Provisional because no fixture yet proves two orderings of one tuple produce one digest |
| Certification result bundle | evidence contract | `packages/schemas/certification-result-v1.schema.json`; `planning-schema.sql` `certification_results` | present-provisional | D-328. Exact tuple digest, suite manifest digest, per-case outcomes, validity, COSE signer and revocation; a pass with no negative case is unrepresentable. Provisional because no suite has been run and no bundle has been signed |
| Certification lifecycle/revocation | universal compatibility contract | `source-certification` machine; `planning-schema.sql` `source_certifications` | present-provisional | D-328. All eight states, with any state other than `active` pinned to a private-analytics ceiling by both the schema and a check constraint. Provisional because every certification reachable today is `candidate` and no API surface publishes the state |
| Accounting profile | accounting contract | accounting schema and registry | present-provisional | PF-040; D-261/D-262. Profiles now carry `component_map` and real canonical digests, and the retry/cancel/nested enums have defined behaviour. Provisional because three planning profiles are registered and no certified source binds one |
| Accounting arithmetic | `docs/product/TOKEN_ACCOUNTING_SPEC.md` | `packages/schemas/accounting-arithmetic-v1.json`; `conformance/accounting/arithmetic-vectors-v1.json` | present-provisional | PF-040; D-260/D-261/D-263. Domain, order, overflow, containment, rounding, digest and correction semantics; the planning validator recomputes every vector. Two independent language implementations remain outstanding |
| Multi-observer deduplication | accounting/integrity contracts | `packages/schemas/observer-equivalence-v1.json`; `conformance/accounting/dedup-vectors-v1.json` | present-provisional | PF-051; D-269. Server-owned preimage, three equivalence classes, exclusivity unit and survivor order across direct, proxy, ACP, OTel, subagent and live-log observation. Provisional until the key-derivation function is exercised rather than declared |
| ACP accounting profile | universal compatibility contract | `packages/schemas/producer-accounting-binding-v1.schema.json`; `conformance/accounting/producer-bindings-v1.json#generic-acp-v1` | present-provisional | D-264. Generic ACP is `uncertified` and its effective ceiling is `private-analytics` by schema constraint. No ACP source version range is pinned yet |
| OpenTelemetry accounting profile | universal compatibility contract | `packages/schemas/producer-accounting-binding-v1.schema.json`; `conformance/accounting/producer-bindings-v1.json`; `conformance/accounting/otel-capture-vectors-v1.json` | present-provisional | PF-041; D-264. Binds schema URL, semantic-conventions version, instrumentation scope, metric shape, reset detection and attribute disposition. `claude-code-otel-v1` is `candidate`, so its effective ceiling is `private-analytics`; the schema URL and conventions version are null because the measured producer emits neither |
| SLM detector | D-053 | local detector result schema | post-launch | advisory only; cannot alter totals, evidence class or enforcement directly |

## Server state, ranking and social specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Public API | authoritative state contract | `openapi-v1.yaml` | present-blocked | SR-006..SR-017; YAML under D-140; no generated production clients yet |
| PostgreSQL model | authoritative state contract | `planning-schema.sql` | present-blocked | named owners, keys and vocabularies must align before migrations |
| Mutable-state registry | authoritative state contract | state-machine registry and schema | present-blocked | every state reachable; every owner exists; no hidden mappings |
| Reason and policy registries | owning domain contracts | reason/policy JSON registries | present-blocked | add stable domain outcomes and accepted D-070..D-077 defaults |
| Ranking definition and audience | product/ranking contracts | ranking-view schema plus proposed audience schema | present-blocked | SR-010; public global only; viewer-relative current authorization |
| Ranking generation, entries and snapshot | `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`; `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md` | `ranking-generation-v1.schema.json`; `planning-schema.sql` `ranking_projection_generations`, `ranking_entries`, `score_snapshots` | present-blocked | D-211, D-212; generations are sealed once and cursors anchor on position; SR-010 and SR-015 remain open and the OpenAPI half is unbuilt |
| Period and season lifecycle | product/ranking contract | `period-calendar-v1.schema.json`; `planning-schema.sql` `seasons`, `periods` | present-blocked | D-088; boundary order is a check-constraint chain from end through freeze, close, appeal window and archive; no calendar instance is populated |
| Score contribution and correction | accounting/ranking contracts; D-070 | `score-contribution-v1.schema.json`; `planning-schema.sql` `score_contributions` | present-blocked | claim-level explainability survives an erasure with the claim reference cleared; consolidation carries claim-level deltas rather than summed totals |
| Movement, overtake and streak events | product contract | `ranking-event-v1.schema.json`; `planning-schema.sql` `ranking_movement_events` | present-blocked | each event cites two sealed generations; duplicate suppression is a unique constraint; retraction is appended |
| Friendship, directional block and rivalry | product/privacy contracts | OpenAPI/SQL/state/events | present-blocked | separate aggregates and generations |
| Board membership, roles and ownership | product contract; D-071 | OpenAPI/SQL/state/events | present-blocked | non-privileged invitation; separate audited promotion/transfer |
| Notifications | product/privacy contracts | proposed source-event, inbox, delivery-attempt and preference schemas | planned-missing | server inbox authority; transport is best-effort hint |
| Moderation and appeal effects | product/integrity contracts | OpenAPI/SQL/state/events | present-blocked | exact reversible effect and ranking/notification corrections |

## Data rights, privacy and observability specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Privacy boundary and egress | privacy contracts | egress and observability allowlists; canary fixtures | present-blocked | all new server/native records require classification and egress review |
| Current viewer authorization | privacy contract | `packages/schemas/projection-authorization-v1.schema.json`; `packages/schemas/projection-authorization-v1.json` | present-provisional | SR-015; D-326. Nine inputs each naming a table and a revision column the validator resolves, a fixed deny-before-widen order, no authorization-result cache, revision recheck and fail-closed. This names the rule; no surface evaluates it, so SR-015 is advanced and remains open |
| Export request, snapshot and package | privacy/product contracts | export manifest plus proposed request/snapshot/artifact/grant schemas | present-blocked | SR-013; coherent encrypted self-describing export |
| Hosted deletion plan/effects | `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md`; ADR-022 | `erasure-record-v1.schema.json`; `planning-schema.sql` `erasure_keys`, `erasure_domains`, `erasure_records`, `erasure_restore_receipts`, `deletion_tombstones` | present-blocked | D-085, D-210..D-214; SR-013 remains open and this supplies its deletion and backup half only; no restore drill has been run |
| Per-device deletion | native/privacy contracts; D-076 | proposed command and execution-receipt schemas | planned-missing | independent device status; no forensic-erasure claim |
| Data disposition registry | privacy contract | `data-disposition-v1.json`; `data-disposition-v1.schema.json` | present-blocked | D-216; one row per persistence owner, every window resolving to a policy key or a named rule, every `expires_at` naming its actor; no sweeper exists |
| Retention and legal hold | privacy/operations contracts | `policy-defaults-v1.json`; `data-disposition-v1.json` | present-blocked | windows are machine-readable and validated; legal hold has no expression in either registry |
| Telemetry and logs | privacy/operations contracts | observability allowlist | present-blocked | fixed allowlist, no content-derived values and bounded retention |
| Application logging form | `docs/operations/LOGGING_AND_INSTRUMENTATION.md`; D-236 | observability allowlist, scope extended to log fields | present-provisional | static message literals, server-generated correlation identifier, salted principal references; no runtime emits a line yet |
| Emitted signal inventory | `docs/operations/LOGGING_AND_INSTRUMENTATION.md`; D-237 | observability allowlist attributes; proposed metric registry | present-provisional | eighteen named metrics and four span boundaries; no export backend, no instrumented service |

## Release, packaging and operations specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| TUF trust and trusted client state | operations contract; ADR-013 | `packages/schemas/tuf-trust-v1.schema.json`; `planning-schema.sql` `tuf_roots`, `tuf_metadata` | present-provisional | SR-014; D-330. Role policy with offline root and targets keys, per-role expiry resolving to the D-239 cadences, and a per-device trusted state whose check constraints refuse metadata below threshold or at or below the trusted version. Provisional because no repository is published, no hostile-metadata fixture has been run, and D-091 leaves the root threshold at one. SR-014 is advanced and remains open |
| Release manifest and components | operations contract | release-set schema | present-blocked | authenticated target, component IDs, paths, hashes, provenance and native signing |
| Compatibility graph | operations/native contracts | `packages/schemas/compatibility-graph-v1.schema.json`; `planning-schema.sql` `compatibility_edges` | present-provisional | D-331. Six independently versioned interfaces, half-open ranges so an empty range is unrepresentable, `breaking` recorded rather than derived, and a sunset refused without a deprecation notice or a named D-234 carve-out. Provisional because one major version exists on every interface, so the graph has nothing to reject yet |
| Migration and rollback | operations/native contracts; D-074 | `packages/schemas/migration-chain-v1.schema.json`; `planning-schema.sql` `storage_migrations` | present-provisional | D-332. Three rollback classes, a snapshot digest required by constraint on the class that needs one, and `down_sql_present` kept separate from reversibility because a down section that drops a column back is not a rollback. Provisional because no migration file exists and no chain has been applied |
| Platform installation plans | native/release contracts | `packages/schemas/install-plan-v1.schema.json`; `planning-schema.sql` `platform_install_plans`, `platform_install_operations` | present-provisional | D-329. Ten typed operations and eight reversals, each operation naming its exact OS mechanism, signature verification fixed at sequence 1 in both directions. Provisional because no plan instance is registered for any of the thirty-four platform profiles |
| Support/certification publication | universal compatibility/operations contracts | compatibility registry | present-blocked | only active non-expired exact tuples are advertised |
| Deployment and operations | operations contract | future infrastructure and runbook artifacts | planned-missing | after P-1104; no deployment automation during planning |
| Open-source release | operations contract; D-033/D-040 | future governance/release checklist | planned-missing | license/dependency review, security policy, contribution path and public docs |
| Environments and promotion | `docs/operations/ENVIRONMENTS_AND_SECRETS.md`; D-238 | future deployment workflow definitions | present-provisional | four environments, no staging; the restore drill runs in an ephemeral `ci` database |
| Secrets custody and rotation | `docs/operations/ENVIRONMENTS_AND_SECRETS.md`; D-239 | provider secret store selected under ADR-017 | present-provisional | cadence per class; dual control unsatisfiable under D-091 and recorded as such |
| Service expectations and alerting | `docs/operations/SLOS_AND_ALERTS.md`; D-263 | policy registry thresholds; future alert definitions | present-provisional | four commitments, six observations; recovery-point conflict owned by D-094 and open |
| Local development environment | `docs/engineering/LOCAL_DEVELOPMENT.md`; D-264 | proposed `compose.yaml` and `make` targets | planned-missing | specification only; the file lands with the first service |

## API edge, origin and time specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Rate-limit classes and quotas | `docs/architecture/API_EDGE_CONTRACT.md`; D-232 | `packages/schemas/policy-defaults-v1.json`; `RATE_LIMIT_EXCEEDED` in `packages/schemas/reason-codes-v1.json` | present-provisional | quotas are planning figures derived from a 200-participant population and no limiter exists |
| API versioning and deprecation | `docs/architecture/API_EDGE_CONTRACT.md`; D-234 | OpenAPI `deprecated` flags; `api_deprecation_window_days` | present-provisional | OpenAPI declares no deprecation flag and no `Sunset` header on any operation |
| Client retry, backoff and budgets | `docs/architecture/API_EDGE_CONTRACT.md`; D-233 | `packages/schemas/policy-defaults-v1.json`; `x-idempotency-contract` in `packages/schemas/openapi-v1.yaml` | present-blocked | the wire half of exact replay landed under D-225; the persistence half is unrepaired and SR-012 stays open |
| Origin validation and loopback controls | `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`; D-230, D-231 | proposed CORS and loopback listener configuration | planned-missing | OpenAPI declares no `Origin` parameter and no preflight response |
| Clock synchronization and skew bounds | `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`; D-235 | `packages/schemas/policy-defaults-v1.json` | present-blocked | the CDDL carries `time_uncertainty_ms` but no clock-domain identifier or generation counter |
| Test strategy and load scenarios | `docs/verification/TEST_STRATEGY.md`; D-260, D-261 | `scripts/ci/coverage-baseline-v1.json`; proposed load scripts | planned-missing | no coverage number has ever been measured, so the floors have no baseline |
| Conformance harness | `docs/verification/CONFORMANCE_HARNESS.md`; D-262 | proposed per-suite `manifest.json` and runners | planned-missing | no manifest and no runner exists in any suite |

## Hosted web and design-system specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Product routes and UX | product specification | OpenAPI and future generated clients | present-blocked | web remains fixture-backed until integration |
| Design system | approved design direction and `assets/` | shared UI components/tokens | prototype-only | preserve canonical assets and accessibility requirements |
| Privacy/evidence disclosures | product/privacy contracts | `packages/schemas/disclosure-projection-v1.schema.json`; `packages/schemas/disclosure-projection-v1.json` | present-provisional | D-333. Every property of seven API schemas classified by audience and by the observed-versus-derived line D-108 uses, resolved against the OpenAPI document, with no field permitted to be narrower than the shape carrying it and the four D-144 figures pinned to `self` by name. Provisional because no client reads it; `packages/ui` remains fixture-backed |
| Exceptional states | owning state machines | `packages/schemas/ui-state-projection-v1.schema.json`; `packages/schemas/ui-state-projection-v1.json` | present-provisional | D-334. All eight states, each either client-local or resolved to a registered machine's declared states or to a viewer-authorization input. Provisional because no surface renders any of them and no generated UI mapping exists |

## Required specification qualities

Every specification family must define, where applicable:

- identifiers and canonical encoding;
- field authority and trusted actor;
- lifecycle and reachable transitions;
- persistence owner and uniqueness/foreign-key invariants;
- transaction and idempotency boundary;
- concurrency, crash and ambiguous-commit behavior;
- privacy classification, retention, export, deletion and backup treatment;
- versioning, compatibility, migration and rollback;
- stable public-safe reason codes;
- observability allowlist and forbidden fields;
- positive, negative, adversarial, resource and race fixtures;
- implementation owner and dependency;
- launch certification or evidence gate.

## Conversion order

1. Repair the normative owner and accepted decisions.
2. Create or repair the machine owner listed here.
3. Align OpenAPI, CDDL/Protobuf/JSON Schema, SQL, state, reason and policy vocabularies.
4. Add planning-safe positive, negative, adversarial, resource and race fixtures.
5. Run structural validators without claiming semantic proof.
6. Obtain exact-head manual semantic review with zero P0/P1 findings.
7. Obtain explicit P-1104 implementation authorization.
8. Pin generators and create reproducible bindings/migrations.
9. Implement through the canonical PR-sized work units.
10. Attach executable evidence before advertising support or launch readiness.

## Completeness rule

A technical specification is not considered “there” merely because prose mentions the concept. It is complete at planning level only when this inventory names its normative owner, machine owner, lifecycle/persistence authority, repair dependency, implementation dependency, and evidence gate. `planned-missing` entries are explicit P-1140F obligations and may not be silently implemented from developer judgment.