# Social, Integrity, and UX Contract

Status: normative planning contract; persistence and state-machine details require P-1140D repair.
Version: 2
Updated: 2026-07-23

## Accounts and profiles

Handles are 3–30 Unicode letters, numbers, underscores or hyphens after the accepted normalization policy. Reserved, deceptive, impersonating or confusable handles are rejected. Rename, redirect, non-reuse, deletion privacy and policy migration must use an append-only assignment/reservation ledger.

Profiles expose only user-approved fields. Default public fields are handle, controlled avatar asset, Credited Token Burn, rank, server-appraised evidence state and selected board memberships. Raw Token Burn and the confidence weight are not public fields under D-144 and D-217; they appear on the participant's own surface and on surfaces they authorize. Estimated Cash Burn, agent/model mix, history, friends and presence have independent visibility controls.

Provider subjects, duplicate-identity signals, device/recovery lineage, raw source records and moderation evidence are private integrity data and never public profile fields.

## Ranked participation

VibeMaxxing strongly enforces one active ranked identity per detected/resolved person without claiming mathematical proof of unique humanity.

Unranked users may browse, use private analytics and participate in non-ranking social surfaces allowed by board policy. Only an eligible ranked identity can appear in leaderboards, affect competitive totals or trigger ranked overtakes/movement.

High-impact duplicate-identity outcomes require corroborating signals, human review and appeal. Shared IP, household, workplace, school, network or hardware is never sufficient alone.

## Friendship and blocking

Friend request states are `pending`, `accepted`, `declined`, `cancelled` and
`expired`. There is no blocked state, and this is load-bearing rather than tidy.

The persistence model must guarantee one canonical relationship per unordered account
pair and prevent reverse-edge duplicates or crossed-request ambiguity.

A block is directional and independent of friendship, which `AGENTS.md` states as a
binding rule. Friendship is keyed on an unordered pair and is therefore symmetric, so
a directional action cannot mutate it without deciding whose intent wins. This
document previously said blocking "removes or disables friendship/rival
relationships" and "does not automatically restore relationships after unblock",
which meant one person blocking permanently destroyed a shared aggregate: the other
party lost a relationship through an action they could not see, take or reverse, and
`blocked` was a terminal state with no transition out, so unblocking could not undo
it. That is repaired under D-585.

Blocking changes no relationship row. Every effect is evaluated at read time against
the block, which `packages/schemas/projection-authorization-v1.json` already declares
as `directional-block`, a deny-hard input evaluated in both directions. While a block
exists it:

- hides presence, profile and notifications in both directions;
- prevents new requests and invitations;
- suppresses discovery where feasible;
- suppresses the relationship from every live surface without deleting it.

Removing the block restores visibility, because nothing was destroyed to begin with.
A participant who wants the relationship gone removes the friendship, which is a
separate and deliberate act.

Every transition requires an initiator, authorization rule, idempotency behavior, timestamp, audit event and user-safe result.

## Rivals and overtakes

Rivals may be user-selected or suggested from comparable ranking neighborhoods. Suggestions never expose private profile or integrity data. Rival edges are private by default unless both users choose display.

An overtake occurs only when one account moves from score less than or equal to another account to strictly greater score within the same immutable `ranking_view_id` and compatible finalized snapshots.

Hysteresis and grouping suppress notification flip-flop. Corrections, moderation reversals and rebuilds may retract or replace prior overtake/movement notifications through explicit typed events.

## Boards, organizations and communities

Board visibility is public, unlisted, invite-only or private. Roles are owner, admin, moderator, member and viewer.

One canonical board aggregate owns:

- board identity and owner authority;
- membership and role state;
- invitations;
- policy versions;
- transfer and deletion state.

The last owner cannot leave without transfer or deletion. Ownership transfer requires recent strong authentication and an auditable transition.

Board policies are versioned and prospective. They may define eligible sources, minimum evidence profile, metric, periods, membership and historical behavior. Rebuilds require explicit authorization and visible member communication.

Organizations, hacker houses and communities reuse board primitives plus optional domain or administrator approval. They do not receive private identity-integrity signals or legal identity data.

## Country feature

Country leaderboards, country profile disclosure and country notifications are **post-launch**.

Launch routes, readiness gates and public marketing must not include countries. Future work requires a separate decision on semantics, season-frozen affiliation, switching, historical attribution, minimum-cohort privacy and moderation.

Schemas may reserve a clearly unused future hook only when it cannot affect launch behavior or imply implemented support.

## Presence

Presence states are active, idle, offline and private.

Active presence must derive from qualifying collector-observed activity that has been safely signed/authorized and accepted under the presence policy. A browser or ordinary web session cannot fabricate indefinite activity.

Presence processing must define:

- device/account lease binding;
- qualifying event freshness;
- renewal and expiry;
- multi-device aggregation;
- audience and board visibility precedence;
- block and privacy revocation;
- no project, repository, filename, prompt, code or detailed source disclosure.

Closing the menu-bar/tray shell does not end collection; disabling presence does not disable accounting.

## Notifications

Launch notification types include friend request/acceptance, rival suggestion, overtake, rank movement, board invitation/administration, device/security event, quarantine, appeal, compatibility change and release/security notice.

