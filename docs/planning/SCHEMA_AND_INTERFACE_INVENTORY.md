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
| Source receipt | `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`; `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md` | `packages/schemas/source-receipt-v1.schema.json`; `conformance/evidence/source-receipt.*.json` | present-provisional | SR-017; D-245; PF-042. Device-local, one per accounting event, records every observation and which one counted; carries no attestation under D-100. Local persistence owner remains planned-missing |
| Evidence bundle | evidence and integrity contracts | `packages/schemas/evidence-bundle-v1.cddl` | present-provisional | SR-017; D-246. At-rest and device-local; binds claim bytes, receipt, profile and arithmetic digests, provenance, privacy and equivalence. No instance-level CDDL conformance checking exists in this repository |
| Verifier appraisal result | `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`; integrity model | `packages/schemas/appraisal-result-v1.schema.json`; `conformance/evidence/appraisal-result.*.json` | present-blocked | SR-017; D-247; PF-043. Seven named dimensions, claim and bundle digests, validity and supersession. Blocked while `packages/schemas/planning-schema.sql#verifier_appraisals` holds three states the record does not use and lacks twenty fields it carries |
| Appraisal policy bundle | evidence contract | `packages/schemas/appraisal-policy-v1.schema.json`; `packages/schemas/appraisal-policy-v1.json` | present-provisional | SR-017; D-248; PF-043. Binds `evidence-profile-policy-v1.json` by digest, adds wire ordinals, the D-078 E1 limb refinement, validity, supersession and the SQL binding. Provisional until a verifier implementation digest exists to pin |

## Identity, authentication, device and continuity specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Provider capability and OAuth transactions | `docs/security/AUTHENTICATION_AND_RECOVERY.md` | OpenAPI, PostgreSQL, state registry; proposed provider registry | present-blocked | SR-006; PF-007..PF-010; O epic |
| Linked identity lifecycle | authentication contract | OpenAPI/PostgreSQL/state registry | present-blocked | exact identity targeting, loss, compromise and unlink safety |
| Account recovery | authentication contract | proposed recovery-case schema and SQL authorities | planned-missing | SR-006; cooling-off, notification, session/device effects |
| Ranked identity and investigation | `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` | proposed ranked-identity, investigation and event persistence | planned-missing | SR-006; one active resolved ranked identity |
| Account consolidation | authentication/ranked-identity contracts; D-070 | proposed consolidation case, plan and result schemas | planned-missing | claim-level recomputation; no stored-total summation |
| Device installation, key and lineage | device/evidence contracts | `device-lineage.schema.json`; OpenAPI; SQL; state registry | present-blocked | SR-007; PF-011..PF-016; D epic |
| Challenge and continuity | VibeProof protocol | CDDL/OpenAPI/SQL | present-blocked | one lineage-scoped authority and identifier vocabulary |
| Fork/clone resolution | integrity/threat models; D-072 | proposed fork case, survivor decision and requalification result | planned-missing | quarantine all post-fork branches; appealable |
| Exact mutation idempotency | authoritative state contract; D-075 | OpenAPI/SQL/state/reason/policy | present-blocked | SR-012; PF-025..PF-027; S epic |

## Native runtime and local trust specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Daemon, collector, sync, shell and CLI boundaries | native runtime contracts; ADR-010/012/013 | `local-control-v1.proto`; platform/state registries | present-blocked | SR-008; PF-017..PF-019; N epic |
| Interactive shell lifecycle | native client/daemon contract | state registry | present-blocked | lifecycle must contain process/connection only; subsystem states are projections |
| Local IPC handshake and capabilities | native runtime contract | `local-control-v1.proto` | present-blocked | OS peer, artifact identity, generation, daemon-assigned role, nonce/sequence and revocation |
| Local persistence | native runtime/storage contract | proposed local SQL schema and migration profile | planned-missing | encrypted stores, commitment/receipt/outbox, crash consistency and deletion |
| Platform supervision | ADR-010/011/012 | platform-profile registry | present-blocked | exact OS mechanisms, restart guarantees and honest weaker-profile labels |
| Presence pulse and visibility | product/privacy contracts; D-073 | proposed presence-pulse, lease-generation and audience projection schemas | planned-missing | native-only qualifying pulses; server-derived active/idle/offline |

