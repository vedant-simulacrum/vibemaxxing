# Anti-cheat implementation plan

Updated: 2026-07-23
Status: implementation plan derived from `docs/research/ANTI_CHEAT_SYSTEMS_RESEARCH_2026-07-23.md`

## Purpose

This document converts the completed anti-cheat research into an executable engineering plan. It does not claim that any listed component is already implemented.

The plan preserves the product's privacy boundary:

- prompts, outputs, code, paths, repositories, tool bodies and raw logs do not leave the device;
- competitive claims contain only typed aggregate accounting and integrity metadata;
- raw local records may be inspected only by an isolated local detector and are never uploaded;
- the server, not the client, derives the public evidence profile.

## Final architecture decision

Build a layered anti-cheat system with these trust boundaries:

1. source adapter;
2. unprivileged per-user collector;
3. deterministic local validator;
4. optional local anomaly/SLM sandbox;
5. protected device signing key;
6. local commitment store;
7. sync client;
8. atomic server verifier;
9. server appraisal and anomaly service;
10. moderation, appeal and ranking-rebuild system.

Do not build a kernel anti-cheat. Do not proxy model traffic through VibeMaxxing. Do not treat OAuth as proof of one human. Do not make the SLM authoritative.

## Component map

### `vibe-adapter-sdk`

A small SDK and schema package used by official and community adapters.

Responsibilities:

- source capability declaration;
- exact source/runtime/version/platform tuple;
- typed source observation output;
- local-only raw source parsing;
- stable duplicate-domain derivation from non-content facts;
- no network access;
- no device-key access;
- no final evidence-tier selection.

Required interfaces:

```text
probe() -> SourceCapabilityReport
observe(cursor) -> SourceObservationBatch
health() -> AdapterHealth
```

`SourceObservationBatch` may contain sensitive local fields only inside the adapter-to-collector process boundary. It is never a sync payload.

### `vibe-collector-core`

Shared Rust core for macOS, Windows and Linux.

Responsibilities:

- adapter lifecycle;
- typed IPC validation;
- source observation normalization;
- accounting profile application;
- deterministic anti-cheat rules;
- local deduplication;
- local append-only commitments;
- claim construction;
- privacy egress filtering;
- diagnostics without content.

The collector is unprivileged and per-user by default.

### `vibe-integrity-rules`

Versioned deterministic policy engine.

Initial rule families:

- schema and integer bounds;
- monotonic start/end ordering;
- source/runtime/version certification;
- adapter/build digest matching;
- token-category containment and no double counting;
- retry, cancellation and partial-output reconciliation;
- cache-read/cache-write semantics;
- duplicate-domain conflict;
- request/session nesting rules;
- clock rollback and suspend/resume;
- counter reset and runtime generation changes;
- source cross-check mismatch;
- model/runtime throughput envelope;
- privacy allowlist and canary rejection.

Output:

```text
IntegrityRuleBundle {
  ruleset_id,
  rule_results[],
  fatal_contradiction,
  quarantine_reasons[],
  diagnostics_codes[]
}
```

No rule inspects usefulness or productivity.

### `vibe-local-detector`

Optional isolated local process.

Phase A input:

- typed structured features only.

Phase B research input:

- bounded raw-local-record windows, inside a stricter sandbox.

Restrictions:

- no network;
- no shell;
- no plugins, tools or MCP;
- read-only access to explicitly approved source locations;
- no device signing key;
- no sync credentials;
- fixed model and runtime digests;
- bounded CPU, memory, input and wall time;
- fixed output enum schema;
- no generated prose;
- output cannot modify token totals or evidence profile.

Output:

```text
LocalDetectorResult {
  detector_bundle_id,
  input_mode,
  anomaly_classes[],
  confidence_bucket,
  execution_status
}
```

The detector ships in shadow mode until the benchmark gate is passed.

### `vibe-device-identity`

Responsibilities:

- per-installation signing key generation;
- key-protection classification;
- public-key enrollment;
- explicit key rotation;
- revocation;
- recovery and new-lineage creation;
- platform attestation collection where available;
- no public stable hardware identifier.

Platform targets:

- macOS: Keychain/Secure Enclave where compatible; App Attest capability must be feature-detected because current platform support depends on OS/app type and is evolving;
- Windows: CNG/TPM-backed non-exportable key where available;
- Linux: best available OS keyring/TPM path, with a disclosed evidence ceiling when non-exportability cannot be established.

Key protection strengthens identity and cloning resistance but does not prove source accounting.

### `vibe-commitment-store`

Local append-only state distinct from mutable source logs.

Each normalized event advances:

```text
local_head_n = H(
  domain_separator,
  local_head_n_minus_1,
  event_commitment,
  adapter_digest,
  accounting_profile_id,
  monotonic_generation,
  sequence
)
```

Commitments must contain no prompt/output-derived hashes.

State includes:

- local sequence;
- current commitment head;
- previous server checkpoint receipt;
- runtime-generation metadata;
- acknowledged gap records;
- key-lineage ID.

Where rollback-resistant storage is unavailable, the evidence profile must disclose the weaker continuity class.

### `vibeproof-protocol`

Use deterministic CBOR with a strict project profile and COSE_Sign1.

Split messages into:

1. `EvidenceClaim` signed by the device;
2. `VerifierAppraisal` created by the server;
3. `CheckpointReceipt` created by the server;
4. `CorrectionRecord` created through an authorized correction flow.

The client must not submit `Standard` or `Hardened` as an authoritative fact.

`EvidenceClaim` binds:

- protocol version;
- claim ID;
- account pseudonym;
- device-lineage ID and key ID;
- local claim sequence;
- previous local commitment;
- current local commitment;
- previous checkpoint receipt ID;
- server challenge ID and nonce;
- source event interval;
- monotonic duration and generation;
- adapter and collector digests;
- exact certification tuple;
- accounting profile ID;
- aggregate token categories;
- duplicate-domain identifier;
- deterministic rule bundle ID/result summary;
- optional detector result reference;
- privacy policy version and pass result.

`VerifierAppraisal` contains:

- claim ID and claim digest;
- policy version;
- independently derived evidence dimensions;
- public evidence state;
- acceptance outcome;
- reason codes;
- anomaly disposition;
- expiry/re-evaluation policy where applicable.

Protocol requirements:

- definite lengths;
- shortest integer encodings;
- duplicate map keys rejected;
- no floats;
- no unregistered generic extension map;
- protected algorithm, protocol, key ID and content-type headers;
- exact external-AAD profile;
- cross-language golden vectors;
- maximum depth, claim size and batch size;
- parser allocation limits before materialization.

### `vibe-verifier-service`

One atomic database transaction must perform:

1. decode and canonical-form validation;
2. signature and key-status validation;
3. account/device-lineage validation;
4. challenge ownership, expiry and single-use validation;
5. expected local sequence/checkpoint validation;
6. replay/idempotency lookup;
7. adapter/certification lookup;
8. accounting profile validation;
9. duplicate-domain conflict check;
10. privacy and eligibility validation;
11. verifier appraisal creation;
12. immutable ledger append;
13. challenge consumption;
14. checkpoint receipt creation;
15. ranking-event emission only after commit.

Exact resubmission returns the stored response. Same identifiers with different bytes are conflicts, not idempotent retries.

### `vibe-anomaly-service`

Server-side analysis uses only accepted aggregate claims and integrity metadata.

Initial feature groups:

- token rate by model/runtime/source profile;
- input/output/cache/reasoning ratios;
- burst and offline interval distributions;
- repeated recovery, rotation and fork events;
- identical structural histories across identities;
- duplicate-domain reuse;
- source-version transition anomalies;
- board-level coordinated timing;
- linked-account/device/recovery risk.

Rollout:

1. offline backtest;
2. shadow mode;
3. reviewer-visible advisory mode;
4. limited quarantine authority;
5. never automatic permanent banning.

### `vibe-ranked-identity`

Separate authentication from uniqueness enforcement.

Authentication:

- authorization code flow;
- transaction-specific PKCE S256;
- exact redirect URI validation;
- refresh-token rotation or sender constraint;
- DPoP for VibeMaxxing's own desktop session if operationally feasible.

Ranked identity integrity:

- one active ranked identity policy;
- private linked-provider graph;
- device and key lineage;
- recovery lineage;
- enforcement lineage;
- duplicate investigation state;
- merge/restriction/appeal/reversal workflow.

OAuth provider accounts are signals, not proof of one human.

### `vibe-moderation-ledger`

Every enforcement record binds:

- subject identity;
- exact claims and periods;
- affected leaderboard scopes;
- reason codes;
- detector/ruleset/policy versions;
- reviewer actions;
- appeal state;
- final disposition;
- reversal record.

Ranking projections must be rebuildable after any reversal.

## Desktop packaging

### macOS

- menu-bar app for status, privacy preview and diagnostics;
- per-user LaunchAgent registered through `SMAppService`;
- authenticated XPC or equivalent local IPC;
- explicit user approval and visible service status;
- no LaunchDaemon unless a later capability requires privileged access;
- signed/notarized app and helper artifacts.

### Windows

