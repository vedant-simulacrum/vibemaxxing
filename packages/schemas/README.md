# Authoritative Schemas

This directory owns planning-grade source interfaces. These files are normative for planning but are not yet production-toolchain validated.

- `accounting-profile.schema.json` — AccountingProfile v1 schema
- `adapter-manifest.schema.json` — VibeMaxxing Adapter Manifest v1 schema
- `device-lineage.schema.json` — DeviceLineageTransition v1 schema
- `egress-allowlist-v1.json` — Claim egress policy registry
- `egress-allowlist-v1.schema.json` — Outbound Egress Field Registry v1 schema
- `evidence-profile-policy-v1.json` — Evidence profile policy dimensions
- `export-manifest-v1.schema.json` — Account export manifest v1 schema
- `local-control-v1.proto` — Local control protocol v1 service definition
- `local-detector-result.schema.json` — LocalDetectorResult v1 schema
- `normalized-event.schema.json` — NormalizedAccountingEvent v1 schema
- `oauth-provider-registry-v1.json` — Preconfigured OAuth provider capability record
- `oauth-provider-registry-v1.schema.json` — OAuth provider configuration registry v1 schema
- `observability-allowlist-v1.yaml` — Observability attributes allowlist v1
- `openapi-v1.yaml` — VibeMaxxing Public API specification, written as YAML under D-140
- `planning-schema.sql` — P-1140D planning DDL contract
- `platform-profile-registry-v1.json` — Platform profile registry data
- `platform-profile-registry-v1.schema.json` — Exact Platform Profile Registry v1 schema
- `policy-defaults-v1.json` — Default configurable policies and change rules
- `pricing-interpretation.schema.json` — Server PricingInterpretation v1 schema
- `ranking-view-v1.schema.json` — Immutable ranking view identity v1 schema
- `reason-codes-v1.json` — Reason code registry with outcomes and severity
- `release-set-v1.schema.json` — VibeMaxxing signed release set v1 schema
- `social-integrity-events-v1.proto` — Social integrity events protocol v1 service
- `source-observation.schema.json` — SourceObservation v1 schema
- `state-machine-registry-v1.json` — Authoritative state machine registry data
- `state-machine-registry-v1.schema.json` — Authoritative State Machine Registry v1 schema
- `vibeproof-claim-v1.cddl` — VibeProof protocol v1 normative CDDL

Examples in `examples/`:
- `adapter-manifest.valid.json` — Valid adapter manifest example
- `normalized-event.valid.json` — Valid normalized event example
- `normalized-event.invalid-forbidden-field.json` — Invalid event with forbidden field

During implementation, generated bindings must originate here and executable PostgreSQL migrations replace the planning DDL. Do not create parallel hand-maintained types.