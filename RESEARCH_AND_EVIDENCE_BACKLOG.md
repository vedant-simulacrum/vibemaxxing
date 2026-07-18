# Research and Evidence Backlog

Research is complete only when it produces executable evidence, a decision, and updated acceptance gates.

## P0 — Product viability

- Three real agent integrations with synthetic fixtures.
- Cross-provider token-accounting semantics.
- Double-counting and nested-agent rules.
- Evidence-state qualification policy.
- Competitive-integrity attack lab.
- Collector CPU, memory, battery, disk, startup, and throughput benchmarks.
- Installation, privacy-verification, and five-minute onboarding studies.

## P1 — Security and protocol

- Rust CBOR/COSE differential bakeoff.
- Cross-language golden vectors.
- Platform IPC and sandbox attack harnesses.
- Device key registration, rotation, revocation, and cloning tests.
- WebAuthn browser and recovery conformance.
- TUF updater implementation and upstream conformance.
- Consumer-side release verification.
- Privacy-safe telemetry canary tests across every signal.

## P1 — Data and ranking

- PostgreSQL benchmarks at 100k, 1m, and 10m users where resources permit.
- 1k and 10k claims-per-second workloads.
- Duplicate storms, late events, period rollover, and worker crashes.
- Tie, streak, movement, and time-boundary semantics.
- Ledger rebuild and corruption recovery.

## P2 — Product operations

- Cash Burn pricing-source operations and correction process.
- Social notification fatigue and rivalry simulations.
- Abuse quarantine, appeals, moderator tooling, and false-positive policy.
- Country-board privacy and manipulation resistance.
- Data export, deletion, retention, and backup-erasure lifecycle.
- Incident, migration, rollback, disaster recovery, and key-rotation drills.

## Explicitly deferred

Do not spend more research time on generic comparisons of languages, orchestration systems, Kubernetes, Kafka, vector databases, frontend frameworks, databases, or model-routing systems unless implementation evidence creates a concrete need.
