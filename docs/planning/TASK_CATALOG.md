# VibeMaxxing Planning Task Catalog

Updated: 2026-07-24

Statuses: `complete-planning`, `in-progress-planning`, `blocked-planning`, `blocked-implementation`, `blocked-approval`, `blocked-launch-evidence`.

A task is `complete-planning` only when its normative planning artifacts exist, references resolve, applicable planning checks pass and its stated review scope is satisfied. It does not imply implementation, security evidence, certification or launch readiness.

## Historical planning groups

P-001 through P-1130 produced useful planning inputs. Where a later P-1140 task repaired or superseded them, the later contract is authoritative. Historical completion reports are not current authority.

## Active planning-repair program

### P-1140A — authority reset and launch-scope alignment

Status: `complete-planning`

Authority hierarchy, scope corrections, decision traceability, implementation handoff ownership and repository consolidation were established. Country leaderboards are post-launch, native mobile/ChromeOS work is out of scope, SLM is post-launch advisory research and implementation remains gated.

### P-1140B — core trust, privacy and accounting contracts

Status: `complete-planning`

Typed source observations, normalized accounting, detector results, local IPC, device lineage, accounting profiles, server-owned appraisal/pricing and deny-by-default egress contracts are present. These remain planning artifacts without runtime security evidence.

### P-1140C — VibeProof v1 protocol rewrite

Status: `complete-planning`

Closed deterministic CBOR/COSE contracts, exact vectors, replay/idempotency, checkpoint continuity, rotation, recovery, fork/clone handling and corrections are present. Independent codecs, fuzzing and interoperability evidence remain implementation work.

### P-1140D — identity, API, ranking, social, native and release contracts

Status: `complete-planning`

Candidate OAuth/session, ranked identity, API/idempotency, PostgreSQL, ranking, pricing, social, moderation, export/deletion, platform lifecycle, update and release-trust contracts are present. P-1140F has identified four semantic P1 repairs within this set, so it is not implementation-ready.

### P-1140E — structural cross-contract validation

Status: `complete-planning`

Dependencies: P-1140B, P-1140C and P-1140D.

Completed scope:

- exact D-001..D-069 registration and traceability closure;
- API operation, state-machine and candidate platform-profile coverage;
- planned positive/invalid transitions, SQL race cases and platform failure cases;
- reason-authority and reference closure;
- rejection of out-of-scope native mobile/ChromeOS paths;
- clean-checkout planning validation.

P-1140E proves structural repository consistency only. It does not prove semantic correctness, standards conformance, security, implementability or runtime behavior.

### P-1140F — semantic review and standards mapping

Status: `in-progress-planning`

Dependencies: P-1140B through P-1140E.

Canonical record: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`.

Open P1 repairs, in dependency order:

1. **SR-001 OAuth provider capability** — make authorization-response issuer verification capability-aware; bind provider configuration, token endpoint and exact redirect; add mix-up/redirect-confusion fixtures.
2. **SR-002 native authentication scope** — use external-browser Authorization Code + PKCE for normal desktop clients; restrict device authorization to explicitly eligible limited-input/headless interactive profiles; prohibit human device-code flow for unattended CI.
3. **SR-003 interactive shell lifecycle** — add one authoritative menu-bar/tray shell state machine and authenticated daemon IPC boundary; distinguish UI exit, collection pause, sync pause, daemon stop and uninstall.
4. **SR-004 immutable source evidence** — replace mutable platform source references with typed version/commit/digest-bound evidence and field authority.
5. Re-run P-1140E structural validation on the repaired exact head and record a final manual semantic review with zero open P0/P1 findings.

P-1140F acceptance:

- SR-001 through SR-004 are repaired in every affected normative owner, schema, fixture and validator;
- provider-specific OAuth and interactive-shell fixtures exist;
- platform source evidence is immutable and digest-bound;
- structural validation passes without claiming semantic proof;
- the exact-head semantic review records zero open P0/P1 findings;
- implementation remains unauthorized until the user separately opens P-1104.

## Future implementation and launch tasks

| ID | Task | Status | Reason |
|---|---|---|---|
| P-1007 | Restore product CI, security, dependency, evaluation and release checks | blocked-implementation | requires executable product code and P-1104 |
| P-1104 | Enter implementation phase | blocked-approval | requires P-1140F completion, clean validation, zero semantic P0/P1 findings and explicit user approval |
| P-1105 | Public-launch readiness review | blocked-launch-evidence | requires implemented system and executable evidence on every advertised profile |
| P-1131 | Select source/model golden paths and produce non-expired certifications | blocked-launch-evidence | requires real adapters, benchmarks and conformance |
| P-1150 | Country leaderboard research and planning | blocked-launch-evidence | post-launch only |
| P-1151 | SLM detector bakeoff | blocked-implementation | post-launch after deterministic baselines and data |

## Current conclusion

P-1140A through P-1140E are complete within their stated planning scopes. P-1140F is active. P-1104 remains blocked and is not ready for user authorization.
