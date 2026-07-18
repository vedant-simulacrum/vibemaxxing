# VibeMaxxing Planning Task Catalog

Updated: 2026-07-19

Statuses: `ready`, `in-progress`, `blocked-planning`, `complete-planning`, `deferred`.

A task is complete only when its committed output contains interfaces, schemas, invariants, limits, negative cases, failures, recovery, compatibility, privacy/security implications, tests, evidence, and explicit unresolved questions.

## P-000 — Repository truth and governance

| ID | Task | Status | Output |
|---|---|---|---|
| P-001 | Align authority order and current decisions | complete-planning | consistent root context/instructions/register |
| P-002 | Enforce planning-only phase | complete-planning | no accidental implementation |
| P-003 | Define evidence and completion language | complete-planning | model operating manual |
| P-004 | Maintain decision register and dependency map | complete-planning | planning control system |
| P-005 | Define artifact lifecycle and generated-file policy | complete-planning | artifact policy |
| P-006 | Define repository operations and launch-time check restoration | complete-planning | repository operations spec |
| P-007 | Regenerate manifest, index, and checksums from live tree | ready | accurate generated metadata |
| P-008 | Mark historical research current, superseded, or incorporated | ready | research provenance headers |
| P-009 | Define license, DCO/CLA, trademark, maintainer, release, and security governance | ready | open-source governance spec |

## P-050 — Complete product scope

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-051 | Freeze comprehensive public-launch feature matrix | ready | P-001 | launch scope contract |
| P-052 | Define staged internal milestones through public launch | ready | P-051 | milestone and gate matrix |
| P-053 | Freeze canonical glossary and consumer terminology | ready | P-051 | glossary |
| P-054 | Define complete user journeys and lifecycle states | ready | P-051, P-053 | journey/state catalog |
| P-055 | Define launch-quality, privacy, security, accessibility, performance, and operations gates | ready | P-051..054 | public launch gate |

## P-100 — Metrics, accounting, pricing, and time

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-101 | Freeze Token Burn formula and category semantics | ready | P-053 | versioned accounting spec |
| P-102 | Define retries, failures, streaming, cache, reasoning, tools, images, audio/video, compaction, and subagents | ready | P-101 | edge-case matrix |
| P-103 | Define cross-provider/local-model comparability and uncertainty | ready | P-101 | comparability policy |
| P-104 | Freeze Estimated Cash Burn for subscriptions, credits, regional pricing, local compute, unknown prices, and corrections | ready | P-101 | pricing interpretation contract |
| P-105 | Freeze periods, time zones, late/offline events, ties, streaks, seasons, resets, and corrections | ready | P-053 | ranking-time policy |

## P-200 — Universal agent compatibility

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-201 | Build machine-readable census of agent families and current products | ready | P-053 | agent registry |
| P-202 | Freeze adapter manifest schema | ready | P-101 | JSON Schema/examples |
| P-203 | Freeze normalized agent-event schema | ready | P-101, P-102 | event contract |
| P-204 | Define source authority, reconciliation, and double-count prevention | ready | P-203 | precedence matrix |
| P-205 | Define support tiers, degradation, suspension, emergency disable, and retirement | ready | P-202..204 | adapter lifecycle |
| P-206 | Define certification, privacy-negative, version, upgrade, and conformance tests | ready | P-202..205 | conformance plan |
| P-207 | Define community adapter governance and maintainer compromise response | ready | P-205, P-206 | contribution policy |
| P-208 | Define generated support claims and compatibility dashboard | ready | P-201..207 | publication contract |

## P-300 — VibeProof protocol

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-301 | Freeze claim fields, types, invariants, privacy classes, and size limits | ready | P-203 | field specification |
| P-302 | Freeze canonical CBOR profile and CDDL | blocked-planning | P-301 | canonical schema |
| P-303 | Freeze COSE algorithms, protected headers, key IDs, rotation, and agility | ready | P-301 | signing profile |
| P-304 | Define error and reason-code registry | ready | P-301..303 | stable taxonomy |
| P-305 | Define challenge, sequence, replay, duplicate, clock, session, crash, fork, and correction semantics | ready | P-301 | protocol state machines |
| P-306 | Define batching, compression, offline queue, acknowledgements, and compatibility negotiation | ready | P-301, P-305 | transport contract |
| P-307 | Complete golden, malformed, fuzz, resource, differential, and cross-language test plans | ready | P-302..306 | conformance plan |

