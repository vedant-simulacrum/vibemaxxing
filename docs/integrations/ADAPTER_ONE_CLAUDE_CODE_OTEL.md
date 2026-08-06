# Adapter One — Claude Code over OpenTelemetry

Updated: 2026-08-06
Status: normative integration contract for `adapter_id` `claude-code-otel`
Owner of the mechanism evidence: `docs/integrations/AGENT_INTEGRATION_RESEARCH_MATRIX.md`
Owner of the stage boundaries this document consumes: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`

This document specifies one adapter. It does not restate the stage contract, the accounting authority, or the privacy boundary; it binds to them. Where it names an identifier, that identifier already exists in the registry that owns it.

D-089 makes Claude Code adapter number one. D-098 makes OTLP metrics its primary mechanism and session JSONL a degraded fallback. D-099 fixes the strip list in section 4. D-100 records why nothing in this document produces attestation. The owning work unit is PF-041; the semantic finding is SR-009.

## 1. What this adapter is and is not

The adapter receives OpenTelemetry metrics that the Claude Code CLI exports on the user's own machine, and converts them into `SourceObservation` values. It reads no file the CLI writes, holds no provider credential, and speaks to no remote host.

It is not attestation. Section 9 states why in full: the receive surface is an unauthenticated loopback endpoint, and no part of the mechanism proves that the process posting a datapoint is Claude Code. The mechanism is better-quality input than the alternatives, and the evidence class that follows from it is attested-local under D-077. The capability ceiling in the manifest is `standard-competitive`; Hardened is unreachable through this mechanism.

## 2. Receive surface

The adapter runs an OTLP-over-HTTP receiver with exactly one accepted route.

| Property | Value | Rule |
|---|---|---|
| Bind address | The loopback interface only, IPv4 `127.0.0.1` and IPv6 `::1` | The receiver resolves its configured bind address before listening and refuses to start when the result is not a loopback address. There is no configuration path that binds a routable interface |
| Port | Assigned at installation, recorded in local adapter state, and written into the environment the CLI receives | A fixed well-known port is accepted for the default installation; the assigned-port form is what a second concurrent collector uses |
| Transport | HTTP/1.1, no TLS | TLS on loopback adds no confidentiality against a local peer that can already reach the socket, and a self-signed local certificate is a maintenance liability with no threat-model benefit |
| Encoding | OTLP protobuf, `Content-Type: application/x-protobuf` | A body that does not decode as `ExportMetricsServiceRequest` is rejected and counted |
| Accepted route | The OTLP metrics route only | Every other route, including the OTLP logs and traces routes, returns 404. A misconfigured exporter that attempts to deliver the logs channel fails at the transport and never reaches a parser |
| Body limit | 1 MiB per request | Enforced before decoding |
| Rate limit | 60 requests per minute per connection, with a bounded connection count | Exceeding either closes the connection |

The receiver holds an inbound loopback socket and no outbound socket capability. This satisfies the process-isolation rule in `docs/privacy/PRIVACY_CONTRACT.md`: the process that touches source-adjacent data cannot reach the network.

The required manifest permission is `bind-loopback`. The adapter declares no other permission.

## 3. Required environment configuration

The collector writes this environment for the CLI process it observes. Each line is load-bearing and the reason is stated.

| Variable | Value | Reason |
|---|---|---|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1` | The CLI exports nothing without it |
| `OTEL_METRICS_EXPORTER` | `otlp` | Selects the OTLP metrics exporter |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | Matches the receiver's single accepted encoding |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | The loopback base URL of the receiver | Directs export at the local receiver and nowhere else |
| `OTEL_LOGS_EXPORTER` | `none` | The logs channel carries prompt and response content on some agents. This adapter never enables it, and section 2 makes delivery impossible even when a user sets it by hand |
| `OTEL_TRACES_EXPORTER` | `none` | No span carries a token fact this adapter uses |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | `false` | Removes `user.account_uuid` and `user.account_id` at the source. This is defence in depth and does not reduce the obligation in section 4; the strip runs whether or not this variable is honoured |

