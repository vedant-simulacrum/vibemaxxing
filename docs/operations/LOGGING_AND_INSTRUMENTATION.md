# Logging and Instrumentation

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-236, D-237

## Scope, and its relationship to the privacy policy

`docs/operations/OBSERVABILITY_PRIVACY.md` and `packages/schemas/observability-allowlist-v1.yaml` govern what may leave a process as telemetry. They are deny-by-default and they are correct. What neither governs is **application logging**, and a log line is not exempt from the privacy boundary merely because nobody wrote down that it was covered. Before this document, the entire logging surface of the repository was two `slog` calls in `apps/api/cmd/api/main.go` with no documented convention behind them.

The division of ownership is:

- `OBSERVABILITY_PRIVACY.md` owns the principle and the forbidden classes.
- `packages/schemas/observability-allowlist-v1.yaml` is the machine allowlist, and this document extends its scope explicitly: **the allowlist governs metric attributes, span attributes and structured log fields alike.** A field name that is not on it does not appear in a log line.
- This document owns the emitted form: format, levels, required fields, correlation, sampling, retention behaviour, and the inventory of signals the services actually emit.

The distinction that motivates it: the allowlist says what may not be exported. It never said what *is*. An operator reading it could not learn whether ingestion failure is observable, and a work unit reading it could not learn what to instrument.

## Logging

### Format

One JSON object per line, written to standard output. The platform collects standard output; no service writes a log file, rotates one, or ships its own logs. On a single managed container under D-093 there is no log-shipping sidecar to pay for, and a service that writes to a file on an ephemeral filesystem is a service whose logs disappear with it.

| Runtime | Library | Handler |
|---|---|---|
| Go | `log/slog`, standard library | `slog.NewJSONHandler` on stdout |
| Rust | `tracing` with `tracing-subscriber` | JSON formatting layer on stdout |
| TypeScript | a thin wrapper over `console` | JSON serialisation, one line per call |

Go's `log/slog` is already in use in `apps/api/cmd/api/main.go` and is standard library, so it adds no dependency. Rust's `tracing` is the only structured-logging facade in that ecosystem with both a span model and a JSON subscriber, and the span model is what carries the correlation identifier through async code without threading it manually. TypeScript gets a wrapper rather than a library because the hosted web application's server-side logging surface is small and a dependency for it would not earn its update burden.

### Levels

Four, and each is defined by what an operator should do about it, not by how bad it feels.

| Level | Means | Operator action |
|---|---|---|
| `ERROR` | a request failed for a reason not attributable to the caller, or an invariant was violated | investigate; something is wrong with the service |
| `WARN` | degraded and handled: a retry succeeded, a fallback engaged, a limit was hit | none immediately; a rising rate is a signal |
| `INFO` | one line per completed request, plus lifecycle and state transitions | none; this is the normal record |
| `DEBUG` | developer detail | off in production |

Two rules follow from those definitions and both are enforceable:

- **A client error is never `ERROR`.** A `400`, `401`, `403`, `404`, `409`, `422` or `429` is `INFO`. Logging them at `ERROR` makes the error rate a measure of how many people are using the product wrong, which destroys the only signal the level was for.
- **`DEBUG` is off in production and cannot be turned on remotely.** It is enabled per-process by an environment variable at start. On a participant's device it additionally requires an explicit, per-session, participant-initiated action with a visible indicator, because `DEBUG` on a device is the level most likely to reach for context the privacy boundary forbids.

### Required fields

Every line carries all of these. A line missing one is a defect.

| Field | Type | Notes |
|---|---|---|
| `ts` | RFC 3339 UTC, millisecond precision | UTC always; a local-time log is unjoinable across an environment |
| `level` | one of the four above | |
| `msg` | **a static string literal** | see below |
| `service_name` | enum | `api`, `worker`, `daemon`, `collector`, `sync`, `web` |
| `build_version` | string | the release-set version, matching the existing allowlist attribute |
| `deployment_environment` | enum | `local`, `ci`, `preview`, `production` |
| `request_id` | UUIDv7 | server-generated, see below |

Server request lines additionally carry `route_template`, `status_class`, `latency_ms_bucket`, and `reason_code` where one applies. Every one of those is an existing allowlist attribute; none is new vocabulary.

**`msg` is a static literal, never an interpolated string.** `"claim batch rejected"` — not `"claim batch 8f2c… rejected for account @vk"`. Two things follow. Lines become aggregatable, because the message is the key and the fields are the data. And interpolation is the single most common way forbidden content reaches a log: a developer formats an error that happens to contain a path, a handle or a body fragment, and the allowlist never sees it because the allowlist checks fields and the payload is inside the message. Making `msg` a literal makes that class of leak a lint failure rather than an incident.

