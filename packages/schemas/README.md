# Authoritative Schemas

This directory owns planning-grade source interfaces. These files are normative for planning but are not yet production-toolchain validated.

- `adapter-manifest.schema.json`
- `normalized-event.schema.json`
- `vibeproof-claim-v1.cddl`
- `local-control-v1.proto`
- `social-integrity-events-v1.proto`
- `openapi-v1.yaml`
- `planning-schema.sql`
- `reason-codes-v1.json`
- `policy-defaults-v1.json`
- `observability-allowlist-v1.yaml`

During implementation, generated bindings must originate here and executable PostgreSQL migrations replace the planning DDL. Do not create parallel hand-maintained types.