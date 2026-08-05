# VibeMaxxing Decision Register

Updated: 2026-08-06

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
| D-014 | Local IPC combines OS peer identity, ACLs, challenge-response, versioning and limits | accepted | adversarial validation disproves design |
| D-015 | Device identities are revocable Ed25519 public keys with sequence/hash continuity and explicit rotation | accepted | cryptographic or platform evidence requires revision |
| D-016 | Passkeys are mandatory primary authentication | superseded | replaced by D-028 |
| D-017 | Append-only claim ledger + transactional outbox + idempotent aggregates | accepted | benchmark or correctness failure |
| D-018 | Competition ranking uses SQL `rank()` gaps, with stable display tie-breakers | accepted | user testing or simulation demonstrates material harm |
| D-019 | Pricing uses immutable versioned datasets with provenance and effective dates | accepted | evidence-backed ADR |
| D-020 | Country boards are part of launch scope | superseded | replaced by D-052 |
| D-021 | Integrity enforcement is progressive, appealable and does not require identity documents by default | accepted | severe integrity evidence |
| D-022 | Public support claims are generated from an exercised adapter registry | accepted | none |
| D-023 | Three named CLI adapters are the complete launch scope | superseded | replaced by D-030 |
| D-024 | Secure updater uses TUF and must pass conformance and hostile-metadata tests | accepted | updater ADR |
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
| D-035 | An SLM is conditional residual-risk detection and may not rewrite totals or permanently ban users | superseded | replaced by D-053 |
| D-036 | GitHub uses a GitHub App with web/device authorization; X uses OAuth 2.0 Authorization Code with PKCE | accepted | provider capability or security changes |
| D-037 | Raw Token Burn remains unnormalized across model capability; filters and disclosures provide context | accepted | explicit new metric ADR |
| D-038 | Technical planning contracts were previously declared complete | superseded | replaced by D-042 after audit found missing schemas and contradictions |
| D-039 | Initial production architecture is cloud-portable managed containers, PostgreSQL, optional Redis and object storage | accepted | provider ADR during implementation |
| D-040 | Apache-2.0 for original code, CC BY 4.0 for docs/specs, DCO without CLA initially | accepted | ADR-009; final dependency/counsel review remains release evidence |
| D-041 | `AGENTS.md` is the sole initialization manual; `docs/project/` owns project authority/status/navigation; implementation planning is limited to one handoff plus one PR work breakdown; research is indexed only through `docs/research/README.md` | accepted | explicit repository-governance change |
| D-042 | Repository remains in planning-hardening until draft schemas, validation, governance and protocol edge semantics pass | superseded | replaced by D-045 after P-1120 through P-1128 passed |
| D-043 | Protocol v1 uses one challenge per atomic batch; partial acceptance is prohibited; bounded signed gap declarations downgrade continuity | provisional | reopened by P-1140C because the current batch, checkpoint and sequence contracts conflict |
| D-044 | Handle normalization uses Unicode 16.0 NFKC/full case fold/confusable skeleton rules; configurable defaults live in a versioned policy registry | accepted | ADR-008 or proven internationalization failure |
| D-045 | Technical planning is complete at validated contract level; implementation remains inactive until explicit P-1104 approval | superseded | replaced by D-049 after the July 23 audit found cross-contract P0/P1 contradictions |
| D-046 | T20 is the rolling golden-path engineering cohort; each active slot requires exact multidimensional certification plus quantitative optimization evidence, while non-T20 models may use lower honest support tiers | provisional | reconcile T20 launch value with capability-based adapter rollout and real usage evidence under P-1140B/E |
| D-047 | Repository artifacts are classified as specification, mock, runnable prototype, production implementation, or executable evidence; the existing fixture-backed web app is a bounded runnable prototype and does not authorize further implementation | accepted | explicit phase change or artifact evidence changes |
| D-048 | Light-mode leaderboard bento is the approved first-screen visual baseline; dark mode and the Signal Ledger, Trackside, and Duel directions are rejected | accepted | explicit visual-direction change after rendered frontend review |
| D-049 | Repository phase is planning alignment and contract repair under P-1140A–E; P-1104 remains blocked afterward until explicit approval | accepted | P-1140A–E complete, clean validation passes and user explicitly opens implementation |
| D-050 | Client claims contain evidence facts only; a server verifier creates the authoritative appraisal and public Standard/Hardened state | accepted | protocol/security evidence requires revision |
| D-051 | Deterministically captured local-model and delayed offline usage may compete; Standard and Hardened both count globally, while Imported never counts | accepted | explicit competition-policy change or material integrity evidence |
| D-052 | Country leaderboards are postponed until post-launch and are removed from launch requirements, routes and readiness gates | accepted | explicit user reversal after country semantics, privacy and moderation contracts mature |
| D-053 | The SLM detector is post-launch research only: local, sandboxed, advisory, non-authoritative and promoted only after measured lift over simpler baselines | accepted | reproducible bakeoff and explicit launch-scope change |
| D-054 | Launch identity strongly enforces one active ranked identity per detected/resolved person without claiming mathematically verified unique humans or requiring government ID/biometrics by default | accepted | severe integrity failure or explicit privacy/identity change |
| D-055 | GitHub and X are the launch authentication providers; Google is deferred until auth, API, persistence, recovery and policy contracts add it coherently | accepted | provider availability or explicit scope change |
| D-056 | VibeProof v1 may be rewritten incompatibly before implementation; no draft field has compatibility protection | accepted | production protocol ships |
| D-057 | Kernel anti-cheat and mandatory VibeMaxxing inference proxying are rejected for the default product | accepted | explicit product/privacy reversal supported by evidence |
| D-058 | Adapter, collector, detector and release trust is digest-addressed and provenance-bound; mutable names or versions alone never establish official identity | accepted | supply-chain evidence requires revision |
| D-059 | Public launch targets the complete core social product except countries; internal staging does not permit weak or placeholder launch behavior | accepted | explicit user scope change |
| D-060 | Open PR #17 is superseded by the July 23 audit, launch decisions, privacy and anti-cheat work and must not be merged unchanged | accepted | none |
| D-061 | `vibemaxxing-daemon` is an always-on OS-supervised per-user background service: enabled at installation, auto-started, automatically restarted, independent of shell state, and resident through paused/offline/degraded/recovery states; platform-imposed session boundaries must be disclosed honestly | accepted | explicit user reversal or executable evidence that the selected platform mechanism cannot meet ADR-010 |
| D-062 | macOS launch support includes both Apple silicon `arm64` and Intel `x86_64` under rolling exact-profile certification | accepted | explicit scope reversal or inability to satisfy release/security gates |
| D-063 | Windows launch support includes native `x64` and native `ARM64` across maintained desktop and applicable Server profiles | accepted | explicit scope reversal or upstream/toolchain infeasibility proven by evidence |
| D-064 | Linux launch support is broad and rolling across maintained desktop/headless distributions, major package ecosystems, `x86_64` and `aarch64`, with exact profile certification | accepted | explicit scope reversal or evidence-backed profile reduction |
| D-065 | WSL, containers and CI/ephemeral runners are globally competitive by default at the verifier-awarded evidence level; boards may impose stronger minimums | accepted | severe integrity failure or explicit competition-policy change |
| D-066 | Android, iOS, iPadOS and ChromeOS have no native collector, companion, control or launch application scope; hosted web remains an ordinary browser surface | accepted | explicit user reversal through a new ADR |
| D-067 | Optional machine-wide privileged supervision is allowed as a separately consented, least-privilege lifecycle profile that cannot inspect source content or bypass user isolation | accepted | independent review failure or explicit privilege-policy reversal |
| D-068 | Automatic updates are mandatory for competitive profiles, with signed release-set verification, bounded deferral, rollback and environment-specific mechanisms | accepted | explicit product reversal or updater evidence requires revision |
| D-069 | Automated Storybook capture is permitted only as read-only prototype/design validation and cannot satisfy product implementation, security or launch gates | accepted | implementation phase opens or workflow scope materially expands |
| D-070 | Duplicate-account consolidation combines valid historical competitive claim contributions under one surviving ranked identity, preserving original period attribution and corrections; stored account totals are never added together, imported records remain excluded, and overlapping or duplicate-domain contributions count once | accepted | explicit user reversal or demonstrated inability to reconstruct non-overlapping contributions safely |
| D-071 | Board invitations may grant only non-privileged membership roles; administrator promotion and ownership transfer are separate recent-authenticated, revision-checked, audited operations | accepted | explicit user reversal after abuse and recovery analysis |
| D-072 | A detected lineage fork quarantines all post-fork branches, preserves accepted pre-fork claims, selects or recovers one survivor where possible, resumes through a new lineage generation, never merges commitment chains, and remains appealable | accepted | cryptographic or recovery evidence requires a safer fork-resolution protocol |
| D-073 | Presence uses qualifying native pulses every 30 seconds, becomes idle after 90 seconds without a qualifying pulse, and becomes offline after 300 seconds; private is an independent viewer-visibility policy | accepted | measured battery/network evidence or user comprehension testing requires adjustment |
| D-074 | Automatic binary rollback is allowed only while the previous release remains read/write compatible with every committed local-state and database mutation; after an irreversible migration recovery is roll-forward or restoration of a verified pre-migration snapshot | accepted | implementation evidence proves a safer equivalent recovery mechanism |
| D-075 | High-impact idempotency records retain the exact replayable result for at least 30 days; claim-batch results remain replayable until a later acknowledged checkpoint safely supersedes them; expired keys are rejected rather than silently treated as new mutations | accepted | measured retention cost or recovery evidence supports a safer operation-specific window |
| D-076 | Hosted deletion and each local-device deletion are reported independently; the product never claims all local data erased while any device is offline, expired, unreachable, waived, or unverified | accepted | explicit user reversal or stronger independently verifiable local-erasure evidence |
| D-077 | Only provider-signed receipts or server-side retrieval under verified account binding may be labelled source-bound; device-signed, adapter-certified, or locally observed evidence is attested-local and cannot be elevated to source-bound by an SLM or client assertion | accepted | a new provider or platform attestation standard proves equivalent external-event authority |
| D-078 | E1 splits into E1-S provider-signed receipts, which remain unavailable, and E1-R provider-retrieved organization aggregates, which organization, hacker-house and community boards may enrol under ADR-016 as a board-scope corroboration input that never binds an individual claim, alters raw score, or reaches Hardened; individual and global boards remain self-reported because no provider exposes an individual usage authorization scope | accepted | a provider ships an individual usage authorization scope or a signed per-claim receipt, or withdraws administrative usage retrieval |
| D-079 | State identifiers use kebab-case in every source — the state-machine registry, SQL CHECK vocabularies, and OpenAPI enums — so one literal spelling appears in all three and no boundary needs a transform. Chosen over snake_case because `state-machine-registry-v1.schema.json` constrains identifiers to `^[a-z0-9]+(?:[.-][a-z0-9]+)*$`, which cannot express an underscore; adopting snake_case would have required either changing that schema or reintroducing the per-boundary mapping that PF-038 exists to remove. Enforced by `scripts/repository/validate_state_vocabularies.py`. | accepted | the registry schema's identifier pattern changes, or a downstream consumer cannot express kebab-case |

## Register rules

- Every material commitment receives a stable ID.
- Only allowed status values may be used.
- `provisional` and `research-required` items cannot be presented as production-proven.
- A planning decision may be complete while implementation evidence remains pending.
- `superseded` decisions remain for history and identify their replacement.
- Reopening an accepted decision requires the stated condition, an ADR where material and updates to dependent specifications, schemas and tasks.
- A completed planning validator proves only its declared structural checks; it does not override a later cross-contract audit.