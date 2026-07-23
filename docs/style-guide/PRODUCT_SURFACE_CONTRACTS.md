# Product Surface Contracts

This file tells humans and coding agents how the bounded hosted-web prototype is organized. It is a UI composition map, not a backend contract, product roadmap, or production-readiness claim.

## Source-of-truth order

1. Binding product rules in `AGENTS.md` and accepted contracts/ADRs.
2. Tokens and governed assets.
3. Public exports from `@vibemaxxing/ui`.
4. Storybook stories and reviewed visual baselines.
5. Hosted prototype routes.

A route, fixture, screenshot, story, or label must never override a binding product rule.

## Public composition map

| User job | Shared export | Storybook status | Hosted prototype route |
|---|---|---|---|
| Global leaderboard | `LeaderboardHubStoryboard` | Candidate visual batch | `/` and `/leaderboards/global` |
| Friends leaderboard | `LeaderboardHubStoryboard` with `initialScope="Friends"` | Candidate visual batch | `/leaderboards/friends` |
| Board leaderboard | `LeaderboardHubStoryboard` with `initialScope="Boards"` | Candidate visual batch | `/leaderboards/boards` |
| Organization leaderboard | `LeaderboardHubStoryboard` with `initialScope="Organizations"` | Candidate visual batch | `/leaderboards/organizations` |
| Own profile | `OwnProfileStoryboard` | Candidate visual batch | `/me` |
| Public profile | `PublicProfileStoryboard` | Approved implemented prototype | `/profile/[handle]` |
| Rival comparison | `RivalComparisonStoryboard` | Approved implemented prototype | `/rivals/[handle]` |
| Friends management | `FriendsStoryboard` | Approved implemented prototype | `/friends` |
| Activity | `ActivityStoryboard` | Approved implemented prototype | `/activity` |
| Board standings | `BoardStandingsStoryboard` | Approved implemented prototype | `/boards/[slug]` |

The candidate batch may be used for implementation review and iteration. It must not move under `Approved baseline/*`, acquire governed reference images, or replace accepted visual baselines until a human explicitly approves its appearance.

Pull-request workflow artifacts include desktop, tablet, and mobile PNGs named `candidate-global-leaderboard-*` and `candidate-own-profile-*`. These are disposable review evidence. They are intentionally excluded from baseline comparison until approval.

## Leaderboard contract

- Token Burn is always the default ranking metric.
- Estimated Cash Burn is secondary and always uses both the words `Cash Burn` and `estimated`.
- The supported UI periods are today, daily, weekly, monthly, seasonal, yearly, and lifetime.
- Supported candidate scopes are global, friends, joined boards, and accessible organizations.
- Country remains visibly unavailable/post-launch.
- Standard and Hardened accepted claims may count. Imported records never count.
- Rank rows use shared identity, model, movement, evidence, and avatar components.
- Scope and period selectors change fixture composition only. They do not imply an implemented ranking API.

## Own-profile contract

The own-profile surface has four sections:

- **Overview:** current standing, accepted Token Burn, explicitly estimated Cash Burn, streak, trend, and model mix.
- **Analytics:** agent/model aggregate breakdowns plus a visually isolated private Imported-history panel.
- **Connections:** fixture collector/adapter status and the binding device privacy boundary.
- **Privacy:** public-preview controls, never-public data, and vendor-neutral one-ranked-identity copy.

Never show prompts, responses, code, diffs, tool contents, filenames, paths, repository/project names, credentials, embeddings, summaries, classifications, or personal insights.

## Data boundary

All current values, identities, health states, timestamps, controls, and interactions are synthetic. Route files must not contain fixtures or recreate shared components. Future route adapters may map typed server/local state into the shared UI only after their authoritative contracts are accepted.

## Agent checklist

Before editing a surface:

1. Find its shared export and story.
2. Reuse existing product patterns and asset registries.
3. Preserve every binding label and exclusion.
4. Add candidate stories for each materially different composition.
5. Verify desktop, tablet, mobile, keyboard, forced-colors, reduced-motion, and exceptional states.
6. Stop for explicit visual approval before promoting a candidate composition.
