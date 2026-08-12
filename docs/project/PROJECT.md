# VibeMaxxing Project Authority

Status: specification. P-1104 is `authorized-open` by owner decision of 2026-08-05; P-1140F semantic repair remains open with 13 active clusters, graded under D-300 as nine P0, three P1 and one P2. Nothing described in this document exists as a running system. `docs/project/STATUS.md` is the authoritative reality map and the only place that may state what is and is not built.

This file is the project spine. It states what VibeMaxxing is, how the system works end to end, what each component owns, what the privacy boundary is, and what the design cannot do. Every other document is detail hanging off this narrative. Use `docs/project/DOCUMENTATION.md` to find the single normative owner of any concept; this file does not replace a normative contract and never overrides one on its own subject matter.

## Identity and product

VibeMaxxing (`vibemaxxing`, `vibemaxxing.dev`) is a greenfield, privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It is inspired by WhoBurnedMore but does not migrate old accounts, rankings or scores. It measures authentic agent usage without judging usefulness or productivity.

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

## How the system works end to end

This section is the narrative the rest of the repository elaborates. It describes intended behavior under accepted contracts, not behavior that exists.

### The path a token takes

1. **A developer runs an AI coding agent.** Claude Code, Codex CLI, Gemini CLI, an IDE extension, a desktop agent or a local inference runtime. This is the *source runtime*. VibeMaxxing does not proxy it, does not hold its credentials and does not route model traffic through any VibeMaxxing-controlled inference service.

2. **An adapter observes the source.** One adapter per source product and version, bound to exact adapter-artifact, manifest, provenance and SBOM digests and to a registered source/version/platform/capture-mode tuple. It emits a `SourceObservation`: a typed token-observation variant, a source cursor, a monotonic clock domain and generation, a bounded wall-time interval, outcome and retry facts, and a non-content source-local reference. Raw source data is discarded after normalization or the shortest configured diagnostic window. No raw alias, provider request ID, prompt, output, path, repository name, tool content or content-derived hash may enter the next stage. The observation is L0, ephemeral, local-only and never network-serializable.

3. **The collector normalizes under a versioned accounting profile.** It resolves the observation into a `NormalizedAccountingEvent` — a durable L1 fact in an encrypted local store — using a digest-addressed accounting profile that fixes source fields, units, containment graph, mutually exclusive outputs, retry/cancellation/nested-execution policy and evidence ceiling. Token Burn is the checked sum of that profile's mutually exclusive outputs; a source total that already contains a subcategory is never added to it. The collector applies deterministic local rules, removes content-bearing fields and runs a deny-by-default privacy scan. `network_eligible=false` is a schema invariant on this object. The collector can read content, and therefore has no network access.

4. **A claim is built, gated and signed.** The claim builder assembles an `EvidenceClaim` from L1 facts and commitments. Immediately before serialization, the egress allowlist gate runs: a field absent from `packages/schemas/egress-allowlist-v1.json` is denied, and forbidden content rejects before egress rather than after. The gate runs after all optional detector and adapter work so nothing can be appended behind it. The surviving structure is serialized as deterministic CBOR (RFC 8949 with stricter rules: definite lengths, shortest encodings, sorted integer map labels, no floats or unregistered tags, re-encode-to-identical-bytes check) and signed by the device key service as COSE_Sign1, EdDSA/Ed25519, outer tag 18, empty unprotected map, 16-byte key UUID in `kid`, external AAD exactly `VIBEMAXXING/VIBEPROOF/V1`. Only fixed-schema aggregate accounting and integrity metadata exist in the result.

5. **The sync process submits.** `vibeproof-sync` is network-capable and cannot read source files or transcript storage. It obtains a server challenge — which binds account pseudonym, lineage, nonce, expected sequence, expected local head, expected checkpoint, expiry and maximum batch — and submits a binary `application/vibemaxxing-claim-batch+cbor` batch under a client-supplied idempotency key.

6. **The API edge is where an adversary first meets trusted code.** Authentication, rate limiting and encoded/body/allocation ceilings are enforced before anything is parsed. Everything in steps 1 through 5 runs on hardware the account owner controls; this is the first point at which it does not.

