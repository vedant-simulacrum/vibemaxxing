# ADR-002: Deliberate Polyglot Production Stack

- Status: Accepted
- Date: 2026-07-18
- Owners: Architecture, VibeProof, Backend, Frontend, Security

## Context

VibeMaxxing has two materially different runtime domains:

1. a privacy-critical, cross-platform native collector and protocol implementation; and
2. a network-facing control/data plane that must sustain high concurrency, predictable operations, rapid iteration, and low infrastructure overhead.

Using one language everywhere would reduce language count, but it would force compromises in at least one domain. The project therefore chooses a small, explicit polyglot stack with hard ownership boundaries and generated contracts.

## Decision

### Rust 2024 owns the trusted local and protocol core

Rust is mandatory for:

- `vibeproof-core`
- local collectors and adapters
- canonical CBOR encoding and CDDL validation
- COSE signing and signature verification reference implementation
- local append-only audit ledger
- sequence, replay, deduplication, and commitment logic
- transcript-private analyzer process boundary
- cross-platform native release binaries
- fuzz targets for parsers, canonicalizers, and claim verification

The Rust workspace must use:

- Rust 2024 edition
- a pinned stable toolchain in `rust-toolchain.toml`
- `#![forbid(unsafe_code)]` by default
- narrowly isolated, documented, reviewed exceptions for platform FFI
- `cargo fmt`, Clippy with warnings denied, tests, Miri where applicable, cargo-fuzz, cargo-deny, and cargo-audit

### Go 1.26 owns server-side online services

Go is mandatory for new server services unless an ADR documents an exception:

- claim ingestion API
- verification orchestration
- leaderboard read API
- aggregation and materialization workers
- presence and overtake event service
- operational CLIs and migration tooling
- load generators and selected conformance harnesses

The Go workspace must use:

- Go 1.26.x, pinned through `go.mod` and CI
- standard library first
- `net/http` with a minimal router only when required
- `pgx/v5` for PostgreSQL
- explicit SQL generated or checked by `sqlc` where it improves correctness
- OpenTelemetry instrumentation
- `go test -race`, fuzzing, benchmarks, `go vet`, Staticcheck, govulncheck, and CodeQL
- bounded goroutines, contexts, deadlines, backpressure, and leak tests
- PGO only after representative profiles exist

### TypeScript owns the web interface

The web app uses:

- Next.js App Router
- React Server Components by default
- client components only for interactivity or browser APIs
- strict TypeScript
- generated API clients
- Tailwind utilities backed by project-owned design tokens
- Radix primitives selectively, never as the visual design system
- Playwright, Testing Library, Vitest, Axe, Storybook, and screenshot regression

### Contracts

- The signed public VibeProof claim format remains canonical CBOR governed by CDDL and COSE.
- Internal service-to-service APIs use Protobuf.
- Buf CLI performs linting, code generation, and breaking-change detection.
- Public HTTP APIs may expose JSON for browser and ecosystem compatibility, generated from a versioned API schema.
- No service may redefine claim semantics independently from the Rust reference implementation and conformance fixtures.

## Consequences

### Positive

- Native privacy and cryptographic code retains Rust's memory-safety and control.
- Online services gain Go's simple concurrency, small deployment footprint, fast builds, profiling, and operational clarity.
- Frontend development remains aligned with the strongest React ecosystem.
- Service contracts become mechanically checked.
- Each language has a narrow reason to exist.

### Costs

- Three language toolchains must be maintained.
- Cross-language fixtures and generated contracts are mandatory.
- Engineers and agents must respect ownership boundaries.
- CI becomes broader.

## Rejected alternatives

### Rust everywhere

Rejected for the online service plane because it increases implementation and operational complexity without a demonstrated need for zero-cost abstractions in every request path.

### Go everywhere

Rejected because the local collector, platform integration, canonical signed encoding, and high-assurance privacy boundary benefit materially from Rust's ownership model and unsafe-code containment.

### TypeScript backend

Rejected for the primary ingestion and aggregation paths because the project prioritizes predictable resource use, simple concurrency, and compact deployable services.

### Microservices from day one

Rejected. Begin with a modular Go service plus separate worker processes only where isolation or scaling requires them. Split services only from measured bottlenecks or ownership needs.

## Validation

This decision must be revisited after the first production-like load test. Reversal requires benchmark and operational evidence, not preference.