The measured configuration on 2026-08-06 used a consumer subscription with no enterprise plan, no organization, and no administrator provisioning, and a loopback listener received OTLP protobuf on the metrics route. No server-side cooperation participates in this mechanism.

## 4. Attribute allowlist and mandatory strip list

`claude_code.token.usage` is a counter with unit `tokens`. Its attribute set, as measured, is `user.id`, `session.id`, `organization.id`, `user.email`, `user.account_uuid`, `user.account_id`, `terminal.type`, `model`, `query_source`, `effort`, `type`.

### 4.1 Allowlist — attributes that reach `SourceObservation`

| Attribute | Use |
|---|---|
| `model` | Resolved through the model registry to a registered `model_id`. An alias that does not resolve fails closed; the raw alias never advances, because `docs/privacy/PRIVACY_CONTRACT.md` forbids raw model aliases that can contain user-controlled text |
| `type` | Selects the canonical token component per section 6 |
| `query_source` | Records whether the consumption came from the main thread, a subagent, or auxiliary work. It participates in the duplicate domain and never in the token arithmetic |

### 4.2 Transformed — never carried in raw form

| Attribute | Transformation |
|---|---|
| `session.id` | Consumed inside the adapter process to derive a keyed local commitment. The commitment feeds `source_event_ref`, the collector `session_id` grouping, and the duplicate domain. The raw UUID is discarded when the datapoint leaves the adapter process |

### 4.3 Mandatory strip list — removed at the device boundary, before aggregation

`user.email`, `user.id`, `user.account_id`, `user.account_uuid`, `organization.id`.

These five are present on every datapoint by default. `user.email` is a direct personal identifier; `user.id`, `user.account_id` and `user.account_uuid` are stable provider-account identifiers; `organization.id` discloses employer or team membership. All five fall inside the absolute server boundary and none appears in `packages/schemas/egress-allowlist-v1.json`, which denies by default.

The strip is a receiver obligation with these exact properties:

1. It runs inside the receiver, on the decoded in-memory datapoint, before the datapoint is admitted to the observation queue and therefore before any aggregation, any counter-delta state, and any grouping.
2. A stripped value is never written to disk, never written to a log or crash report, never included in a diagnostic capture, and never used to key any local structure, cache, or metric.
3. A datapoint from which the five cannot be removed — for example a future attribute that nests an identifier inside a structured value — is rejected whole. There is no partial-clean path.
4. An attribute in neither the allowlist nor the strip list is dropped and the observation carries an unknown-attribute reason code. The receiver never fails open on an unrecognised attribute.
5. The strip does not depend on `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`. No documented setting removes `user.email`, so configuration is not a control here.

`effort` and `terminal.type` are read inside the adapter process and discarded at normalization. No downstream stage consumes them.

The negative fixtures in `conformance/adapters/claude-code-otel/` hold the executable form of this section: an observation that carries any of the five is rejected by `packages/schemas/source-observation.schema.json`, and the equivalent normalized event is rejected by `packages/schemas/normalized-event.schema.json`. `conformance/privacy/p1140b-boundary-canaries-v1.json` carries the adapter-boundary canary for the same five.

## 5. Datapoint to `SourceObservation`

The counter is cumulative. For each distinct attribute-set key within one runtime generation the adapter keeps the last cumulative value and emits the delta. A decrease, or a change of the datapoint's start time, is a reset: the adapter increments `runtime_generation` and treats the new value as the delta. Four `type` values sharing one `(session commitment, model, query_source)` group at one export timestamp combine into one observation.