7. **The atomic verifier checks, then appraises.** In one transaction: enforce limits, canonically decode the batch and each COSE message, authenticate and lock the account/lineage verifier state, resolve the idempotency key plus exact request digest, check challenge ownership/expiry/expected tuple/single use, check every signature and key status, check artifact and profile digests, check numeric, time, accounting, privacy and duplicate-commitment invariants, then create claim facts and appraisals, consume the challenge, advance checkpoint state, write receipts and outbox rows, and commit all or none. A byte-identical retry returns the stored response bytes; a conflicting reuse is a conflict, never a partial success.

   The `VerifierAppraisal` is immutable and server-owned. It records ten independent dimensions — source authority, capture binding, accounting authority, device-key protection, continuity strength, environment assurance, freshness, exact compatibility and certification evidence, deterministic rule result, and anomaly disposition — and from them awards a named public profile: **Standard Competitive v1**, **Hardened Source-Bound v1**, or, for retrospective E5 material, **Imported v1**. Failure to satisfy Hardened evaluates Standard; failure to satisfy Standard becomes private analytics. A stronger value in one dimension never repairs a failed mandatory requirement in another. The client submits facts and can never select this outcome, nor eligibility, nor pricing, nor a correction.

8. **Facts land append-only in PostgreSQL.** Accepted claim bytes never mutate. Uniqueness constraints protect claim ID, `(device_id, sequence)`, challenge use and scoped dedup fingerprint, so a duplicate race can increase score at most once. A server-authorized `CorrectionRecord` appends; a reversal appends another correction referencing the prior one. Rejected claims are stored only with privacy-safe metadata, payload hash, reason code and bounded diagnostics.

9. **Projection workers derive the public rank.** Workers claim outbox rows with `FOR UPDATE SKIP LOCKED`, process idempotently, and apply additive deltas to `minute_scores` and `period_scores` keyed by unique source claim references. Corrections insert inverse and forward deltas. The canonical ranking query partitions by scope, period, eligibility, evidence filter and optional agent/model filter; score is `sum(token_burn_total)` or a separately selected estimated-cost interpretation, ordered by `rank() over (order by score desc)` with presentation tie-breakers `first_reached_score_at asc, account_id asc`. Rebuild truncates derived tables for a scope/version, deterministically replays accepted claims plus corrections, and hash-compares output before promotion. Estimated Cash Burn is computed here, server-side, from immutable usage facts and versioned pricing rules, and is always labelled an estimate.

Standard and Hardened accepted claims may both contribute to global boards. Imported claims may not. Boards may impose stronger environment or evidence minimums but may never redefine token accounting.