### Correlation

`request_id` is a UUIDv7 generated **at the server edge, always, and never accepted from a client**. A client-supplied correlation identifier is an attacker-controlled value that gets written into logs and then used to join them, which is both an injection surface and a way to poison another principal's trace. UUIDv7 rather than v4 because it sorts by creation time, so a log store can range-scan it.

It is returned to the caller in the `X-Request-Id` response header and is the value a participant quotes in a support request.

`trace_id` and `span_id` are generated and logged. They are **not exported to a tracing backend**, because there is no tracing backend: a hosted trace vendor is a recurring cost against the D-093 ceiling and, under ADR-017, would have to process inside the European Union, which narrows the field to options that cost more. Correlation is therefore done in logs, which the platform already collects at no additional cost. Emitting the identifiers anyway costs nothing and means that adopting a backend later is a configuration change rather than an instrumentation project.

The local daemon's `correlation_id` in the local IPC message envelope is a separate identifier with a separate lifetime. It never crosses the device boundary. A local correlation identifier that reached the server would let the server join a participant's local activity, which is precisely the joinability the privacy contract exists to prevent.

### Identifying a principal in a log line

`handle` is a forbidden class and stays forbidden. A raw `account_id` in a log is a stable global identifier that makes every log line joinable to every other, forever.

Logs carry `account_ref`: the first 16 hexadecimal characters of `HMAC-SHA256(account_id, log_salt)`, where `log_salt` is per-environment and rotates every 90 days. `device_ref` is derived the same way from the device identifier.

The rotation is the point. Within a salt epoch an operator can follow one principal through a day's logs, which is what debugging requires. Across epochs the references do not join, so a log corpus older than the retention window cannot be re-identified even if it survives. Truncating to 16 hex characters — 64 bits — keeps collisions negligible at this population while making the value useless as a lookup key against anything else.

The mapping is not stored. There is no table from `account_ref` to `account_id`; an operator investigating a specific account computes the reference from the account, not the other way round.

### Never logged

Binding, and it is the `forbidden_classes` list from `packages/schemas/observability-allowlist-v1.yaml` in full, plus these, which are not in that list because they are log-specific shapes rather than telemetry attribute classes:

- **Full request URLs.** The route template only. A raw URL carries path parameters and a query string, and a handle in a path is still a handle.
- **Request or response bodies**, in whole or in part, at any level, including inside an error.
- **Whole header maps.** Individual allowlisted header values only.
- **`Idempotency-Key` values.** A truncated SHA-256 of the key, when correlation needs one. The key itself is a client-chosen value that joins a client's requests across principals.
- **Exception messages from third-party libraries, verbatim.** A driver error can contain a query with bound parameters. Errors are logged as a mapped `reason_code` plus a stable type name; the free text is dropped, which the allowlist's `free_text_exception` class already forbids and which is stated here because it is the rule engineers most often break by accident.
- **IP addresses**, except in the security-audit log described below.
- **Environment variables**, or any dump of process configuration.

### The two log streams

| Stream | Contains | Retention | Governed by |
|---|---|---|---|
| operational | everything above | 30 days | `operational_telemetry_retention_days` |
| security audit | authentication outcomes, session and device lifecycle, moderation actions, privacy-boundary canary results, administrative access | 365 days | `security_audit_retention_days` |
| security audit, network address field | the IP address associated with a security-audit event | **30 days**, then the field is erased in place while the event is retained | `operational_telemetry_retention_days` |

They are separate streams with separate access control, and the split exists so that the one place an IP address is retained is bounded, purposeful and separately audited.

The third row is the reason this is three rows rather than two. `docs/privacy/DATA_MAP.md` records that a network address is retained for 30 days under `operational_telemetry_retention_days`, and that record is the Article 30 authority. A security-audit stream that held the address for 365 days would silently extend the retention of personal data beyond what the record states, so the address is erased from the audit event at 30 days while the event itself — which by then carries only `account_ref`, `device_ref` and an outcome — is retained for the full year. The field expires on the shorter clock; the record does not.

Access to either stream is role-based and every access is itself an audit event, which the observability privacy policy already requires.

### Sampling

`ERROR` and `WARN`: never sampled. `INFO` request lines: 100% below 10 requests per second, 10% above, with the sampling decision recorded on the line so a rate computed from logs can be corrected. `DEBUG`: not applicable, since it is off.

At the derived beta load of roughly 20 requests per second, sampling engages on the read paths and produces on the order of a few hundred thousand lines a day, which is within the free tier of every log product on the ADR-017 shortlist. That is the reason for the threshold: it is set where the bill starts.

