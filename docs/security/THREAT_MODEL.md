# Threat Model

Updated: 2026-07-23
Status: normative planning contract; P-1140F semantic review is active and implementation remains blocked by P-1104

## Security objective

Make ordinary and scalable manipulation substantially harder than editing local logs while preserving the absolute content-privacy boundary. VibeMaxxing must detect or contain replay, duplication, fabricated histories, modified collectors, cloned state, identity abuse and coordinated manipulation without uploading prompts, outputs, code, paths, repositories or raw logs.

The system does not claim mathematical cheat-proofing. A contestant with complete control of an unrestricted machine can alter software and local state. The design objective is layered resistance, explicit evidence ceilings, server-enforced continuity, reproducible appraisal, progressive enforcement and appeal.

## Protected assets

- competitive token totals and period attribution;
- claim, checkpoint and correction ledgers;
- ranked-identity uniqueness state;
- device/key lineage and challenge state;
- adapter, collector and detector release integrity;
- pricing interpretations and ranking projections;
- social relationship and board authorization state;
- moderation and appeal records;
- OAuth credentials, sessions and recovery state;
- update trust roots and release metadata;
- the privacy boundary itself.

## Trust boundaries

1. **Source runtime** — provider client, coding agent, local inference server or runtime.
2. **Adapter** — source-specific observation process or module.
3. **Collector** — no-network normalization, accounting, deterministic rules and commitment process.
4. **Local detector** — optional post-launch sandbox with no authority.
5. **Device key service** — protected signing operation and lineage metadata.
6. **Local durable store** — normalized facts, commitments, pending claims and receipts.
7. **Sync process** — network-capable process with no source-content access.
8. **Public API edge** — authentication, rate limiting and input-size enforcement.
9. **Atomic verifier** — canonical decoding, signature, continuity, certification, privacy and eligibility checks.
10. **PostgreSQL fact ledger** — immutable claims, appraisals, receipts, corrections and moderation effects.
11. **Projection workers** — ranking, pricing, presence and notification derivation.
12. **Reviewer/admin systems** — high-impact enforcement and recovery.
13. **Release/update system** — TUF metadata, platform signatures, provenance and compatibility.

No boundary may be collapsed merely for convenience when doing so gives a content-capable process network access or lets a client select server-owned policy outcomes.

## In-scope attackers

### Contestant-controlled device

- edits source logs or local databases;
- fabricates structured events;
- patches adapters, collectors or detector output;
- calls ingestion endpoints directly;
- replays valid claims or batches;
- reuses claim, sequence, challenge, commitment or duplicate-domain identifiers;
- restores old disk images, home directories, credential stores or VM snapshots;
- clones exportable keys or complete installations;
- manipulates wall clocks, suspend/resume and runtime counters;
- double-counts host/guest, proxy/provider, IDE/CLI or parent/subagent usage;
- misrepresents source, model, platform, version or accounting mode;
- generates genuine but strategically pointless activity.

Genuine, non-duplicated and correctly accounted wasteful usage is not cheating.

### Network and API attacker

- sends malformed CBOR/COSE or oversized objects;
- attempts parser differential, allocation exhaustion or algorithm confusion;
- races challenge consumption, idempotency or duplicate checks;
- enumerates identities, devices or moderation state;
- abuses OAuth callbacks, device polling and native browser handoff;
- performs credential stuffing, token replay, CSRF or confused-deputy attacks;
- amplifies expensive leaderboard filters or notification workloads.

### Identity and social attacker

- creates multiple ranked identities;
- links compromised or rented provider accounts;
- exploits recovery to reset identity or enforcement lineage;
- shares networks/devices to trigger false merges against others;
- spams friend requests, invitations or notifications;
- manipulates boards, ownership or organization verification;
- coordinates collusive claims or timing patterns.

### Supply-chain and release attacker

- compromises adapter, collector, server or update builds;
- publishes a malicious package under a similar name;
- steals online release keys;
- serves stale, rolled-back or mixed release metadata;
- substitutes incompatible component versions;
- compromises dependencies, build workers or provenance.

