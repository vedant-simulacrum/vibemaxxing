# Leaderboard First Baseline

Status: general visual direction approved; implementation specification locked; not production implementation

Approved: 2026-07-19

Visual reference: [`references/leaderboard-first-approved.png`](references/leaderboard-first-approved.png)

The reference image is authoritative for composition and hierarchy. This document is authoritative for typography, spacing, color, component boundaries, responsive behavior, and copy. Image-generated glyph rendering, incidental gradients, faces, icons, and one-off measurements are not implementation instructions.

## Decision

The **Leaderboard First** direction replaces the earlier five-tile leaderboard bento as the canonical first-screen direction.

The approved composition is:

1. a quiet global header;
2. one continuous personal-status strip;
3. one dominant six-column leaderboard;
4. a subordinate right rail containing trend and rival context.

The design is bento-like because its regions have different proportions and jobs. It must not become a collection of equal cards or nested generic widgets.

## Why the reference still looks less polished than the target product should

The mock-up successfully establishes hierarchy, but several generated-image artifacts must not survive implementation:

- the synthetic monospace treatment is used too broadly and makes ordinary data feel like editorial display type;
- some font weights and baselines vary between otherwise equivalent labels;
- the table does not yet use a formal width, alignment, and truncation contract;
- panel borders, row rules, and shadows occasionally compete instead of forming one elevation hierarchy;
- some gaps are visually plausible but not drawn from a repeatable scale;
- the chart fill reads as a gradient even though gradients are not part of the product language;
- avatar imagery and icons are illustrative rather than approved component assets.

The implementation fixes these issues through the contracts below. It does not search for a more decorative font or add more surface effects.

## Anatomy

```text
GlobalHeader
└── Wordmark | PrimaryNav | SearchTrigger | AccountTrigger

LeaderboardFirstShell
├── PlayerStatusStrip
│   ├── CurrentPlayer
│   ├── CurrentRank
│   ├── BurnToday + RankMovement
│   ├── TopModel
│   └── ClosestRivalSummary
└── LeaderboardWorkspace
    ├── LeaderboardPanel
    │   ├── LeaderboardToolbar
    │   │   ├── PeriodControl
    │   │   └── FreshnessStatus
    │   └── LeaderboardDataTable
    └── LeaderboardRail
        ├── TrendCard
        └── RivalComparisonCard
```

`PlayerStatusStrip` is one component with semantic regions. It is not five cards placed next to one another. `LeaderboardRail` is contextual and never outranks the table.

## Desktop geometry

Review viewport: `1536 × 1024`.

| Property | Locked value |
|---|---:|
| Header height | `72px` |
| Page gutter | `24px` |
| Content maximum | `1536px` including gutters |
| Header-to-status gap | `24px` |
| Status-strip height | `128px` |
| Status-to-workspace gap | `24px` |
| Workspace columns | `minmax(0, 2.2fr) minmax(384px, 464px)` |
| Workspace gap | `24px` |
| Rail card gap | `24px` |
| Major radius | `16px` |
| Compact radius | `9px` |
| Control radius | `9px` |
| Major card padding | `24px` |
| Status horizontal padding | `28px` |

The page uses the existing 4px token ladder while treating 8px as the primary layout beat. Approved layout values are `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`. One-off 1–3px values are allowed only for borders, optical icon alignment, and focus treatment.

### Personal-status strip

| Property | Locked value |
|---|---:|
| Grid | `1.15fr .82fr 1.25fr .92fr 1.2fr` |
| Vertical padding | `20px` |
| Region horizontal padding | `28px` |
| Avatar | `80px` |
| Region separator | `1px`, inset `24px` from top and bottom |
| Icon field | `48px` square |
| Icon | `20px` |
| Identity gap | `20px` |
| Metric icon-to-copy gap | `16px` |

Separators use the quiet row-line token. The strip receives one outer border and one surface shadow. Regions never receive their own border, radius, or shadow.

### Leaderboard panel

| Property | Locked value |
|---|---:|
| Toolbar height | `80px` |
| Toolbar horizontal padding | `24px` |
| Period control height | `44px` |
| Column-header height | `48px` |
| Body row height | `58px` |
| Cell horizontal padding | `20px` |
| Row avatar | `36px` |
| Avatar-to-identity gap | `12px` |
| Name-to-handle gap | `2px` |
| Selected-row leading rule | `3px` |

