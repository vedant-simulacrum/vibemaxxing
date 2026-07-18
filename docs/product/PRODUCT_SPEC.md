# Product Specification

## Product definition

VibeMaxxing is a public social leaderboard for people using AI coding agents. It combines a polished competitive identity layer with privacy-preserving local measurement.

## Primary metrics

### Token Burn

Accepted token usage attributed to live qualifying activity.

The interface may break it down into:

- Input
- Output
- Cache read
- Cache write
- Reasoning, where exposed
- Tool/context activity where applicable

### Cash Burn

Estimated current API-equivalent value of the accepted usage.

Rules:

- It is not presented as the user's actual bill.
- Subscription users are still shown an estimate.
- Local-model usage may show `Local compute` or no dollar equivalent until a defensible local-compute estimator exists.
- Pricing tables are versioned and time-aware.

## Ranking periods

Launch with:

- Daily
- Weekly
- Monthly
- Season
- Annual
- Lifetime

Leaderboard updates should materialize approximately once per minute.

## Ranking scopes

- Global
- Friends
- Private boards
- Organizations
- Hacker houses
- Communities
- Countries

Private boards may define their own eligible agents, visibility, and ranking preferences.

## Social layer

- Anyone may send friend requests.
- Users can control discoverability and request handling.
- Presence is active only while a qualifying agent session is active.
- Friends can see overtakes, movement, and active-agent state subject to privacy settings.
- Core initial loop: add friend → see activity → get overtaken → return and compete.

Challenges, levels, achievements, and collectible badges should be architected for later but are not required for the first production milestone.

## Public profile

Default profile may expose:

- Token Burn
- Cash Burn
- Rank
- Agent/model mix
- Daily activity
- Current presence
- Rank movement
- Board memberships

User-controlled visibility:

- Hide Cash Burn
- Hide agent/model breakdown
- Hide activity history
- Hide presence
- Hide friends
- Hide country
- Hide board membership
- Show rank only within a specific board

## Presence

States:

- Active
- Idle
- Offline
- Private

No project name, repository, path, prompt, or transcript-derived detail may appear in presence.

## Deletion

Users can:

- Disconnect a device
- Stop collection
- Remove adapters
- Restore changed source configuration
- Delete local models
- Delete local intelligence data
- Delete the outbound audit ledger
- Delete public profile
- Delete server-side claims and aggregates
- Delete everything

## Explicit non-goals

- Measuring engineering productivity
- Judging whether usage is useful
- Rewarding code quality
- Uploading transcripts
- Asking users for provider API keys
- Claiming local evidence is provider-authenticated
