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

The same rule reaches boards, and until PF-025 it did not. `board-membership`
carried a terminal `blocked` state reached by a `block-cascade` from four states with
no transition out, and `board-invitation` carried `invalidated-by-block`. Both are
worse than the friendship case rather than milder: a block is an act between two
accounts, and what it destroyed was a membership and an invitation granted by a third
party — the board owner — who had no part in it and no way to undo it. Neither state
exists now. A pending invitation between a blocked pair is suppressed at read time and
expires on its own clock, and a membership is suppressed at read time and stays a
membership. A board can still refuse a person: that is `removed`, it is a board
admin's act under recent authentication, and it is reversible.

Every transition requires an initiator, authorization rule, idempotency behavior, timestamp, audit event and user-safe result.

## Rivals and overtakes

Rivals may be user-selected or suggested from comparable ranking neighborhoods. Suggestions never expose private profile or integrity data. Rival edges are private by default unless both users choose display.

An overtake occurs only when one account moves from score less than or equal to another account to strictly greater score within the same immutable `ranking_view_id` and compatible finalized snapshots.

Hysteresis and grouping suppress notification flip-flop. Corrections, moderation reversals and rebuilds may retract or replace prior overtake/movement notifications through explicit typed events.

## Boards, organizations and communities

Board visibility is public, unlisted, invite-only or private, and `boards.visibility`
is where it is stored. It was stored nowhere until PF-025 while `AGENTS.md` makes it
load-bearing: only the global leaderboard view is universally public by default, so
an unlisted or private board view requires current viewer authorization and the rule
needs a value to read.

Roles are owner, admin, member and viewer. `moderator` appeared in this list and
nowhere else — no membership state, no transition, no column and no authorization
row ever carried it — so it was a word rather than a role, and it is removed. Board
moderation is the `moderation-case` aggregate, which is not a board membership role.

Board kinds are private, organization, hacker-house and community. The API's `kind`
enum offered three of those four until PF-025, omitting the one the route map
publishes a public surface for, so a stored hacker-house board had no representation
on the wire.

One canonical board aggregate owns:

- board identity and owner authority;
- membership and role state;
- invitations;
- policy versions;
- transfer and deletion state.

**Exactly one owner is two rules and one of them is not an index.**
`board_one_active_owner` is a partial unique index on `state = 'active-owner'`: it
refuses a second owner and is silent about a board that has none. The other half is
that a board and its owner membership are one write — planned as `board-create-owner`
in `conformance/p1140e/sql-race-plans-v1.json` — so no board is ever readable without
an owner, and a later update cannot be the thing that creates one.

**An invitation grants membership or viewership and can grant nothing else.**
`board_invites.role` admits `member` and `viewer`. The wire enum admitted `owner` and
`admin` until PF-025, against a `board_invites` table that held neither a role column
nor an invitee: the rule that an invitation cannot grant a privileged role was a
refusal comparing fields no record held. Admin promotion is a separate transition
requiring recent authentication, and ownership moves only through the paired transfer.

The last owner cannot leave without transfer or deletion. Ownership transfer requires
recent strong authentication and an auditable transition; it demotes the outgoing
owner to admin and promotes the successor inside one transaction, and the demotion is
a transition the machine declares rather than a step the plan assumed.

Board policies are versioned and prospective. They may define eligible sources, minimum evidence profile, metric, periods, membership and historical behavior. Rebuilds require explicit authorization and visible member communication.

Organizations, hacker houses and communities reuse board primitives plus optional domain or administrator approval. They do not receive private identity-integrity signals or legal identity data.

## Country feature

Country leaderboards, country profile disclosure and country notifications are **post-launch**.

Launch routes, readiness gates and public marketing must not include countries. Future work requires a separate decision on semantics, season-frozen affiliation, switching, historical attribution, minimum-cohort privacy and moderation.

Schemas may reserve a clearly unused future hook only when it cannot affect launch behavior or imply implemented support.

## Presence

The lease states are `absent`, `active`, `idle`, `expired` and `revoked`, owned by the
`presence-lease` machine. What a viewer is shown is the coarser `online`, `idle`,
`offline`; `private` is a visibility policy and not a state, which is why it does not
appear in either list.

Active presence must derive from qualifying collector-observed activity that has been safely signed/authorized and accepted under the presence policy. A browser or ordinary web session cannot fabricate indefinite activity.

**The renewal request carries a pulse and never a state.** That sentence above had
nothing behind it until PF-026: `renewPresence` accepted a session cookie and a body
whose only field was `availability` over `online`, `idle` and `offline`, declared as a
coarsening of the machine — a projection running inbound. A browser could therefore
PUT `online` on a repeating timer, which is precisely the fabrication the paragraph
forbids, and presence would have been a measure of who had a tab open. The request now
requires a device, the lease generation it was minted under and a qualifying boolean,
every alternative on the route requires device proof, and the state is derived.

