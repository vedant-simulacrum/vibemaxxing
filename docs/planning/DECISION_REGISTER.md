# VibeMaxxing Decision Register

Updated: 2026-07-19

Allowed statuses: `accepted`, `provisional`, `research-required`, `deferred`, `rejected`, `superseded`.

| ID | Decision | Status | Validation or reopen condition |
|---|---|---|---|
| D-001 | Greenfield VibeMaxxing; no migration of old accounts or scores | accepted | explicit product reset |
| D-002 | Product thesis: Codex restraint × Steam social competition | accepted | explicit strategy change |
| D-003 | Visual thesis: The Competitive Ledger | accepted | tested design failure |
| D-004 | Token Burn is the default raw-volume ranking metric | accepted | evidence that it materially misleads competition |
| D-005 | Cash Burn is always labelled estimated, never actual spend | accepted | explicit product approval |
| D-006 | Forbidden content never crosses the device boundary | accepted | never silently reopen |
| D-007 | Historical imports are private analytics only and never affect active competition | accepted | explicit competition-policy change |
| D-008 | Public evidence labels are Standard, Hardened, and Imported | accepted | validated comprehension failure |
| D-009 | Development is local-first; no remote coding control plane | accepted | explicit user reversal |
| D-010 | Rust native/protocol core, Go server, Next.js/TypeScript web, PostgreSQL/pgx | accepted | benchmarked ADR showing material benefit |
| D-011 | Deterministic CBOR + CDDL + COSE_Sign1 for signed public claims | accepted | conformance failure requiring a protocol ADR |
| D-012 | Final Rust CBOR/COSE implementation crates are selected during implementation bakeoff behind an internal boundary | research-required | malformed, fuzz, differential and resource tests pass |
| D-013 | OS-specific isolation; never claim equal sandbox strength | accepted | platform evidence changes |
| D-014 | Local IPC combines OS peer identity, ACLs, challenge-response, versioning and limits | accepted | attack laboratory disproves design |
| D-015 | Device identities are revocable Ed25519 public keys with sequence/hash continuity and explicit rotation | accepted | cryptographic or platform evidence requires revision |
| D-016 | Passkeys are mandatory primary authentication | superseded | replaced by D-028 |
| D-017 | Append-only claim ledger + transactional outbox + idempotent aggregates | accepted | benchmark or correctness failure |
| D-018 | Competition ranking uses SQL `rank()` gaps, with stable display tie-breakers | accepted | user testing or simulation demonstrates material harm |
| D-019 | Pricing uses immutable versioned datasets with provenance and effective dates | accepted | evidence-backed ADR |
| D-020 | Country boards use user assertions, change cooldowns, optional stronger evidence and minimum-cohort privacy thresholds | accepted | privacy or abuse evidence requires revision |
| D-021 | Anti-abuse is progressive, appealable and does not require government ID by default | accepted | severe integrity evidence |
| D-022 | Public support claims are generated from an exercised adapter registry | accepted | none |
| D-023 | Three named CLI adapters are the complete launch scope | superseded | replaced by D-030 |
| D-024 | Secure updater uses TUF and must pass conformance and malicious-metadata tests | accepted | updater ADR |
| D-025 | Telemetry is allowlisted and content-bearing fields are forbidden | accepted | never silently reopen |
| D-026 | Kubernetes, Kafka, GraphQL, service mesh, vector DB, workflow engine and ORM-heavy persistence are excluded absent ADR evidence | accepted | evidence-backed ADR |
| D-027 | Product implementation requires explicit user phase approval | accepted | explicit user phase change |
| D-028 | Primary account access is OAuth-based; passkeys/hardware credentials are optional stronger factors | accepted | provider or security research failure |
| D-029 | Internal delivery is staged, but public launch targets the complete initial product | accepted | explicit user scope change |
| D-030 | Agent coverage is a universal tiered compatibility system with certified, generic, imported and unsupported states | accepted | ecosystem or feasibility evidence |
| D-031 | Local UX includes daemon, private collector, network-safe sync, CLI, macOS menu bar, Windows/Linux tray, local controls and hosted web | accepted | platform feasibility evidence |
| D-032 | Genuine but intentionally wasteful usage counts when authentic and non-duplicated | accepted | explicit product-policy change |
| D-033 | Repository is private during planning and becomes public open source before public launch | accepted | explicit user change |
| D-034 | Product CI, eval, dependency, security and release automation remains manual-only during planning; read-only planning validation is allowed | accepted | implementation phase begins |
| D-035 | An SLM is conditional residual-risk detection and may not rewrite totals or permanently ban users | accepted | measured detector bakeoff |
| D-036 | GitHub uses a GitHub App with web/device authorization; X uses OAuth 2.0 Authorization Code with PKCE | accepted | provider capability or security changes |
| D-037 | Raw Token Burn remains unnormalized across model capability; filters and disclosures provide context | accepted | explicit new metric ADR |
| D-038 | Technical planning contracts were previously declared complete | superseded | replaced by D-042 after audit found missing schemas and contradictions |
| D-039 | Initial production architecture is cloud-portable managed containers, PostgreSQL, optional Redis and object storage | accepted | provider ADR during implementation |
| D-040 | Apache-2.0 for original code, CC BY 4.0 for docs/specs, DCO without CLA initially | accepted | ADR-009; final dependency/counsel review remains release evidence |
| D-041 | `AGENTS.md` is the sole initialization manual; `docs/project/` owns project authority/status/navigation; implementation planning is limited to one handoff plus one PR work breakdown; research is indexed only through `docs/research/README.md` | accepted | explicit repository-governance change |
| D-042 | Repository remains in planning-hardening until draft schemas, validation, governance and protocol edge semantics pass | superseded | replaced by D-045 after P-1120 through P-1128 passed |
| D-043 | Protocol v1 uses one challenge per atomic batch; partial acceptance is prohibited; bounded signed gap declarations downgrade continuity | accepted | ADR-007 or protocol-major revision |
| D-044 | Handle normalization uses Unicode 16.0 NFKC/full case fold/confusable skeleton rules; configurable defaults live in a versioned policy registry | accepted | ADR-008 or proven internationalization failure |
| D-045 | Technical planning is complete at validated contract level except for explicitly reopened targeted hardening | provisional | P-1130A through P-1130E pass and no new P0/P1 contradiction remains |
| D-046 | T20 remains the rolling golden-path engineering cohort, but launch certification is multidimensional and selection/evidence semantics require completed planning validation | research-required | reproducible selection, evidence classes, accounting profiles, coverage thresholds and validator evidence pass |
| D-047 | Repository artifacts are classified as specification, mock, runnable prototype, production implementation, or executable evidence; the existing fixture-backed web app is a bounded runnable prototype and does not authorize further implementation | accepted | explicit phase change or artifact evidence changes |\n| D-048 | Light-mode leaderboard bento is the approved first-screen visual baseline; dark mode and the Signal Ledger, Trackside, and Duel directions are rejected | accepted | explicit visual-direction change after rendered frontend review |

## Register rules

- Every material commitment receives a stable ID.
- Only allowed status values may be used.
- `provisional` and `research-required` items cannot be presented as production-proven.
- A planning decision may be complete while implementation evidence remains pending.
- `superseded` decisions remain for history and identify their replacement.
- Reopening an accepted decision requires the stated condition, an ADR where material, and updates to dependent specifications and tasks.
