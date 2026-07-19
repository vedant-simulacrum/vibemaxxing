# Approved Leaderboard Bento Baseline

Status: approved visual baseline; Storybook fidelity prototype; not production implementation

Approved: 2026-07-19

Visual reference: [`references/leaderboard-bento-approved.png`](references/leaderboard-bento-approved.png)

Executable review surface: `packages/ui/src/concepts/leaderboard-bento.stories.tsx`

Coded render previews:

- [`references/leaderboard-bento-coded-desktop.png`](references/leaderboard-bento-coded-desktop.png)
- [`references/leaderboard-bento-coded-tablet.png`](references/leaderboard-bento-coded-tablet.png)
- [`references/leaderboard-bento-coded-mobile.png`](references/leaderboard-bento-coded-mobile.png)

## Decision

The light-mode bento leaderboard is the canonical starting point for the first VibeMaxxing product screen. It replaces the rejected Signal Ledger, Trackside, and Duel explorations as the direction from which future screen and component work proceeds.

This approval locks the visual grammar and information hierarchy, not production readiness. The current Storybook recreation uses static fixture data and local interaction state only. It deliberately contains no backend requests, authentication, routing, analytics, persistence, real-time transport, or product authorization logic.

## Visual intent

The interface is a first-party developer tool with social competitive context:

- light mode only;
- Codex-like restraint, precision, and density;
- a warm neutral canvas with white working surfaces;
- one dominant ledger rather than a grid of equally important analytics cards;
- bento grouping for identity, position, core metrics, and rival context;
- indigo used for selection, focus, the current user, and the comparison line;
- social energy expressed through rank, movement, rival gap, and data—not decorative game chrome;
- brand-editorial devices remain in brand assets and do not become the product UI style.

## Page anatomy

```text
GlobalHeader
└── content: wordmark | primary navigation | search | account

LeaderboardBentoShell
├── SummaryGrid
│   ├── IdentityTile
│   ├── RankMetricTile
│   ├── BurnMetricTile
│   ├── ModelMetricTile
│   └── ClosestRivalTile
└── WorkspaceGrid
    ├── LeaderboardPanel (dominant)
    │   ├── PeriodControl
    │   ├── UpdateStatus
    │   └── LeaderboardTable
    └── RivalRail
        ├── RivalSnapshot
        └── ComparisonChart
```

The component names above describe responsibilities, not generic visual containers. Do not introduce public components named `BentoBox`, `Card`, or `Widget`. A shared surface primitive may be admitted later only if its semantic variants and accessibility contract are clear.

## Desktop specification

Target review viewport: 1536 × 1024.

| Property | Locked value |
|---|---|
| Header height | `66px` / `--vm-layout-header-height` |
| Page maximum | `1536px` for prototype review; production content may use `--vm-layout-content-max` after fidelity review |
| Outer gutter | `24px` / `--vm-space-6` |
| Summary and rail gap | `16px` / `--vm-space-4` |
| Workspace gap | `20px` / `--vm-space-5` |
| Summary height | minimum `122px` |
| Summary columns | `1.55fr .82fr .92fr .9fr 1.13fr` |
| Workspace columns | approximately `2.45fr 1fr` |
| Panel radius | `12px` / `--vm-radius-md` |
| Control radius | `7px` / `--vm-radius-control` |
| Ledger row | `58px` |
| Ledger header | `40px` |
| Major panel padding | `24px` / `--vm-space-6` |

The summary row is intentionally asymmetric. Identity receives the most room; rank, burn, and model use compact metric tiles; the rival tile is wide enough for identity plus rank context. Equal-width KPI cards are not allowed.

The leaderboard remains the visual anchor. The right rail may support it but must not become louder, darker, or more saturated than the ledger.

## Color and surface specification

All implementation values come from `packages/ui/src/tokens.source.json`.

| Role | Token | Current value |
|---|---|---|
| Canvas | `color.canvas` | `#fbfaf9` |
| Primary surface | `color.surface` | `#ffffff` |
| Primary text | `color.ink` | `#171714` |
| Secondary text | `color.muted` | `#716f68` |
| Hairline | `color.line` | `#dedad1` |
| Row divider | `color.row-line` | `#e9e7e1` |
| Accent | `color.indigo` | `#5847e8` |
| Accent text | `color.indigo-dark` | `#4636c9` |
| Selected row | `color.surface-indigo` | `#fbfaff` |
| Positive movement | `color.positive` | `#18794e` |
| Surface elevation | `shadow.surface` | canonical subtle two-layer shadow |

Raw color literals are forbidden in the component CSS. The visual reference is illustrative; repository tokens are the authoritative reproducible values.

## Typography

