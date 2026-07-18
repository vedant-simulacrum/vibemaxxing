# Schema and Interface Inventory

Status: active planning-hardening inventory
Updated: 2026-07-19

## Authoritative draft artifacts

| Interface | Format | Path | Planning status | Implementation conversion |
|---|---|---|---|---|
| Adapter manifest | JSON Schema 2020-12 | `packages/schemas/adapter-manifest.schema.json` | draft present | generate Rust/types and validation |
| Normalized event | JSON Schema 2020-12 | `packages/schemas/normalized-event.schema.json` | draft present | generate/reference Rust type and fixtures |
| VibeProof claim | CDDL | `packages/schemas/vibeproof-claim-v1.cddl` | draft present | compile with selected CDDL/CBOR toolchain |
| COSE profile | ADR/protocol prose + future vectors | VibeProof contract and ADR-007 | specified | exact-byte vectors and independent verifiers |
| Local IPC | Protobuf | `packages/schemas/local-control-v1.proto` | draft present | Buf module and generated clients |
| Notification/moderation/appeal events | Protobuf | `packages/schemas/social-integrity-events-v1.proto` | draft present | Buf module, generated clients and idempotency tests |
| Public API | OpenAPI 3.1 | `packages/schemas/openapi-v1.yaml` | partial draft present | expand endpoint families before dependent feature work |
| PostgreSQL model | SQL planning DDL | `packages/schemas/planning-schema.sql` | partial draft present | ordered executable migration history |
| Reason codes | JSON registry | `packages/schemas/reason-codes-v1.json` | draft present | expand alongside endpoints and conformance failures |
| Configurable defaults | JSON registry | `packages/schemas/policy-defaults-v1.json` | draft present | typed loader, version persistence and controls |
| Observability | YAML allowlist | `packages/schemas/observability-allowlist-v1.yaml` | draft present | schema validation and canary enforcement |
| Agent support | JSON registry + schema | `conformance/adapters/agent-registry-v1.*` | planning registry present | populate exact certifications only after exercised tests |
| Adversarial cases | JSON registry + schema | `conformance/adversarial/anti-cheat-registry-v1.*` | planning registry present | implement fixture corpus and runners later |

## Compatibility

- JSON Schema trust boundaries reject unknown fields unless an explicit extension point exists.
- VibeProof uses protocol-major negotiation and ADR-007 atomic batch semantics.
- Protobuf follows additive evolution within a major version and future Buf breaking checks.
- OpenAPI `/v1` changes are additive unless a new API major is introduced.
- Planning SQL is not a migration history; implementation uses expand/migrate/contract.
- Stable reason codes are never reused.
- Policies and certification decisions persist their version with resulting records.

## Remaining planning validation

P-1120 remains open until:

1. all draft files parse with selected validators;
2. representative examples validate;
3. the OpenAPI and SQL drafts cover every launch-critical family at sufficient planning depth;
4. canonical references resolve;
5. the repository doctor passes from a clean checkout;
6. an independent reviewer finds no critical behavior still requiring invention.

These drafts do not prove cross-language correctness, cryptographic conformance, migration safety, performance or production compatibility.