The table has exactly six desktop columns:

| Column | Width contract | Alignment | Type treatment |
|---|---|---|---|
| Rank | `72px` | left | technical, tabular |
| User | `minmax(240px, 1fr)` | left | name + handle |
| Burn today | `128px` | right | Inter tabular figures |
| 7d burn | `132px` | right | Inter tabular figures |
| Top model | `140px` | left | technical identifier |
| Change | `88px` | right | direction + magnitude |

Comparable numbers align on the right edge. Column widths do not change per row or data value. Handles truncate before names. Model identifiers truncate before current-burn values. Movement always includes a direction glyph and magnitude; color is supplementary.

### Context rail

Both rail panels use `24px` padding. The trend panel receives approximately `1.05fr` of available rail height and the rival panel `1fr`. The chart has no gradient fill. Use a 2px indigo line, 6px terminal point, and no more than four labelled horizontal guides. Comparison bars share a single scale.

## Typography contract

### Font decision

Use the official **Inter Variable** upright font already specified by the brand system. Do not replace it with a fashionable display face. The polish problem is incorrect role assignment and generated rendering, not Inter itself.

Required root behavior:

```css
font-family: var(--vm-font-sans);
font-optical-sizing: auto;
font-synthesis: none;
font-feature-settings: "liga" 1, "calt" 1;
text-rendering: optimizeLegibility;
```

Numeric columns use Inter's tabular figures rather than switching the entire value to monospace:

```css
font-variant-numeric: tabular-nums lining-nums;
font-feature-settings: "tnum" 1, "calt" 1;
```

The personal-status strip uses Inter for every visible value, including `#07` and `GPT-5.4`. It is an identity-and-status surface, not a code readout. The canonical monospace stack is reserved for dense table ranks and model identifiers only. Token totals, percentages, dates, navigation, names, handles, headings, and all status-strip copy remain Inter.

### Type roles

| Role | Size / line height | Weight | Tracking |
|---|---|---:|---:|
| Navigation | `14 / 20px` | `500`; active `600` | `0` |
| Player name | `20 / 28px` | `600` | `-0.01em` |
| Status metric | `20 / 28px` | `500` | `-0.01em` |
| Status rank / model | `18 / 24px` | `500–600` | `0` |
| Card title | `16 / 24px` | `600` | `-0.01em` |
| Table name | `14 / 20px` | `500` | `0` |
| Table numeric | `14 / 20px` | `500` | `0` |
| Body | `14 / 20px` | `400` | `0` |
| Label / column header | `12 / 16px` | `500` | `0` |
| Handle / metadata | `12 / 16px` | `400` | `0` |
| Rank / model identifier | `14 / 20px` | `500` | `0` |

Rules:

- sentence case everywhere;
- no uppercase tracked eyebrow labels in this screen;
- no product text below `12px`;
- no weight above `600` except the outlined wordmark asset;
- never use monospace as a shortcut for “developer aesthetic”;
- never use monospace anywhere inside `PlayerStatusStrip`;
- verify the real font loaded with `document.fonts.check()` before visual comparison;
- screenshots rendered with fallback fonts fail the fidelity gate.

## Surface hierarchy

| Role | Token |
|---|---|
| Canvas | `color.canvas` |
| Primary panels | `color.surface` |
| Quiet icon fields | `color.surface-subtle` or semantic status halo |
| Panel border | `color.row-line` |
| Control border | `color.line` |
| Row divider | `color.row-line` |
| Selected row | `color.surface-indigo` |
| Primary accent | `color.indigo` |
| Positive / negative | `color.positive` / `color.negative` |

Only major white surfaces may use `shadow.surface`. The table has one panel border; it does not add an inner rounded table border. Default rows are white. Hover and selected states use tonal surfaces. Avoid gradients, glass, glow, dark chrome, double borders, and visible shadows around every control.

## Content contract

