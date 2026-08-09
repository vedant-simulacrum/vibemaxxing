# Agent Integration Research Matrix

Updated: 2026-08-06
Status: supporting research under `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`

This file records what each agent's capture surface **is**, measured, and what it is not. It does not award a tier, a certification, or an evidence profile — `conformance/adapters/agent-registry-v1.json` holds registry state and `packages/schemas/evidence-profile-policy-v1.json` holds the appraisal dimensions. A row here that says a mechanism works says only that the mechanism produces the named signal; it is not certification evidence and it never raises the ceiling in the registry.

The Claude Code rows below carry the highest confidence because they were exercised on a real machine on 2026-08-06 against a local OTLP listener. The remaining rows are read from published configuration surfaces and public issue trackers, marked as such per row.

## Verified capability rows

Each row answers one question: can the collector obtain a token count for this agent that is deterministic, complete, and stable after the fact, on the machine the user already owns, without the provider's cooperation.

| Agent and mode | Mechanism | Exact signal | Plan tier required | Local collector sufficient | Known defects | Deterministic local capture |
|---|---|---|---|---|---|---|
| Claude Code — OTLP metrics | OpenTelemetry metrics exported by the CLI process over OTLP to an endpoint the user configures | Metric `claude_code.token.usage`, instrument type counter, unit `tokens`; attributes `user.id`, `session.id`, `organization.id`, `user.email`, `user.account_uuid`, `user.account_id`, `terminal.type`, `model`, `query_source`, `effort`, `type` with `type` in `input`, `output`, `cacheRead`, `cacheCreation`. Also emitted: `claude_code.cost.usage` in USD, `claude_code.session.count`, `claude_code.active_time.total` | Consumer subscription. No enterprise plan, no organization, no administrator provisioning | Yes. A loopback listener receiving OTLP protobuf on the metrics path is the entire receive surface; no server-side cooperation participates | Every datapoint carries `user.email`, `user.account_id`, `user.account_uuid` and `organization.id` by default. `OTEL_METRICS_INCLUDE_ACCOUNT_UUID=false` removes the account UUIDs. No documented toggle removes `user.email`; the vendor documentation lists it as included whenever available | **CAN.** Counts are emitted after the API response with finalised values |
| Claude Code — session JSONL | Reading the CLI's own session transcript files under the user's home directory | Per-entry `usage` objects inside newline-delimited JSON session files, mode `-rw-------`, carrying no signature and no attestation of any kind | Consumer subscription | Yes, but the substrate is unsound — see the defect column | `ryoppippi/ccusage#866`: input tokens undercounted by roughly 174x, because approximately 75% of entries hold a literal `0` or `1` placeholder — the file is written during streaming before counts finalise and is never updated. `ryoppippi/ccusage#950`: subagent execution replays the parent thread's whole token history with new timestamps, producing a 91x overcount. `viberank#83`: the CLI rewrites its own session files on resume and compaction — a measured month-to-date total fell 11% in 16 hours while the file count rose | **CANNOT.** The substrate is mutable, unsigned, and quantitatively wrong in both directions |
| Gemini CLI — OTLP metrics | OpenTelemetry metrics exported by the CLI process | Metric `gemini_cli.token.usage`, plus the OpenTelemetry GenAI semantic-convention metric `gen_ai.client.token.usage`; attributes `model` and `type` with `type` in `input`, `output`, `thought`, `cache`, `tool` | Consumer account | Yes for the metrics channel | The `logPrompts` setting defaults to `true`, so prompt text is present on the telemetry logs channel unless the user explicitly disables it. The metrics channel does not carry prompt text; ingesting the logs channel would import L0 content directly | **CAN**, restricted to the metrics channel. The logs channel is unusable at any tier |
| Codex CLI — OTLP metrics | The `[otel]` configuration block in the CLI's own configuration file | Metric `codex.turn.token_usage` | Consumer account | Yes for the interactive surface only | `openai/codex#12913`: `codex exec` emits zero metrics and `codex mcp-server` emits nothing. Those two surfaces are silent, so any total derived from this adapter is missing whatever ran through them. Separately, `metrics_exporter` in that block defaults to **`statsig`**, not `none`: telemetry enabled without pinning the exporter sends token metrics to a third party rather than to a local collector, and the collector can neither detect nor prevent it | **PARTIAL.** Deterministic for the interactive surface; a real and unclosable coverage gap for `exec` and MCP-server execution |
| Cursor | No individual-scope programmatic surface exists | None. Every documented endpoint is team-scoped; the only individual-reachable endpoints are undocumented and reachable solely by replaying a browser session cookie | Team or business plan for the documented surface | No | An undocumented cookie-replayed endpoint has no stability contract, no version probe, and requires holding a session credential — which the privacy contract forbids the collector from touching | **CANNOT** for an individual account |

Rows below have not been exercised on a real machine and carry no measured signal. They stay listed so the coverage gap is visible rather than absent.

| Agent | Best current candidate path | State | Main risk | Required spike |
|---|---|---|---|---|
| OpenCode | Plugin/event interface or live wrapper | Unresolved | API churn and incomplete authoritative usage | Pin version and implement lifecycle probe |
| GitHub Copilot | Extension API or local service | Unresolved | Closed product; usage surface not documented for individual accounts | Verify documented integration path; otherwise label unsupported |
| Gemini IDE agent | Gemini CLI/IDE surface telemetry | Candidate | IDE surface differences from the terminal surface | Exercise terminal and IDE surfaces separately |
| OpenHands | Runtime event stream and model usage metadata | Candidate | Worker version/schema variability | Run containerized synthetic task and verify safe fields |
| Goose | Extension/recipe/event interfaces | Unresolved | Token authority and schema stability | Executable local probe |
| Unknown terminal agent | PTY wrapper and live process accounting | Weak baseline | No provider-authoritative token data | Estimate-only adapter with explicit evidence downgrade |