### Data path and trust boundaries

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ACCOUNT-OWNER HARDWARE — everything in this box runs on a machine the    ║
║  beneficiary of the score controls and can modify. Nothing here is        ║
║  trusted. Trust boundaries 1-7 of docs/security/THREAT_MODEL.md.          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  ┌────────────────────┐  Claude Code · Codex CLI · Gemini CLI · IDE       ║
║  │   source runtime   │  extension · desktop agent · local model server   ║
║  └─────────┬──────────┘  VibeMaxxing does not proxy or wrap provider      ║
║            │             traffic and holds no provider credential.        ║
║            │  L0 raw: log lines, response objects, transcript fragments,  ║
║            │  paths, local DB rows.  NEVER LEAVES THIS BOX.               ║
║  ┌─────────▼──────────┐  Binds exact artifact + manifest digests and the  ║
║  │      adapter       │  registered source/version/platform/mode tuple.   ║
║  │    NO NETWORK      │  Discards raw data after normalization.           ║
║  └─────────┬──────────┘                                                   ║
║            │  SourceObservation — L0, ephemeral, never network-           ║
║            │  serializable, forbidden from backups.                       ║
║  ┌─────────▼──────────┐  Digest-addressed accounting profile → mutually   ║
║  │     collector      │  exclusive token components. Deterministic rules. ║
║  │    NO NETWORK      │  Content-bearing fields removed; deny-by-default  ║
║  └─────────┬──────────┘  scan. Optional detector sandbox has no authority.║
║            │  NormalizedAccountingEvent — L1, encrypted local store,      ║
║            │  network_eligible=false as a schema invariant.               ║
║  ┌─────────▼──────────┐                                                   ║
║  │   claim builder    │  ▓▓▓▓▓▓ EGRESS ALLOWLIST GATE ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ║
║  │  + privacy gate    │  A field absent from egress-allowlist-v1.json is  ║
║  └─────────┬──────────┘  denied. Runs last, immediately before encoding.  ║
║            │  Deterministic CBOR, canonical, re-encode-checked.           ║
║  ┌─────────▼──────────┐  Ed25519 COSE_Sign1, tag 18, empty unprotected    ║
║  │ device key service │  map, kid = 16-byte key UUID, external AAD        ║
║  │  (class K1…K5)     │  VIBEMAXXING/VIBEPROOF/V1. Private keys never     ║
║  └─────────┬──────────┘  serialize. Lineage: enroll/rotate/recover/retire.║
║            │  EvidenceClaim — L2, the only class permitted to cross.      ║
║  ┌─────────▼──────────┐  Network-capable and therefore forbidden from     ║
║  │   sync process     │  reading source files or transcript storage.      ║
║  │  NO SOURCE READ    │  Holds challenge, batch, receipts, audit ledger.  ║
║  └─────────┬──────────┘                                                   ║
║            │      vibemaxxing-daemon supervises every process above and   ║
║            │      routes typed local IPC. CLI, tray/menu-bar shell and    ║
║            │      loopback dashboard are replaceable control clients.     ║
╚════════════╪══════════════════════════════════════════════════════════════╝
             │
 ════════════▼══════════════ DEVICE BOUNDARY ═══════════════════════════════
  Only fixed-schema aggregate accounting and integrity metadata cross.
  Below this line the code is operated by VibeMaxxing rather than by the
  measured party. This is the first place an adversarial party meets
  trusted code, and it is the line that bounds every integrity claim the
  system is allowed to make.
 ═══════════════════════════════════════════════════════════════════════════
             │  HTTPS · application/vibemaxxing-claim-batch+cbor
╔════════════▼══════════════════════════════════════════════════════════════╗
║  VIBEMAXXING-OPERATED — trust boundaries 8-13.                            ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  ┌────────────────────┐  Authentication, rate limits, encoded/body/       ║
║  │     API edge       │  allocation ceilings enforced before parsing.     ║
║  └─────────┬──────────┘                                                   ║
║  ┌─────────▼──────────┐  One transaction: canonical decode → signature →  ║
║  │  atomic verifier   │  challenge → expected sequence/head/checkpoint →  ║
║  │                    │  artifact/profile digests → accounting, privacy,  ║
║  │                    │  duplicate invariants → VerifierAppraisal.        ║
║  └─────────┬──────────┘  Standard | Hardened | private analytics.         ║
║            │             Server-assigned. Always. All-or-none commit.     ║
║  ┌─────────▼──────────┐  Append-only claims, payloads, appraisals,        ║
║  │  PostgreSQL ledger │  checkpoint receipts, corrections, quarantines.   ║
║  └─────────┬──────────┘  Accepted bytes never mutate. Transactional outbox║
║  ┌─────────▼──────────┐  FOR UPDATE SKIP LOCKED, idempotent, additive     ║
║  │ projection workers │  deltas → minute_scores → period_scores.          ║
║  └─────────┬──────────┘  Corrections append inverse deltas. Rebuild is    ║
║            │             deterministic and hash-compared before promotion.║
║  ┌─────────▼──────────┐  scope × period × eligibility × evidence filter.  ║
║  │    public rank     │  Token Burn is the raw metric. Estimated Cash     ║
║  └────────────────────┘  Burn is server-interpreted and labelled estimated║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### What each component owns

