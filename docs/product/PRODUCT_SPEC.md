# VibeMaxxing Product Specification

Updated: 2026-07-19
Status: planning contract

## Product definition

VibeMaxxing is a privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It measures authentic agent usage without judging usefulness or productivity.

## Public-launch scope

Public launch targets the complete initial product. Internal delivery may be staged, but launch includes:

- global, friends, private-board, organization, hacker-house, community, and country leaderboards;
- daily, weekly, monthly, seasonal, yearly, and lifetime periods;
- profiles, friendships, blocks, rivals, overtakes, rank movement, streaks, presence, notifications, boards, organizations, communities, moderation, appeals, export, and deletion;
- background daemon, CLI installation/control, macOS menu-bar, Windows/Linux tray, local privacy/audit controls, and hosted web dashboard;
- broad agent compatibility through explicit support tiers.

## Metrics

### Token Burn

The default ranking metric is accepted live Token Burn. A normative accounting specification must define input, output, cache read/write, reasoning, tool/context, multimodal, retries, failures, streaming, compaction, subagents, local models, unknown categories, and double-count prevention.

Genuine but intentionally wasteful use counts. Fabricated, copied, replayed, duplicated, backdated, or source-misrepresented activity does not.

### Estimated Cash Burn

Estimated Cash Burn is API-equivalent interpretation of immutable usage facts. It is never actual spend. Pricing datasets are versioned with provenance and effective dates. Subscription, credit, enterprise, regional, batch, cache, local-compute, unknown-price, correction, and model-alias behavior require explicit policy. Historical estimates may not silently change.

## Evidence states

- **Standard** — live qualifying capture with ordinary supported controls.
- **Hardened** — stronger source, process, device, continuity, and available attestation evidence.
- **Imported** — retrospective private analytics only.

Internal capture and environment strength remain separate. Weak evidence may not masquerade as strong evidence.

## Agent support

Support states are Hardened-certified, Competitive-certified, Community-certified, Generic live, Imported, and Unsupported. Public support claims are generated from a versioned exercised adapter registry.

## Accounts and identity

Users sign in through GitHub or X/Twitter OAuth. Accounts may link multiple providers. Optional passkeys or hardware credentials provide stronger protection for sensitive actions but are not mandatory.

Identity behavior must cover stable provider subjects, mutable handles, username allocation, rename, impersonation, provider compromise/loss/suspension, account linking, merge conflicts, sessions, recovery, restrictions, export, and deletion.

## Leaderboards

Every leaderboard defines scope, period, eligibility, evidence policy, privacy, tie behavior, pagination, current-user rank, late/offline claims, corrections, quarantines, deletion, and season closure.

Private boards may configure visibility and eligible evidence/agents within global safety and privacy rules. Board rules may not redefine token accounting.

## Profiles

Profiles may expose Token Burn, Estimated Cash Burn, rank, movement, periods, agent/model mix, daily activity, presence, friends, boards, organization/community memberships, evidence state, and achievements introduced by the launch scope.

Users control visibility of Cash Burn, activity history, agent/model breakdown, presence, friends, country, and memberships. Privacy rules must prevent inference of projects, repositories, files, prompts, tools, or work content.

## Friends, blocks, and rivals

Friend requests require explicit lifecycle, limits, discoverability, blocking, removal, privacy, and abuse handling. Rivals may be manual or product-selected only under documented rules. Blocking overrides discovery, requests, presence, notifications, and private-board interaction as specified.

## Overtakes, rank movement, streaks, and seasons

Define tie-aware overtake events, hysteresis, duplicate suppression, movement comparison windows, late-event corrections, streak qualification, season start/end, archived standings, post-close appeals, and reset behavior.

## Presence

Presence states include active, idle, offline, and private. Presence exists only while qualifying live agent activity is genuinely active. It exposes no prompt, response, tool, path, file, project, repository, or transcript-derived detail.

The presence contract must define heartbeat, expiry, idle threshold, multi-device, multi-agent, sleep/resume, offline sync, private mode, false-active prevention, and restricted/quarantined behavior.

## Notifications

Notifications cover requests, acceptances, rivals, overtakes, movement, streaks, seasons, boards, organizations, moderation, appeals, device/security changes, and product operations. Define channels, grouping, rate limits, quiet hours, hysteresis, duplicate suppression, privacy, retention, and user controls.

## Boards, organizations, hacker houses, and communities

Define ownership, administrators, invitations, approval, public/private/unlisted visibility, membership, removal, transfer, eligibility, evidence requirements, score history, moderation, deletion, and audit. Organization verification must not require access to private code or prompts.

## Country boards

Country representation must be coarse, privacy-preserving, user-understandable, change-limited, and protected by minimum cohort thresholds. Research must define assertion source, travel/dual-country behavior, abuse, hiding, deletion, and whether government identity is ever necessary; it is not the default.

## Native local experience

The daemon owns lifecycle and supervision; collector owns transcript-private observation; sync owns network transport of safe claims; CLI owns installation/control/headless operation; menu-bar/tray owns local status and controls. Closing the shell must not silently stop collection. Local UX owns permissions, adapters, device state, privacy verification, outbound ledger, diagnostics, export, deletion, and updates.

## Hosted web experience

The hosted product owns leaderboards, profiles, social graph, boards, organizations, communities, countries, notifications, account settings, moderation, appeals, and server-side lifecycle controls. It never requires access to transcript content.

## Moderation and appeals

Anti-abuse is progressive, reason-coded, reviewable, and appealable. Define claim exclusion, evidence downgrade, session/account-score quarantine, temporary ranking restriction, device revocation, moderator actions, restoration, insider controls, notifications, retention, and appeal service levels. An SLM cannot permanently ban by itself.

## Export, deletion, and lifecycle

Users can stop collection, remove adapters, disconnect/revoke devices, inspect/export local and server-side safe data, delete local models/intelligence, delete outbound ledger, delete profile, delete claims/aggregates subject to legal policy, and delete the account. Define grace periods, backups, derived data, social references, leaderboard history, moderation records, and irreversible completion.

## Explicit non-goals

- Measuring productivity, code quality, usefulness, or commercial value.
- Uploading prompts, responses, transcripts, code, diffs, tools, paths, files, projects, repositories, embeddings, summaries, or personal insights.
- Asking for provider API keys merely to prove usage.
- Claiming provider authentication or mathematical cheat-proofing without evidence.
- Treating social login as proof of one-person uniqueness or activity authenticity.

## Launch gate

Public launch requires complete functional scope, major agent-family coverage, privacy/control traceability, adversarial integrity evidence, accessibility, performance, native packaging/update verification, production operations, moderation/appeals, legal/privacy readiness, and public open-source governance. A narrow vertical slice is an internal milestone, not the launch product.
