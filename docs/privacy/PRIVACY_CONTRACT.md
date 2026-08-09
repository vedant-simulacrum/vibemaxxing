# Privacy Contract

Updated: 2026-08-06
Status: normative planning contract; P-1140B egress contract frozen, P-1140F semantic review is active, and P-1104 is `authorized-open` under `conformance/p1140f/gate-authorization-v1.json`, which owns gate state

This contract governs the engineering boundary. `docs/privacy/DATA_MAP.md` governs what personal data exists on each side of it, on which lawful basis and for how long, and is also the Article 30 record of processing activities. `PRIVACY.md` is the participant-facing notice derived from that map. Neither has been reviewed by counsel; D-109 records that review as an unmet release gate.

## The boundary is a content guarantee, not a metadata guarantee

Stated here because ADR-019 identified this contract as its owner and required the statement, and because every other section reads as stronger than it is without it.

Everything below is a guarantee about **content**: no prompt, response, transcript, line of code, diff, tool body, filename, path, project name or repository name crosses the device boundary, in any form, including hashed, embedded, summarized or classified. That guarantee is absolute and is enforced by a deny-by-default allowlist.

It is not a guarantee about **metadata**. An allowlist constrains which fields exist; it does not constrain how much information a permitted field carries. Token counts at fine granularity leak a participant's working pattern and the approximate scale of their work, and presence leaks the same timeline from a different field. Both are recorded as accepted, unmitigated residual risks in ADR-019 as RR-002 and RR-001. No surface, claim, support answer or privacy notice may state or imply that presence is safe from monitoring, or that fixed-schema aggregate publication leaks nothing. Those two sentences are false and are permanently unavailable.

## Absolute server boundary

VibeMaxxing servers, hosted web, observability, reviewer tools, support systems and release telemetry must never receive:

- prompts, responses or transcripts;
- source code, diffs, commands or tool bodies;
- tool arguments or results;
- filenames, paths, project names or repository names;
- session titles or user-authored local labels;
- emails extracted from local content;
- API keys, cookies, OAuth tokens or credentials;
- raw provider request identifiers;
- raw source logs or local database records;
- raw model aliases when they can contain user-controlled text;
- embeddings, topics, summaries, coaching findings or classifications;
- transcript, prompt, output or code hashes;
- content-derived fingerprints intended to evade the content ban;
- local detector prose or hidden reasoning;
- arbitrary diagnostic text.

This boundary is non-negotiable. Hashing or embedding forbidden content does not make it safe to upload.

## Process isolation rule

A process capable of reading raw source content must not have network access.

The minimum launch topology is:

1. source adapter/collector reads approved local sources;
2. collector normalizes and applies deterministic accounting locally;
3. collector removes content-bearing fields and performs a deny-by-default privacy scan;
4. only typed safe facts enter sync-accessible storage;
5. networked sync can read only safe claims, receipts and account/session material;
6. server receives only the fixed outbound contract.

No privileged helper, daemon consolidation or debugging mode may bypass this separation without a new accepted privacy and architecture decision.

## Data-stage classification

### Class L0 — ephemeral raw local source data

Examples:

- source log lines;
- provider response objects;
- transcript fragments;
- paths and project metadata;
- raw local database rows.

Rules:

- readable only by the source adapter/collector or separately approved local detector sandbox;
- never copied into sync-accessible storage;
- shortest practical retention;
- excluded from backups by default;
- no network or telemetry access.

### Class L1 — normalized local accounting facts

Examples:

- canonical source/model IDs;
- token observations;
- runtime generation;
- monotonic intervals;
- local duplicate-domain fingerprints;
- deterministic rule results.

Rules:

- stored encrypted locally;
- may contain richer machine facts than the outbound claim;
- not directly network serializable;
- raw aliases and provider request IDs remain absent;
- retention is configurable and visible.

### Class L2 — outbound-safe claim data

Only the exact `EvidenceClaim` allowlist may cross the network.

Allowed classes include:

- protocol and schema versions;
- registered source/provider/model IDs;
- adapter, collector, accounting-profile and certification digests;
- canonical token components;
- bounded event interval and uncertainty;
- monotonic duration and generation code;
- device lineage/key IDs;
- claim sequence and commitment heads;
- challenge ID/nonce;
- duplicate-domain commitment;
- deterministic rule bundle/result codes;
- privacy policy ID and pass result;
- optional local-detector result commitment;
- device signature.

No arbitrary text, generic metadata map or unregistered extension channel is permitted.

### Class S1 — server private integrity data

Examples:

- provider subject identifiers;
- device/key lineage;
- challenge and replay state;
- verifier appraisals;
- duplicate-identity signals;
- moderation evidence references;
- session/token-family lineage;
- appeal records.

Rules:

- access-controlled by role and purpose;
- never public leaderboard fields;
- not shared with organizations or board administrators beyond minimum eligibility state;
- retention and deletion policy documented per table;
- reviewer access audited.

### Class P1 — public product data

Examples:

- handle and approved avatar;
- Token Burn score and rank;
- public evidence state/profile disclosure;
- user-approved board memberships;
- public social state selected by the user.

Public disclosure never includes private identity signals, device identifiers, exact source timestamps, raw claim data or moderation evidence.

## Outbound field rules

Every outbound field must have:

- stable field identifier;
- type and maximum encoded size;
- semantic owner;
- privacy classification;
- source process;
- destination;
- retention policy;
- user-visible explanation;
- positive and privacy-negative fixture.

A field absent from the allowlist is forbidden.

The registry schema is `packages/schemas/egress-allowlist-v1.schema.json`; the only current claim registry is `packages/schemas/egress-allowlist-v1.json`. Each entry fixes wire type, maximum encoded bytes, semantic owner, source process, destination, retention policy, user explanation and positive/negative fixture IDs. Boundary canaries are enumerated in `conformance/privacy/p1140b-boundary-canaries-v1.json`.

The egress filter runs after all optional detector and adapter processing, immediately before canonical serialization and signing. The user-facing privacy preview renders the exact serialized safe structure, not a hand-written approximation.

## Identifiers and fingerprints

- Raw provider request IDs do not leave the device by default.
- Deduplication uses keyed local commitments over approved non-content structural facts.
- Keys for local fingerprints are device-local and separate from signing keys.
- The server receives only a domain-scoped commitment necessary for conflict detection.
- Fingerprints must not be stable across unrelated accounts or products.
- No stable public hardware identifier is created.
- Device lineage IDs are private server/account identifiers, not public profile fields.

## Time privacy

- Raw source timestamps remain local.
- Claims may contain bounded coarse event intervals required for ranking, delayed-sync policy and replay analysis.
- Exact precision is the minimum required by the accounting profile and is not publicly displayed.
- Public history is day-level by default.
- Presence uses a separate lease and privacy policy.
- Client wall time is diagnostic and cannot alone determine competitive periods.

## Presence privacy

Presence is derived only from qualifying collector activity and projected per viewer.

The server may retain:

- account and device references;
- coarse registered agent family;
- activity/lease state;
- start/renewal buckets;
- evidence state;
- privacy policy version.

It must never retain prompts, project names, filenames, repository names, tool contents or free-form activity descriptions.

Blocking, device revocation and privacy changes invalidate visibility immediately. Multiple devices merge into a deterministic public state without exposing which project or source is active.

### Pulse, lease generation and audience projection

`packages/schemas/presence-pulse-v1.schema.json` is the machine-readable form of the three records this section needs, and D-618 and D-619 record the choices.

A qualifying pulse names a device, a lease generation and a boolean. `qualifying` is a boolean rather than a description because a description would be content. Only a native collector produces one: a browser tab open on a leaderboard is not evidence that a participant is working, and counting it would make presence a measure of who is looking at the product.

The lease generation is what stops a resumed process from reviving an expired lease. A daemon restart mints a new generation, and a pulse naming a superseded one is discarded rather than applied.

Presence visibility is a policy and not a state. A private participant still holds a lease and still transitions; what changes is who may read the projection. Collapsing the two would make going private indistinguishable from going offline. It is one policy per account and lives on `profiles.presence_visibility`. It was a column on `presence_leases`, one value per device, against a projection that answers once per account: going private on a laptop while a desktop stayed authorized published the participant anyway, and nothing said which value the merge took.

The three D-073 thresholds are bound to policy keys by `const` in that schema, and the validator asserts the resolved values are 30, 90 and 300 seconds against `presence_heartbeat_seconds`, `presence_idle_after_seconds` and `presence_offline_after_seconds`. Two of those keys used to be misnamed: `presence_lease_expiry_seconds` held 90 and meant idle, `presence_idle_after_seconds` held 300 and meant offline, so the registry read straight described a lease expiring before it could go idle. D-618 renamed them, and the idle threshold is now additionally required to be strictly before the offline one, so the pair cannot be swapped back by value.

None of this is a presence history. ADR-019 accepts a live-sampling risk on the stated basis that no history is stored, so `presence_events` carries `no-retention` in `packages/schemas/data-disposition-v1.json` and rows are discarded when their generation closes. Retaining them would convert an accepted risk into a larger one without anybody deciding to.

A projection suppressed for a reason other than the subject being offline records why, and never discloses it to the viewer: telling a viewer they were suppressed tells them the subject is online.

## Notification privacy

Notification payloads are typed closed-world events. They may contain only IDs and display fields authorized for the recipient at delivery time.

Required controls:

- authorization and visibility recheck before delivery and rendering;
- no cached private profile fields after a block/privacy change;
- stable dedup/grouping keys;
- retraction when the underlying relationship, ranking or moderation state changes;
- no arbitrary JSON payload;
- no source-content-derived text;
- quiet hours and preference enforcement without leaking event details to disabled channels.

## Current viewer authorization

The rule above — recheck before delivery and rendering — appears in this contract, in the social contract and in the product specification, and none of them said what is rechecked or against what. SR-015 records that gap. `packages/schemas/projection-authorization-v1.json` closes the naming half of it and D-386 records the choices.

Nine inputs are read. Each names the table it reads and the column that changes when it changes, and the validator fails when either does not resolve: directional blocks, subject visibility, friendship, rivalry, board membership, board container state, presence visibility, account lifecycle and ranked-identity state.

Deny inputs are evaluated before widen inputs, in that fixed order, because two orders decide differently for a viewer who is simultaneously a friend and blocked. A directional block and a `deletion-pending` account are hard denials that no other input restores.

No authorization result is cached anywhere, including in a request-scoped memo that outlives the statement that produced it. A cached decision is the defect, not an optimisation of it. A projection may be cached only when it is identical for every viewer, which is true of a sealed generation's figures and of nothing else.

A change racing the response fails the request rather than serving the earlier answer: the decision compares the revisions it read against the revisions present when the response is emitted. A participant who pressed block is entitled to assume it took effect, and a retry costs one request. An input that cannot be read is a denial, because an authorization system whose outage widens access has the wrong default.

Nine surfaces evaluate it. Eight recheck at read or delivery time; the export package is the single snapshot-time exception, and it is one because the subject and the viewer are the same person and no third party's authorization can change under it.

This names the rule. No surface in this repository evaluates it, so SR-015 is advanced and not closed.

## Moderation and support privacy

Reviewers may inspect:

- accepted claim IDs and digests;
- verifier appraisal dimensions;
- reason codes;
- device/account/recovery lineage summaries;
- aggregate anomaly features;
- exact affected ranking views and periods;
- prior enforcement and appeal records.

Reviewers must not receive local raw logs, transcripts, prompts, code, paths or detector raw input.

User-safe explanations are separate from private reviewer evidence. Organization/board administrators receive only the minimum restriction or eligibility state required for their role.

## Authentication and identity privacy

- Provider subjects are private linkage identifiers.
- Mutable provider usernames are not identity keys.
- Public profiles may remain pseudonymous.
- Government IDs, facial scans, biometric templates, legal names, addresses and exact dates of birth are not required by default.
- IP and user-agent data are minimized, purpose-bound and retained only under documented policy.
- Duplicate-identity signals are never exposed publicly.
- A shared IP, network or device is not sufficient by itself for high-impact enforcement.

## Telemetry and logs

Telemetry is deny-by-default and limited to registered dimensions such as:

- route template;
- status class;
- latency and byte counts;
- registered reason code;
- worker type and queue age;
- database operation class;
- adapter ID/version and evidence profile;
- release/update verification state.

Forbidden in telemetry/logs:

- request/response bodies;
- claim bytes;
- handles unless an explicitly approved audit event requires a private account ID instead;
- OAuth tokens, cookies or headers;
- model aliases containing free text;
- arbitrary exception messages from source-processing code;
- local paths, repos or transcript-derived fields.

Errors crossing a boundary use stable reason codes and bounded typed diagnostics.

## Local outbound audit ledger

The client maintains an encrypted local audit ledger with a default retention of 90 days, subject to policy and user control.

Each entry records:

- claim ID;
- exact field names and serialized values sent;
- destination and protocol version;
- encoded byte count;
- adapter/accounting/certification digests;
- local contributing event references;
- send time and receipt outcome;
- server appraisal and checkpoint receipt reference;
- rejection reason codes.

The ledger contains no raw source content and can be exported or deleted locally.

## Storage, backup and deletion

Every table/store must define:

- purpose and owner;
- data classification;
- access roles;
- retention;
- export behavior;
- deletion behavior;
- backup treatment;
- legal-hold behavior.

Server deletion and local deletion are separate state machines.

- A server endpoint can hide/delete/anonymize hosted account data and trigger projection rebuilds.
- It cannot guarantee destruction of data on offline user devices.
- Local deletion is performed by each authorized device and produces a local receipt/state.
- “Delete everything” is a coordinated UX workflow, not one server command claiming remote local erasure.
- Restored backups must reapply deletion tombstones before serving production traffic.

### Per-device deletion

`packages/schemas/local-deletion-v1.schema.json` is the machine-readable form of this section; `packages/schemas/planning-schema.sql` holds `local_deletion_commands` and `local_deletion_receipts`, and the `local-deletion-command` machine owns the lifecycle. Nothing here is implemented: no command has been issued, no daemon has executed one, and no receipt has been signed.