| Component | Owns | Must not | Normative contract |
|---|---|---|---|
| Source runtime | Producing the activity being measured | Be proxied, wrapped by a VibeMaxxing inference service, or surrender credentials | `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.json` |
| Adapter | Source-specific observation; binding exact artifact, manifest, certification, source-version, platform and capture-mode digests; declaring capture strength and a capability-derived maximum public profile | Emit any raw alias, request ID, prompt, output, path, repository name, tool content or content-derived hash; raise its own ceiling by registry presence | `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `packages/schemas/adapter-manifest.schema.json` |
| Collector | Normalization under a digest-addressed accounting profile; mutually exclusive canonical token components; deterministic local rules; content removal and the deny-by-default scan; local commitments | Have network access; emit a network-serializable normalized event; produce overlapping token totals | `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`, `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`, `packages/schemas/accounting-profile.schema.json` |
| Local detector (post-launch) | Optional advisory anomaly enums and confidence buckets from an isolated sandbox | Emit prose, embeddings or explanations; hold keys or credentials; touch counts or evidence state; reach the network | `docs/privacy/PRIVACY_CONTRACT.md`, `packages/schemas/local-detector-result.schema.json` |
| Claim builder and privacy gate | Assembling the `EvidenceClaim`; running the egress allowlist gate last; canonical CBOR serialization | Permit an unregistered field, arbitrary text, generic metadata map or extension channel | `docs/privacy/PRIVACY_CONTRACT.md`, `packages/schemas/egress-allowlist-v1.json` |
| Device key service | Ed25519 COSE_Sign1 signing; key protection class; enrollment, dual-authorized rotation, lost-key recovery, restore/clone detection, retirement, requalification | Serialize a private key; sign anything but facts and commitments; inherit Hardened across a reset lineage | `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `packages/schemas/device-lineage.schema.json` |
| Local durable store | Normalized facts, commitments, pending claims, receipts and the encrypted 90-day outbound audit ledger | Place L0 data in sync-accessible storage or in backups | `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md` |
| Sync process | Challenge acquisition, atomic batch submission, receipt handling, outbound audit entries | Read source files or transcript storage | `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` |
| Daemon | Always-on supervision, lifecycle, health, local policy, service-manager reconciliation, typed IPC routing | Read transcript contents; expose an ordinary "quit daemon" action; be stopped by closing the shell | `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, ADR-010 |
| CLI, tray/menu-bar shell, loopback dashboard | Installation, control, local status, privacy inspection, export, deletion, diagnostics | Be load-bearing — all three are replaceable clients of one versioned local control API | `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md` |
| Privileged machine supervisor (optional) | Service registration, supervision, bounded health, signed update coordination, repair and uninstall under separate consent | Read source content, hold ordinary user claim keys, intercept provider traffic, install kernel anti-cheat, open remote-control ports, or award Hardened by existing | ADR-012, `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md` |
| API edge | Authentication, rate limiting, size and allocation ceilings, request IDs, safe error details | Reveal abuse thresholds; parse before enforcing limits | `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` |
| Atomic verifier | Canonical decoding, signature, challenge, sequence/head/checkpoint continuity, certification and privacy invariants, idempotency, and the immutable `VerifierAppraisal` | Accept a client-selected evidence profile, eligibility, price or correction; commit partially | `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `packages/schemas/evidence-profile-policy-v1.json` |
| PostgreSQL fact ledger | Append-only claims, payload hashes, appraisals, receipts, corrections, quarantines, moderation effects; uniqueness constraints; transactional outbox | Mutate accepted claim bytes; retain invalid raw payloads by default | `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` |
| Projection workers | Minute and period aggregation, ranking materialization, pricing interpretation, presence leases, notification derivation, deterministic rebuild | Produce a rank not reproducible by replay from accepted claims plus corrections | `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`, `docs/product/CASH_BURN_PRICING_PROVENANCE.md` |
| Reviewer and admin systems | High-impact enforcement, moderation cases, appeals, recovery | Receive local raw logs, transcripts, prompts, code, paths or detector raw input | `docs/privacy/PRIVACY_CONTRACT.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` |
| Release and update system | TUF metadata, platform signatures, provenance, compatibility and rollback resistance | Be permanently disabled while competitive submission continues | ADR-013, `docs/operations/RELEASE_VERIFICATION.md` |