Notifications use typed schemas rather than unrestricted JSON. `packages/schemas/notification-delivery-v1.schema.json` is the machine-readable form of this section, `packages/schemas/planning-schema.sql` is the persistence authority, and the `notification-delivery` machine in `packages/schemas/state-machine-registry-v1.json` owns the lifecycle. Nothing below is implemented: no aggregate appends an event, no worker groups one, and no surface renders an inbox.

### What generates a source event

A source event is appended by the aggregate that changed, in the transaction that changed it, and by nothing else. Friendship and board transitions append their own; moderation and appeal decisions append theirs; a sealed ranking generation appends `rank_overtake` through the movement events that cite two generations; device, security, compatibility and release events append theirs. No worker decides that something is interesting, which is what keeps the type set closed and what makes every event traceable to a revision of a named aggregate.

An event names references and carries no rendered sentence. There is no title, body, summary or preview anywhere in the model, and a validator refuses those names. A sentence written at append time freezes a handle, a figure and an authorization decision at the moment of the change, so a later rename is wrong, a later block leaks, and a retraction arrives after the recipient has already read the claim it withdraws. The surface renders from current state at read time, or renders nothing.

### Deduplication, grouping and hysteresis

These are three different mechanisms and the contract keeps them apart.

**Deduplication is exact and is a database constraint.** `notification_events` is unique on recipient, event type, source aggregate and source revision — the same pair `outbox_events` carries — so an at-least-once outbox is exactly-once for the recipient and no worker has to get that right.

**Grouping is a digest, not a decision.** `grouping_digest` is SHA-256 over the deterministic CBOR encoding of the recipient, the event type, the scope and the group window start, under D-191. Two workers presented with the same facts collapse the same events without coordinating, and a group is reproducible afterwards. A group is one inbox item carrying `group_count`, never n items, so it cannot be unwound into the flood it collapsed.

**Hysteresis applies to `rank_overtake` and to nothing else.** An overtake that does not clear `overtake_material_lead_tokens`, or that reverses inside `overtake_notification_hysteresis_hours`, is suppressed. Both numbers live in `packages/schemas/policy-defaults-v1.json` and are named rather than repeated.

`grouped`, `ready` and `suppressed` exist only between the dedup worker and the delivery worker, and `created` exists before either. All four are internal: a notification exists for its recipient exactly when it is in the inbox, so no client is ever shown a state from before that. A suppressed event records which of the five causes suppressed it, because a suppressed event and a lost event otherwise leave the same trace.

### The inbox projection

`notifications` is the recipient's inbox and is the notification authority. An item exists when a row is there. Every item carries the D-386 authorization revision it was generated under; the read path rechecks current authorization and refuses to render an item whose recorded revision is stale, so a block or a board removal between generation and read cannot be served out of the inbox. Retention is `notification_retention_days` and is enforced by dropping whole partitions.

### Delivery attempts and transports

`notification_deliveries` records one row per transport attempt. Only `server-inbox` rows exist at launch, because D-086 ships no push and no email; the transport half is specified now so that shipping one later adds rows rather than changing the model.

Three constraints carry the authority relation rather than leaving it to a worker. A `server-inbox` attempt is written in the same transaction as the inbox item and therefore has the single outcome `accepted`. A `push` or `email` attempt cannot exist without the opt-in timestamp that authorized it, copied from the preferences row at send time, so no such row is writable until a participant opts in. And the table has no read column: `accepted` means a provider took the message and `acknowledged` means a device confirmed receipt, and neither is ever a read.

### Preferences and quiet hours

The four category flags decide whether an inbox item is created at all. Quiet hours and the two opt-in timestamps decide only whether a best-effort transport carries a hint about an item that exists either way. The split is fixed rather than configurable: the inbox is the authority, so an inbox item withheld overnight is a lost notification and not a deferred one. With no transport shipping at launch, quiet hours therefore have no observable effect, which is stated here rather than shipped as a control that appears to do something.

Security and recovery notices cannot be muted. `security_enabled` is constrained true in the schema and in the DDL, and a `security` event has no suppression path at all.

### Retraction

Corrections, moderation reversals and rebuilds retract prior notifications, and `retracted` is API-visible.

A retracted item stays in the inbox. Deleting it would leave a participant who already read the original holding a fact the product has withdrawn, with nothing to tell them it withdrew it. Each retraction carries one of three registered reason codes and, for a rebuild, the superseding generation.

Rebuild retraction is deterministic rather than a judgement: when a rebuild supersedes a generation, every item whose source event cites that generation is retracted. It follows from ADR-020 making rebuild the mechanism for a trust-state change, and it is the notification half of the correction path ADR-022 describes for sealed generations.

### What inbox-only costs

In-app is the only channel at launch. D-086 records the decision and the tension it accepts: the owner's stated day-7 retention mechanism is rank movement and overtake notification, and an inbox-only product delivers that only once the participant opens the product — which is the behaviour the notification was supposed to cause. The model here does not work around it. No push or email path is half-built to soften it, and no retention claim is made for it; the decision's reopen condition is measured retention evidence that inbox-only is insufficient, and no such evidence exists in either direction.

