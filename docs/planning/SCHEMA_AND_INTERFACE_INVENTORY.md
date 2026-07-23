# Schema and Interface Inventory

Status: current repair index; P-1140D candidate present, P-1140E cross-validation pending
Updated: 2026-07-24

## Authority and use

`packages/schemas/` owns the planning-grade source interfaces. Syntax validation, successful parsing, fixture loading or PostgreSQL loading proves only that an artifact is structurally processable. It does not make the artifact semantically coherent, implementation-ready or production-proven.

The July 23 repository audit superseded the earlier blanket “validated planning-grade” conclusion. P-1140B through P-1140E now own semantic repair and cross-contract validation. No production bindings, migrations or policy engines may be generated from a blocked artifact.

## Current artifact status

| Interface | Path | Structural evidence | Current semantic status | Repair owner |
|---|---|---|---|---|
| Adapter manifest | `packages/schemas/adapter-manifest.schema.json` | JSON Schema + updated positive fixture | P-1140B repaired planning contract: artifact/manifest/provenance/SBOM digests, exact certification, accounting profiles and capability ceiling are closed-world | P-1140B complete; P-1140E cross-validation |
| Local data stages | `source-observation.schema.json`, `normalized-event.schema.json`, `local-detector-result.schema.json` | JSON Schema + positive/negative examples | P-1140B repaired planning contract: L0/L1 roles, retention/direction, typed counts/time/dedup/rules and `network_eligible=false` are explicit | P-1140B complete; P-1140E cross-validation |
| VibeProof protocol records | `vibeproof-claim-v1.cddl`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` | CDDL parse plus fixed Ed25519 vectors and malformed/resource registry | P-1140C repaired planning contract: claim/appraisal/receipt/challenge/batch/gap/rotation/correction, numeric limits and closed labels are mutually mapped | P-1140C complete; P-1140E independent codecs |
| COSE profile | VibeProof protocol + `conformance/vibeproof/v1/` | protected/payload/Sig_structure/signature/COSE exact bytes and Ed25519 verification | P-1140C repaired planning contract: mandatory tag 18, empty unprotected map, EdDSA, content type, raw UUID kid, protocol header and exact external AAD | P-1140C complete; P-1140E independent codecs |
| Local IPC | `packages/schemas/local-control-v1.proto` | Protobuf compilation + opaque-payload guard | P-1140B repaired planning contract: typed observation/ack/claim/queue/receipt/export/deletion bodies with role, nonce, sequence and deadline | P-1140B complete; P-1140E cross-validation; protocol bytes in P-1140C |
| State and platform authority | `state-machine-registry-v1.*`, `platform-profile-registry-v1.*`, `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` | JSON Schema instance validation, transition reference checks and exact failure-matrix checks | P-1140D candidate: 23 mutable-state authorities and exact launch platform tuples, all uncertified/unadvertised | P-1140D candidate; P-1140E execution matrix |
| Release/ranking/export records | `release-set-v1.schema.json`, `ranking-view-v1.schema.json`, `export-manifest-v1.schema.json` | JSON Schema metaschema validation | P-1140D candidate: signed release sets, immutable ranking views and typed export contents are closed-world | P-1140D candidate; P-1140E fixtures |
| Social/integrity events | `packages/schemas/social-integrity-events-v1.proto` | Protobuf compilation + opaque-field guard | P-1140D candidate: closed event union for canonical relationship, board, presence, notification, moderation, appeal and retraction facts | P-1140D candidate; P-1140E fixtures |
| Public API | `packages/schemas/openapi-v1.yaml` | OpenAPI 3.1 validation + authority/idempotency/rate-limit guards | P-1140D candidate: endpoint-specific closed resources, typed problems, CBOR claim batch, ranking views and deletion semantics | P-1140D candidate; P-1140E fixtures |
| PostgreSQL model | `packages/schemas/planning-schema.sql` | PostgreSQL 16 clean-schema load + ownership/constraint guards | P-1140D repaired planning migration contract: typed session, lineage, appraisal, receipt, idempotency, ranking, social, deletion and release state | P-1140D candidate; P-1140E race plans |
| Reason codes | `packages/schemas/reason-codes-v1.json` | parse, uniqueness, reference and authority-field checks | P-1140D candidate: subsystem, retry, safe message, internal visibility, severity, appeal, owning state machine and lifecycle are explicit | P-1140D candidate; P-1140E references |
| Policy defaults | `packages/schemas/policy-defaults-v1.json` | parse, range, owner and lifecycle-field checks | P-1140D candidate: type, unit, effective time, prospective/rebuild/notice and emergency override semantics are explicit | P-1140D candidate; P-1140E fixtures |
| Privacy egress | `egress-allowlist-v1.*`, `conformance/privacy/p1140b-boundary-canaries-v1.json`, observability allowlist | JSON Schema/registry plus positive/negative boundary coverage | P-1140B claim egress candidate repaired; P-1140D must extend typed server/social/reviewer state boundaries without weakening it | P-1140B complete; P-1140E cross-validation/P-1140D |
| Accounting profiles | `accounting-profile.schema.json`, `conformance/accounting/` | Schema, registry and representative cases | P-1140B repaired planning contract: containment and mutually exclusive outputs cover cloud/local, cache, reasoning, retry, cancellation and contradiction | P-1140B complete; P-1140E cross-validation |
| Evidence appraisal policy | `evidence-profile-policy-v1.json` | Parsed policy plus authority/downgrade validation | P-1140B repaired planning contract: independent dimensions and server-owned downgrade order | P-1140B complete; P-1140E cross-validation |
| Device lineage | `device-lineage.schema.json` | JSON Schema structural validation | P-1140B repaired planning contract: enroll/rotate/recover/restore/clone/requalify dispositions | P-1140B complete; P-1140E cross-validation; transaction state in P-1140D |
| Pricing interpretation | `pricing-interpretation.schema.json` | JSON Schema structural validation | P-1140B repaired planning contract: immutable server-owned alias resolution and line items; claims have no pricing authority | P-1140B complete; P-1140E cross-validation/P-1140D persistence |
| Agent support registry | `conformance/adapters/agent-registry-v1.*` | registry/schema validation existed | planning registry only; empty or planned certification records make no support claim | P-1140B/P-1140E |
| Adversarial registry | `conformance/adversarial/anti-cheat-registry-v1.*` | registry/schema validation existed | planning inventory only; cases are not executable evidence until runners and result bundles exist | P-1140E |
| T20 registry/evidence | `conformance/models/` | provisional planning validation exists | provisional candidate engineering input under D-046; not launch support or current certification | P-1140B/P-1140E |

## Conversion order

1. Repair the owning normative prose and decision/state authority.
2. Repair the authoritative schema in `packages/schemas/` or adjacent registry.
3. Add positive, negative, adversarial, boundary and resource fixtures.
4. Prove cross-language numeric, time, enum and unknown-field compatibility.
5. Run all planning validators from a clean checkout on the exact head.
6. After P-1104 only, select and pin generation/migration toolchains.
7. Generate reproducible bindings or ordered migrations; never hand-maintain a parallel semantic model.
8. Attach implementation and executable evidence before advertising support.

## Compatibility boundary

No draft VibeProof field has production compatibility protection under D-056. Compatibility rules for JSON Schema, Protobuf, OpenAPI, CDDL/COSE, SQL and registries become implementation authority only after their repair owner closes and P-1140E confirms cross-contract consistency.

Stable reason codes must never be reused once implementation persists them. Policy, pricing, certification, appraisal and alias decisions must persist their exact version with resulting records.

## Historical validation evidence

The July 19 workflow demonstrated syntax, parsing, fixture/reference consistency and structural PostgreSQL loading against an older planning state. `PLANNING_HARDENING_VALIDATION_REPORT.md` is explicitly historical and superseded as an implementation entrance signal.

Current validation must be attached to the exact repaired head. Even a pass proves planning structure only; it does not prove runtime behavior, cryptographic interoperability, migration safety, performance, platform isolation, certified source support, packaging, deployment, security hardening or launch readiness.