Component-level service topology, deployment shape and language ownership are detailed in `docs/architecture/ARCHITECTURE.md`. Trust boundaries 1 through 13, attacker capabilities and required controls per attack class are owned by `docs/security/THREAT_MODEL.md`.

## The privacy boundary

Stated precisely: **content never crosses the device boundary, and the architecture can hold that line without trusting the user.**

Servers, hosted web, observability, reviewer tools, support systems and release telemetry never receive prompts, responses or transcripts; source code, diffs, commands, tool bodies, arguments or results; filenames, paths, project names or repository names; session titles or user-authored local labels; emails extracted from local content; API keys, cookies, OAuth tokens or credentials; raw provider request identifiers; raw source logs or local database records; raw model aliases that can contain user-controlled text; embeddings, topics, summaries, coaching findings or classifications; transcript, prompt, output or code hashes; content-derived fingerprints intended to evade the content ban; local detector prose or hidden reasoning; or arbitrary diagnostic text. Hashing or embedding forbidden content does not make it safe to upload.

The guarantee is structural rather than behavioral, and it rests on three properties, each of which is testable:

1. **Process isolation.** A process capable of reading raw source content has no network access, and a network-capable process cannot read source files or transcript storage. The adapter and collector can read; they cannot reach the network. The sync process can reach the network; it cannot read. No privileged helper, daemon consolidation or debugging mode may bypass this separation without a new accepted privacy and architecture decision.

2. **A closed allowlist, not a denylist.** `packages/schemas/egress-allowlist-v1.json` enumerates every field permitted to cross, each with a stable identifier, wire type, maximum encoded size, semantic owner, classification, source process, destination, retention policy, user-visible explanation and a positive plus a privacy-negative fixture. A field absent from the registry is denied. There is no extension map, no generic metadata field and no free-text channel through which an unenumerated value could travel.

3. **The gate runs last.** The egress filter executes after all adapter and optional detector processing, immediately before canonical serialization and signing, so nothing can be appended behind it. Boundary canaries in `conformance/privacy/p1140b-boundary-canaries-v1.json` cover the adapter, IPC, local store, detector, claim, HTTP, telemetry, notification, moderation and export boundaries.

The consequence matters: the property to be checked is not "did the user behave" but "did the collector ever emit a forbidden field". That is a statement about a program, and a program can be tested against it — by canary fixtures, by schema tests that reject arbitrary text, maps and bytes, and by packet capture that exercises destination and payload allowlists. The user-facing privacy preview renders the exact serialized safe structure rather than a hand-written approximation, so what a user inspects is what the wire carries.

The boundary is symmetric in the other direction too. Because the servers hold no content, no server compromise, insider, reviewer, subpoena or telemetry pipeline can produce content that was never uploaded.

Documentation and a passing parser are not privacy evidence. `docs/privacy/PRIVACY_CONTRACT.md` owns this boundary in full, including data-stage classification L0/L1/L2/S1/P1, time privacy, presence privacy, notification privacy, telemetry rules, export privacy and the separation of server-side from local deletion.

## What the design cannot do

Measurement happens on hardware owned by the person who benefits from the score. That single fact bounds every integrity claim the system may make, and softening it would be a product defect rather than a marketing decision.

Consistent with `docs/security/THREAT_MODEL.md`:

- A device signature establishes only that the registered key signed those bytes. It does not establish that the local source was honest.
- A server challenge establishes submission freshness. It does not establish that an offline event existed before the challenge unless the event was bound to a previously acknowledged commitment head.
- Hardware-backed keys reduce cloning risk. They say nothing about token accounting.
- OAuth establishes control of a provider account, not one unique human.
- Ordinary provider usage metadata is not a provider-issued receipt.
- Platform attestation, where available, is a scoped input with issuer, measurement, nonce, freshness, expiry and revocation. It is never a blanket trust flag.
- A contestant with complete control of an unrestricted machine can alter software and local state.

The security objective is therefore stated as resistance and containment, not integrity in the strong form: make ordinary and scalable manipulation substantially harder than editing local logs, while preserving the absolute content-privacy boundary. The mechanisms are layered controls, explicit evidence ceilings per dimension, server-enforced sequence and checkpoint continuity, reproducible appraisal, progressive enforcement, human review and appeal.

