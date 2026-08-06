# `telemetry` conformance suite

Case prefix: `TM`. Subjects: `rust`, `go`, `typescript`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That the deny-by-default allowlist is enforced by a processor rather than by a convention, across metrics, spans and structured log fields alike.

Authorities:

- `packages/schemas/observability-allowlist-v1.yaml`
- `docs/operations/OBSERVABILITY_PRIVACY.md`
- `docs/operations/LOGGING_AND_INSTRUMENTATION.md`
- `packages/schemas/egress-allowlist-v1.json`

## Required cases

- One case per entry in `forbidden_classes`: an emitted signal carrying that class, asserted dropped, with the process failing closed where the class cannot be removed rather than emitting a partial record.
- An unrecognised attribute name, asserted dropped **and flagged**, not silently passed.
- The five OTLP identity attributes of D-099 present on an inbound datapoint, asserted stripped inside the receiver before the datapoint reaches the observation queue, and asserted absent from disk, logs and crash output.
- A datapoint from which those attributes cannot be removed, asserted rejected whole.
- A log line whose `msg` is an interpolated string rather than a literal, asserted rejected by the lint stage.
- A high-entropy value in an otherwise allowed field, asserted caught by the entropy scan.
- A network address in the operational stream, asserted dropped; the same address in the security-audit stream, asserted retained.
- A captured packet trace of a full claim submission, asserted to contain only allowlisted fields.

The last case is the one that matters most and the one a schema check cannot substitute for: the privacy commitment is about what crosses the wire, and only a capture observes that.

## Status

**Nothing here executes.** No fixture, no `manifest.json`, no runner, and no instrumented service to observe. The `observability-privacy` eval suite is `not_applicable` and names `apps/api/internal/telemetry` and `evals/fixtures/observability-privacy.json` (new) as the paths whose absence justifies that status; `telemetry-canary-leakage` is `not_applicable` for the same reason. The adapter-one identity-strip canary in `conformance/adapters/claude-code-otel/` is the one telemetry assertion that does run today, enforced by `scripts/repository/validate_planning_artifacts.py`. A README is not executable evidence and this one does not change any status.
