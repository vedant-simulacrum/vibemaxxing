# Schema and Interface Inventory

Status: validated planning-grade inventory
Updated: 2026-07-19

## Authoritative planning artifacts

| Interface | Format | Path | Planning status | Implementation conversion |
|---|---|---|---|---|
| Adapter manifest | JSON Schema 2020-12 | `packages/schemas/adapter-manifest.schema.json` | validated with positive fixture | generate Rust/types and runtime validation |
| Normalized event | JSON Schema 2020-12 | `packages/schemas/normalized-event.schema.json` | validated with positive and privacy-negative fixtures | generate/reference Rust type and property fixtures |
| VibeProof claim | CDDL | `packages/schemas/vibeproof-claim-v1.cddl` | parsed and required rules verified | exact-byte vectors and independent codecs |
| COSE profile | ADR/protocol prose | VibeProof contract and ADR-007 | specified | cryptographic conformance vectors |
| Local IPC | Protobuf | `packages/schemas/local-control-v1.proto` | compiled | Buf module, generated clients and breaking checks |
| Notification/moderation/appeal events | Protobuf | `packages/schemas/social-integrity-events-v1.proto` | compiled | generated clients and idempotency tests |
| Public API | OpenAPI 3.1 | `packages/schemas/openapi-v1.yaml` | validated; every launch-critical family covered | generated clients, authorization and contract tests |
| PostgreSQL model | SQL planning DDL | `packages/schemas/planning-schema.sql` | loaded in PostgreSQL 16; all logical groups covered | ordered executable migration history |
| Reason codes | JSON registry | `packages/schemas/reason-codes-v1.json` | parsed, unique and cross-linked | expand with implementation errors without reuse |
| Configurable defaults | JSON registry | `packages/schemas/policy-defaults-v1.json` | parsed, ranged, owned and cross-checked | typed loader, persisted versions and admin controls |
| Observability | YAML allowlist | `packages/schemas/observability-allowlist-v1.yaml` | parsed and cross-checked against policy retention | enforcement and privacy canaries |
| Agent support | JSON registry + schema | `conformance/adapters/agent-registry-v1.*` | validated planning registry | populate certifications only after exercised tests |
| Adversarial cases | JSON registry + schema | `conformance/adversarial/anti-cheat-registry-v1.*` | validated planning registry | implement fixture corpus and runners |

## Compatibility

- JSON Schema trust boundaries reject unknown fields unless an explicit extension point exists.
- VibeProof uses protocol-major negotiation and ADR-007 atomic batch semantics.
- Protobuf follows additive evolution within a major version and future Buf breaking checks.
- OpenAPI `/v1` changes are additive unless a new API major is introduced.
- Planning SQL is a validated logical model, not an executable migration history; implementation uses expand/migrate/contract.
- Stable reason codes are never reused.
- Policies and certification decisions persist their version with resulting records.

## Validation evidence

P-1120 is complete. The full workflow passed JSON Schema, examples, registries, OpenAPI, CDDL, Protobuf, PostgreSQL 16 DDL, policy/observability consistency, launch-critical API/SQL coverage and repository-doctor checks. See `PLANNING_HARDENING_VALIDATION_REPORT.md`.

These artifacts do not prove runtime correctness, cryptographic interoperability, migration safety under production load, performance, platform isolation or product compatibility. Those remain implementation evidence.
