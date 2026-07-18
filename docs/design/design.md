# VibeMaxxing Design System

## Product Direction

VibeMaxxing is a premium, public, gamified leaderboard for AI-agent activity.

The primary leaderboard metrics are:

- **Token Burn** — accepted token count
- **Cash Burn** — estimated API-equivalent value

The default leaderboard sort is **Token Burn**. Cash Burn is a first-class alternate sort.

The experience should feel like:

> **Codex restraint × Steam social competition**

The balance should be approximately:

- 70% refined technical product
- 30% competitive social network

The launch theme is light, with an indigo accent.

---

## Core Visual Principles

### 1. One designed composition, not a dashboard grid

Avoid assembling the interface from many rounded cards. Use:

- Continuous primary canvases
- Typographic hierarchy
- Fine separators
- Quiet surface changes
- Negative space
- Precise alignment

Reserve bordered containers for truly independent objects such as dialogs, notifications, compact social rails, or isolated controls.

### 2. Strong hierarchy

The first screen must immediately answer:

- Who is winning?
- By how much?
- Where am I?
- What changed?

The dominant visual objects should be:

- Global or current-period burn total
- Top leaderboard ranks
- Current user's position
- Token Burn / Cash Burn control
- Active friend and rival state

Everything else should visually recede.

### 3. Typography as the primary design material

Use a clean, neutral grotesk such as Inter, Geist, or Instrument Sans.

Use a monospace only for:

- Commands
- Collector versions
- Integrity metadata
- Technical identifiers

Use tabular numerals for all burn values, ranks, and cash amounts.

Recommended hierarchy:

- Network total: 64–80px
- Profile burn: 40–48px
- Page title: 28–32px
- Leaderboard value: 15–17px
- Body: 14px
- Metadata: 12px

Large numbers should feel editorial, exact, and confident rather than oversized for spectacle.

### 4. Indigo must be scarce

Indigo is used only for:

- Current selection
- Live competitive movement
- Primary action
- Current user emphasis
- Active rank movement

The interface should remain approximately:

- 90% neutral
- 10% indigo

Avoid covering charts, navigation, buttons, labels, and status elements with the accent simultaneously.

### 5. Minimal card usage

Avoid:

- Repeated rounded statistic cards
- Generic analytics tiles
- Donut-chart cards
- Highlight cards with no strong purpose
- Multiple nested bordered panels

Prefer:

- Open sections
- Hairline dividers
- Direct labels and values
- Full-width visualizations
- Compact contextual rails

### 6. Charts must answer real questions

Do not use generic dashboard charts as filler.

Preferred visualizations:

- Stepped burn timeline
- Rank-history line
- Agent/model horizontal distribution bars
- Daily activity heat strip
- Overtake and personal-record annotations

Avoid donut charts on the main leaderboard.

### 7. Professional motion

Motion should be almost invisible:

- Row movement: 180–240ms
- Rank highlight: brief and restrained
- Number interpolation: only on live updates
- Presence pulse: low-amplitude and infrequent
- Overtake notification: subtle slide and settle
- Full reduced-motion support

Avoid:

- Bouncing
- Particles
- Constant chart animation
- Excessive glow
- Gaming-style effects

---

## Color System

### Foundation

- Page background: `#F7F7F5`
- Primary surface: `#FFFFFF`
- Primary text: `#111113`
- Secondary text: `#6B6B73`
- Hairline border: `#E7E7E4`

### Accent

- Indigo: `#5856E8`
- Indigo hover: `#4947D6`
- Indigo soft: `#F0EFFF`

### Status

- Positive: `#14804A`
- Warning: `#A56400`
- Critical: `#C9362B`

Avoid pure-white full-screen canvases. Use warm neutral backgrounds with white content surfaces and minimal shadow.

---

## Shape Language

- Main radius: 6–10px
- Button radius: 7–8px
- Table: no rounded outer card
- Hairline dividers: 1px
- Shadows: nearly absent
- Pills: only for statuses and compact filters
- Icons: small, consistent, neutral stroke

---

## Brand Direction

### Name

Use the canonical wordmark:

`vibemaxxing`

Prefer lowercase presentation.

### Logo

Begin with a wordmark before forcing a standalone symbol.

Explore:

- A custom `x`
- Crossing signals
- Overtaking
- Two competitive paths
- A subtle active cursor or signal mark

Avoid:

- Coins
- Flames
- Gauges
- Lightning bolts
- Literal token icons
- Generic code brackets
- Crypto aesthetics
- Esports motifs
- Generic rounded monograms

The mark must work in:

- Full wordmark
- App icon
- CLI
- GitHub badge
- Social card
- Monochrome
- Small sizes

### Tone

Balanced:

- Serious
- Premium
- Slightly playful
- Internet-native
- Competitive
- Never corporate
- Never childish

---

## Desktop Information Architecture

### Global Navigation

Use a quiet top navigation:

- Rankings
- Friends
- Boards
- Search
- Notifications
- Profile

### Rankings Controls

Period:

- Today
- Week
- Month
- Season
- Year
- All time

Scope:

- Global
- Friends
- Private boards
- Organizations
- Countries

Metric:

- Tokens
- Cash

Avoid duplicating these controls in multiple locations.

---

## Leaderboard

### Header

The leaderboard header should contain:

- Scope and period
- Total network Token Burn
- Estimated network Cash Burn
- Live participant count
- User rank
- Tokens / Cash sort

### Table

Use the familiar WhoBurnedMore-style columns as a functional reference, but simplify visual weight.

Core columns:

- Rank
- User
- Tokens Burned
- Cash Burn
- Models
- Agents
- Country
- Streak
- Movement

Rules:

- Right-align numerical values
- Use tabular figures
- Increase row height and whitespace
- Make rank numerals typographically prominent
- Treat top three subtly, not with gaudy medals
- Reduce visual weight of flags, model icons, and agent counts
- Pin and emphasize the current user row
- Show movement as `↑ 4`, `↓ 2`, `NEW`, or `—`
- Show live state only during an active agent session

Secondary identity information can sit beneath the username:

- Active in Codex
- 12-day streak
- Just overtook a friend

### Social Rail

Use a collapsible rail rather than a permanent dashboard sidebar.

Collapsed:

- Friend avatars
- Active indicators
- One meaningful event
- Overtake alert

Expanded:

- Friend activity
- Requests
- Rival comparisons
- Active sessions

Never expose project names, files, or transcript-derived details.

---

## Profile

The public profile opens with identity and competitive position:

- Username
- Handle
- Country
- Active agent state
- Global rank
- Token Burn
- Cash Burn
- Streak
- Agents used

Tabs:

- Overview
- History
- Agents
- Models
- Boards

Profile content:

- One full-width burn timeline
- Rank history
- Agent distribution
- Model distribution
- Records
- Streaks
- Recent milestones

Avoid four identical statistics cards.

### Profile Privacy

Users may independently hide:

- Cash Burn
- Model breakdown
- Agent breakdown
- Activity history
- Presence
- Friend list
- Country
- Board participation

Private boards may show:

- Exact burn
- Rank only
- Relative comparison
- Agent mix
- Presence

---

## Presence

Presence is active only while a qualifying agent session is active.

States:

- Active
- Idle
- Offline
- Private

Example copy:

- `Vedant is active in Codex`
- `Arham just overtook you`
- `Riya entered the weekly top 10`

---

## Privacy and Integrity UI

Avoid the word `verified`.

Use:

- Standard
- Hardened
- Imported

Explain these states plainly.

The strongest user-facing statement:

> The process that can read your transcripts cannot access the internet. The process that accesses the internet cannot read your transcripts.

Privacy should feel like a product feature, not compliance copy.

---

## Mobile

Mobile must be recomposed rather than compressed.

Requirements:

- Dedicated leaderboard row layout
- Sticky period and metric switcher
- Current-user position always accessible
- Social rail becomes a bottom sheet
- Large burn values remain legible
- Secondary columns move into expandable rows
- Full keyboard and screen-reader support where relevant

---

## Quality Bar

The UI must not contain generic AI-generated patterns.

Required:

