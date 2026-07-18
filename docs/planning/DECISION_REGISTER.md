# VibeMaxxing Decision Register

Updated: 2026-07-19

Statuses: `accepted`, `provisional`, `research-required`, `deferred`, `rejected`.

| ID | Decision | Status | Source | Reopen condition |
|---|---|---|---|---|
| D-001 | Greenfield VibeMaxxing; no migration of old accounts or scores | accepted | project context | explicit product reset |
| D-002 | Product thesis: Codex restraint × Steam social competition | accepted | product spec | explicit product strategy change |
| D-003 | Visual thesis: The Competitive Ledger | accepted | design docs | tested design failure |
| D-004 | Token Burn is default ranking metric | accepted | metrics spec | evidence of misleading competition |
| D-005 | Cash Burn is always labeled estimated, never actual spend | accepted | pricing spec | none without product approval |
| D-006 | Prompts, responses, code, paths, repos, transcripts, and semantic insights never leave device | accepted | privacy contract | never silently reopen |
| D-007 | Historical imports are private analytics only and never active ranking | accepted | product context | explicit competition-policy change |
| D-008 | Public evidence labels: Standard, Hardened, Imported | accepted | integrity model | validated user comprehension failure |
| D-009 | Local-first development; no remote coding control plane | accepted | ADR-001 | explicit user reversal |
| D-010 | Rust collector/protocol, Go server, Next.js/TypeScript web, PostgreSQL/pgx | accepted | ADR-002 | benchmarked ADR demonstrating material benefit |
| D-011 | Canonical CBOR + CDDL + COSE for signed public claims | accepted direction | ADR-002/003 | protocol bakeoff failure |
| D-012 | Final Rust CBOR/COSE crate selection | research-required | ADR-004/005 | malformed, fuzz, differential, and resource tests pass |
| D-013 | OS-specific isolation; do not claim equal sandbox strength | accepted | ADR-003 | platform evidence changes |
| D-014 | Local IPC combines OS peer identity, ACLs, challenge-response, sequences, and limits | accepted direction | ADR-004 | attack lab disproves design |
| D-015 | Device identities are revocable public keys with explicit rotation | accepted direction | ADR-004 | recovery research requires revision |
| D-016 | Passkeys/WebAuthn with multiple credentials and hardened recovery | accepted direction | ADR-003/004 | interoperability or recovery failure |
| D-017 | Append-only claim ledger + transactional outbox + idempotent aggregates | accepted direction | ADR-003/005 | benchmark failure |
| D-018 | Competition ranking uses `rank()` gaps, not dense ranking | provisional | ranking architecture | product simulation/user test |
| D-019 | Pricing uses immutable versioned datasets with provenance and effective dates | accepted | pricing spec | none without ADR |
| D-020 | Country boards use coarse assertions and cohort thresholds | accepted direction | abuse/privacy spec | privacy or abuse testing failure |
| D-021 | Anti-abuse is progressive, appealable, and does not require government ID by default | accepted | abuse spec | severe integrity evidence |
| D-022 | Public support claims are generated from exercised adapter registry | accepted | ADR-005 | none |
| D-023 | Initial adapter research targets Gemini CLI, Claude Code, and Codex | provisional | roadmap | capability evidence changes |
| D-024 | Secure updater must pass TUF conformance and malicious metadata tests | accepted gate | ADR-005 | updater strategy ADR |
| D-025 | GenAI telemetry is allowlisted; content-bearing fields are forbidden | accepted | observability/privacy docs | never silently reopen |
| D-026 | Kubernetes, Kafka, GraphQL, service mesh, vector DB, workflow engine, and ORM-heavy persistence are excluded absent ADR evidence | accepted | project instructions | evidence-backed ADR |
| D-027 | Current phase is planning and decision-closing; no product implementation | accepted current constraint | user instruction | explicit user phase change |

## Register rules

- Every new architectural or product commitment receives an ID.
- `provisional` and `research-required` items cannot be presented as settled.
- Reopening an accepted item requires the named condition, an ADR where material, and updates to dependent tasks.
- A model must update this register when resolving a decision or discovering a contradiction.