- Product UI: Inter Variable, self-hosted/package-delivered as documented in `assets/brand/FONT_PROVENANCE.md`.
- Technical values: canonical monospace stack from `font.mono`.
- UI body and navigation: 12–14px, weights 400–600.
- Eyebrows and table headers: 10px, semibold, uppercase, approximately `0.10em` tracking.
- Summary metrics: 28px semibold monospace with tabular numerals.
- Dense table numbers: 12px monospace with tabular numerals.
- Sentence case is the default. Uppercase is reserved for short structural labels.

## Interaction contract for the prototype

- `Today`, `7 days`, and `Season` are real keyboard-focusable buttons with a single pressed state.
- Search is a button-shaped command entry point; the prototype does not open a command palette.
- Table overflow actions and profile actions are labelled controls but perform no product action.
- The selected Vedant row uses a pale indigo background plus a 3px indigo leading rule; selection never relies on color alone.
- The chart exposes an accessible summary; its SVG lines are decorative.
- Visible focus uses the canonical indigo focus ring.

Production work must decide whether period selection is URL state, controlled application state, or server input. It must not preserve prototype-local state merely because the mock-up uses it.

## Data and copy contract

The fixture exists to validate layout and must remain internally consistent:

- current user: Vedant, `@vedant`, rank `#07`, up 3;
- Token Burn today: `86.4M`;
- seven-day Token Burn: `498.7M`;
- top model: `GPT-5.4`;
- closest rival: Sam Rivera, `@samrivera`, rank `#08`;
- Sam Token Burn today: `81.1M`;
- Sam seven-day Token Burn: `476.2M`;
- Vedant leads Sam by `5.3M`; therefore the copy is exactly `Sam is 5.3M behind`.

Never describe the relationship as Vedant being behind. Cash values, when added later, must use `Estimated Cash Burn` and cannot be labelled spend or cost.

## Responsive recomposition

### Tablet: 821–1180px

- Summary becomes four columns and the rival tile spans the full second row.
- The rival rail moves below the ledger as two columns.
- The ledger stays above all rival detail.

### Compact tablet: 561–820px

- Primary navigation hides; search becomes icon-only with an accessible name.
- Summary becomes two columns; identity and rival span both.
- Rival panels stack vertically.
- Seven-day table values hide before identity, rank, current burn, or model.

### Mobile: up to 560px

- Outer gutter becomes 16px.
- Summary tiles use 16px internal padding and a tighter 12px grid gap.
- Period control occupies the ledger width; update status moves below it.
- Table retains rank, identity, current Token Burn, and the action.
- Model, seven-day burn, row avatars, and inline movement progressively hide.
- No primary ledger row uses horizontal scrolling.

These breakpoints belong to the template contract. Production components own their internal reflow; pages may not patch the same component differently per route.

## Component extraction plan

The Storybook prototype is intentionally colocated while fidelity is being tested. After visual acceptance of the rendered code, extract in this order:

1. Reuse the existing `Wordmark`, `ProfileAvatar`, button/focus behavior, and token system.
2. Admit `MetricTile` only if the same labelled-value-detail job recurs on profile or board screens.
3. Implement `PeriodControl` as the existing finite-choice contract rather than a second tab system.
4. Implement `LeaderboardTable` as a product pattern with typed columns, selected-current-user state, loading/empty/error states, and responsive disclosure.
5. Implement `RivalSnapshot` and `ComparisonChart` as separate product patterns because their semantics and accessibility differ.
6. Compose those patterns into a `LeaderboardBentoShell` template that owns layout only.
7. Keep data fetching, authorization, URL state, and realtime updates in the application route.

Nothing becomes a stable public component merely because it appears in this prototype.

## Required states before production implementation

The next component phase must storyboard and approve:

- leaderboard loading skeleton with stable column geometry;
- empty board and no-rival states;
- recoverable error and offline/stale states;
- private/restricted builder state;
- Imported historical data outside active rankings;
- long names, long handles, and missing avatars;
- ties and multi-digit movement;
- rank outside the visible top page;
- no recent comparison data;
- keyboard, 200% zoom, forced-colors, and reduced-motion behavior.

## Explicit non-goals of the current recreation

- no application route;
- no backend or mock API;
- no OAuth or account menu;
- no real search;
- no real pagination, sorting, filtering, or realtime updates;
- no charting dependency decision;
- no final public component API;
- no dark theme;
- no production bundle or deployment claim.

## Fidelity acceptance gate

Before production extraction, compare the Storybook desktop render against the approved PNG at 1536 × 1024 and review:

1. macro grid and panel proportions;
2. summary-tile alignment and optical balance;
3. ledger dominance and row density;
4. typographic hierarchy and numeric alignment;
5. restraint of borders, shadows, and indigo;
6. correct rival gap and chart labels;
7. tablet and mobile recomposition.

Differences must be resolved in the prototype or recorded here as deliberate improvements. The production route must not become the place where the design is discovered.
