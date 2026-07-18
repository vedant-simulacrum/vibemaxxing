# Research Audit — July 2026

## Scope

This audit evaluates the VibeMaxxing technology and engineering plan against current primary documentation and the project's actual constraints. It does not treat fashionable technology as evidence.

## Principal findings

### 1. A deliberate Rust + Go split is stronger than a single-language mandate

Rust remains the best fit for the trusted local collector and public protocol reference because those components parse untrusted local artifacts, cross OS boundaries, hold signing material, construct canonical signed claims, and must tightly contain unsafe code.

Go 1.26 is a better default for network-facing services. The release enables the Green Tea garbage collector by default, reports significant reductions in GC overhead for relevant workloads, reduces cgo overhead, improves runtime metrics, and provides an experimental goroutine-leak profile. Go also provides mature profile-guided optimization once representative profiles exist.

Decision: Rust for VibeProof and native binaries; Go for server services.

### 2. Do not replace canonical VibeProof claims with Protobuf

Protobuf is excellent for internal APIs and generated clients, and Buf provides mechanical linting and breaking-change detection. It is not automatically a canonical signing representation. The signed public claim format remains deterministic CBOR governed by CDDL and COSE. Protobuf is used only behind that boundary.

### 3. The backend should begin as a modular service, not a premature fleet

The required launch scale does not justify a broad microservice topology. Start with:

- one Go API binary with explicit internal modules;
- one Go worker binary for aggregation/materialization;
- PostgreSQL as source of truth;
- an outbox table for reliable asynchronous publication;
- Redis only for ephemeral presence, rate limiting, and hot caches when measurements justify it.

A queue is introduced only when durable asynchronous separation is required. Database transactions and the outbox pattern should precede distributed workflow machinery.

### 4. PostgreSQL should remain authoritative

Use PostgreSQL for users, social graph, boards, devices, claims, receipts, replay state, aggregates, and audit metadata. Use `pgx/v5` directly because the product is PostgreSQL-specific and benefits from PostgreSQL features and the native driver's performance.

Do not add an ORM as the default abstraction. Prefer explicit SQL, migrations, and generated typed query wrappers.

### 5. Next.js remains appropriate, but client JavaScript must be constrained

Use App Router and React Server Components by default. Fetch leaderboard and profile data on the server where appropriate. Use client components only for interactions, live updates, browser APIs, and local optimistic state. Track route-level JavaScript budgets and Core Web Vitals.

### 6. Supply-chain claims must be verifiable

GitHub artifact attestations can establish build provenance, but attestations are useful only when consumers verify them. Release workflows must produce binaries, checksums, SBOMs, provenance attestations, and documented verification commands. Reusable hardened workflows should be used to progress toward SLSA Build Level 3.

### 7. Existing eval scaffolding is too shallow

A directory-existence check is not an evaluation. The eval runner may retain `not_applicable` during pre-implementation, but every suite needs:

- versioned fixture manifests;
- case identifiers;
- expected outcomes;
- measured values;
- thresholds;
- deterministic seeds;
- environment metadata;
- machine-readable results;
- a milestone switch that turns absence into failure.

### 8. Performance must be a release property

Add explicit budgets for:

- collector idle CPU and RSS;
- collector event processing throughput;
- claim size;
- ingestion p50/p95/p99 latency;
- verification throughput;
- aggregation freshness;
- leaderboard read latency;
- web JavaScript and CSS weight;
- Core Web Vitals;
- cold-start time;
- database query plans and regression thresholds.

Performance regressions require evidence and approval like API regressions.

## Technology decisions

| Area | Decision |
|---|---|
| Local collector and protocol | Rust 2024 |
| Server API and workers | Go 1.26 |
| Database | PostgreSQL with pgx |
| SQL access | Explicit SQL; sqlc where useful |
| Signed public claims | Canonical CBOR + CDDL + COSE |
| Internal APIs | Protobuf + Buf |
| Browser-facing API | Versioned JSON/OpenAPI or Connect-compatible generated client where justified |
| Web | Next.js App Router + strict TypeScript |
| Telemetry | OpenTelemetry |
| Load tests | k6 plus Go/Rust microbenchmarks |
| Fuzzing | cargo-fuzz, Go fuzzing, property-based protocol tests |
| Supply chain | SBOM, GitHub attestations, Sigstore verification, TUF for updater metadata |

## Explicit non-decisions

The audit does not approve:

- Kubernetes as a default;
- Kafka as a default;
- event sourcing for all domain state;
- GraphQL;
- a generic workflow engine;
- a vector database;
- a service mesh;
- WebAssembly for the collector core;
- an ORM-heavy data layer;
- multiple databases before measured need.

Each requires a separate ADR and benchmarked need.