- tray app separate from collector process;
- per-user background collector by default;
- Windows Service only for approved system-level capability;
- local-only named pipe or local RPC;
- explicit DACL restricted to the logged-in user/service identity;
- deny network/anonymous pipe access;
- signed installer and binaries.

### Linux

- user-level systemd unit where available;
- Unix-domain socket restricted by filesystem permissions and peer credentials;
- fallback foreground/background process for non-systemd environments;
- no root service by default;
- package signatures and explicit update provenance.

## Adapter support plan

Implement representative adapters in this order:

1. Ollama or llama.cpp runtime-native counters;
2. one cloud API structured-usage adapter;
3. Claude Code;
4. Codex;
5. Cursor;
6. vLLM/OpenAI-compatible local server;
7. generic community adapter SDK.

The first two deliberately cover both local and cloud accounting paths before broad agent expansion.

Each adapter requires:

- capability manifest;
- exact supported versions/modes/platforms;
- accounting profile;
- privacy review;
- duplicate-domain contract;
- positive and adversarial fixtures;
- certification expiry/sunset behavior;
- emergency disable path.

Support grades:

- `hardened_capable`;
- `standard_competitive`;
- `private_analytics_only`;
- `unsupported`.

## Database entities

Minimum server-side entities:

- accounts;
- ranked_identities;
- identity_links;
- device_lineages;
- device_keys;
- key_attestations;
- challenges;
- evidence_claims;
- verifier_appraisals;
- checkpoint_receipts;
- duplicate_domains;
- claim_conflicts;
- quarantine_cases;
- enforcement_actions;
- appeals;
- correction_records;
- adapter_releases;
- certification_tuples;
- accounting_profiles;
- policy_versions;
- ranking_events;
- ranking_projection_versions.

Immutable fact tables must be separated from mutable projections and case status.

## API surface

Initial endpoints:

```text
POST /v1/devices/enroll
POST /v1/devices/{lineage}/rotate-key
POST /v1/devices/{lineage}/recover
POST /v1/challenges
POST /v1/claims
GET  /v1/claims/{id}/appraisal
GET  /v1/devices/{lineage}/checkpoint
GET  /v1/adapters/registry
GET  /v1/accounting-profiles
GET  /v1/integrity-policies
POST /v1/appeals
GET  /v1/appeals/{id}
```

Claim acceptance must not be split into non-atomic challenge, replay and ledger writes.

## Work phases

### Phase 0 — contract repair

Deliverables:

- reconcile privacy/evidence contradictions;
- replace provider-receipt terminology;
- remove client-authoritative evidence state;
- separate source observation, normalized event, detector result, evidence claim and verifier appraisal;
- freeze threat model and reason-code taxonomy;
- supersede stale PR #17 content where incompatible.

Exit gate:

All normative documents and schemas agree. No implementation starts before this gate.

### Phase 1 — protocol and deterministic core

Deliverables:

- Rust domain types;
- accounting profile engine;
- deterministic rule engine;
- commitment store;
- strict CBOR/COSE profile;
- independent decoder implementation;
- golden vectors and mutation corpus;
- local privacy egress scanner.

Exit gate:

Cross-language encoders/verifiers agree byte-for-byte; malformed, duplicate-key, overflow and privacy-canary inputs fail closed.

### Phase 2 — device, sync and server verifier

Deliverables:

- device enrollment and protected keys;
- challenge service;
- claim signing;
- atomic verifier transaction;
- replay/idempotency/fork handling;
- checkpoint receipts;
- offline interval handling;
- immutable ledger.

Exit gate:

Replay storms, concurrent forks, clone/restore, challenge races and exact retries have reproducible passing tests.

### Phase 3 — two-source vertical slice

Deliverables:

- one local-runtime adapter;
- one cloud structured-usage adapter;
- desktop background collectors for macOS first, then Windows and Linux;
- claim ingestion through ranking projection;
- evidence-state UI and privacy preview.

Exit gate:

Both sources run end-to-end without uploading forbidden content. Imported history cannot enter competitive rankings.

### Phase 4 — anomaly, moderation and identity integrity

Deliverables:

- aggregate feature registry;
- server anomaly shadow mode;
- ranked-identity linkage and duplicate workflow;
- quarantine and moderation ledger;
- appeals;
- ranking rebuild/reversal.

Exit gate:

No detector can permanently ban automatically; every enforcement action can be reversed and projections rebuild deterministically.

### Phase 5 — SLM bakeoff

Deliverables:

- synthetic/consented tamper corpus;
- deterministic baseline;
- classical statistical baseline;
- structured-feature SLM;
- optional raw-local-record sandbox prototype;
- prompt-injection red-team suite;
- false-positive and detection-lift report.

