# Technology Stack

This stack is deliberately polyglot. Every language has a narrow ownership boundary. Adding another primary language requires an ADR.

## Trusted local VibeProof core — Rust 2024

- Rust 2024 edition with pinned stable toolchain
- Tokio only where asynchronous I/O is required
- Clap for native CLI surfaces
- canonical CBOR and CDDL for signed claims
- COSE signatures
- SQLite with encryption appropriate to each supported platform
- OS-native credential storage
- Unix-domain sockets / Windows named pipes for process isolation
- pinned tokenizer implementations and golden fixtures
- TUF-compatible update metadata
- Sigstore/GitHub provenance attestations
- CycloneDX or SPDX SBOMs
- `cargo-nextest`, Clippy, rustfmt, Miri where applicable
- `cargo-fuzz`, property tests, `cargo-deny`, `cargo-audit`

Safety policy:

- safe Rust by default;
- `unsafe` forbidden at crate roots unless a platform-specific crate receives an approved exception;
- every unsafe block documents invariants and has dedicated tests;
- transcript-reading processes have no network capability;
- synchronization processes have no transcript-path capability.

## Online services — Go 1.26

- Go 1.26.x pinned in `go.mod` and CI
- standard library first
- `net/http` with minimal routing
- `pgx/v5` for PostgreSQL
- explicit SQL and migrations; `sqlc` where generated query types improve correctness
- Protobuf for internal service contracts
- Buf CLI for schema linting, generation, and breaking-change checks
- OpenTelemetry for traces, metrics, and logs
- SSE for primary live leaderboard/presence delivery; WebSockets only when bidirectional semantics are required
- transactional outbox before introducing a distributed message broker
- Redis-compatible cache only for ephemeral presence, rate limiting, and measured hot paths
- `go test -race`, fuzzing, benchmarks, `go vet`, Staticcheck, govulncheck, CodeQL
- PGO only from representative production or production-like profiles

Initial process boundaries:

- API/ingestion service
- aggregation/materialization worker
- migration and administrative CLI

Do not create additional services until scaling, security isolation, or ownership evidence requires them.

## Web — TypeScript

- Next.js App Router
- React Server Components by default
- strict TypeScript with no unchecked implicit `any`
- Tailwind utilities backed by project-owned design tokens
- Radix primitives selectively
- Motion for React only for restrained meaningful motion
- TanStack Query/Table/Virtual where client state or large datasets require them
- D3 primitives for bespoke charts, not a generic dashboard chart layer
- generated API clients
- Zod at untrusted runtime boundaries
- React Hook Form for complex forms
- Vitest and Testing Library
- Playwright across Chromium, WebKit, and Firefox
- Axe accessibility automation
- Storybook for component states
- screenshot-based visual regression
- bundle and Core Web Vitals budgets

## Data and protocol

- PostgreSQL is the source of truth
- append-only accepted-claim ledger with explicit correction records
- idempotency keys and replay state enforced transactionally
- server-derived aggregates and ranks
- canonical public claim format: CBOR + CDDL + COSE
- internal contracts: Protobuf + Buf
- public browser/ecosystem API: versioned JSON with generated schema/client
- no ORM as the default persistence abstraction

## Production platform

Production hosting remains a separate decision from local development. Current preferred managed components are:

- CDN/WAF/DDoS edge
- managed container runtime
- managed PostgreSQL
- managed secrets and identities
- object storage for public release artifacts and retained evidence
- OpenTelemetry-compatible observability backend
- OpenTofu/Terraform for reproducible infrastructure

Do not introduce Kubernetes, Kafka, a service mesh, or a workflow engine without a measured need and ADR.

## Supply chain and engineering

- GitHub Actions with least privilege and pinned action SHAs before production release
- reusable hardened release workflows
- artifact and SBOM attestations
- verification instructions tested in release CI
- Dependabot or Renovate with grouped updates
- Gitleaks, CodeQL, Semgrep where signal is demonstrated
- cargo-deny/audit and govulncheck
- Trivy for container/release filesystem scanning
- k6 for load and soak tests
- deterministic protocol and privacy conformance fixtures


## Platform isolation

- Portable two-process baseline with versioned safe-claim IPC.
- macOS App Sandbox/app-group containers where compatible.
- Linux Landlock + seccomp + no-new-privileges, with namespaces/cgroups where available.
- Windows AppContainer/LPAC + named-pipe ACLs + job objects.
- Platform strength is reflected in evidence state; do not label baseline isolation Hardened.

## Identity

- WebAuthn/passkeys as preferred account authentication.
- Multiple credentials per account.
- Recovery codes only as single-use hashed verifiers.
- No email-only default recovery.
- Sensitive credential changes require recent strong authentication and session review.

## Active leaderboard storage

- Append-only accepted claim ledger.
- Transactional outbox in the same write transaction.
- Idempotent delta aggregation into minute, period, and current-score tables.
- PostgreSQL window functions for explicit rank semantics.
- Materialized views only for slower analytical surfaces.

## Release verification

- Platform-native signing/notarization.
- Sigstore/Cosign bundles and GitHub provenance/SBOM attestations.
- TUF update metadata.
- Clean consumer-side CI verification from public release endpoints.

## Privacy-safe observability

- OpenTelemetry semantic conventions with project-owned allowlisted attributes.
- No serialized claims, request bodies, free text, paths, repository/project names, auth headers, cookies, or transcript-derived data.
- Automated telemetry privacy tests.
