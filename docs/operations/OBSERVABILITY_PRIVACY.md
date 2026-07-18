# Observability Privacy Policy

## Principle

Operational visibility must never recreate the private data the product promises not to collect.

## Allowlisted telemetry

- Service and version.
- Deployment environment.
- Route template, not raw URL.
- Status class.
- Duration and bounded size bands.
- Error code enum.
- Evidence category enum.
- Replay/duplicate outcome enum.
- Queue lag and aggregate freshness.
- Pseudonymous identifiers only where necessary.

## Forbidden telemetry

- Prompts or responses.
- Claims as serialized payloads.
- Code, diffs, filenames, paths, repository/project names.
- Headers, cookies, access tokens, authorization data.
- User-entered free text.
- Semantic summaries, embeddings, classifications, or local findings.

## Enforcement

- Telemetry schema allowlist.
- Processor that drops unknown attributes.
- Secret/high-entropy scanning in telemetry tests.
- Retention by signal and purpose.
- Access controls and audit logging.
- Sampling that retains errors without retaining payloads.
