# VibeMaxxing Project Authority

Status: planning alignment and contract repair; implementation not authorized.

## Identity and product

VibeMaxxing (`vibemaxxing`, `vibemaxxing.dev`) is a greenfield, privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It is inspired by WhoBurnedMore but does not migrate old accounts, rankings or scores.

Product thesis: **Codex restraint × Steam social competition**.

Visual thesis: **The Competitive Ledger**.

Public launch targets:

- global, friends, private-board, organization, hacker-house and community leaderboards;
- daily, weekly, monthly, seasonal, yearly and lifetime periods;
- profiles, friends, rivals, overtakes and rank movement;
- source-bound active presence;
- groups, boards and administration;
- notifications;
- moderation, restrictions and appeals;
- Token Burn and Estimated Cash Burn;
- native local UX, hosted web and broad tiered agent compatibility;
- complete launch support for macOS, Windows, Linux, WSL, containers and CI under exact exercised profiles.

Country leaderboards are explicitly post-launch. Internal implementation may be staged but must not silently redefine the public-launch target.

## Platform authority

Under ADR-011 and D-062 through D-066:

- macOS launch support includes Apple silicon `arm64` and Intel `x86_64`;
- Windows launch support includes native `x64` and native `ARM64` on maintained desktop and applicable Server profiles;
- Linux launch support spans maintained desktop, headless and remote profiles through exact distribution/package/architecture certification;
- WSL, containers and CI/ephemeral runners are globally competitive by default at the verifier-awarded evidence level;
- boards may impose stronger environment or evidence minimums;
- Android, iOS, iPadOS and ChromeOS have no native collector, companion, control or launch application scope;
- hosted web remains usable as an ordinary browser surface without creating native-platform support claims.

“All platforms” means all accepted platform families through a rolling exact-profile registry, not unsupported historical releases or untested derivatives.

## Non-negotiable privacy and integrity

- Servers never receive prompts, responses, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights or content-derived hashes.
- Only fixed-schema aggregate accounting and integrity metadata crosses the device boundary.
- Transcript-capable processes have no network access; networked synchronization processes cannot inspect transcript content.
- Token Burn is the default raw ranking metric; Estimated Cash Burn is always explicitly an estimate and is computed server-side from immutable usage facts and versioned pricing rules.
- Historical imports remain private analytics and never enter active competition.
- Authentic intentionally pointless usage counts when non-duplicated.
- Deterministic controls own accounting, signatures, canonicalization, sequences, replay, duplicates, continuity and hard eligibility.
- Standard and Hardened accepted claims may both contribute globally; Imported claims may not.
- The server verifier awards public evidence status under a named, versioned profile. The client never self-awards Standard or Hardened.
- Local-model and delayed offline usage are first-class competitive usage when deterministically captured by a certified source profile.
- Models and statistical detectors are secondary signals and cannot independently rewrite totals, award stronger evidence or permanently ban users.
- The SLM detector is post-launch research only and is not a launch dependency.
- The system must never be marketed as mathematically cheat-proof or as universally proving provider origin or unique human identity.

## Always-on local service

`vibemaxxing-daemon` is a core always-on product service under D-061 and ADR-010.

- Successful installation registers and enables the daemon with the platform service manager.
- The daemon auto-starts at the earliest supported boot or user-login boundary.
- It is automatically restarted after crashes and resumes health reconciliation after sleep, hibernation, network loss and OS restart.
- Closing or crashing the menu-bar/tray shell never stops the daemon, collector or pending synchronization.
- Pausing collection or synchronization changes only that function; the daemon remains resident for health, recovery, privacy inspection, export, update, rollback and uninstall.
- Offline, authentication-required, permission-required, disk-full, corrupt-state, security-hold and update-failure conditions place the daemon in an explicit degraded or recovery state rather than causing it to exit.
- The product never silently exposes an ordinary “quit daemon” action.
- Users and the operating system retain the ability to disable or uninstall the background service. VibeMaxxing detects and visibly reports that state instead of bypassing user control.
- “Always-on” applies only while the machine is powered on, the OS can schedule the applicable service context, and the service remains installed and enabled.
- WSL, containers and CI disclose host/orchestrator/job lifecycle limitations honestly.

## Privilege model

The default runtime is unprivileged and per-user.