| `SourceObservation` field | Value |
|---|---|
| `observation_schema_version` | `1` |
| `adapter_id` | `claude-code-otel` |
| `adapter_artifact_sha256`, `adapter_manifest_sha256` | Digests of the built adapter artifact and of the canonical manifest payload with its digest field omitted |
| `source_product_id` | `claude-code` |
| `source_version` | The OTLP resource version attribute, cross-checked against the installation version probe. A mismatch fails closed and no observation is emitted |
| `platform` | The collector's own platform enum. No source-supplied value selects it |
| `execution_mode` | `otel` |
| `source_cursor` | `domain` `claude-code-otel-metrics`; `generation` the runtime generation; `ordinal` a monotonically increasing export ordinal per attribute-set key |
| `runtime_generation` | Incremented on counter reset and on CLI process restart |
| `source_event_ref` | A base64url keyed commitment over the session commitment, the attribute-set key, and the export ordinal. Device-local key, separate from any signing key |
| `local_wall_time` | `observed_at` is the receive time at the collector; `uncertainty_ms` is the configured export interval plus the measured receive-jitter bound |
| `monotonic_clock` | The collector's clock domain and generation, with `start_ns` and `end_ns` bracketing the export interval the delta covers |
| `token_observation` | `kind` `category-counts`, with the categories of section 6. A category the datapoint did not carry is an absent key, never a zero |
| `outcome` | `success`, with the meaning fixed in section 5.1 |
| `retry` | Omitted. The metrics channel exposes no retry fact |
| `modality` | Omitted. The metrics channel exposes no modality fact |
| `sensitivity` | `classification` `L0`, `contains_raw_content` `false`, `network_eligible` `false` |

### 5.1 What `success` asserts

The CLI emits `claude_code.token.usage` after the API response returns, with finalised counts. A datapoint therefore evidences one completed model execution whose consumption is final. That is the whole of what `outcome` `success` asserts here.

It does not assert that the turn the user perceived completed. The channel carries no outcome attribute, so this adapter never emits `failed-after-consumption` or `cancelled-after-consumption`; it cannot distinguish them. That inability is a capability limit of the mechanism and is recorded in the manifest rather than papered over.

### 5.2 Metrics received and discarded

`claude_code.cost.usage` carries a USD figure. Pricing is server-owned and a claim never carries a price, a currency, or a cost estimate, so the adapter discards it at the receiver. `claude_code.session.count` and `claude_code.active_time.total` carry no token fact and are discarded at the receiver. None of the three reaches an observation.

## 6. The `type` enum and the accounting model

The adapter binds the registered accounting profile `cloud-separate-cache-v1` in `conformance/accounting/accounting-profiles-v1.json`. That profile is the exact shape of this source: four mutually exclusive provider-reported categories, separate cache read and write, no source total, reasoning unavailable, modality unavailable, and a `quarantine` contradiction policy. PF-041 owns any narrower profile; a narrower profile changes the bound identity through the adapter manifest, not through this document.

| OTLP `type` | Profile source field | Observation category | Canonical component | Containment |
|---|---|---|---|---|
| `input` | `input-tokens` | `input` | `input_uncached` | `exclusive` |
| `output` | `output-tokens` | `output` | `output_visible` | `exclusive` |
| `cacheRead` | `cache-read-tokens` | `cache_read` | `cache_read` | `exclusive` |
| `cacheCreation` | `cache-write-tokens` | `cache_write` | `cache_write` | `exclusive` |

The four are mutually exclusive at the source: an input count from this provider excludes cache reads and cache creations rather than containing them. The profile therefore declares no containment edge, nothing is subtracted, and Token Burn is the plain sum of the four canonical components. A payload in which the categories contradict that structure hits the profile's `quarantine` policy and does not enter accounting.

`reasoning`, `multimodal_input` and `multimodal_output` are structurally zero for this adapter. The zero is not an unknown: the bound profile declares `reasoning_semantics` and `modality_semantics` unavailable, so the absence is carried by the profile identity and the schema's required components stay satisfiable.

## 7. `SourceObservation` to `NormalizedAccountingEvent`

