# Research Audit — Wave 5: Product Viability Closure

Date: 2026-07-19
Status: Authoritative research requirements; implementation evidence remains required.

## Executive conclusion

VibeMaxxing should stop broad stack research. The production stack is sufficiently constrained. The remaining go/no-go question is whether the product can measure real agent activity accurately and privately, resist obvious competitive manipulation, run unobtrusively, and onboard a user to a trustworthy leaderboard in under five minutes.

The competitive beta remains **NO-GO** until the evidence artifacts listed in `docs/operations/COMPETITIVE_BETA_GATE.md` exist and pass.

## Research tracks completed

### 1. Agent integration feasibility

Officially documented surfaces differ materially:

- Gemini CLI exposes local OpenTelemetry metrics including input, output, thought, cache, and tool token categories. It can also emit prompts, messages, system instructions, tool definitions, and tool results when content-rich telemetry is enabled. A safe adapter must consume a strict local metrics-only export, disable content-bearing traces/logging, reject forbidden attributes, and scan every export for privacy canaries.
- Claude Code usage depends on authentication mode. API-backed usage is token-billed, while subscription and enterprise seats are metered through usage pools. A public Cash Burn estimate must therefore remain explicitly API-equivalent and must not claim to reproduce an invoice. Structured CLI modes are candidate integration surfaces, but exact stable token fields require exercised fixtures per version.
- Codex has multiple execution surfaces. Each mode must be certified independently; support in one mode cannot be inferred for interactive, exec, MCP, cloud, or IDE modes.

Decision: public support is generated only from exercised adapter manifests. Marketing intent, an installed CLI, documentation, or an unofficial editable log is not support evidence.

### 2. Cross-provider accounting

Provider and instrumentation conventions disagree on category boundaries. OpenTelemetry guidance says total input should include cached input and reasoning output should be included in output totals. Gemini exposes additional thought and tool token categories. Anthropic publishes different prices for base input, cache writes, cache reads, and output. Therefore:

- `token_burn_total` is the non-overlapping provider-reported billable-token total when authoritative.
- Category fields may overlap only when explicitly marked `included_in`.
- VibeMaxxing never sums overlapping totals twice.
- Provider-authoritative totals win over local tokenizer estimates.
- Estimated counts cannot silently receive the same evidence state as authoritative counts.
- Failed requests count only when the provider reports billable usage.
- Retries count once per independently billable model operation.
- Tool-event counts are not tokens unless the provider explicitly reports tool tokens.
- Reasoning/thought tokens are included in output when the provider says they are billable or the authoritative usage total includes them.

The complete normative rules are in `docs/product/TOKEN_ACCOUNTING_SPEC.md`.

### 3. Competitive integrity

The system must assume a user controls their ordinary machine and can copy files, alter clocks, replay network traffic, run multiple adapters, and generate pointless but genuine usage. It cannot prove usefulness and should not try.

The minimum attack campaign includes:

- same operation observed through two adapters;
- replay from the same and different device;
- state-directory cloning;
- sequence rollback and reset;
- wall-clock rollback and period-boundary manipulation;
- crash between persistence, receipt, and aggregation;
- duplicate request races;
- adapter identity spoofing;
- telemetry mutation before collection;
- nested-agent double counting;
- excessive micro-event flooding;
- pricing-dataset substitution;
- evidence-level downgrade or upgrade confusion.

Decision: competitive eligibility depends on live observation, source/evidence binding, server epochs, device identities, monotonic sequences, deterministic deduplication, and explicit evidence classes. No document may promise manipulation-proof operation on a root-controlled host.

### 4. Collector performance and battery

The collector must be effectively idle when no qualifying agent is active. Polling loops and high-frequency energy instrumentation can themselves distort measurements. Platform-native measurement is required:

- macOS: Instruments, Activity Monitor Energy Impact, App Nap behavior, and MetricKit/App Store metrics when distributed through supported channels.
- Windows: Windows Performance Recorder/Analyzer and battery reports; test both AC and battery modes.
- Linux: `perf`, cgroups, `/proc`, and RAPL/powercap where available; measurement overhead must be recorded.

