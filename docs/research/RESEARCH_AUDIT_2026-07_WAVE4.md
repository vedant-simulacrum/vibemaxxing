# Research Audit — Wave 4: Decision-Closing Spikes

Date: 2026-07-19

## Purpose

This wave stops broad stack expansion. Its purpose is to close the remaining product-viability decisions with executable evidence.

## Findings

### 1. Agent integrations are heterogeneous

No single collection mechanism works across all coding agents. The collector must use a capability ladder and publish the evidence level of each adapter.

Current strongest documented paths:

- Gemini CLI exposes local OpenTelemetry with token counts and lifecycle hooks. Prompt and response logging must be disabled for VibeProof use.
- Claude Code provides structured `json` and `stream-json` output for programmatic runs and lifecycle hooks, but the adapter must prove that usage fields are stable and must never ingest conversation bodies.
- Codex CLI has OpenTelemetry support, but documented issue history shows entry-point differences. Every supported mode must have a conformance probe.
- OpenCode, Cursor, IDE agents, and closed products require separate executable discovery. Unsupported or brittle log scraping must never be labeled hardened.

Decision: ship an adapter only after its versioned capability probe and privacy-negative tests pass. Marketing support lists must be generated from the adapter registry, not handwritten.

### 2. Protocol library selection remains conditional

`coset` is the strongest current COSE structure candidate, but it builds on `ciborium` and does not itself establish the VibeProof canonical profile. The accepted design is:

- use a small internal `vibeproof-codec` boundary;
- reject duplicate keys, indefinite lengths, non-minimal integers, forbidden tags, floats, oversized values, and excessive nesting before semantic decoding;
- preserve and verify exact protected-header bytes;
- pin algorithms and reject algorithm ambiguity;
- maintain independent golden vectors and differential decoders.

Decision gate: no final crate selection until the bakeoff passes malformed vectors, fuzzing, memory limits, and cross-language exact-byte tests.

### 3. Rankings need benchmark evidence

PostgreSQL provides explicit `rank()` and `dense_rank()` semantics, but the product must define one tie policy. Core materialized-view refresh replaces view contents and is not the minute-fresh incremental mechanism.

Decision: benchmark append-only claims + transactional outbox + idempotent period score tables. The benchmark must measure top-N reads, arbitrary-user rank, duplicate storms, late claims, period rollover, and ledger rebuild.

### 4. Secure updates need conformance, not merely signatures

TUF has maintained Go, Rust, Python, and JavaScript implementations plus a conformance project. VibeMaxxing must test root bootstrap, expiry, rollback, freeze, threshold signatures, interrupted downloads, atomic install, and recovery.

Decision: prototype the updater behind an interface and run the upstream TUF conformance suite before choosing Rust or Go for the shipping updater.

### 5. Telemetry is a privacy risk by default

Current GenAI semantic conventions can represent complete prompts, outputs, tool definitions, and system instructions when enabled. Token-count fields are useful, but content-bearing attributes are forbidden.

Decision: use an explicit allowlist and continuously seed canary prompts, paths, repository names, tokens, and transcript fragments into test traffic. CI must scan every exported trace, log, metric, profile, and crash artifact.

### 6. Go WebAuthn is viable but security-sensitive

`github.com/go-webauthn/webauthn` supports current Go toolchains and reports conformance testing, but remains pre-v1 and may introduce breaking changes for security reasons.

Decision: isolate it behind an internal interface, pin the version, and require browser/RP-ID/origin/recovery conformance before account alpha.

## Go/no-go assessment

### Go

Proceed with the first vertical slice using:

- one synthetic adapter;
- frozen claim schema;
- Rust codec spike;
- Go ingestion and ranking prototype;
- PostgreSQL score tables;
- privacy canary scanner;
- no automatic updater in the first slice.

### Conditional go

Real competitive beta is conditional on:

1. at least three production agent adapters with live evidence;
2. canonical protocol differential tests passing;
3. ranking benchmarks meeting budgets;
4. platform IPC attack tests passing;
5. replay, duplicate, rollback, and state-cloning campaigns passing;
6. clean-consumer release verification passing.

### No-go conditions

Do not launch competitive rankings if token accounting depends primarily on retrospective editable logs, if adapters transmit content-bearing telemetry, or if identical activity can be accepted from cloned device state.