## The privacy defect this matrix exists to surface

Claude Code's metrics channel ships account identity on every datapoint. `user.email` is a direct personal identifier, `user.account_id` and `user.account_uuid` are stable provider-account identifiers, and `organization.id` discloses employer or team membership. The binding product rule is that servers never receive personal insights or content-derived identifiers, and `packages/schemas/egress-allowlist-v1.json` denies by default, so none of the four may reach the network under any configuration.

Configuration cannot carry that guarantee. `OTEL_METRICS_INCLUDE_ACCOUNT_UUID=false` removes only the account UUIDs, and no documented setting removes `user.email`. The removal is therefore a collector obligation performed at the device boundary before aggregation, specified in `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` and proven by the negative fixtures under `conformance/adapters/claude-code-otel/`.

## The three defaults a receiver must assume

Two of the three rows above turn on a default rather than on a capability, and a receiver written against documented behaviour rather than default behaviour gets both wrong. `packages/schemas/accounting-profile-otel-v1.json` encodes all three under D-614, so they are a record a validator reads rather than a paragraph a reader may skip.

| Producer | Default | Is configuration a control | What the receiver does |
|---|---|---|---|
| Claude Code | Five account-identity attributes on every datapoint of every metric | Partial. `OTEL_METRICS_INCLUDE_ACCOUNT_UUID=false` removes the account UUIDs and nothing documented removes `user.email` | Strips all five in the receiver before admission, rejects whole any datapoint it cannot clean, and never treats a telemetry attribute as identity |
| Gemini CLI | `logPrompts` is `true` | No. The safety of a receiver cannot rest on a setting it does not own | Opens no logs channel for any producer. The metrics channel is the only admissible one |
| Codex CLI | `metrics_exporter` is `statsig`, not `none` | Yes, and weak. The export happens inside the producer, where the collector has no visibility | Never instructs a participant to enable Codex telemetry without pinning the exporter at the loopback receiver. This is one of the reasons the producer stays uncaptured |

The Codex row was absent from this file and from `conformance/adapters/agent-registry-v1.json` until PF-041. It is the one of the three that leaks outward rather than inward: the other two risk importing content or identity into the collector, and this one risks exporting the participant's token activity to a vendor neither party chose.

## Provider attestation is structurally unavailable

Anthropic's Admin API and its Claude Code Analytics API do expose authoritative per-account usage, and either would make a claim self-evidencing. Neither is reachable: the documentation states the Admin API is unavailable for individual accounts and requires an organization-provisioned administrator key. OpenAI has the same shape — an Admin key held by an Organization Owner. Cursor's endpoints are team-scoped, with individual access only through undocumented cookie-scraped endpoints.

No provider offers an attestation path for an individual account. Every claim from an individual participant is therefore self-reported at the source, whatever the local capture quality, and the confidence weighting in ADR-020 rather than source attestation is what carries the integrity load. This is a structural constraint on the product, not a gap awaiting an integration; it is recorded as D-100 and it is the reason D-078 leaves individual and global boards self-reported.

## Acceptance rule

An adapter is not production-supported until it has:

1. a machine-readable manifest;
2. deterministic synthetic fixtures;
3. a version probe;
4. token reconciliation tests;
5. forbidden-field negative tests;
6. upgrade-breakage tests;
7. an explicit evidence class;
8. a written statement of whether provider attestation exists for the account class the adapter serves, and an explicit downgrade when it does not — no adapter is described as self-evidencing while the provider exposes no individual-account authorization scope;
9. a quantified error bound for every file-scraping substrate it reads, stated as a measured ratio against a finalised-count source, with the substrate rejected for competitive capture when the bound is unbounded or the file is rewritten after the fact.

Criterion 9 disqualifies Claude Code's session JSONL as a competitive substrate on the measured evidence above: 174x under, 91x over, and an 11% retroactive decrease in a stable window. Criterion 8 applies to every row in this file, because criterion 8 currently fails for every provider.

## Owner decisions this matrix implements

- D-089 makes Claude Code adapter number one.
- D-098 makes OTLP metrics the primary Claude Code capture mechanism and session JSONL a degraded fallback.
- D-099 fixes the mandatory strip list.
- D-100 records provider-attestation impossibility as a constraint.
- D-614 fixes the metric support set at one — `claude_code.token.usage`, the only metric a fixture in this repository replays — and encodes the three defaults above.

The owning work unit is PF-041. The semantic finding this research serves is SR-009.

A row in the first table saying a mechanism produces a signal is not a support claim, and `packages/schemas/accounting-profile-otel-v1.json` is where the difference is enforced: a metric is `supported` there only when a capture fixture replays it, so `gemini_cli.token.usage`, `gen_ai.client.token.usage` and `codex.turn.token_usage` are recorded as read surfaces with no capture. Both Gemini CLI rows also carry a hazard this table states and no fixture exercises: the CLI emits the vendor metric and the OpenTelemetry GenAI semantic-convention metric, so a receiver that consumed both would double count.