Decision: continuous semantic models are not a baseline requirement. Deterministic collection runs continuously; expensive local analysis runs on explicit user request, idle power, suspicious samples, or scheduled windows.

### 5. Installation, trust, and onboarding

The onboarding objective is not merely installation success. A new user must understand what is collected, verify the outbound schema, connect one supported agent, generate a qualifying synthetic or real event, and see a leaderboard result in under five minutes without pasting credentials into chat.

Required usability studies measure:

- install completion;
- permission comprehension;
- native-binary download trust;
- adapter setup success;
- outbound-claim comprehension;
- distinction between Token Burn and estimated Cash Burn;
- understanding of Standard, Hardened, and Imported;
- uninstall and deletion confidence;
- time to first qualifying claim;
- abandonment reasons.

### 6. Privacy-verification UX

The privacy promise must be inspectable. The product must expose:

- current adapter and evidence state;
- collector/sync process separation status;
- safe outbound claim preview;
- last synchronization receipt;
- local audit ledger;
- networking status of the transcript-reading process;
- collected field allowlist;
- explicit absence of content-bearing fields;
- export, disconnect, and deletion controls.

### 7. Cash Burn operations

Provider prices are temporally unstable and structurally different. Pricing must be an immutable versioned dataset, not a live scrape. Each estimate records provider, canonical model, source reference, retrieval time, effective dates, modality, service tier, token category, currency, unit, source digest, and dataset version.

Historical estimates retain their original dataset version. A separate repriced-at-current-rates view may be offered. Subscription fees, promotional credits, negotiated enterprise rates, taxes, and actual invoices are excluded unless a future private analytics feature explicitly imports them.

### 8. Ranking and social mechanics

Product simulations must settle:

- competition rank versus dense rank;
- deterministic tie-break display without pretending tied scores differ;
- period boundaries stored in UTC and presented locally;
- late-claim policy;
- seasonal reset behavior;
- streak definitions;
- presence expiry;
- overtake notification hysteresis;
- notification rate limits;
- private-board visibility;
- country cohort suppression;
- friend-request abuse limits.

The default remains competition ranking with gaps for equal scores. Stable secondary sorting is display-only and does not alter the shared rank.

### 9. Moderation and abuse operations

A competitive social product requires operational tooling before public growth:

- report and appeal queues;
- reason-coded quarantine;
- device revocation;
- account restrictions;
- username and profile moderation;
- friend-request spam controls;
- board-owner controls;
- country correction history;
- moderator audit logs;
- retention limits for abuse evidence;
- two-person approval for irreversible high-impact enforcement.

### 10. Deletion and recovery

Deletion must distinguish user-facing identity data from integrity-preserving pseudonymous records. The design must minimize retained data and permit dissociation where legal and technically safe. Backups need expiry-aware deletion and restore tests proving deleted personal data does not reappear.

Recovery tests must cover aggregate corruption, failed migrations, duplicate workers, delayed outbox processing, pricing-ledger corruption, key rotation, release rollback, and complete leaderboard rebuild from the accepted-claim ledger.

## Immediate implementation order

1. Implement and exercise three adapters: Gemini CLI, Claude Code, and Codex.
2. Freeze accounting schema v1 and add provider fixtures.
3. Build duplicate/replay/state-cloning attack harnesses.
4. Add collector performance harnesses on macOS, Windows, and Linux.
5. Build the inspectable privacy onboarding flow.
6. Benchmark ranking at realistic scale.
7. Implement immutable pricing datasets and verification.
8. Implement moderation, deletion, and recovery runbooks before open beta.

## Explicit non-go conditions

Competitive beta is blocked if any of the following is true:

- fewer than three independently exercised production adapters;
- editable retrospective logs are the primary competitive evidence;
- provider totals and overlapping categories can be double counted;
- a replay or concurrent duplicate can increase score;
- cloned local state can continue as the same trusted device without detection;
- content can appear in telemetry or outbound claims;
- idle collector impact exceeds approved budgets;
- a new user cannot inspect outbound data;
- Cash Burn is presented as actual spend;
- historical estimates silently change after pricing updates;
- deletion cannot be validated through backup restoration;
- required evals pass only because implementation is absent.
