# VibeMaxxing Project Authority

Status: planning alignment and contract repair; implementation not authorized.

## Identity and product

VibeMaxxing (`vibemaxxing`, `vibemaxxing.dev`) is a greenfield, privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It is inspired by WhoBurnedMore but does not migrate old accounts, rankings or scores.

Product thesis: **Codex restraint × Steam social competition**.

Visual thesis: **The Competitive Ledger**.

Public launch targets:

- global, friends, private-board, organization, hacker-house and community leaderboards;
- daily, weekly, monthly, seasonal, yearly and lifetime periods;
- profiles, friends, rivals, overtakes and rank movement;
- source-bound active presence;
- groups, boards and administration;
- notifications;
- moderation, restrictions and appeals;
- Token Burn and Estimated Cash Burn;
- native local UX, hosted web and broad tiered agent compatibility.

Country leaderboards are explicitly post-launch. Internal implementation may be staged but must not silently redefine the public-launch target.

## Non-negotiable privacy and integrity

- Servers never receive prompts, responses, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights or content-derived hashes.
- Only fixed-schema aggregate accounting and integrity metadata crosses the device boundary.
- Transcript-capable processes have no network access; networked synchronization processes cannot inspect transcript content.
- Token Burn is the default raw ranking metric; Estimated Cash Burn is always explicitly an estimate and is computed server-side from immutable usage facts and versioned pricing rules.
- Historical imports remain private analytics and never enter active competition.
- Authentic intentionally pointless usage counts when non-duplicated.
- Deterministic controls own accounting, signatures, canonicalization, sequences, replay, duplicates, continuity and hard eligibility.
- Standard and Hardened accepted claims may both contribute globally; Imported claims may not.
- The server verifier awards public evidence status under a named, versioned profile. The client never self-awards Standard or Hardened.
- Local-model and delayed offline usage are first-class competitive usage when deterministically captured by a certified source profile.
- Models and statistical detectors are secondary signals and cannot independently rewrite totals, award stronger evidence or permanently ban users.
- The SLM detector is post-launch research only and is not a launch dependency.
- The system must never be marketed as mathematically cheat-proof or as universally proving provider origin or unique human identity.

## Product topology and identity

The local product has separate adapter, collector, deterministic validation, local commitment, device-key, sync, daemon/control, CLI, menu-bar/tray, privacy/audit and updater responsibilities. A process capable of reading content does not receive network access. Closing the shell does not stop collection unless the user explicitly requests it.

The default runtime is unprivileged and per-user. Privileged helpers require a separate accepted capability, privacy and platform decision.

Primary launch identity paths are:

- GitHub through the accepted GitHub App/web/device authorization architecture;
- X through OAuth 2.0 Authorization Code with PKCE, subject to provider availability.

Google is not a launch provider until authentication, API, persistence, recovery and policy contracts add it coherently.

OAuth proves control of provider accounts, not one unique human. VibeMaxxing strongly enforces one active ranked identity per detected/resolved person using private linked-account, device, recovery and enforcement lineage, progressive restrictions, human review and appeals. Government identity documents and biometric proofing are not required by default.

Agent compatibility is capability-based, versioned and evidence-backed. Public support states are derived from exercised exact-version, mode, platform, artifact and accounting-profile certification rather than marketing claims.

## Anti-cheat architecture

The planned anti-cheat system consists of:

1. source-specific deterministic accounting;
2. signed, digest-addressed adapters and collector builds;
3. typed local collection and privacy filtering;
4. deterministic local integrity rules;
5. protected device signing keys and explicit device lineage;
6. append-only local commitments and server checkpoint receipts;
7. atomic server replay, duplicate, fork and challenge validation;
8. independent verifier appraisal;
9. privacy-safe server anomaly analysis in shadow-first rollout;
10. progressive enforcement, human review, appeal and deterministic ranking rebuild.

Kernel anti-cheat and mandatory provider proxying are rejected.

## Accepted stack

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundaries, accounting, canonical encoding and signing.
- Go: OAuth, APIs, server verification/appraisal, ingestion, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router with strict TypeScript: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal typed contracts.
- Deterministic CBOR/CDDL/COSE: signed public evidence claims, receipts and appraisals.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases or ORM-heavy persistence without an evidence-backed ADR.

## Planning and evidence boundary

The July 23 repository audit reopened planning because current prose and machine contracts disagree on evidence authority, accounting containment, offline continuity, protocol batching, rotation, identity, ranking views, social state machines and release integrity.

P-1140A–E must repair and validate those contracts before implementation may begin. Current schemas and registries are planning inputs and must not be treated as implementation-ready where the audit marks them inconsistent.

Implementation requires explicit user approval under P-1104 after P-1140A–E and clean planning validation complete.

Planning artifacts are not working code, cryptographic interoperability evidence, certified adapters, performance evidence, packages, deployments, security hardening or launch readiness.

The repository remains private during planning and must become public open source before public launch.

## Authority

When sources disagree:

1. the user's latest explicit instruction;
2. this file;
3. `docs/project/STATUS.md`;
4. `docs/planning/DECISION_REGISTER.md`;
5. accepted ADRs;
6. repaired normative contracts and authoritative schemas;
7. the inactive implementation handoff;
8. research, audits and historical records.

Never resolve a material contradiction silently. Update decisions and affected contracts; use an ADR for material architectural or behavioral changes.