**How it composes with the hosted erasure.** The two mechanisms answer different questions and are never merged into one result. The hosted side destroys the erasure-domain key and appends a signed record under ADR-022 and `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md`; that record proves which key was destroyed and says nothing whatever about any device. The local side deletes device-held stores and produces a device-signed receipt that says nothing whatever about the server. They share a deletion job and nothing else.

**The hosted side does not wait for devices.** `server-deletion` reaches `complete` from `awaiting-local-receipt` deliberately. A device that is offline, wiped, sold or never opened again is the normal case, and blocking an Article 17 erasure on one would make the right unexercisable. What the participant sees instead is every device reported separately, which is what D-076 requires, and a completed hosted erasure alongside devices that are still `pending`, `unreachable` or `waived` is a correct display and not an inconsistency.

**What a receipt attests.** That the daemon holding the named device key ran the delete operations the command named, over the stores that daemon controls, at the stated time, and counted the rows and keystore entries it reports. The signature is COSE_Sign1 with Ed25519 under D-190, D-191 and D-192 — the same profile as the evidence protocol and the erasure log.

**What it does not attest, and no surface may imply.** That the bytes are unrecoverable. That no operating-system backup, filesystem snapshot or cloud-synced home directory holds a copy. That the participant made no copy. That the physical residue block remapping leaves on flash storage has been reached. A user-space process observes none of those, so no field reports on them; `residual_risk` names what could not be ruled out, and its strongest value is `none-observed`, which says observed and not none. A `partial` receipt is a first-class outcome, and a command whose device answered `partial` or `refused` reaches `failed` rather than rounding an incomplete deletion up to a success.

**What it means when a receipt never arrives.** The command expires, and the product may say exactly one thing: the command expired unanswered. It may not say the device was cleared and it may not say it was not. It observed nothing, and reporting an absence of evidence as either outcome is the claim D-076 exists to forbid. A command that expired without ever being acknowledged is reported `unreachable` rather than `expired`, because a device that never heard the request and a device that heard it and then stopped are different facts about the participant's own hardware.

**Waiver.** A participant may proceed without a device rather than wait. The waiver is recorded, is reported as `waived` rather than as a success, and is not final: a waived device that later returns and completes reports what it actually did.

**What this does not close.** SR-013 in `conformance/p1140f/semantic-findings-v1.json` covers export, deletion, retention and backup tombstones. This section supplies the per-device half of its deletion part; `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` supplies the hosted and backup half, and the export, retention and legal-hold parts are untouched. SR-009 covers duplicated authority, and reusing the device store's receipt vocabulary instead of inventing a second one advances it in one place. Both findings remain open, and this change records no closure evidence and no review verdict against either.

## Export privacy

Exports require:

- typed scope;
- recent authentication for sensitive scope;
- coherent snapshot time;
- manifest and checksums;
- encryption at rest and in transit;
- short-lived revocable download grant;
- download and purge audit;
- exclusion of other users' private data and internal abuse thresholds.

## Local detector privacy

The SLM is post-launch research.

Structured-feature mode uses only approved local features. A raw-local-record mode requires separate approval and must run in a stricter sandbox with:

- no network, shell, tools, plugins or MCP;
- read-only explicit source paths;
- no signing keys, sync credentials or provider credentials;
- bounded input, memory, CPU and wall time;
- no prose output;
- fixed anomaly enums and confidence buckets;
- post-detector egress scanning.

Raw detector input and intermediate state never leave the device.

## Third-party assets and avatars

- Public pages must not embed arbitrary external avatar URLs that enable viewer tracking.
- Provider avatar import is fetched server-side or client-side through an approved controlled path, re-encoded, stripped of metadata and served under an internal asset ID.
- Fetchers require SSRF defenses, size/type limits and destination allowlists.
- User-uploaded assets require malware/content validation, re-encoding and lifecycle deletion.

## Incident rule

Any suspected forbidden-content transmission is treated as highest severity until scoped.

Immediate actions include:

1. stop affected egress path;
2. preserve privacy-safe evidence;
3. rotate or revoke affected release/configuration if needed;
4. identify destinations and retention;
5. purge where possible;
6. notify affected users and authorities when required;
7. add a regression canary and contract repair.

## Required validation

Before launch:

- canary fixtures at adapter, IPC, local store, detector, claim, HTTP, telemetry, notification, moderation and export boundaries;
- packet capture proving destination and payload allowlists;
- schema tests rejecting arbitrary text/maps/bytes;
- log and crash-report scanning;
- reviewer/admin authorization tests;
- block/privacy-change notification and presence invalidation tests;
- server/local deletion separation tests;
- backup tombstone restore drill;
- independent privacy review.

Documentation and a passing parser do not constitute privacy evidence.