## Adapter, accounting and certification specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Adapter capability manifest | universal compatibility contract | adapter manifest schema and registry | present-blocked | capability declaration must not imply certification |
| Per-adapter integration contract | `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` for `claude-code-otel`; one file per adapter thereafter | agent registry `capability` block; `conformance/adapters/claude-code-otel/` fixtures | present-blocked | receive surface, environment, attribute allowlist and D-099 strip list, stage mapping, degraded-fallback bounds and certification tuple; binds `cloud-separate-cache-v1` until PF-041 registers a narrower profile |
| Atomic compatibility tuple | universal compatibility/evidence contracts | proposed compatibility-tuple schema | planned-missing | artifact, source/version, mode, platform, profile and privacy binding |
| Certification result bundle | evidence contract | proposed signed certification-result schema | planned-missing | exact tuple, suite, result, validity, signer and revocation |
| Certification lifecycle/revocation | universal compatibility contract | proposed registry/state authority | planned-missing | candidate/testing/active/degraded/suspended/expired/superseded/retired |
| Accounting profile | accounting contract | accounting schema and registry | present-provisional | PF-040; D-241/D-242. Profiles now carry `component_map` and real canonical digests, and the retry/cancel/nested enums have defined behaviour. Provisional because three planning profiles are registered and no certified source binds one |
| Accounting arithmetic | `docs/product/TOKEN_ACCOUNTING_SPEC.md` | `packages/schemas/accounting-arithmetic-v1.json`; `conformance/accounting/arithmetic-vectors-v1.json` | present-provisional | PF-040; D-240/D-241/D-243. Domain, order, overflow, containment, rounding, digest and correction semantics; the planning validator recomputes every vector. Two independent language implementations remain outstanding |
| Multi-observer deduplication | accounting/integrity contracts | `packages/schemas/observer-equivalence-v1.json`; `conformance/accounting/dedup-vectors-v1.json` | present-provisional | PF-051; D-249. Server-owned preimage, three equivalence classes, exclusivity unit and survivor order across direct, proxy, ACP, OTel, subagent and live-log observation. Provisional until the key-derivation function is exercised rather than declared |
| ACP accounting profile | universal compatibility contract | `packages/schemas/producer-accounting-binding-v1.schema.json`; `conformance/accounting/producer-bindings-v1.json#generic-acp-v1` | present-provisional | D-244. Generic ACP is `uncertified` and its effective ceiling is `private-analytics` by schema constraint. No ACP source version range is pinned yet |
| OpenTelemetry accounting profile | universal compatibility contract | `packages/schemas/producer-accounting-binding-v1.schema.json`; `conformance/accounting/producer-bindings-v1.json`; `conformance/accounting/otel-capture-vectors-v1.json` | present-provisional | PF-041; D-244. Binds schema URL, semantic-conventions version, instrumentation scope, metric shape, reset detection and attribute disposition. `claude-code-otel-v1` is `candidate`, so its effective ceiling is `private-analytics`; the schema URL and conventions version are null because the measured producer emits neither |
| SLM detector | D-053 | local detector result schema | post-launch | advisory only; cannot alter totals, evidence class or enforcement directly |