**The thresholds.** A qualifying pulse every `presence_heartbeat_seconds`; `active`
becomes `idle` after `presence_idle_after_seconds`; the lease expires after
`presence_offline_after_seconds`. The values are 30, 90 and 300 and live in
`packages/schemas/policy-defaults-v1.json`. The last two keys used to be named the
other way round — `presence_lease_expiry_seconds` held 90 and meant idle,
`presence_idle_after_seconds` held 300 and meant offline — so reading the registry
straight gave a lease that expired at 90 seconds and an idle threshold at 300, which
is an `idle` state nothing can ever reach. The superseded D-385 recorded the
misnaming, deferred the rename, and named its own reopen condition; D-618 is the
rename PF-026 performed.

**Multi-device aggregation is a stated fold, not an implementation detail.** An
account holds one lease per device and the projection answers once, and nothing said
how. The rule is precedence over lease states — `active`, `idle`, `expired`,
`revoked`, `absent` — projected onto the three audience values, so the answer is the
projection of the most-present lease the account holds and does not depend on which
device was read first. `conformance/social/presence-merge-vectors.json` states it with
six cases and the validator evaluates each under both orderings. A revoked device
cannot raise the answer: revocation is a security act, and a revoked device
contributing presence would be that act undone by a projection.

**Visibility is one policy per account.** It lives on `profiles.presence_visibility`.
It was a column on `presence_leases`, one value per device, against a projection that
produces one answer per account — so going private on a laptop while a desktop stayed
authorized published the participant anyway, and nothing said which value the merge
took. A viewer the policy excludes reads `offline`, which is the value an inactive
participant reads, so the suppression is not itself a signal.

Presence processing must define:

- device/account lease binding;
- qualifying event freshness;
- renewal and expiry;
- multi-device aggregation;
- audience and board visibility precedence;
- block and privacy revocation;
- no project, repository, filename, prompt, code or detailed source disclosure.

Closing the menu-bar/tray shell does not end collection; disabling presence does not disable accounting.

Presence is a last-active answer and an authorized viewer can infer working hours by
watching it. ADR-019 accepts that on the stated basis that no history is stored:
`presence_events` carries `no-retention` and rows are discarded when their generation
closes. Nothing above reduces that exposure and none of it should be read as doing so.

## Notifications

The launch type set is closed and has exactly eight members: `friend_request`,
`board_invitation`, `rank_overtake`, `moderation`, `appeal`, `security`,
`compatibility` and `release`. This paragraph used to list eleven English phrases
including rival suggestion, rank movement and quarantine, none of which the enum can
carry, so the contract promised notifications the model could not express. Where the
phrases survive, they map: a friend acceptance is a `friend_request` event on a later
revision of the same aggregate, quarantine and device events are `moderation` and
`security`, and board administration is `board_invitation`. Rank movement without an
overtake and rival suggestion are not launch types; adding either means adding an
enum member in four artifacts, not a sentence here.

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

The five category flags decide whether an inbox item is created at all. Quiet hours and the two opt-in timestamps decide only whether a best-effort transport carries a hint about an item that exists either way. The split is fixed rather than configurable: the inbox is the authority, so an inbox item withheld overnight is a lost notification and not a deferred one. With no transport shipping at launch, quiet hours therefore have no observable effect, which is stated here rather than shipped as a control that appears to do something.

**Which flag governs which type is declared, and until PF-027 it was not.** Four flags
faced eight event types and no artifact anywhere held the mapping, so
`suppression_cause = 'category-disabled'` named a category nothing defined, and
`compatibility` and `release` fell under no flag at all — a worker deciding whether to
create one had no preference to read and had to invent a rule. Worse, whether a
security notice could be muted depended on which rule it invented. The map is
`event_categories` in `packages/schemas/notification-delivery-v1.schema.json`:
`friend_request` and `board_invitation` are `social`, `rank_overtake` is `ranking`,
`moderation` and `appeal` are `moderation`, `compatibility` and `release` are
`product`, and `security` is `security`. `product_enabled` is the fifth flag the two
uncovered types needed. Every category has a column on `notification_preferences` and
a property on the preferences record, and the validator requires all three to agree.

**A participant can now set them.** `notification_preferences` was a table with no
operation of any kind — described in the schema, persisted in the DDL, reachable by
nobody — so the flags that decide whether an item is created were settable only by a
migration. `getNotificationPreferences` and `updateNotificationPreferences` are the
two routes. The update body carries no `security_enabled`, no `quiet_hours_scope` and
neither opt-in timestamp: the first two are constants and the timestamps record a
consent granted through transport enrollment, and a field a client may send that the
server must refuse is a control that appears to work.

Security and recovery notices cannot be muted. `security_enabled` is constrained true in the schema and in the DDL, `security` maps to that flag rather than to a mutable one, and a `security` event has no suppression path at all.

### Retraction

Corrections, moderation reversals and rebuilds retract prior notifications, and `retracted` is API-visible.

A retracted item stays in the inbox. Deleting it would leave a participant who already read the original holding a fact the product has withdrawn, with nothing to tell them it withdrew it. Each retraction carries one of three registered reason codes and, for a rebuild, the superseding generation. `notifications.retraction_reason_code` admitted any string until PF-027, so "registered" was a convention; the column now carries the same closed vocabulary as the schema enum and the validator compares the two sets.

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