Promotion gate:

The SLM becomes enforcement-relevant only if it provides material incremental detection at a predeclared false-positive ceiling, remains reproducible, and passes all privacy and sandbox escape tests. Otherwise it remains advisory or is removed.

### Phase 6 — adapter expansion and release hardening

Deliverables:

- Claude Code, Codex, Cursor and vLLM adapters;
- adapter certification tooling;
- signed release manifests;
- TUF-style rollback/freeze-resistant update metadata;
- in-toto provenance;
- signature transparency logging;
- key compromise and emergency-disable drills.

Exit gate:

Official artifact identity and update rollback protections are independently verifiable.

### Phase 7 — adversarial beta and launch gate

Required tests:

- modified adapter;
- modified collector;
- forged claims;
- copied sessions;
- exact and conflicting replay;
- sequence fork;
- home-directory restore;
- VM snapshot/clone;
- key migration;
- clock rollback and suspend;
- source counter reset;
- malformed and oversized CBOR;
- algorithm/header confusion;
- duplicate-key parsing;
- retry/cancellation/cache edge cases;
- offline multi-day legitimate use;
- legitimate high-volume local inference;
- cross-account duplicate-domain reuse;
- coordinated identities;
- detector prompt injection;
- update/signing compromise simulation;
- privacy canaries;
- appeal reversal and ranking rebuild.

Launch requires executable evidence, not completed planning documents.

## Dependency-ordered first five implementation epics

### AC-I1 — Repair normative contracts

Depends on: none.

Changes eventually required:

- `docs/project/STATUS.md`;
- `docs/planning/DECISION_REGISTER.md`;
- `docs/planning/TASK_CATALOG.md`;
- `docs/security/THREAT_MODEL.md`;
- `docs/security/INTEGRITY_MODEL.md`;
- `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`;
- `docs/specs/ADAPTER_AND_VIBEPROOF_CONTRACT.md`;
- current schemas and ADRs.

Acceptance:

- one privacy boundary;
- one evidence vocabulary;
- no unsupported provider verification claim;
- implementation explicitly unopened until contract approval.

### AC-I2 — Implement typed accounting and deterministic validation core

Depends on: AC-I1.

Acceptance:

- source observation cannot cross sync boundary;
- exact accounting profiles;
- no double counting;
- deterministic rule bundle;
- privacy canaries fail closed;
- property and mutation tests.

### AC-I3 — Implement VibeProof evidence/appraisal protocol

Depends on: AC-I1 and type definitions from AC-I2.

Acceptance:

- strict CBOR/COSE profile;
- client cannot award evidence tier;
- independent decoders;
- golden vectors;
- batch, correction, rotation and checkpoint formats;
- parser resource limits.

### AC-I4 — Implement device lineage, commitments and atomic verifier

Depends on: AC-I2 and AC-I3.

Acceptance:

- protected keys;
- enrollment/rotation/recovery;
- precommitted local continuity;
- challenge/checkpoint flow;
- atomic idempotency/replay/fork handling;
- clone/restore tests.

### AC-I5 — Ship two-source end-to-end anti-cheat vertical slice

Depends on: AC-I4.

Acceptance:

- one local source and one cloud source;
- macOS per-user collector first;
- server appraisal and ranking event;
- zero forbidden-content egress;
- Standard/Hardened derived by server;
- imported records excluded;
- operational diagnostics and recovery.

## User decisions required before implementation

1. Whether raw-local-record SLM inspection is enabled by default, opt-in, or research-only.
2. Maximum offline interval before Hardened continuity downgrades on platforms without rollback-resistant state.
3. Whether Hardened must remain attainable without hardware/OS attestation.
4. Whether private organizations may require stronger identity proofing than the global leaderboard.
5. Which exact local runtime and cloud source form the first two-source vertical slice.

## Known current-source correction

Apple documentation is in transition around App Attest on macOS. Existing API documentation still states that Mac returns unsupported, while WWDC 2026 material announces support on macOS 27 and later for eligible app types. Implementation must feature-detect `isSupported`, record OS/app-type capability, and never make App Attest a launch-wide requirement.

## Definition of done

The anti-cheat system is not done when documents, schemas or UI badges exist. It is done only when:

- claims are generated by real adapters;
- privacy boundaries are tested;
- cryptographic interoperability is exercised;
- replay, cloning and rollback attacks have executable tests;
- server appraisal is authoritative;
- moderation and reversal work;
- release integrity is independently verifiable;
- launch gates pass on supported platforms and source tuples.