Two structural gaps follow and are not scheduled to close:

- **Individual usage cannot be corroborated by a provider.** E1 provider-authoritative evidence splits into E1-S (a provider-signed receipt — reserved, and unavailable because no provider issues a qualifying artifact) and E1-R (server-side retrieval of an organization aggregate from a provider-operated administrative interface, authenticated by an administrator-supplied credential). No provider exposes a scope by which an individual permits third-party read of their own consumption, so E1-R is unreachable for individual accounts and individual evidence remains bounded by the user-controlled device. E1-R is partial by construction — administrative endpoints report API-key traffic while subscription-backed agent usage is largely unexposed — binds at board scope for a stated interval rather than to any single claim, never reaches Hardened, and does not alter raw score.
- **Kernel anti-cheat and mandatory provider proxying are rejected.** Both were considered and refused; neither is a future escape hatch.

The system must therefore never be marketed as mathematically cheat-proof, nor as universally establishing provider origin or unique human identity. Models and statistical detectors are secondary signals and cannot independently rewrite totals, raise evidence strength or permanently ban a user. The SLM detector is post-launch research and is not a launch dependency.

## Current state

This repository is a specification. The narrative above describes intended behavior under accepted contracts; it does not describe a running system.

`docs/project/STATUS.md` is the authoritative reality map and owns the complete implemented / not-implemented lists. In summary: what exists is a bounded fixture-backed hosted-web and Storybook prototype, planning validators and the repository doctor, planning-grade schemas, registries, fixtures and vectors, and bounded exploratory Rust and Go protocol/accounting prototypes whose evidence ceiling is cross-language parity only. The production collector, daemon, sync process, shell, installers, updater, local storage, certified adapters, normative VibeProof codecs, verifier, server services, PostgreSQL migrations and production infrastructure do not exist.

A green validator is not security, privacy, standards conformance, implementability or runtime behavior. A prototype is not product implementation. Empty or expired certification is not support evidence. Read the current evidence classification in `docs/project/DOCUMENTATION.md` before citing any artifact as evidence of anything.

## Platform authority

Under ADR-011 and D-062 through D-066:

- macOS launch support includes Apple silicon `arm64` and Intel `x86_64`;
- Windows launch support includes native `x64` and native `ARM64` on maintained desktop and applicable Server profiles;
- Linux launch support spans maintained desktop, headless and remote profiles through exact distribution/package/architecture certification;
- WSL, containers and CI/ephemeral runners are globally competitive by default at the verifier-awarded evidence level;
- boards may impose stronger environment or evidence minimums;
- Android, iOS, iPadOS and ChromeOS have no native collector, companion, control or launch application scope;
- hosted web remains usable as an ordinary browser surface without creating native-platform support claims.

"All platforms" means all accepted platform families through a rolling exact-profile registry, not unsupported historical releases or untested derivatives.

## Non-negotiable privacy and integrity

- Servers never receive prompts, responses, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights or content-derived hashes.
- Only fixed-schema aggregate accounting and integrity metadata crosses the device boundary.
- Transcript-capable processes have no network access; networked synchronization processes cannot inspect transcript content.
- Token Burn is the raw ranking metric of record; public rank is computed on Credited Token Burn, which is Token Burn times a server-assigned confidence weight under ADR-020, and public surfaces publish the credited figure only. Estimated Cash Burn is always explicitly an estimate and is computed server-side from immutable usage facts and versioned pricing rules.
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
- The product never silently exposes an ordinary "quit daemon" action.
- Users and the operating system retain the ability to disable or uninstall the background service. VibeMaxxing detects and visibly reports that state instead of bypassing user control.
- "Always-on" applies only while the machine is powered on, the OS can schedule the applicable service context, and the service remains installed and enabled.
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

## Identity and agent compatibility

The local product has separate adapter, collector, deterministic validation, local commitment, device-key, sync, always-on daemon/control, CLI, menu-bar/tray, privacy/audit and updater responsibilities, as laid out in the ownership table above. A process capable of reading content does not receive network access. The daemon owns supervision and lifecycle; the shell is only a replaceable control surface.