ADR-012 and D-067 allow optional machine-wide privileged supervision only as a separately consented lifecycle profile. A privileged supervisor may register, start, monitor, update and recover approved services, but may not inspect source content, hold ordinary user claim keys, intercept provider traffic, install kernel anti-cheat, bypass cross-user isolation or open remote-control ports.

Privileged profiles require independent packaging, least-privilege review, cross-user tests, privacy canaries and platform-specific release evidence. Enabling privilege never self-awards Hardened evidence.

## Mandatory automatic updates

Under ADR-013 and D-068, automatic updates are mandatory for competitive profiles.

- Users may select supported release channels and bounded maintenance timing but may not permanently disable required security or compatibility updates while continuing competitive submission.
- Updates are signed, provenance-bound, release-set compatible and rollback/freeze resistant.
- Active work reaches a safe durable checkpoint before ordinary restart.
- Emergency privacy or integrity updates may stop unsafe collection immediately.
- Blocked versions retain update, export, diagnostics and uninstall where safely possible.
- Containers update through immutable image replacement; CI uses current pinned tool artifacts rather than a persistent updater.

## Product topology and identity

The local product has separate adapter, collector, deterministic validation, local commitment, device-key, sync, always-on daemon/control, CLI, menu-bar/tray, privacy/audit and updater responsibilities. A process capable of reading content does not receive network access. The daemon owns supervision and lifecycle; the shell is only a replaceable control surface.

Primary launch identity paths are:

- GitHub through the accepted GitHub App/web/device authorization architecture;
- X through OAuth 2.0 Authorization Code with PKCE, subject to provider availability.

Google is not a launch provider until authentication, API, persistence, recovery and policy contracts add it coherently.

OAuth proves control of provider accounts, not one unique human. VibeMaxxing strongly enforces one active ranked identity per detected/resolved person using private linked-account, device, recovery and enforcement lineage, progressive restrictions, human review and appeals. Government identity documents and biometric proofing are not required by default.

Agent compatibility is capability-based, versioned and evidence-backed. Public support states are derived from exercised exact-version, mode, platform, artifact and accounting-profile certification rather than marketing claims.

## Anti-cheat architecture

The planned anti-cheat system consists of:

1. source-specific deterministic accounting;
2. signed, digest-addressed adapters and collector builds;
3. typed local collection and privacy filtering;
4. deterministic local integrity rules;
5. protected device signing keys and explicit device lineage;
6. append-only local commitments and server checkpoint receipts;
7. atomic server replay, duplicate, fork and challenge validation;
8. independent verifier appraisal;
9. privacy-safe server anomaly analysis in shadow-first rollout;
10. progressive enforcement, human review, appeal and deterministic ranking rebuild.

Kernel anti-cheat and mandatory provider proxying are rejected.

## Accepted stack

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundaries, accounting, canonical encoding and signing.
- Go: OAuth, APIs, server verification/appraisal, ingestion, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router with strict TypeScript: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal typed contracts.
- Deterministic CBOR/CDDL/COSE: signed public evidence claims, receipts and appraisals.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases or ORM-heavy persistence without an evidence-backed ADR.

## Planning automation boundary

ADR-014 and D-069 permit the existing Storybook workflow only as read-only prototype/design-system validation using synthetic fixtures. It is not product CI, security evidence, production build evidence, deployment automation or launch evidence. All other product automation remains governed by D-034 until P-1104.

## Planning and evidence boundary

P-1140A–E must repair and validate current contracts before implementation may begin. Current schemas and registries are planning inputs and must not be treated as implementation-ready where the audit marks them inconsistent.

Implementation requires explicit user approval under P-1104 after P-1140A–E and clean planning validation complete.

Planning artifacts and prototype workflows are not working code, cryptographic interoperability evidence, certified adapters, performance evidence, packages, deployments, security hardening or launch readiness.

The repository remains private during planning and must become public open source before public launch.

## Authority

When sources disagree:

1. the user's latest explicit instruction;
2. this file;
3. `docs/project/STATUS.md`;
4. `docs/planning/DECISION_REGISTER.md`;
5. accepted ADRs;
6. repaired normative contracts and authoritative schemas;
7. the inactive implementation handoff;
8. research, audits and historical records.

Never resolve a material contradiction silently. Update decisions and affected contracts; use an ADR for material architectural or behavioral changes.