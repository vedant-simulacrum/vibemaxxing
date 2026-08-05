# Social, Integrity, and UX Contract

Status: normative planning contract; persistence and state-machine details require P-1140D repair.
Version: 2
Updated: 2026-07-23

## Accounts and profiles

Handles are 3–30 Unicode letters, numbers, underscores or hyphens after the accepted normalization policy. Reserved, deceptive, impersonating or confusable handles are rejected. Rename, redirect, non-reuse, deletion privacy and policy migration must use an append-only assignment/reservation ledger.

Profiles expose only user-approved fields. Default public fields are handle, controlled avatar asset, Token Burn, rank, server-appraised evidence state and selected board memberships. Estimated Cash Burn, agent/model mix, history, friends and presence have independent visibility controls.

Provider subjects, duplicate-identity signals, device/recovery lineage, raw source records and moderation evidence are private integrity data and never public profile fields.

## Ranked participation

VibeMaxxing strongly enforces one active ranked identity per detected/resolved person without claiming mathematical proof of unique humanity.

Unranked users may browse, use private analytics and participate in non-ranking social surfaces allowed by board policy. Only an eligible ranked identity can appear in leaderboards, affect competitive totals or trigger ranked overtakes/movement.

High-impact duplicate-identity outcomes require corroborating signals, human review and appeal. Shared IP, household, workplace, school, network or hardware is never sufficient alone.

## Friendship and blocking

Friend request states are `pending`, `accepted`, `declined`, `cancelled`, `expired` and `blocked`.

The persistence model must guarantee one canonical relationship per unordered account pair and prevent reverse-edge duplicates or crossed-request ambiguity.

Blocking immediately:

- removes or disables friendship/rival relationships;
- hides presence and notifications in both directions;
- prevents requests and invitations;
- suppresses discovery where feasible;
- does not automatically restore relationships after unblock.

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

Notifications use typed schemas rather than unrestricted JSON. Each type defines:

- allowed privacy-safe fields;
- stable source-event identity;
- deduplication/grouping;
- hysteresis;
- quiet-hour and channel behavior;
- block/revocation interaction;
- correction/retraction semantics;
- retention and deletion.

In-app is the initial required channel. Email or push requires explicit preference. Security and recovery notices cannot be fully muted.

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