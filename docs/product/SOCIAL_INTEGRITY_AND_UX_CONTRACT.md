# Social, Integrity, and UX Contract

Status: normative planning contract
Version: 1

## Accounts and profiles

Handles are 3-30 Unicode letters, numbers, underscores, or hyphens after normalization; reserved, deceptive, impersonating, or confusable handles are rejected. Rename cooldown is 30 days and old handles redirect for 90 days without exposing deleted identities. Provider usernames are not automatically claimed as VibeMaxxing handles.

Profiles expose only user-approved fields. Default public fields: handle, avatar, Token Burn, rank, evidence state, and selected board memberships. Cash Burn, agent/model mix, history, country, friends, and presence each have independent visibility controls.

## Friendship and blocking

Friend request states: `pending`, `accepted`, `declined`, `cancelled`, `expired`, `blocked`. Requests expire after 30 days. Per-account and per-target limits prevent spam.

Blocking immediately removes friendship/rival edges, hides presence and notifications in both directions, prevents requests and invitations, and suppresses search/discovery where feasible. Unblocking does not restore previous relationships.

## Rivals and overtakes

Rivals may be user-selected or suggested from comparable leaderboard neighborhoods. Suggestions never expose private profile data. Rival edges are private by default unless both users choose display.

An overtake event occurs only when a user moves from score <= another user's score to strictly greater within the same finalized scope/period/filter. Hysteresis suppresses repeated flip-flop notifications: at most one pairwise overtake notification per six hours unless the lead changes by a configurable material threshold.

## Boards and organizations

Board visibility: public, unlisted, invite-only, or private. Roles: owner, admin, moderator, member, viewer. Owners can transfer ownership only after recent authentication. The last owner cannot leave without transfer or deletion.

Board policy freezes: eligible agents, evidence tiers, metric, period set, membership rules, country/community scope, and historical behavior. Policy changes are versioned and apply prospectively unless a rebuild is explicitly approved and shown to members.

Organizations, hacker houses, and communities use the same board primitives plus optional verified-domain or administrator approval. No government ID is required by default.

## Country boards

Country is a user assertion with optional stronger evidence and a 90-day change cooldown. Public boards require a minimum cohort threshold to prevent singling out users. Country is independently hideable. IP geolocation may be a fraud signal but never silently defines public country identity.

## Presence

States: active, idle, offline, private. Active requires a qualifying live session and renewable lease. Idle begins after no qualifying model event for five minutes; offline after lease expiry. Multiple devices merge to the strongest non-private state while preserving no project details. Users may disable presence globally or per board.

## Notifications

Types include friend request, acceptance, rival suggestion, overtake, rank movement, board invite, board administration, device/security event, quarantine, appeal, compatibility change, and release/security notice.

Channels: in-app initially; email/push only with explicit preference. Notifications group by type/scope, obey quiet hours, expose no private agent details, and support per-type mute. Security and account-recovery notices cannot be fully muted.

## Moderation and integrity policy

Deterministic outcomes: accept, idempotent accept, Standard downgrade, Hardened downgrade, claim exclusion, session quarantine, score quarantine, stronger-evidence requirement, temporary ranking restriction, device revocation, account suspension, restoration.

Every action has a stable reason code, evidence references, policy version, actor, timestamp, expiry/review date, user-safe explanation, and appeal eligibility. Automated models cannot permanently ban or alter token totals independently.

Appeal states: `submitted`, `needs_information`, `under_review`, `upheld`, `partially_upheld`, `reversed`, `expired`. High-impact decisions require human review. Moderator actions are append-only audited; privileged access uses least privilege, recent strong authentication, dual control for irreversible actions, and periodic review.

## Detector architecture

Priority order: deterministic validation, source conformance, replay/clone controls, transparent rules, robust statistics, graph/cohort analysis, classical anomaly detection, optional SLM, human review.

The SLM receives bounded privacy-safe structural features by default. No network, shell, tools, plugins, MCP, or autonomous loop. Output is a schema of risk band, reason codes, calibrated confidence, recommended action, model/runtime/policy versions. Acceptance requires measured lift over simpler methods within false-quarantine and resource budgets.

## Anti-cheat calibration

Before launch define budgets by evidence tier and attack class. Initial planning targets:

- deterministic replay/duplicate false accept: zero in conformance campaigns;
- invalid signature/canonical claim false accept: zero;
- account-level false quarantine: <0.1% of legitimate active accounts per month in prelaunch simulation;
- appeal overturn attributable to detector error: <5% for high-impact cases;
- automated quarantine notification latency: <5 minutes;
- ordinary appeal first human review target: 72 hours.

These are launch gates subject to measured revision, not hidden promises.

## Route map

Public: landing, global leaderboard, period/scope/filter views, public profile, public boards, compatibility, downloads, protocol/privacy, open-source/security.

Authenticated: home leaderboard, friends, rivals, notifications, personal analytics, devices, adapters, privacy audit, account identities, settings, exports, deletion, board creation/administration, organizations/communities/countries, appeals.

Local shell/dashboard: daemon health, current activity, adapter status, evidence tier, outbound claim inspection, sync queue, permissions, privacy controls, update/rollback, diagnostics, export/delete/uninstall.

## UI state contract

Every page/component defines loading, empty, partial, stale, offline, error, rate-limited, unauthorized, private, blocked, restricted, quarantined, deleted, unsupported-agent, incompatible-version, and maintenance states. No generic blank screen or raw server error.

Evidence state and uncertainty are visible at the point of score interpretation. Estimated Cash Burn always includes `Estimated` and pricing-version access. Imported data is visually distinct and absent from active ranking.

## Accessibility and performance

WCAG 2.2 AA target; complete keyboard operation; semantic landmarks/tables; focus management; screen-reader announcements for live rank changes; reduced motion; non-color status cues; 200% zoom; responsive recomposition.

Web targets: LCP <=2.5s p75, INP <=200ms p75, CLS <=0.1; leaderboard virtualizes large rows without breaking accessibility. Native shell idle memory and CPU follow the native runtime contract.

## Privacy UX

Onboarding shows exact data classes that stay local and cross the network. Users can inspect serialized safe claim fields, pause collection/sync independently, hide social surfaces, revoke devices, remove adapters, export data, delete local-only analytics, delete server data, or delete everything.

## Required tests

State-machine/property tests for friendship, blocks, boards, roles, ownership, presence, overtakes, notifications, moderation, and appeals; abuse simulations; Sybil/collusion campaigns; accessibility automation/manual audits; browser matrix; responsive/visual regression; usability tests for evidence labels, privacy boundary, OAuth/device enrollment, quarantine, export, and deletion.
