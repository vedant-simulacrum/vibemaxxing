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

Ten surfaces evaluate it. Nine recheck at read or delivery time; the export package is the single snapshot-time exception, and it is one because the subject and the viewer are the same person and no third party's authorization can change under it.

Each surface partitions all nine inputs into the ones it evaluates and the ones it omits with a stated reason. That is not bookkeeping: an input a surface does not mention and an input nobody considered produce the same file, and adding a tenth input now forces every surface to answer for it.

### Which boundary the rule applies to

Naming the rule was half of it. The other half is knowing where it applies, and until PF-033 the two lists were written independently and never resolved against each other. Three things were true at once and nothing could find any of them.

`board-member-list` was declared a surface. No operation in `packages/schemas/openapi-v1.yaml` lists board members, so it was a rule about a surface the API does not have. While it sat in the list, `listBlocks` — which returns a third party's account identifier on every row — had no surface at all, and `Relationship`, the shape that carries that identifier, was the one schema reachable from a success response that named another account and that `disclosure-projection-v1.json` classified nowhere.

And one `leaderboard-page` surface claimed nine read-time inputs on behalf of three operations, one of which is `getGlobalLeaderboard`. That operation carries `security: []` because AGENTS.md makes exactly one view universally public. An anonymous reader has no block row, no friendship and no membership, so four of the nine inputs had nothing to evaluate — and `directional-block`, the deny-hard one, resolves to admit. **A blocked participant reads the global board by logging out.** That is the same shape as the `getPublicProfile` defect PF-021 repaired, and the repair is not the same, because here the operation is public by decision rather than by oversight: the surface is split, `global-leaderboard-page` evaluates the four subject-only inputs it can, and the five it cannot are recorded with the reason. The alternative — hiding one participant's row from one reader on a public ranking — is itself a disclosure, because the gap is visible.

The boundary matrix is keyed on the operation identifiers of the API document and compared against them for equality, so an operation added later has no boundary and fails rather than escaping. Whether a response carries a third party is computed from the document in both directions: a boundary cannot declare itself out of a gate it needs, nor into one it does not.

### Every viewer-visible field carries its gate

`disclosure-projection-v1.json` owns which audience each field is written for. This rule owns which current authorization revision gates it. They are two files because they answer two questions, and the join between them is derived rather than written: the validator recomputes one row for every `(surface, schema, field)` that reaches an account other than the one it is about, and asserts the matrix in `projection-authorization-v1.json` matches row for row. A field added to a projected shape appears there or the check fails.

The key is the surface and not the schema alone. `RankEntry` is rendered by two surfaces with two different gates, and a matrix that unioned them would hide that one of the two evaluates four inputs rather than nine.

### The three things a decision outlives

The rule forbids caching a decision. Three records pin one anyway, and each says what destroys it. A leaderboard cursor pins the authorization revision it was issued under, and a presentation whose revision has moved is refused rather than served. An export download grant pins the authorization that issued it, and `revoked_at` withdraws the capability while the row survives for the audit trail. A shared HTTP cache pins the whole response — and the API declared no cache directive at all, so a proxy, a CDN or a browser back-forward cache was free to store `GET /profiles/{handle}` and hand it to a second viewer. `x-response-cache-policy` now declares every operation, `no-store` by construction, `public-shared` only for the operations `x-public-operations` already calls universally public or reference data. The split is derived from that reason rather than listed twice.

A fourth record is named because leaving it out would be the same mistake in reverse. A sealed ranking generation is never invalidated by an authorization change. It holds figures and positions and carries no handle, no viewer and no authorization state, so a block changes what renders from it and not what it contains. This is the line the whole finding turns on: an immutable historical fact and a current authorization are two records precisely so that changing the second never has to rewrite the first.

`conformance/planning/authorization-invalidation-vectors-v1.json` states one case per trigger and records what each retains as well as what it destroys, because a corpus in which everything invalidates everything proves nothing. A block reaches seven surfaces and not the global board, the viewer's own block list or the export. A board removal reaches two. Only a deletion request reaches the export download grant, because account lifecycle is the one input every surface evaluates.

This names the rule and makes it total over the API. No surface in this repository evaluates it, so SR-015 is advanced by what a document can carry and closed by what code does.

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

### The hosted deletion plan

One row per data domain per job, in `deletion_effects`, keyed on the seven keys `docs/privacy/DATA_MAP.md` declares. The plan is immutable in the sense that matters: a domain appears exactly once per job, so the set of questions a job answers is fixed when it is created and cannot be narrowed later by a worker that skipped one.

Each row carries what the erasure did to that domain, in the disposition registry's own vocabulary — `delete`, `key-destroy-retain`, `retain-unlinked`, `retain-pseudonymous` — rather than in a second spelling of it. That is what lets a participant be told two true things at once: their accepted claims were deleted, and their moderation record was retained with its subject gone.

There is no state meaning that a domain was not looked at. A domain that held nothing for this account reaches `complete` with an affected row count of zero, which is a statement about the account; an enum member for silence would have let every plan be complete by declining to answer, which is the reason `packages/schemas/consolidation-plan-v1.schema.json` refuses the same value in the same position.

**During execution the account is frozen.** `accounts.state` is `deletion-pending` from the request until the job leaves the machine, and `packages/schemas/projection-authorization-v1.json` already makes `deletion-pending` deny every surface. A cancellation inside the cooling-off window returns the account to `active`; a restriction that was in force before the request is re-applied from the append-only moderation effects, because one state column cannot hold "pending deletion" and "restricted" at once.

**A held deletion is not a silent one.** A legal hold stops the job before execution and is published to the participant as the fact that the request is held. What the hold is stays server-side.

Nothing here is implemented. No plan has been built, no domain has been erased, and no hold has been placed.

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

`packages/schemas/export-manifest-v1.schema.json` is the manifest and `packages/schemas/planning-schema.sql` holds `exports`, `export_artifacts` and `export_download_grants`. Four of the requirements above were words until PF-028: the row had no scope, no snapshot time, no manifest digest and no encryption reference, and the grant row had no expiry, no revocation and no reference to the export it opened.

**The package answers for every domain, included or not.** One entry per key in `docs/privacy/DATA_MAP.md`, always all seven. A file list cannot record an absence, so a package that omitted a domain was indistinguishable from one that held nothing for it and from one whose producer forgot it existed. Every exclusion now names a reason from a closed set: `derived-not-portable` for the Article 20 split D-108 records, `rights-of-others` for the Article 20(4) limit, and `out-of-scope-for-request` for the participant's own typed scope — which a request for everything may not use. A domain excluded as derived is still supplied under Article 15, and the manifest says so rather than implying the data does not exist.

**One snapshot instant for the whole package.** Two domains read at two instants produce a package whose claims and whose social edges disagree about what existed, and no reader can tell which half is current. This is the single snapshot-time exception recorded above, and it holds only because the subject and the viewer are the same person.

**The grant is short-lived and revocable, as values.** `expires_at` is `not null`, so an eternal grant is one the table refuses rather than one an issuing worker forgot to bound; `revokeExportDownloadGrant` is the route that ends one, and revocation and expiry are separate timestamps because they are different endings. Revoking a grant does not destroy the package: closing a link is not the same act as discarding an export the participant may still want.

**The manifest carries no key material.** `encryption.key_reference` is an identifier that resolves inside the key store. A manifest travels beside the ciphertext it describes, and a manifest holding the key would make the encryption a label.

No export has been produced, no manifest has been written and no grant has been issued.

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