### Enforcement

- A field-name allowlist assertion in the `observability-privacy` eval suite, applied to captured log output as well as to captured telemetry.
- A canary fixture that emits a line containing each forbidden class and asserts it is dropped or the process fails. This is the same shape as the existing OTLP identity-attribute canary.
- A lint rule rejecting non-literal `msg` arguments.
- High-entropy scanning over captured log output, which the observability privacy policy already requires for telemetry.

## Instrumentation

### Metrics

Names are OpenTelemetry-style, dotted, namespaced `vibemaxxing.`. Every attribute below is on the machine allowlist. This is the complete emitted set; a metric not on this list is not emitted, and adding one is a change to this document and to the allowlist together.

| Metric | Kind | Unit | Attributes | Answers |
|---|---|---|---|---|
| `vibemaxxing.http.server.request.duration` | histogram | s | `route_template`, `status_class` | is the API up, and how fast |
| `vibemaxxing.http.server.ratelimit.rejected` | counter | 1 | `route_template`, `principal_class` | is a limit biting, and whose |
| `vibemaxxing.claims.accepted` | counter | 1 | `evidence_state`, `adapter_id`, `adapter_version` | is ingestion working |
| `vibemaxxing.claims.rejected` | counter | 1 | `reason_code`, `adapter_id` | why claims fail |
| `vibemaxxing.claims.duplicate` | counter | 1 | `reason_code` | replay and idempotent-retry rate |
| `vibemaxxing.claims.batch.size` | histogram | 1 | `adapter_id` | are batches near the 500 ceiling |
| `vibemaxxing.outbox.pending` | gauge | 1 | `worker_type` | is the transactional outbox draining |
| `vibemaxxing.outbox.age` | gauge | s | `worker_type` | how far behind the oldest undelivered event is |
| `vibemaxxing.aggregate.freshness` | gauge | s | — | accepted-claim to public-aggregate lag |
| `vibemaxxing.ranking.generation.duration` | histogram | s | — | is ranking recomputation keeping up |
| `vibemaxxing.db.operation.duration` | histogram | s | `database_operation_class` | database health without a query text |
| `vibemaxxing.db.connections.inuse` | gauge | 1 | — | pool saturation, the first thing to break on a small instance |
| `vibemaxxing.auth.oauth.exchange` | counter | 1 | `status_class` | provider outage |
| `vibemaxxing.presence.leases.active` | gauge | 1 | — | how many devices are live |
| `vibemaxxing.notifications.delivered` | counter | 1 | `status_class`, `worker_type` | inbox and best-effort hint delivery |
| `vibemaxxing.privacy.canary.violation` | counter | 1 | — | **must always be zero** |
| `vibemaxxing.update.blocked` | counter | 1 | `build_version`, `platform` | how many clients are past a deadline |
| `vibemaxxing.backup.age` | gauge | s | — | time since the last verified backup |

`vibemaxxing.privacy.canary.violation` is the only metric in this product whose correct value is a constant. Any non-zero reading is an incident under the operations contract's rule that privacy-boundary violations are the highest severity until scoped.

`vibemaxxing.aggregate.freshness` and `vibemaxxing.backup.age` are the two gauges the restated service expectations in `docs/operations/SLOS_AND_ALERTS.md` are measured from.

### Spans

Spans are created and their identifiers logged; no span is exported. Named spans exist at exactly four boundaries, because a span at every function call costs allocation and yields nothing when there is no backend to view it:

- the inbound HTTP request;
- the database transaction;
- the outbox delivery attempt;
- the verification and appraisal of a claim batch.

On the device, `OTEL_TRACES_EXPORTER` is `none`, which `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` already sets for the ingest side, and no span leaves the device under any configuration.

### Health endpoints

`/livez` returns 200 when the process is running. `/readyz` returns 200 when the process holds a usable database connection **and** the applied migration version is inside the range the binary declares support for, which is the ADR-018 version gate. A binary outside its range fails readiness rather than serving, which is what converts a schema mismatch into a visible outage instead of silent corruption.

Neither endpoint is rate limited, neither requires authentication, and neither returns any detail beyond the status code — a readiness endpoint that explains why it is unready is a reconnaissance surface.

## Evidence

None of this is implemented. `apps/api/cmd/api/main.go` has a JSON handler and two call sites with no request logging, no correlation identifier and no field convention; no metric is emitted anywhere; the `observability-privacy` eval suite is `not_applicable` and names `apps/api/internal/telemetry` as the path whose absence justifies it. This document is the specification that path is built against, and the suite becoming executable is what turns any of it into evidence.