## Server state, ranking and social specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Public API | authoritative state contract | `openapi-v1.yaml` | present-blocked | SR-006..SR-017; YAML under D-140; no generated production clients yet |
| PostgreSQL model | authoritative state contract | `planning-schema.sql` | present-blocked | named owners, keys and vocabularies must align before migrations |
| Mutable-state registry | authoritative state contract | state-machine registry and schema | present-blocked | every state reachable; every owner exists; no hidden mappings |
| Reason and policy registries | owning domain contracts | reason/policy JSON registries | present-blocked | add stable domain outcomes and accepted D-070..D-077 defaults |
| Ranking definition and audience | product/ranking contracts | ranking-view schema plus proposed audience schema | present-blocked | SR-010; public global only; viewer-relative current authorization |
| Ranking generation, entries and snapshot | ranking contract | proposed generation/entry/snapshot schemas and SQL | planned-missing | immutable retained generations and durable cursors |
| Period and season lifecycle | product/ranking contract | proposed calendar/period/season registry | planned-missing | exact boundaries, delayed claims, freeze, close, appeal and archive |
| Score contribution and correction | accounting/ranking contracts; D-070 | proposed contribution and correction manifest | planned-missing | claim-level explainability and consolidation/retraction |
| Movement, overtake and streak events | product contract | proposed typed event schemas | planned-missing | exact prior/current snapshots and correction retraction |
| Friendship, directional block and rivalry | product/privacy contracts | OpenAPI/SQL/state/events | present-blocked | separate aggregates and generations |
| Board membership, roles and ownership | product contract; D-071 | OpenAPI/SQL/state/events | present-blocked | non-privileged invitation; separate audited promotion/transfer |
| Notifications | product/privacy contracts | proposed source-event, inbox, delivery-attempt and preference schemas | planned-missing | server inbox authority; transport is best-effort hint |
| Moderation and appeal effects | product/integrity contracts | OpenAPI/SQL/state/events | present-blocked | exact reversible effect and ranking/notification corrections |

## Data rights, privacy and observability specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Privacy boundary and egress | privacy contracts | egress and observability allowlists; canary fixtures | present-blocked | all new server/native records require classification and egress review |
| Current viewer authorization | privacy contract | proposed projection-authorization revision profile | planned-missing | SR-015; display/delivery always rechecks current blocks/privacy/membership |
| Export request, snapshot and package | privacy/product contracts | export manifest plus proposed request/snapshot/artifact/grant schemas | present-blocked | SR-013; coherent encrypted self-describing export |
| Hosted deletion plan/effects | privacy/product contracts | proposed deletion plan, effect result and tombstone schemas | planned-missing | account freeze, projections, backups, legal hold and completion |
| Per-device deletion | native/privacy contracts; D-076 | proposed command and execution-receipt schemas | planned-missing | independent device status; no forensic-erasure claim |
| Data disposition registry | privacy contract | proposed domain-disposition registry | planned-missing | export/delete/anonymize/retract/retain/legal-hold/backup for every store |
| Retention and legal hold | privacy/operations contracts | policy registry additions | present-blocked | exact artifact, audit, tombstone, grant and command windows |
| Telemetry and logs | privacy/operations contracts | observability allowlist | present-blocked | fixed allowlist, no content-derived values and bounded retention |
| Application logging form | `docs/operations/LOGGING_AND_INSTRUMENTATION.md`; D-236 | observability allowlist, scope extended to log fields | present-provisional | static message literals, server-generated correlation identifier, salted principal references; no runtime emits a line yet |
| Emitted signal inventory | `docs/operations/LOGGING_AND_INSTRUMENTATION.md`; D-237 | observability allowlist attributes; proposed metric registry | present-provisional | eighteen named metrics and four span boundaries; no export backend, no instrumented service |

