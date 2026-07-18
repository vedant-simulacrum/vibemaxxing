# Technology Stack

Updated: 2026-07-19
Status: accepted direction; implementation validation required

The stack is deliberately polyglot. Every language has a narrow ownership boundary. Adding another primary language requires an ADR.

## Trusted local and VibeProof core — Rust 2024

- Rust 2024 with pinned stable toolchain.
- Tokio only where asynchronous I/O is required.
- Clap for native CLI surfaces.
- Canonical CBOR/CDDL and COSE for signed claims.
- SQLite with platform-appropriate encryption.
- OS-native credential storage.
- Unix-domain sockets or Windows named pipes.
- TUF-compatible updates, platform signing/notarization, Sigstore/provenance, and SBOMs.
- rustfmt, Clippy, tests, Miri where applicable, fuzzing, property tests, cargo-deny, and cargo-audit.

Safety policy:

- safe Rust by default;
- narrowly isolated/documented platform FFI exceptions;
- transcript-reading processes have no network capability;
- network synchronization processes have no transcript-path capability.

Local product components include daemon, collector, sync, CLI, menu-bar/tray shell, local audit/control UX, updater, and platform service integration. Exact process/privilege boundaries are defined in `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`.

## Online services — Go 1.26

- Go 1.26.x pinned in `go.mod` and launch CI.
- Standard library first; minimal routing.
- `pgx/v5`, explicit SQL/migrations, `sqlc` where it improves correctness.
- Protobuf/Buf for internal contracts.
- OpenTelemetry with project-owned allowlists.
- SSE for primarily server-to-client live updates; WebSockets only for proven bidirectional needs.
- Transactional outbox before any distributed broker.
- Redis-compatible storage only for ephemeral presence, rate limits, or measured hot paths.
- Race tests, fuzzing, benchmarks, vet, Staticcheck, govulncheck, and CodeQL before launch.

Begin as a modular service plus isolated workers only where required. Split services based on measured scaling, security, or ownership evidence.

## Hosted web — TypeScript

- Next.js App Router and React Server Components by default.
- Strict TypeScript.
- Project-owned design tokens with selective Tailwind utilities and Radix primitives.
- TanStack Query/Table/Virtual where justified.
- D3 primitives for bespoke visualizations.
- Generated API clients, Zod at untrusted boundaries, React Hook Form for complex forms.
- Vitest, Testing Library, Playwright, Axe, Storybook, visual regression, bundle, and Core Web Vitals budgets.

## Data and protocol

- PostgreSQL is the server source of truth.
- Append-only accepted-claim ledger with explicit corrections.
- Transactional idempotency, replay state, outbox, and deterministic aggregates.
- Canonical public claim format: CBOR + CDDL + COSE.
- Internal contracts: Protobuf + Buf.
- Public browser/ecosystem API: versioned JSON with generated schemas/clients.
- No ORM as the default persistence abstraction.

## Authentication and authorization

- Primary sign-in: GitHub and X/Twitter OAuth.
- Stable provider subject IDs, not mutable handles, are linkage keys.
- Multiple linked providers are supported.
- Passkeys or hardware-backed credentials are optional stronger factors.
- Native CLI/daemon authorization must bind browser completion to the initiating local device/process.
- Recovery, merge, provider compromise/loss, sessions, revocation, and permissions require explicit state machines.
- OAuth identity is not anti-cheat evidence.

## Agent compatibility

Use the tiered universal compatibility architecture in `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`. Do not hard-code launch support to a finite list. Public claims come from an exercised registry.

## Production platform

Production hosting remains an open ADR. Candidate managed components include CDN/WAF/DDoS edge, managed container runtime, managed PostgreSQL, managed identities/secrets, release-artifact storage, and OpenTelemetry-compatible observability. Infrastructure should be reproducible with OpenTofu/Terraform or an evidence-backed alternative.

Do not introduce Kubernetes, Kafka, service mesh, GraphQL, workflow engine, vector database, or ORM-heavy persistence without measured need and ADR.

## Supply chain and engineering

Before launch require least-privilege CI, pinned action SHAs, hardened release workflows, SBOM/provenance, consumer verification, dependency update automation, secret scanning, static analysis, dependency audits, container/release scanning, load/soak tests, and deterministic conformance fixtures.

During planning, CI, security, release, dependency, and eval automation are manual-only or disabled. Their presence in this stack is a launch requirement, not a claim that they currently run automatically.

## Platform isolation

- Portable privacy-separated baseline.
- Platform-specific stronger controls where available.
- Baseline support must not require elevated privileges.
- Platform strength is reflected in evidence state.
- No claim of equivalent sandboxing across macOS, Windows, Linux, WSL, containers, CI, or remote environments.

## Ranking storage

- Append-only accepted claims.
- Transactional outbox.
- Idempotent minute/period/current-score aggregation.
- Explicit rank semantics with deterministic ties and current-user position.
- Materialized views only for slower analytical surfaces.
- Rebuild and correction behavior defined before implementation.

## Privacy-safe observability

Use explicit event/attribute allowlists. Never export serialized claims, request bodies, free text, paths, repository/project names, auth headers, cookies, prompts, responses, tools, or transcript-derived data. Seed privacy canaries and scan every trace, log, metric, profile, crash report, and release artifact before launch.
