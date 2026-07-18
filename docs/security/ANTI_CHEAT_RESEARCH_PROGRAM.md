# VibeMaxxing Anti-Cheat Research Program

Updated: 2026-07-19
Status: planning contract; no product implementation authorized

## Objective

Design and validate a privacy-preserving integrity system that makes manipulation materially harder than editing local records, detects common and advanced cheating strategies, limits false positives, and never claims mathematical cheat-proofing on a user-controlled machine.

## Governing principles

1. Deterministic controls own accounting, signatures, replay prevention, duplicate handling, sequence validation, and eligibility rules.
2. Source-bound evidence is stronger than retrospective local records.
3. The SLM is a residual-risk detector only. It never changes token totals or bans a user by itself.
4. No integrity feature may weaken the privacy contract or upload transcript content.
5. Every high-impact action needs an explainable reason code, review path, and appeal path.
6. Standard, Hardened, and Imported remain consumer-facing evidence states; internal evidence dimensions stay separate.
7. Genuine but intentionally pointless usage counts. Fraud, replay, fabrication, copying, and source misrepresentation do not.

## Control hierarchy

Apply controls in this order:

1. Adapter/source conformance and capability probes.
2. Deterministic normalization and token accounting.
3. Server challenge, monotonic sequence, nonce, and claim-expiry checks.
4. Canonical encoding, signatures, protected headers, and key lifecycle.
5. Previous-claim chaining, rollback resistance, and device-state continuity.
6. Idempotency keys, database uniqueness, transactional duplicate handling, and append-only ledgering.
7. Signed official builds, updater integrity, process identity, local IPC controls, and optional attestation.
8. Cross-claim statistical and graph analysis.
9. Deterministic anomaly rules.
10. Experimental SLM residual-risk analysis.
11. Human review, quarantine, appeals, and restoration.

A model or heuristic must never replace a deterministic control that can solve the same problem.

## Research workstreams

### AC-100 — Threat catalog

Create a machine-readable and human-readable catalog covering:

- fabricated or edited events;
- copied sessions and claims;
- replay and duplicate submission;
- backdating, clock rollback, and period-boundary abuse;
- device cloning, snapshot restore, and state rollback;
- modified collectors, adapters, verifiers, and local databases;
- source/model/version impersonation;
- host/guest and nested-agent double counting;
- stolen credentials or device keys;
- colluding accounts and coordinated score manipulation;
- synthetic event generators;
- API abuse and ingestion races;
- supply-chain and update compromise;
- SLM prompt injection, model substitution, and runtime tampering;
- privacy attacks disguised as integrity collection.

For each attack record prerequisites, cost, expected gain, affected evidence tiers, deterministic controls, detection signals, residual risk, false-positive risk, user impact, appeal route, and required tests.

### AC-200 — Deterministic control mapping

Map every attack to prevention, detection, downgrade, quarantine, or review. Produce explicit reason codes and reject/downgrade semantics. Anything unresolved becomes a named research question rather than an implied capability.

### AC-300 — Adversarial fixture and attack laboratory

Define reproducible campaigns for edited counts, malformed claims, duplicate storms, replay, concurrent races, copied sessions, source-version mismatch, clock manipulation, state cloning, snapshot restore, modified binaries, key theft, collusion, synthetic session generation, and pathological inputs.

Fixtures committed to Git must contain only safe structural data. Raw consenting sessions, when required, remain outside the repository and are transformed into privacy-safe representations.

### AC-400 — Statistical baseline

Evaluate transparent methods before an SLM:

- per-agent invariant rules;
- robust descriptive statistics;
- change-point detection;
- sequence consistency checks;
- repeated-fingerprint detection;
- graph and cohort anomalies;
- isolation-based anomaly detection;
- calibrated risk scoring.

Every detector must be tested across agents, versions, platforms, workloads, regions, and user behavior styles.

### AC-500 — SLM feasibility study

The SLM may examine bounded local structural features and, only when explicitly justified, transient local content that never leaves the isolated process. It must have no network, tools, shell, MCP, plugins, autonomous loop, or unrestricted output.

Compare the SLM against deterministic rules and classical anomaly methods on detection lift, false positives, calibration, adversarial robustness, binary size, CPU, memory, battery, startup latency, model-distribution risk, and reproducibility.

The SLM is accepted only if it provides material measured value beyond simpler methods. Otherwise it remains optional or is rejected.

Allowed output is a constrained schema containing risk band, reason codes, confidence/calibration metadata, recommended policy action, model version, runtime version, and policy version. It may not emit replacement token totals or a permanent-ban decision.

### AC-600 — Policy and appeals

Define deterministic outcomes:

- accept;
- accept idempotently;
- accept as Standard;
- downgrade from Hardened;
- exclude one claim;
- quarantine a session;
- quarantine an account score;
- require stronger evidence;
- require human review;
- revoke a device key;
- temporarily restrict ranking;
- restore after appeal.

Measure false acceptance, false rejection, false quarantine, detection latency, appeal overturn rate, and disparate effects across supported environments.

### AC-700 — Continuous red-team program

Before launch, run repeated internal cheat tournaments and independent review against adapters, collector, IPC, local storage, key lifecycle, protocol codec, sync, ingestion, database, aggregation, SLM, policy engine, moderation, and updater.

Every confirmed weakness becomes a regression case. Publish broad integrity principles and evidence semantics, but keep exploit-enabling thresholds and active abuse signatures outside the public repository.

## Required outputs

- `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`
- `conformance/adversarial/anti-cheat-cases.json`
- deterministic reason-code registry;
- SLM feasibility report and benchmark plan;
- privacy-safe fixture policy;
- quarantine and appeal state machine;
- evidence-tier qualification matrix;
- prelaunch red-team report template;
- launch integrity gate in the product launch checklist.

## Completion gate

This planning program is complete only when every attack class has an owner, control mapping, residual-risk statement, test design, policy consequence, and appeal route. Product implementation and automated eval execution remain disabled until the user opens the implementation phase.