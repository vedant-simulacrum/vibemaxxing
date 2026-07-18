# VibeMaxxing Decision Register

Updated: 2026-07-19

Allowed statuses: `accepted`, `provisional`, `research-required`, `deferred`, `rejected`, `superseded`.

| ID | Decision | Status | Validation or reopen condition |
|---|---|---|---|
| D-001 | Greenfield VibeMaxxing; no migration of old accounts or scores | accepted | explicit product reset |
| D-002 | Product thesis: Codex restraint × Steam social competition | accepted | explicit strategy change |
| D-003 | Visual thesis: The Competitive Ledger | accepted | tested design failure |
| D-004 | Token Burn is the default ranking metric | accepted | evidence that it materially misleads competition |
| D-005 | Cash Burn is always labelled estimated, never actual spend | accepted | explicit product approval |
| D-006 | Prompts, responses, code, paths, repositories, transcripts, tool contents, embeddings, summaries, classifications, and insights never leave the device | accepted | never silently reopen |
| D-007 | Historical imports are private analytics only and never affect active competition | accepted | explicit competition-policy change |
| D-008 | Public evidence labels are Standard, Hardened, and Imported | accepted | validated comprehension failure |
| D-009 | Development is local-first; no remote coding control plane | accepted | explicit user reversal |
| D-010 | Rust native/protocol core, Go server, Next.js/TypeScript web, PostgreSQL/pgx | accepted | benchmarked ADR showing material benefit |
| D-011 | Canonical CBOR + CDDL + COSE for signed public claims | accepted | protocol bakeoff failure |
| D-012 | Final Rust CBOR/COSE crate selection | research-required | malformed, fuzz, differential, and resource tests pass |
| D-013 | OS-specific isolation; never claim equal sandbox strength | accepted | platform evidence changes |
| D-014 | Local IPC combines OS peer identity, ACLs, challenge-response, sequences, and limits | accepted | attack laboratory disproves design |
| D-015 | Device identities are revocable public keys with explicit rotation | accepted | recovery research requires revision |
| D-016 | Passkeys are mandatory primary authentication | superseded | replaced by D-028 |
| D-017 | Append-only claim ledger + transactional outbox + idempotent aggregates | accepted | benchmark failure |
| D-018 | Competition ranking uses `rank()` gaps rather than dense ranking | provisional | product simulation and user testing |
| D-019 | Pricing uses immutable versioned datasets with provenance and effective dates | accepted | evidence-backed ADR |
| D-020 | Country boards use coarse assertions and minimum-cohort privacy thresholds | provisional | privacy and abuse research |
| D-021 | Anti-abuse is progressive, appealable, and does not require government ID by default | accepted | severe integrity evidence |
| D-022 | Public support claims are generated from an exercised adapter registry | accepted | none |
| D-023 | Gemini CLI, Claude Code, and Codex are the complete launch adapter scope | superseded | replaced by D-030 |
| D-024 | Secure updater must pass TUF conformance and malicious-metadata tests | accepted | updater ADR |
| D-025 | GenAI telemetry is allowlisted and content-bearing fields are forbidden | accepted | never silently reopen |
| D-026 | Kubernetes, Kafka, GraphQL, service mesh, vector DB, workflow engine, and ORM-heavy persistence are excluded absent ADR evidence | accepted | evidence-backed ADR |
| D-027 | Current phase is planning and decision-closing; no product implementation | accepted | explicit user phase change |
| D-028 | Primary account access is OAuth-based through GitHub and X/Twitter; passkeys or hardware credentials are optional stronger factors | accepted | provider or security research failure |
| D-029 | Internal delivery is staged, but public launch targets the complete initial product | accepted | explicit user scope change |
| D-030 | Agent coverage is a universal, tiered compatibility system with Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported, and Unsupported states | accepted | ecosystem or feasibility evidence |
| D-031 | Local UX includes a background daemon installed through CLI, macOS menu-bar UX, Windows/Linux tray UX, local controls, and hosted web dashboard | accepted | platform feasibility evidence |
| D-032 | Genuine but intentionally wasteful usage counts when it is authentic and non-duplicated | accepted | explicit product-policy change |
| D-033 | Repository is private during planning and becomes public open source before public launch | accepted | explicit user change |
| D-034 | Automated CI, eval, dependency, security, and release workflows remain manual-only during planning | accepted current constraint | implementation phase begins |
| D-035 | An SLM is optional research-required residual-risk detection and may not rewrite totals or permanently ban users | accepted | measured detector bakeoff |

## Register rules

- Every material commitment receives a stable ID.
- Only allowed status values may be used.
- `provisional` and `research-required` items cannot be presented as settled.
- `superseded` decisions remain for history but must identify their replacement.
- Reopening an accepted decision requires the stated condition, an ADR where material, and updates to dependent specifications and tasks.