- current user: Vedant, `@vedant`, rank `#07`, up 3;
- Burn today: `86.4M`;
- seven-day Burn: `498.7M`;
- top model: `GPT-5.4`;
- closest rival: Sam Rivera, `@samrivera`, rank `#08`;
- Sam Burn today: `81.1M`;
- Sam seven-day Burn: `476.2M`;
- current lead: `5.3M`.

The table desktop columns are Rank, User, Burn today, 7d burn, Top model, and Change. “Tokens today” is not the approved heading. “Burn today” is canonical.

## Responsive recomposition

### 1181px and wider

Use the complete desktop structure and all six columns.

### 821–1180px

- Status strip becomes a two-row grid: identity spans two rows; rank, burn, model, and rival occupy the remaining cells.
- Rail moves below the leaderboard as two unequal columns.
- All six table columns remain until they fail the minimum widths above.

### 561–820px

- Hide primary navigation; keep an icon-labelled search trigger.
- Status strip becomes identity plus a compact three-metric row.
- Rail panels stack below the leaderboard.
- Hide `7d burn`, then `Top model`; keep Rank, User, Burn today, and Change.

### Up to 560px

- Use `16px` page gutters and `16px` panel padding.
- Status strip becomes a compact identity header with a two-column metric region.
- Period control spans the toolbar; freshness moves below it.
- Keep Rank, User, and Burn today in the row. Move model, seven-day burn, and change into row disclosure.
- Do not horizontally scroll the primary leaderboard.

## Component and reuse plan

Implementation may begin only after a final reference review. Extract in this order:

1. `PlayerStatusStrip` as a product pattern composed from the existing Avatar, RankMovement, and formatting utilities.
2. `LeaderboardToolbar` using the existing ChoiceGroup contract.
3. `LeaderboardDataTable` with typed column definitions and responsive visibility priorities.
4. `TrendCard` with a semantic text alternative independent of its SVG.
5. `RivalComparisonCard` using the existing Progress primitive.
6. `LeaderboardFirstShell` as a layout-only template.

Do not create `BentoCard`, `DashboardCard`, `StatCard`, or route-local copies of existing controls. A surface primitive may be used internally, but product components are named for their job.

## Required component states

- loading with stable column geometry;
- empty leaderboard;
- no rival;
- stale and offline freshness;
- recoverable error;
- long names and handles;
- missing avatar;
- ties and unchanged rank;
- multi-digit rank and movement;
- model identifier overflow;
- private or restricted user;
- 200% zoom, keyboard, forced colors, and reduced motion.

## Polish acceptance gate

The coded screen is not accepted until all are true:

1. Inter Variable is confirmed loaded; no fallback screenshot is used.
2. Every visible gap maps to an approved spacing token or documented optical correction.
3. Status regions share one surface and do not read as five cards.
4. All table numbers use tabular figures and stable right edges.
5. Text baselines remain consistent across every row.
6. The table is visually dominant at first glance.
7. Borders and shadows remain subordinate to whitespace and typography.
8. Desktop, tablet, and mobile are reviewed from real browser captures.
9. Loading, empty, error, stale, and overflow stories preserve the layout hierarchy.
10. Visual regression compares the browser render—not Storybook chrome—to approved captures.

## Research basis

- Inter is specifically designed for detailed interfaces and provides text/display optical designs, contextual alternates, and tabular figures. The screen therefore keeps Inter, enables its UI-oriented features, and uses `tnum` for comparable data: https://rsms.me/inter/
- Carbon's data-table guidance uses 14px regular row text, 14px semibold column headers, and 16px horizontal table spacing. VibeMaxxing uses the same readable density class while slightly increasing cells to 20px for this spacious direction: https://carbondesignsystem.com/components/data-table/style/
- Atlassian's spacing guidance uses an 8px base unit and a limited token scale to create consistency and responsive readiness. VibeMaxxing retains its 4px sub-step but locks page composition to the 8px rhythm: https://atlassian.design/foundations/grid-beta/applying-grid
- Atlassian's primitives guidance supports token-bound layout building blocks instead of repeated page-local spacing decisions: https://atlassian.design/components/primitives/overview/

## Non-goals

- no backend, routing, authentication, or live updates;
- no production data-table API yet;
- no charting-library decision;
- no dark theme;
- no generic dashboard component family;
- no attempt to reproduce incidental image-generation artifacts.