## Release, packaging and operations specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| TUF trust and trusted client state | operations contract; ADR-013 | proposed root/role policy and client-state schema | planned-missing | SR-014; L epic |
| Release manifest and components | operations contract | release-set schema | present-blocked | authenticated target, component IDs, paths, hashes, provenance and native signing |
| Compatibility graph | operations/native contracts | proposed compatibility schema | planned-missing | protocol/API/IPC/storage/schema/platform compatibility |
| Migration and rollback | operations/native contracts; D-074 | proposed migration-chain and rollback-class schemas | planned-missing | binary rollback only while storage remains compatible |
| Platform installation plans | native/release contracts | proposed verified install-plan schema | planned-missing | typed platform operations; not generic IPC lifecycle actions |
| Support/certification publication | universal compatibility/operations contracts | compatibility registry | present-blocked | only active non-expired exact tuples are advertised |
| Deployment and operations | operations contract | future infrastructure and runbook artifacts | planned-missing | after P-1104; no deployment automation during planning |
| Open-source release | operations contract; D-033/D-040 | future governance/release checklist | planned-missing | license/dependency review, security policy, contribution path and public docs |
| Environments and promotion | `docs/operations/ENVIRONMENTS_AND_SECRETS.md`; D-238 | future deployment workflow definitions | present-provisional | four environments, no staging; the restore drill runs in an ephemeral `ci` database |
| Secrets custody and rotation | `docs/operations/ENVIRONMENTS_AND_SECRETS.md`; D-239 | provider secret store selected under ADR-017 | present-provisional | cadence per class; dual control unsatisfiable under D-091 and recorded as such |
| Service expectations and alerting | `docs/operations/SLOS_AND_ALERTS.md`; D-243 | policy registry thresholds; future alert definitions | present-provisional | four commitments, six observations; recovery-point conflict owned by D-094 and open |
| Local development environment | `docs/engineering/LOCAL_DEVELOPMENT.md`; D-244 | proposed `compose.yaml` and `make` targets | planned-missing | specification only; the file lands with the first service |

## API edge, origin and time specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Rate-limit classes and quotas | `docs/architecture/API_EDGE_CONTRACT.md`; D-232 | `packages/schemas/policy-defaults-v1.json`; `RATE_LIMIT_EXCEEDED` in `packages/schemas/reason-codes-v1.json` | present-provisional | quotas are planning figures derived from a 200-participant population and no limiter exists |
| API versioning and deprecation | `docs/architecture/API_EDGE_CONTRACT.md`; D-234 | OpenAPI `deprecated` flags; `api_deprecation_window_days` | present-provisional | OpenAPI declares no deprecation flag and no `Sunset` header on any operation |
| Client retry, backoff and budgets | `docs/architecture/API_EDGE_CONTRACT.md`; D-233 | `packages/schemas/policy-defaults-v1.json`; `x-idempotency-contract` in `packages/schemas/openapi-v1.yaml` | present-blocked | the wire half of exact replay landed under D-225; the persistence half is unrepaired and SR-012 stays open |
| Origin validation and loopback controls | `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`; D-230, D-231 | proposed CORS and loopback listener configuration | planned-missing | OpenAPI declares no `Origin` parameter and no preflight response |
| Clock synchronization and skew bounds | `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`; D-235 | `packages/schemas/policy-defaults-v1.json` | present-blocked | the CDDL carries `time_uncertainty_ms` but no clock-domain identifier or generation counter |
| Test strategy and load scenarios | `docs/verification/TEST_STRATEGY.md`; D-240, D-241 | `scripts/ci/coverage-baseline-v1.json`; proposed load scripts | planned-missing | no coverage number has ever been measured, so the floors have no baseline |
| Conformance harness | `docs/verification/CONFORMANCE_HARNESS.md`; D-242 | proposed per-suite `manifest.json` and runners | planned-missing | no manifest and no runner exists in any suite |

## Hosted web and design-system specifications

| Specification family | Normative owner | Machine owner | Status | Repair / implementation dependency |
|---|---|---|---|---|
| Product routes and UX | product specification | OpenAPI and future generated clients | present-blocked | web remains fixture-backed until integration |
| Design system | approved design direction and `assets/` | shared UI components/tokens | prototype-only | preserve canonical assets and accessibility requirements |
| Privacy/evidence disclosures | product/privacy contracts | typed API projection schemas | planned-missing | no client-side policy invention |
| Exceptional states | owning state machines | future generated UI state mapping | planned-missing | loading, empty, blocked, private, stale, retracted, appeal and recovery states |

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