## P-400 — Native daemon, collector, storage, IPC, and device identity

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-401 | Freeze process/privilege separation and transcript/network boundary | ready | P-301 | component contract |
| P-402 | Freeze daemon, collector, sync, CLI, shell, local UI, and hosted-web ownership | ready | P-401 | native topology |
| P-403 | Freeze local database schema, encryption, retention, export, and deletion | ready | P-301, P-305 | storage spec |
| P-404 | Define crash consistency, checkpoints, retries, disk-full, corruption, sleep/resume, and offline behavior | ready | P-403 | recovery state machines |
| P-405 | Freeze IPC schemas, peer authentication, limits, negotiation, and errors | ready | P-401, P-402 | IPC protocol |
| P-406 | Freeze macOS, Windows, Linux, WSL, container, CI, and remote-environment capability matrix | ready | P-401, P-405 | platform matrix |
| P-407 | Freeze device enrollment, OAuth binding, key rotation, revocation, cloning, loss, and transfer | ready | P-303, P-305 | device state machine |
| P-408 | Freeze CLI commands, installer, menu-bar/tray UX, autostart, update, rollback, and uninstall | ready | P-402, P-406 | native UX/packaging contract |
| P-409 | Define CPU, memory, battery, disk, startup, and throughput budgets and benchmarks | ready | P-401..408 | benchmark protocol |

## P-500 — Authentication, account identity, and authorization

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-501 | Research GitHub App versus OAuth App and X/Twitter sign-in constraints | ready | P-053 | identity ADR |
| P-502 | Freeze account, linked-provider, optional stronger-factor, session, recovery, merge, and deletion state machines | ready | P-501, P-407 | auth contract |
| P-503 | Freeze native device authorization and browser binding | ready | P-501, P-407 | native auth protocol |
| P-504 | Define provider compromise, suspension, rename, loss, and takeover handling | ready | P-502 | recovery/abuse contract |
| P-505 | Freeze authorization matrix for profiles, devices, boards, organizations, moderation, export, and deletion | ready | P-502 | permission matrix |

## P-600 — Server, database, ingestion, aggregation, and ranking

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-601 | Freeze public APIs, requests, responses, auth, limits, idempotency, privacy classes, and errors | ready | P-304, P-407, P-502 | API contract |
| P-602 | Freeze PostgreSQL entities, keys, constraints, partitions, retention, and migrations | ready | P-601 | logical schema |
| P-603 | Freeze claim-acceptance transaction and sequence/idempotency boundaries | ready | P-602 | transaction spec |
| P-604 | Freeze outbox, workers, aggregates, rollover, late events, rebuild, correction, and cache invalidation | ready | P-603 | worker state machines |
| P-605 | Freeze leaderboard queries, ties, pagination, current-user rank, privacy, evidence filters, and quarantines | ready | P-105, P-604 | ranking/query contract |
| P-606 | Define capacity, duplicate storm, crash, failover, period rollover, and rebuild benchmarks | ready | P-602..605 | benchmark protocol |

## P-700 — Social, boards, presence, notifications, abuse, and lifecycle

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-701 | Freeze profiles, usernames, rename, discoverability, and impersonation rules | ready | P-502 | identity product contract |
| P-702 | Freeze friendships, blocks, rivals, overtakes, movement, and streaks | ready | P-605, P-701 | social domain model |
| P-703 | Freeze private boards, organizations, hacker houses, communities, ownership, invitations, and administration | ready | P-505, P-605 | board domain model |
| P-704 | Freeze country-board assertion, privacy threshold, changes, and abuse policy | ready | P-105, P-505 | country policy |
| P-705 | Freeze presence heartbeat, idle, expiry, privacy, multi-device, multi-agent, and offline behavior | ready | P-402, P-605 | presence state machine |
| P-706 | Freeze notification taxonomy, channels, grouping, hysteresis, rate limits, quiet hours, and privacy | ready | P-702, P-705 | notification contract |
| P-707 | Freeze abuse signals, quarantine, restrictions, moderator actions, appeals, restoration, and insider controls | ready | P-603, P-702..706 | moderation state machine |
| P-708 | Freeze retention, audit, data export, deletion, legal hold, and account lifecycle | ready | P-602, P-707 | lifecycle contract |

