# VibeMaxxing Product Specification

Updated: 2026-08-06
Status: planning contract

## Product definition

VibeMaxxing is a privacy-preserving public leaderboard and Steam-like social competition layer for AI-agent activity. It measures authentic agent usage without judging usefulness or productivity.

## Public-launch scope

Public launch targets the complete initial product. Internal delivery may be staged, but launch includes:

- global, friends, private-board, organization, hacker-house, and community leaderboards; country leaderboards are post-launch;
- daily, weekly, monthly, seasonal, yearly, and lifetime periods;
- profiles, friendships, blocks, rivals, overtakes, rank movement, streaks, presence, notifications, boards, organizations, communities, moderation, appeals, export, and deletion;
- background daemon, CLI installation/control, macOS menu-bar, Windows/Linux tray, local privacy/audit controls, and hosted web dashboard;
- broad agent compatibility through explicit support tiers.

## Metrics

### Token Burn and Credited Token Burn

**Token Burn is the raw ranking metric of record.** It is accepted live usage, unnormalized across model capability, immutable once accepted, and it is what every accounting rule in this product is written against. D-004 and D-037 are unchanged.

**Credited Token Burn is what public rank is computed on.** It is Token Burn multiplied by a server-assigned confidence weight derived from the awarded evidence profile and the ranked-identity trust state. ADR-020 owns the function, its bounds and its disclosure; D-082 and D-144 own the consequences.

The two are never merged and never both public. The word "score" names neither of them, on any surface or in any field.

Where each figure appears:

| Surface | Token Burn | Credited Token Burn |
|---|---|---|
| The participant's own surface | Visible, with both weight factors and the reason either is below 100 | Visible |
| A viewer the participant has authorized | Visible if the participant permits it | Visible |
| Public leaderboards and public profiles | **Not published** | Published |

**Publishing both in public would publish the sanction.** The credited figure divided by the raw figure is the composite weight; the evidence profile is already public under D-008, so the evidence factor is known and the trust factor follows by division — and the trust factor is the sanction that D-084 keeps private. Narrowing Token Burn to the participant's own surface and to viewers they authorize is the price of that rule.

**The residual leak, stated rather than hidden.** An observer who records a participant's published Credited Token Burn across periods sees a discontinuity when a trust state changes, with no evidence-profile change to explain it, and can infer that something happened. No weighting whose output is visible can prevent that. What the design keeps is deniability: there is no marker, no badge and no label, and an ordinary drop in activity looks identical. That is materially weaker than secrecy and it is the honest description.

A normative accounting specification defines input, output, cache read/write, reasoning, tool/context, multimodal, retries, failures, streaming, compaction, subagents, local models, unknown categories, and double-count prevention.

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

A public profile may expose Credited Token Burn, Estimated Cash Burn, rank, movement, periods, agent/model mix, daily activity, presence, friends, boards, organization and community memberships, evidence state, and achievements introduced by the launch scope. **It may not expose Token Burn.** The raw figure appears on the participant's own surface, and on a viewer's surface only where the participant has authorized that viewer. This is narrower than an earlier revision of this specification, which permitted profiles to expose Token Burn without qualification, and the reason is in the metrics section above.

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

The hosted product owns leaderboards, profiles, social graph, boards, organizations, communities, notifications, account settings, moderation, appeals, and server-side lifecycle controls. Country surfaces are post-launch. It never requires access to transcript content.

### Exceptional states

Every surface renders eight states besides the one where everything worked, and `packages/schemas/ui-state-projection-v1.json` says where each comes from. D-334 records the choices.

`loading`, `empty` and `stale` are client-local: derived from a request in flight, a response with no items, or held data older than the freshness budget, and from nothing the server sends. `blocked` and `private` resolve to inputs of the current-viewer-authorization profile. `retracted`, `appeal` and `recovery` resolve to registered state machines and to states those machines declare, which the validator checks — so a surface cannot render a state from a lifecycle that does not exist.

Three of the eight carry a disclosure rule that a screenshot cannot express and a matrix test can:

- `blocked` and `private` are both indistinguishable from a subject that does not exist. Two distinguishable refusals let a viewer work out which one applies, and one of them is a fact about a relationship the other party did not disclose.
- `empty` is not distinguishable from a page every entry of which the viewer is unauthorized to see, because a count of what was filtered discloses what was filtered.
- `appeal` shows `submitted` where the case is in `screening`. The automated pre-review pass is not a decision and gives the appellant nothing to act on, which is why the binding table marks it internal.

## Moderation and appeals

Anti-abuse is progressive, reason-coded, reviewable, and appealable. Define claim exclusion, evidence downgrade, session/account-score quarantine, temporary ranking restriction, device revocation, moderator actions, restoration, insider controls, notifications, retention, and appeal service levels. An SLM cannot permanently ban by itself.

## Export, deletion, and lifecycle

Users can stop collection, remove adapters, disconnect and revoke devices, inspect and export local and server-side safe data, delete local models and intelligence, delete the outbound ledger, delete their profile, delete claims and aggregates subject to legal policy, and delete the account.

An account deletion that is an Article 17 erasure removes every live personal record and makes every retained historical standing unattributable, by destroying the key that binds the retained pseudonym to the person and appending a signed record. It does not delete a sealed leaderboard generation and it does not renumber one. `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` is the normative owner, including the parts the product cannot promise: a third party who copied a standing before the erasure is outside the controller's reach, and physical removal from backups completes at the backup window rather than immediately.

## Explicit non-goals

- Measuring productivity, code quality, usefulness, or commercial value.
- Uploading prompts, responses, transcripts, code, diffs, tools, paths, files, projects, repositories, embeddings, summaries, or personal insights.
- Asking for provider API keys merely to prove usage.
- Claiming provider authentication or mathematical cheat-proofing without evidence.
- Treating social login as proof of one-person uniqueness or activity authenticity.

## Launch gate

Public launch requires complete functional scope, major agent-family coverage, privacy/control traceability, adversarial integrity evidence, accessibility, performance, native packaging/update verification, production operations, moderation/appeals, legal/privacy readiness, and public open-source governance. A narrow vertical slice is an internal milestone, not the launch product.