Primary launch identity paths are:

- GitHub through a provider-capability-aware GitHub App/web authorization architecture; device authorization is restricted to eligible limited-input or headless interactive profiles;
- X through OAuth 2.0 Authorization Code with PKCE, subject to provider availability.

Google is not a launch provider until authentication, API, persistence, recovery and policy contracts add it coherently.

OAuth establishes control of provider accounts, not one unique human. VibeMaxxing strongly enforces one active ranked identity per detected/resolved person using private linked-account, device, recovery and enforcement lineage, progressive restrictions, human review and appeals. Government identity documents and biometric proofing are not required by default.

Agent compatibility is capability-based, versioned and evidence-backed. Support states are Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported and Unsupported, and they are derived from exercised exact-version, mode, platform, artifact and accounting-profile certification rather than marketing claims. The collection ladder prefers the strongest available integration: ACP session broker, native OpenTelemetry, official hook or plugin, PTY/stdio wrapper, live source-bound log observation, then historical import. Generic ACP, OpenTelemetry, proxy, wrapper and unknown-version integrations remain private analytics until an exact tuple is certified.

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

Kernel anti-cheat and mandatory provider proxying are rejected. See **What the design cannot do** for the ceiling these layers operate under.

## Accepted stack

- Rust 2024: VibeProof, adapters, collector, native core, privacy boundaries, accounting, canonical encoding and signing.
- Go: OAuth, APIs, server verification/appraisal, ingestion, aggregation, ranking, presence, notifications, migrations and operations.
- Next.js App Router with strict TypeScript: hosted web.
- PostgreSQL/pgx and explicit SQL: server source of truth.
- Protobuf/Buf: internal typed contracts.
- Deterministic CBOR/CDDL/COSE: signed public evidence claims, receipts and appraisals.

Do not add Kubernetes, Kafka, GraphQL, service mesh, workflow engines, vector databases or ORM-heavy persistence without an evidence-backed ADR.

## Planning automation boundary

ADR-014 and D-069 permit the existing Storybook workflow only as read-only prototype/design-system validation using synthetic fixtures. It is not product CI, security evidence, production build evidence, deployment automation or launch evidence. All other product automation remains governed by D-034 until P-1104-related restoration work (`P-1007`) is completed against executable product code.

## Planning and evidence boundary

P-1140A–E are complete within their stated planning scopes. P-1140F remains open: 13 semantic clusters (SR-005 through SR-017) are active, tracked and explicitly not waived. D-300 graded them nine P0, three P1 and one P2; `conformance/p1140f/gate-authorization-v1.json` carries a non-regression ceiling for each severity and `docs/project/STATUS.md` owns the live counts. Current schemas and registries are planning inputs and must not be treated as implementation-ready where the audit marks them inconsistent.

P-1104 is `authorized-open` as of 2026-08-05 by owner decision recorded in GitHub issue 44 and in `conformance/p1140f/gate-authorization-v1.json`. It was opened while its own documented preconditions were unmet. Opening it authorizes work; it is not evidence, and it changed nothing about what exists. `docs/project/STATUS.md` and the `conformance/p1140f/` registries own the exact gate, finding and review-target state; prose here summarizes them and may not independently redefine counts or state.

Planning artifacts and prototype workflows are not working code, cryptographic interoperability evidence, certified adapters, performance evidence, packages, deployments, security hardening or launch readiness.

The repository is public, and has been since it was created on 2026-07-18. D-033 recorded the opposite and is superseded by D-540. Everything committed here is world-readable now, not at some later release decision, and the pre-publication audit `docs/planning/REPOSITORY_OPERATIONS.md` requires was never performed against it.

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

The narrative in **How the system works end to end** is a summary of the normative contracts named in the ownership table. Where it and one of those contracts disagree on a detail, the contract wins and this file is repaired — but a contract may not silently redefine the shape of the system without the narrative being updated in the same change.

Never resolve a material contradiction silently. Update decisions and affected contracts; use an ADR for material architectural or behavioral changes.