## P-800 — Anti-cheat and evidence integrity

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-801 | Populate complete attack catalog with controls, residual risk, tests, policy, and appeals | in-progress | P-101..708 | attack/control catalog |
| P-802 | Define deterministic reason codes and evidence qualification matrix | ready | P-304, P-801 | policy registry |
| P-803 | Design replay, cloning, rollback, source impersonation, collusion, downgrade, Sybil, and poisoning campaigns | ready | P-801 | attack laboratory |
| P-804 | Define privacy-safe structural feature schema and fixture policy | ready | P-203, P-801 | feature/fixture contract |
| P-805 | Compare rules, robust statistics, graph methods, classical anomaly detection, and SLMs | ready | P-804 | detector bakeoff |
| P-806 | Define SLM isolation, signed model/runtime distribution, reproducibility, update, rollback, and adversarial tests | blocked-planning | P-805 | SLM feasibility decision |
| P-807 | Define false-accept, false-reject, false-quarantine, latency, appeal, and disparate-effect budgets | ready | P-707, P-805 | calibration policy |
| P-808 | Define continuous red-team, responsible disclosure, regression, and private-threshold operations | ready | P-803..807 | integrity operations plan |

## P-900 — Web, native UX, design, accessibility, and privacy verification

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-901 | Freeze complete route and information architecture | ready | P-051, P-605, P-701..708 | route map |
| P-902 | Freeze page/component data contracts and all loading, empty, error, offline, private, restricted, quarantined, deleted, and unsupported states | ready | P-901 | frontend contract |
| P-903 | Freeze local privacy audit, outbound ledger, permission, adapter, device, and deletion UX | ready | P-402..408 | local UX spec |
| P-904 | Freeze evidence labels, explanations, uncertainty, and support-state presentation | ready | P-205, P-802 | content/component spec |
| P-905 | Define responsive, browser, keyboard, screen-reader, reduced-motion, visual-regression, and performance plans | ready | P-901..904 | QA plan |

## P-1000 — Packaging, production operations, and open-source launch

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-1001 | Freeze supported platform/install matrix and signing/notarization requirements | ready | P-406, P-408 | packaging matrix |
| P-1002 | Freeze TUF roles, root bootstrap, rotation, expiry, freeze/rollback defense, atomic install, and recovery | ready | P-1001 | updater contract |
| P-1003 | Freeze observability allowlist, event schema, sampling, access, retention, canaries, and incident use | ready | all domains | telemetry contract |
| P-1004 | Decide providers, regions, environments, config, secrets, queues/cache, migrations, and promotion | ready | P-601, P-602 | deployment ADR/spec |
| P-1005 | Freeze SLOs, capacity, backup, restore, RPO/RTO, disaster recovery, incident, rollback, and key compromise | ready | P-1002..1004 | operations plan |
| P-1006 | Freeze license, DCO/CLA, trademark, security advisories, maintainer, contributor, release, and adapter governance | ready | P-009, P-207 | open-source launch policy |
| P-1007 | Restore and validate required automated CI, security, dependency, eval, release, provenance, and consumer-verification checks | blocked-planning | implementation phase | launch automation evidence |

## P-1100 — Final planning and launch reviews

| ID | Task | Status | Dependencies | Output |
|---|---|---|---|---|
| P-1101 | Cross-document contradiction and stale-claim audit | blocked-planning | P-050..1000 | zero unresolved P0 contradictions |
| P-1102 | Privacy/threat/control traceability review | blocked-planning | P-050..1000 | traceability matrix |
| P-1103 | Schema, API, state-machine, migration, recovery, and task completeness review | blocked-planning | P-050..1000 | implementation handoff report |
| P-1104 | User approval to enter implementation | blocked-planning | P-1101..1103 | explicit phase change |
| P-1105 | Comprehensive public-launch readiness review | blocked-planning | implementation and evidence | launch decision |