| `NormalizedAccountingEvent` field | Value |
|---|---|
| `event_id`, `session_id` | Collector-generated UUIDv7. One `session_id` groups the observations that share a session commitment within one runtime generation |
| `adapter` | The observation's `adapter_id` and the two digests |
| `certification` | `bundle_sha256` from the certification bundle; `platform_profile_id` from `packages/schemas/platform-profile-registry-v1.json`; `capture_mode` `otel` |
| `source_id` | `claude-code` |
| `provider_id` | `anthropic` |
| `model_id` | The registered ID resolved from the `model` attribute. An unresolved alias downgrades the event to private analytics; the raw alias never advances |
| `accounting_profile` | `cloud-separate-cache-v1` and its content digest |
| `monotonic_interval`, `wall_time_observation` | Carried from the observation |
| `canonical_tokens` | Section 6, with the three unavailable components at zero |
| `source_observed_categories` | The four categories the datapoint carried, each `exclusive` |
| `count_authority` | `runtime-reported`. The counts originate provider-side but reach the collector through the CLI process carrying no signature, so the recorded authority is the runtime that reported them. Recording `provider-reported` here would overstate the evidence and is forbidden |
| `reconstruction_method` | `none` |
| `outcome` | `success`, meaning section 5.1 |
| `retry` | `scope` `none`, `ordinal` `0`, `distinct_execution` `false`. The channel exposes no retry fact and provider-side retries are already collapsed into one counter increment, so the duplicate domain rather than these fields is what prevents double counting |
| `duplicate_domain` | `domain_id` `claude-code-otel-datapoint`, `scope` `source-runtime`. The dedup key is the session commitment, the attribute-set key, the counter start time, and the export ordinal |
| `local_fingerprint` | A 43-character base64url keyed commitment over the duplicate-domain key |
| `rule_result` | `bundle_id` `deterministic-rules-v1`, `disposition` `accept-local` |
| `privacy_scan` | `policy_id` `claim-egress-v1`, `result` `pass` |
| `local_detector_commitment` | `null`. No detector participates |
| `network_eligible` | `false`, a schema invariant |

### 7.1 Multi-observer precedence

When both this adapter and the section 8 fallback observe the same session, the OTLP observation supersedes the fallback observation for that session. The two are never summed and never merged. The fallback record is discarded rather than retained alongside, so no ranking input can contain both.

## 8. Degraded fallback — session JSONL

The fallback engages only when the OTLP receiver has taken no datapoint for a session and the CLI's telemetry configuration is absent. It reads the `usage` objects inside the CLI's own newline-delimited session files under the user's home directory. Those files also contain full transcripts, which are L0 content; the reader process holds no network capability, carries nothing but the `usage` numbers out of the source process, and writes nowhere outside its own working area.

Fallback observations use `execution_mode` `live-log` and `capture_mode` `live-log`.

**The fallback ceiling is private analytics.** A fallback observation is never competitively eligible, never Standard, and never Hardened. The reason is measured, not cautious:

| Defect | Measured magnitude | Reference |
|---|---|---|
| Input undercount | Approximately 174x. Roughly 75% of entries hold a literal `0` or `1` placeholder, because the file is written during streaming before counts finalise and is never updated afterwards | `ryoppippi/ccusage#866` |
| Subagent overcount | 91x. Subagent execution replays the parent thread's whole token history with new timestamps | `ryoppippi/ccusage#950` |
| Retroactive mutation | A month-to-date total fell 11% in 16 hours while the file count rose, because the CLI rewrites its own session files on resume and compaction | `viberank#83` |

The files carry mode `-rw-------` and no signature or attestation of any kind, so nothing detects an edit.

Three rules follow, and the fallback adapter implements all three:

1. Every fallback observation records the error bounds above as a fixed reason-code set. The bounds travel with the record; a consumer cannot read the number without reading the bound.
2. An entry whose input count is a literal `0` or `1` alongside a non-zero output count matches the documented placeholder shape and is marked rather than trusted.
3. A file whose content changes after an observation was taken from it invalidates every observation derived from that file, and the fallback re-reads rather than reconciling.

OTLP metrics escape all three defects because the metric is emitted after the API response with finalised counts, into a channel the CLI does not revisit.

## 9. Threat model for the receive surface

