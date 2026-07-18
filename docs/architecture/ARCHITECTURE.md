# System Architecture

## High-level architecture

VibeMaxxing consists of:

- Public web application
- Social and leaderboard API
- Ingestion and claim-verification service
- Ranking materialization workers
- VibeProof local collector
- VibeProof transcript-private analyzer
- VibeProof sync process
- Agent adapter registry
- Conformance and adversarial test suites

## Privacy boundary

### Private evidence process

May:

- Read user-approved transcript/session sources
- Parse deterministic usage
- Run secret redaction
- Run local SLM analysis
- Maintain local commitments and audit data
- Produce fixed-schema claims

May not:

- Access the internet
- Resolve DNS
- Execute shell commands
- Load arbitrary plugins
- Read unrelated credentials

### Sync process

May:

- Connect to VibeMaxxing
- Obtain server challenges
- Send signed fixed-schema claims
- Receive server receipts
- Download signed update metadata

May not:

- Read transcript directories
- Read semantic findings
- Read private summaries or embeddings

## Collection ladder

Use the strongest available integration:

1. ACP session broker
2. Native OpenTelemetry
3. Official hook/plugin
4. PTY/stdio wrapper
5. Live source-bound log observation
6. Historical import

Every adapter declares its capture strength and supported evidence capabilities.

## Platform coverage

Common portable Rust core:

- macOS Apple Silicon and Intel
- Windows x86-64 and ARM where dependencies permit
- Linux x86-64 and ARM64
- WSL
- Docker/dev containers
- Local and hosted execution environments
- SSH workspaces
- Codespaces
- CI runners

Optional hardening:

- macOS Endpoint Security
- Windows minifilter/WFP/TPM
- Linux eBPF/fanotify/IMA/TPM
- Optional hardware-backed attestation

## Server architecture

- Go ingestion and verification service (`net/http`, `pgx`, OpenTelemetry)
- PostgreSQL source of truth
- Append-only claim ledger
- Server-derived aggregates and ranks
- Redis-compatible cache for ephemeral ranking/presence state
- Transactional outbox first; durable queue only when measured scaling or isolation requires it
- SSE for primary presence/overtake delivery; WebSockets only for proven bidirectional requirements
- Next.js web app

## Deployment recommendation

Cloudflare edge + Azure core:

- Cloudflare DNS/CDN/WAF/DDoS/Turnstile/R2
- Azure Container Apps
- Azure Database for PostgreSQL Flexible Server
- Azure Managed Redis
- Azure Service Bus
- Azure Key Vault
- Managed identities
- Private networking
- OpenTofu/Terraform


## Language ownership boundaries

- Rust owns the local collector, transcript-private analyzer boundary, canonical claim encoding, signing, replay primitives, and protocol reference implementation.
- Go owns network-facing APIs, verification orchestration, aggregation/materialization workers, presence, and operational tooling.
- TypeScript owns the web application and generated browser clients.
- Protobuf + Buf governs internal contracts; canonical CBOR + CDDL + COSE governs signed VibeProof claims.
- Cross-language behavior is accepted only through shared golden fixtures and conformance suites.

## Initial service topology

Start with a modular monolith rather than speculative microservices:

1. `api` Go binary: authentication, social graph, boards, ingestion, verification orchestration, leaderboard reads, SSE.
2. `worker` Go binary: outbox consumption, minute aggregation, rank materialization, notifications.
3. PostgreSQL: source of truth, replay/idempotency state, append-only accepted-claim ledger.
4. Redis-compatible service: optional and limited to ephemeral presence, rate limiting, and measured hot caches.

Additional services require an ADR with load, security-isolation, or ownership evidence.


## Accepted detailed designs

- Platform isolation: `docs/security/PLATFORM_ISOLATION.md`
- Authentication and recovery: `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- Ranking storage: `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`
- Release verification: `docs/operations/RELEASE_VERIFICATION.md`
- Observability privacy: `docs/operations/OBSERVABILITY_PRIVACY.md`

These documents are mandatory constraints for their respective implementation areas.