### Insider and reviewer attacker

- accesses more identity or integrity data than required;
- fabricates moderation evidence;
- applies irreversible actions without authorization;
- exports sensitive diagnostics;
- manipulates ranking corrections or release policy.

## Phase 1 protocol boundary

The Phase 1 decoder rejects noncanonical CBOR, duplicate and unknown keys, tags,
floats, indefinite lengths, malformed or truncated lengths, trailing bytes,
oversized claims, wrong map cardinality, unordered or missing keys, invalid version,
zero sequence, invalid evidence enum, and malformed fixed-length or nested token
fields before claims reach accounting. This limits parser disagreement and
content-smuggling risk, but does not provide signature verification. COSE key,
algorithm, and library selection remain a gated bakeoff; unsigned fixture claims are
never authority evidence. Pricing fixtures are also unsigned and test-only pending a
separate pricing authority and signing-key decision.

On rollback of a decoder or accounting release, quarantine the affected version and
replay only with its immutable vector/dataset binding. Do not silently reinterpret
accepted claim bytes or pricing history.

## SLM safety

## Fundamental limitations

A device signature proves only that the registered key signed bytes. It does not prove the local source was honest.

A server challenge proves submission freshness. It does not prove an offline event existed before the challenge unless the event was bound to a previously acknowledged commitment head.

Hardware-backed keys reduce cloning risk but do not prove token accounting. OAuth proves provider-account control but not one unique human. Ordinary provider usage metadata is not a cryptographic provider receipt.

Attestation, where available, is a scoped input with issuer, measurement, nonce, freshness, expiry and revocation. It is never a blanket verified flag.

## Attack classes and required controls

### Forged or mutated claims

Controls:

- deterministic CBOR;
- fixed COSE algorithm and protected headers;
- exact key-to-lineage binding;
- canonical decimal/byte encodings;
- parser depth, item and allocation limits;
- independent Rust and Go implementations;
- malformed and mutation corpus.

Failure outcome: reject without retaining raw invalid payload by default.

### Replay and idempotency abuse

Controls:

- scoped idempotency ledger with request fingerprint;
- unique claim ID, device sequence, challenge and commitment constraints;
- stored exact response bytes;
- byte-identical retries return stored outcome;
- conflicting reuse quarantines or rejects.

### Fabricated retrospective history

Controls:

- append-only local commitment chain;
- periodic server checkpoint receipts;
- single-use challenges;
- delayed-sync policy based on checkpoint distance and source profile;
- no claim that an uncheckpointed interval is pre-proven;
- lower continuity/evidence ceiling for weak intervals.

### Clone, rollback and restore

Controls:

- separate installation, key and lineage identities;
- protected-key classification;
- server checkpoint and expected local head;
- explicit restore/recovery/new-lineage state;
- no automatic Hardened inheritance after migration uncertainty;
- fixtures for VM snapshot, home-directory restore and credential migration.

### Duplicate accounting

Controls:

- source-specific duplicate-domain definitions;
- keyed non-content structural fingerprints;
- authority/precedence rules;
- parent-child inclusion semantics;
- transactional uniqueness;
- conflict quarantine rather than averaging.

### Accounting manipulation

Controls:

- immutable accounting profile digest;
- source category containment graph;
- canonical mutually exclusive totals;
- checked arithmetic;
- source total reconciliation;
- retry, cancellation, cache, reasoning, modality and nested-agent fixtures;
- client cannot select pricing or evidence state.

### Modified adapter or collector

Controls:

- exact artifact digest and provenance in certification;
- signed release and update metadata;
- fail closed for unknown stronger-profile builds;
- capability/evidence ceiling;
- privacy scan after normalization and before signing;
- server registry emergency disable.

An official signature does not make a compromised release trustworthy; update and revocation policy must respond to compromise.

### Privacy-boundary exfiltration

Controls:

- source-content process has no network;
- typed local IPC instead of opaque bytes;
- closed outbound schema;
- no arbitrary strings, JSON maps or content-derived hashes;
- privacy canaries in logs, telemetry, claims, notifications and reviewer tools;
- local exact outbound preview;
- packet-capture and destination allowlist tests.

Any confirmed forbidden-content egress is a highest-severity incident until scoped.

### OAuth and session takeover

Controls:

- exact issuer, client and redirect binding;
- state and PKCE S256;
- one-time native browser handoff;
- refresh-token families with rotation and replay detection;
- web/native session separation;
- CSRF protection and recent authentication;
- optional DPoP only after ADR and bakeoff;
- revoke-one and revoke-all.

### Duplicate ranked identities

Controls:

- provider subject uniqueness;
- linked-account, device, recovery and enforcement lineage;
- velocity and maturity signals;
- no single IP, network or device as sufficient proof;
- corroboration and human review for high-impact restrictions;
- consolidation without duplicate claim transfer;
- appeal and deterministic reversal.

### Social and board abuse

Controls:

- canonical friendship pair constraints;
- request and invitation limits;
- block precedence;
- recent-auth ownership transfer;
- one authoritative board-owner model;
- typed authorization matrix;
- audit and reversible moderation.

### Presence fabrication

Controls:

- renewal only from authorized native device;
- qualifying collector activity reference;
- bounded lease and heartbeat;
- privacy/audience re-evaluation;
- immediate invalidation on block, revocation or privacy change;
- no browser-only indefinite renewal.

### Notification leakage or amplification

Controls:

- typed event union;
- fixed privacy-safe fields;
- stable grouping/dedup key;
- hysteresis and quiet hours;
- authorization/visibility recheck at delivery and render;
- retraction events;
- queue, fan-out and per-recipient limits.

### Moderation abuse

Controls:

- append-only case/action/reversal ledger;
- exact claims, periods and ranking views bound to effects;
- least privilege and recent strong authentication;
- dual control for irreversible operations;
- no model-only permanent bans;
- appeal and deterministic projection rebuild.

### Update compromise

Controls:

- offline threshold root;
- delegated target roles;
- timestamp/snapshot expiry;
- rollback/freeze/mix-and-match defenses;
- release-set compatibility manifest;
- platform signature, hashes, SBOM and provenance;
- compromised-version block preserving export/uninstall;
- atomic install, health check and rollback.

## SLM boundary

The SLM is post-launch research only.

It may operate in two separately approved modes:

1. structured privacy-safe features;
2. bounded raw-local-record windows inside a stricter no-network sandbox.

It must have:

- no network, shell, tools, plugins, MCP or autonomous loop;
- read-only access to explicit local paths;
- no device key, sync credential or provider credential access;
- pinned model and runtime digests;
- bounded CPU, memory, input and wall time;
- fixed enum output with abstention;
- deterministic controls above it.

It may recommend review or contribute an advisory risk signal. It may not alter totals, award Hardened, independently quarantine indefinitely or permanently ban.

## Enforcement principles

- deterministic contradictions may reject or quarantine immediately;
- probabilistic signals begin in shadow mode;
- high-impact identity/account outcomes require human review;
- every action has stable reason codes, policy versions and affected facts;
- every reversible action has a deterministic inverse/rebuild path;
- public explanations reveal no sensitive detector thresholds or linked identity signals;
- appeals restore all affected projections when reversed.

## Required evidence before launch

- exact-byte and malformed protocol suites;
- replay, race, fork and duplicate storms;
- accounting fixtures for every launch source profile;
- clone/restore/key-migration campaigns;
- OAuth/session/token-family abuse tests;
- Sybil/collusion simulations with shared-network false-positive cases;
- social state-machine and authorization property tests;
- moderation reversal and ranking rebuild equivalence;
- updater rollback/freeze/mix-and-match tests;
- privacy canaries and packet capture at every boundary;
- independent privacy and security review.

Planning documents are not this evidence.