**The OTLP receiver is an unauthenticated localhost endpoint.** OTLP over HTTP carries no authentication and no signature. Any process that can reach the loopback socket can POST an arbitrary `ExportMetricsServiceRequest` and mint token counts that this adapter accepts as an observation. On a single-user machine that is any process running as the user; the collector cannot distinguish it from Claude Code.

Controls that narrow the surface without closing it:

- loopback-only bind, with a start-time refusal on any non-loopback resolution;
- a per-installation port recorded in local state rather than a guessable well-known port;
- one accepted route, a 1 MiB body limit, and a per-connection rate limit;
- a monotonic export ordinal per attribute-set key, so a replayed datapoint is a duplicate rather than an addition;
- rejection of a cumulative counter that decreases without a corresponding start-time change;
- loopback peer credentials where the platform exposes them;
- the `Host` allowlist and `Origin` rules in `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`, which are what stop a web page in the participant's own browser from reaching this socket by DNS rebinding. The list above previously had no browser-facing control at all, and the loopback bind is not one: a browser is already inside the machine.

What none of these prove: that the posting process is Claude Code. Peer credentials yield a uid that is the uid the local attacker already holds. This is the mechanism's ceiling, not an implementation gap.

The consequences are carried, not hidden:

- The adapter's evidence class is attested-local under D-077, never source-bound.
- The manifest's `capability_ceiling.max_public_profile` is `standard-competitive`. Hardened is unreachable through this adapter.
- The confidence weight of ADR-020 carries the integrity load that source attestation would otherwise carry, because section 10 shows no source attestation exists.
- ADR-019 registers the residual, consistent with D-095.

The metrics channel carries no prompt, response, transcript, path, filename, or repository name in any measured attribute, so the content risk on this surface is the identity attributes of section 4 rather than source content. The fallback of section 8 reads files that do contain content, which is a second reason its ceiling is private analytics.

## 10. Certification tuple and current registry state

The tuple this adapter binds, in the form `packages/schemas/adapter-manifest.schema.json` requires:

| Element | Value |
|---|---|
| Source product | `claude-code` |
| Source version | One exact version, inside the manifest's declared version range. An unknown version fails closed |
| Platform profile | One `profile_id` from `packages/schemas/platform-profile-registry-v1.json` per certified platform |
| Mode | `otel` |
| Suite version | The conformance suite version that produced the result |
| Certification bundle | The bundle digest covering the exercised result |

All six bind together. A change to any one is a different tuple and carries no result from the previous one.

### 10.1 This is an exact tuple, not generic OpenTelemetry

The binding product rule holds generic OpenTelemetry integrations to private analytics until an exact tuple is certified. That rule is not relaxed here and this adapter is not an exception to it. The distinction is the tuple above: a generic OTLP receiver accepts any producer, any schema, and any attribute set, and can state nothing about what produced a datapoint. This adapter accepts one named metric from one named product at one resolved version on one certified platform profile in one mode, with an attribute disposition fixed in section 4 and a version probe that fails closed on a mismatch. An unknown source version, an unrecognised metric, or an artifact digest mismatch drops this adapter to the generic path and therefore to private analytics.

### 10.2 Current state

`conformance/adapters/agent-registry-v1.json` records `claude-code` with an empty `certifications` array. Under that file's publication rule, an empty array means no public product-level support claim exists. D-089 makes Claude Code the first agent certified end to end; that is a target and this document is not evidence that it has been reached. This document specifies a mechanism, and nothing in it raises the registry ceiling.

## 11. Provider attestation does not exist for this adapter's population

Anthropic's Admin API and its Claude Code Analytics API expose authoritative per-account usage, and either would make a claim self-evidencing. Neither is reachable by the population this adapter serves: the documentation states the Admin API is unavailable for individual accounts and requires an organization-provisioned administrator key. The same shape holds at OpenAI, whose usage endpoints require an Admin key held by an Organization Owner.

No provider offers an attestation path for an individual account. Every observation this adapter produces is self-reported at the source, at any capture quality. D-100 records the constraint and ADR-016 holds the only corroboration path that does exist, which is organization-scoped and never binds an individual claim.