1. Consistent tabular alignment
2. Designed empty states
3. Long-name and huge-number handling
4. Responsive behavior at 320px, 768px, 1280px, and ultrawide
5. Hover, focus, loading, offline, error, private, and hidden states
6. Non-color status indicators
7. Visible keyboard focus
8. Geometry-matched skeletons
9. Normalized provider/tool icons
10. Consistent copy voice
11. Locale-aware dates, numbers, and currencies
12. Contextual privacy explanations
13. Current user always easy to find
14. Mobile recomposition
15. No decorative filler sections
16. No visible TODOs
17. No dead buttons
18. No fake interactions

---

## Design Review Checklist

Before approving a screen, ask:

- Is the primary action or information unmistakable?
- Can 30–40% of the visible chrome be removed?
- Is indigo reserved for meaning?
- Is every card necessary?
- Does every chart answer a question?
- Are numbers aligned and readable?
- Is the current user easy to locate?
- Does it still work with very long names and huge values?
- Does it feel calm before it feels competitive?
- Could this plausibly have been designed by a top product team?


---

## Final UI Generation Directive

The next UI iteration must follow these additional constraints:

### Composition

- Treat the desktop product as one continuous composition, not a grid of dashboard cards.
- The leaderboard is the dominant object.
- The social rail is secondary and collapsible.
- The current user's row remains visible and easy to locate.
- The page header must establish period, scope, Token Burn, Cash Burn, active users, and current rank immediately.
- Remove decorative analytics that do not support a clear user question.
- Avoid a generic hero + card-grid SaaS composition.

### Leaderboard Detail

Use the useful WhoBurnedMore column structure as the functional reference:

- Rank
- User
- Tokens Burned
- Cash Burn
- Models
- Agents
- Country
- Streak
- Movement

Improve it through:

- Larger rank numerals
- More vertical breathing room
- Tabular number alignment
- Reduced visual weight for flags and provider icons
- Subtle top-three distinction
- A pinned current-user row
- Live-state cues only during active agent sessions
- Secondary metadata beneath usernames rather than excessive columns

### Brand and Theme

- Canonical wordmark: `vibemaxxing`
- Light theme first
- Warm-white page background
- White primary surfaces
- Near-black text
- Electric indigo accent
- Indigo should occupy no more than roughly 10% of the screen
- Prefer a refined lowercase wordmark before forcing a standalone symbol
- Explore a custom `x` or crossing/overtake motif
- Avoid coins, flames, crypto visuals, esports visuals, and generic code brackets

### Quality Standard

The result must feel intentionally authored by an elite product team.

Reject or revise any output containing:

- Excessive rounded cards
- Generic donut charts
- Default Tailwind appearance
- Unnecessary gradients
- Glassmorphism
- Huge empty marketing slogans
- Random metric tiles
- Inconsistent spacing
- Overuse of pills
- Fake metallic rank badges
- Overly saturated accent usage
- Weak hierarchy
- Repeated component templates
- Placeholder copy
- Decorative sections without product value

### Codex-Level Polish

Match the qualities—not the exact layouts—of highly polished Codex interfaces:

- Quiet hierarchy
- Tight information architecture
- Strong typographic rhythm
- Minimal visual chrome
- Precise alignment
- Restrained motion
- Highly considered empty, loading, private, offline, and error states
- Keyboard-friendly controls
- Mobile recomposition rather than desktop compression

### Social Competition

Steam-like social mechanics should be integrated with restraint:

- Friends currently active in an agent session
- Overtake notifications
- Weekly rank changes
- Friend comparison
- Private boards
- Organization and country boards

Do not turn the product into a gaming dashboard. Competition should emerge through data, movement, presence, and rivalry—not flashy decoration.

### Privacy and Integrity

Use these consumer-facing states:

- Standard
- Hardened
- Imported

Avoid the word `verified`.

The privacy message should be presented as a premium system property:

> The process that can read your transcripts cannot access the internet. The process that accesses the internet cannot read your transcripts.

### Final Review Rule

Before a screen is approved, remove at least one unnecessary visual element and verify that the screen becomes clearer rather than emptier.