### What this does not close

SR-015 in `conformance/p1140f/semantic-findings-v1.json` covers current authorization at every display and delivery boundary. Recording the authorization revision on every inbox item, and requiring the read path to recheck rather than trust it, is a precondition for that recheck and is not the recheck: nothing evaluates it, because no surface exists. SR-015 is advanced and remains open, and this change records no closure evidence and no review verdict against it.

## Moderation and integrity policy

Possible outcomes include accept, idempotent accept, profile downgrade, claim/session/score quarantine, claim exclusion, stronger-evidence requirement, temporary ranking restriction, device revocation, account suspension and restoration.

Every action binds:

- exact subject;
- exact claims, periods and ranking views;
- registered reason codes;
- policy/ruleset/detector versions;
- actor and timestamp;
- expiry/review date;
- user-safe explanation;
- appeal eligibility;
- deterministic ledger effect and reversal path.

Automated models cannot permanently ban, alter totals or award stronger evidence independently. High-impact decisions require human review. Moderator access is least-privilege, recently authenticated and audited.

Appeal state is owned by the `appeal` machine in `packages/schemas/state-machine-registry-v1.json` and is not restated here. The appellant-visible states are `submitted`, `needs-information`, `reviewing`, `approved`, `denied`, `withdrawn` and `expired`; `screening` is internal. The decision outcome — `upheld`, `partially-upheld`, `reversed` — is not a state and is published separately as `Appeal.decision`, present exactly when the appeal is `approved`.

A reversal creates an immutable reversal record, rebuilds affected ranking views and retracts or corrects dependent notifications.

## Detector architecture

Priority order:

1. deterministic schema/accounting/signature rules;
2. source conformance;
3. replay, duplicate, fork and clone controls;
4. transparent statistics and graph/cohort analysis;
5. classical anomaly detection;
6. optional model research;
7. human review.

Server anomaly detectors use only privacy-safe aggregate and integrity features, begin in shadow mode and require calibrated thresholds.

The SLM is post-launch research only. It is local, sandboxed, advisory and non-authoritative. It may not rewrite totals, award Hardened, permanently ban or become a launch requirement without a new accepted decision backed by a reproducible bakeoff.

## Anti-cheat calibration

Planning targets to validate with implementation evidence include:

- invalid signature/canonical claim false accept: zero in conformance campaigns;
- deterministic exact replay/duplicate false accept: zero;
- account-level false quarantine: below a predeclared prelaunch threshold measured on representative legitimate activity;
- high-impact detector-error appeal overturn rate: explicitly monitored;
- automated quarantine notification latency and human-review service targets: published before beta.

Targets are gates, not hidden guarantees. They may be revised only through recorded evidence and decision updates.

## Route map

Public launch routes:

- landing;
- global and period/filter leaderboard views;
- public profiles;
- public boards/organizations/communities/hacker houses;
- compatibility;
- downloads;
- protocol/privacy/open-source/security.

Authenticated routes:

- home leaderboard;
- friends and rivals;
- notifications;
- personal analytics;
- devices, adapters and privacy audit;
- account identities and sessions;
- settings, exports and deletion;
- board/community/organization administration;
- moderation and appeals.

Country routes are absent at launch.

Local shell/dashboard:

- daemon health;
- current safe activity state;
- adapter/support status;
- server-appraised evidence state;
- outbound claim inspection;
- sync queue;
- permissions and privacy controls;
- update/rollback;
- diagnostics, export, local deletion and uninstall.

## UI state contract

Every page/component defines loading, empty, partial, stale, offline, error, rate-limited, unauthorized, private, blocked, restricted, quarantined, deleted, unsupported-source, incompatible-version and maintenance states.

Evidence state and uncertainty are visible where scores are interpreted. Estimated Cash Burn always says `Estimated` and exposes pricing provenance. Imported data is visually distinct and absent from active ranking.

## Accessibility and performance

Target WCAG 2.2 AA, complete keyboard operation, semantic landmarks/tables, focus management, screen-reader announcements for meaningful live changes, reduced motion, non-color status cues and 200% zoom.

Web targets remain LCP <= 2.5 s p75, INP <= 200 ms p75 and CLS <= 0.1 for launch-supported environments, subject to implemented measurement. Virtualization must not break accessibility.

## Privacy UX

Onboarding and settings show exactly which data remains local and which fixed fields synchronize. Users can inspect serialized safe claims, pause collection and sync independently, hide social surfaces, revoke devices, remove adapters, export data, request server deletion and issue separate per-device local deletion.

The server must never claim it directly deleted data on an offline local device.

## Required implementation evidence

- state-machine/property tests for profiles, handles, friendships, blocks, rivals, boards, ownership, invitations, presence, overtakes, notifications, moderation, appeals, export and deletion;
- SQL uniqueness and race tests;
- authorization matrix;
- abuse/Sybil/collusion simulations including shared-network false positives;
- privacy canaries;
- accessibility automation and manual audits;
- browser/responsive/visual regression;
- usability tests for evidence labels, privacy boundary, OAuth/device enrollment, quarantine and appeal.