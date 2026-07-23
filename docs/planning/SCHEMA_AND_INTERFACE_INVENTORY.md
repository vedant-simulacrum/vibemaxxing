# Schema and Interface Inventory

Status: current repair index; planning artifacts are blocked where listed
Updated: 2026-07-24

## Authority and use

`packages/schemas/` owns the planning-grade source interfaces. Syntax validation, successful parsing, fixture loading or PostgreSQL loading proves only that an artifact is structurally processable. It does not make the artifact semantically coherent, implementation-ready or production-proven.

The July 23 repository audit superseded the earlier blanket “validated planning-grade” conclusion. P-1140B through P-1140E now own semantic repair and cross-contract validation. No production bindings, migrations or policy engines may be generated from a blocked artifact.

## Current artifact status

| Interface | Path | Structural evidence | Current semantic status | Repair owner |
|---|---|---|---|---|
| Adapter manifest | `packages/schemas/adapter-manifest.schema.json` | JSON Schema and fixture validation existed | blocked: exact artifact digest, provenance, source profile, accounting profile and capability-derived evidence ceiling remain incomplete | P-1140B |
| Normalized event | `packages/schemas/normalized-event.schema.json` | JSON Schema and privacy-negative fixture validation existed | blocked: source observation, normalized accounting, detector result, time, metadata and network-egress boundaries must be separated | P-1140B |
| VibeProof claim | `packages/schemas/vibeproof-claim-v1.cddl` | CDDL parsing and structural checks existed | blocked: claim/appraisal/checkpoint ownership, batch, replay, commitment, rotation, correction, numeric limits and extension semantics require an incompatible v1 rewrite | P-1140C after P-1140B |
| COSE profile | VibeProof contract and ADR-007 | prose-level profile only | blocked: exact protected headers, external AAD, key representation, signed bytes and independent vectors are incomplete | P-1140C |
| Local IPC | `packages/schemas/local-control-v1.proto` | Protobuf compilation existed | blocked: opaque JSON/bytes and incomplete process-role, method, deadline, limit and privacy semantics | P-1140B/P-1140C |
| Social/integrity events | `packages/schemas/social-integrity-events-v1.proto` | Protobuf compilation existed | blocked: canonical social, presence, notification, moderation, appeal and reversal state ownership is incomplete | P-1140D |
| Public API | `packages/schemas/openapi-v1.yaml` | OpenAPI syntax and family-coverage checks existed | blocked: endpoint resources, authorization, idempotency, quotas, ranking views, deletion and repaired state semantics remain incomplete | P-1140D |
| PostgreSQL model | `packages/schemas/planning-schema.sql` | PostgreSQL 16 structural loading existed | blocked structural inventory only: not a migration design and missing final lineage, appraisal, receipt, idempotency, ranking, social and release state | P-1140D |
| Reason codes | `packages/schemas/reason-codes-v1.json` | parse, uniqueness and reference checks existed | provisional where repaired state machines have not frozen outcomes | P-1140C/P-1140D |
| Policy defaults | `packages/schemas/policy-defaults-v1.json` | parse, range and owner checks existed | provisional where accounting, delay, identity, update and moderation policy remains under contract repair | P-1140B/P-1140D |
| Observability allowlist | `packages/schemas/observability-allowlist-v1.yaml` | YAML and retention consistency checks existed | blocked until every local, privileged, network, review and support boundary has a fixed allowlist and privacy canaries | P-1140B/P-1140D |
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
