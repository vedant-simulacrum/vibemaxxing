# Competitive Ledger UI Foundations

Status: approved foundations; Leaderboard First baseline approved for final reference review

This is the sole owner of product layout, interaction, and screen-composition foundations. It absorbed the former `docs/design/design.md` on 2026-08-06; where that document disagreed with this one or with `BRAND.md`, both claims are recorded in [§17](#17-superseded-values-recorded-from-designmd) rather than silently reconciled.

## 1. Purpose

This document defines the stable UI grammar for VibeMaxxing before page-specific designs are implemented. It is not approval for any particular route, screen, or component composition.

The UI thesis is:

> The leaderboard is the product. Everything else creates context, competition, or trust around it.

## 2. Product principles

1. **Ledger first.** Rank, identity, evidence, period, and burn must remain visually dominant.
2. **Competition through data.** Social energy comes from rivals, overtakes, movement, streaks, and presence—not decorative gamification.
3. **Privacy made visible.** The UI explains what leaves the device and what never does.
4. **Exact language.** Token Burn is canonical; cash is always Estimated Cash Burn.
5. **Calm density.** Tables may be information-rich without becoming cramped or dashboard-like.
6. **Honest evidence.** Standard, Hardened, and Imported are never visually conflated.
7. **Responsive recomposition.** Mobile is a deliberate hierarchy, not a shrunken desktop table.

## 3. Shared tokens

Canonical machine-readable tokens live in:

- `packages/ui/src/tokens.css`
- `packages/ui/src/tokens.ts`

They cover color, typography, spacing, radii, elevation, layout, focus, and motion. Product code consumes these tokens rather than duplicating raw values.

The governing reuse architecture, component contract, inventory, and AI-authoring rules live alongside this file in `docs/style-guide/`. `README.md` in this directory is the required entry point before any component or page implementation. Brand identity, the canonical palette, and voice are owned by `BRAND.md`; this document does not restate hex values.

## 4. Layout

### Desktop

- Maximum content width: 1396px.
- Standard outer gutter: 32px.
- Primary pattern: fluid ledger column plus a 320px contextual rail.
- Header height: 68px.
- Major vertical rhythm: 48–64px.

### Tablet

- Outer gutter: 20–24px.
- Context rail may become a two-column section below the ledger.
- Controls wrap by group; they do not become an unlabelled icon strip.

### Mobile

- Outer gutter: 16px.
- Minimum touch target: 44px.
- Rank, identity, and selected burn value remain visible in leaderboard rows.
- Evidence, presence detail, and secondary metadata move to progressive disclosure when space is constrained.
- Horizontal scrolling is acceptable for period tabs, not for the primary leaderboard row.

## 5. Spacing

Use the 4px base scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, and 64px.

- 4–8px: icon/label and tightly related metadata.
- 12–16px: controls and row-internal spacing.
- 20–24px: panel padding and component groups.
- 32–40px: section separation.
- 48–64px: page-level rhythm.

Avoid arbitrary one-off spacing unless optical correction is documented.

## 6. Surfaces and borders

- Canvas is the environmental background.
- Surface is the principal ledger and navigation plane.
- Surface subtle identifies table headers, quiet groups, and hover state.
- Hairlines create most hierarchy.
- Shadows separate only major floating or white surfaces from Canvas.
- Do not build pages from a uniform grid of equally weighted analytics cards.

Radii:

- 7px controls.
- 9px compact containers.
- 12px callouts and secondary panels.
- 16px primary ledger.
- Pill radius only for binary/scope selectors and status tags.

## 7. Typography and data

- Product UI family: Inter; self-host the official `InterVariable.woff2` upright variable font (100–900) under SIL OFL 1.1.
- Allowed product weights: 400 Regular, 500 Medium, 600 SemiBold, and 700 Bold.
- Canonical sans stack: `"InterVariable", "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- Canonical technical stack: `ui-monospace, "SFMono-Regular", "Cascadia Mono", Menlo, Consolas, "Liberation Mono", monospace`.
- Font source, license links, logo-construction font identity, and pinned checksum are recorded in `assets/brand/FONT_PROVENANCE.md`.
- Use sentence case for headings and controls.
- Use uppercase tracked eyebrows sparingly.
- Use Inter tabular figures for comparable token totals, money, percentages, dates, and movement. Reserve the technical monospace stack for dense-table ranks, model identifiers, and code-like values whose identity benefits from fixed-width glyphs. Identity and summary surfaces keep rank and model values in Inter so they read as product status rather than terminal output.
- Align comparable numbers on the decimal or right edge.
- Use abbreviated values in dense views and expose exact values on focus, hover, or detail.
- Do not animate counters continuously.

## 8. Component grammar

### Ledger row

Required priority order:

1. Rank.
2. Builder/group identity.
3. Movement.
4. Evidence.
5. Selected burn metric.
6. Presence or secondary detail.

Movement includes direction plus a number or plain-language description. Color is secondary.

### Scope and period controls

- Broad scope selection may use solid Ink pills.
- Period and metric selection inside a surface uses Indigo Soft with Indigo Dark text.
- Controls retain visible text; unfamiliar icon-only filters are prohibited.

### Evidence

- `Hardened`: indigo shield and label.
- `Standard`: neutral label.
- `Imported`: visually quiet and explicitly outside active competition.
- Evidence explanations must be accessible without leaving the current task.

### Presence

Presence may reveal the active agent family, such as `Active in Codex`. It never reveals prompts, tasks, files, paths, projects, or repository names.

### Notifications

Notifications emphasize the event and its competitive consequence:

- `You were overtaken.`
- `You moved to #184.`
- `A rival is 240K ahead.`

They do not expose private work context.

### Empty and unavailable states

Every component must account for loading, empty, error, offline, private, restricted, quarantined, deleted, unsupported, and imported-only states. A polished happy path is not a complete component.

## 9. Iconography

- 1.5–1.8px outline icons with round caps and joins.
- Filled icons are reserved for selected or high-emphasis state.
- Icons support labels; they do not replace unfamiliar language.
- Do not mix system icons with illustrative 3D icons.

## 10. Motion

- Default duration: 160ms.
- Fast feedback: 120ms.
- Use ease-out timing.
- Motion may communicate rank change, new entries, overtakes, and disclosure.
- Avoid bouncing values, slot-machine counters, ambient pulsing, and routine confetti.
- `prefers-reduced-motion` receives a static, functionally equivalent state.

## 11. Accessibility

- Meet WCAG 2.2 AA as the minimum.
- Visible 2px Indigo focus ring with offset.
- Logical keyboard order matches visual order.
- Interactive targets are at least 36px in dense desktop contexts and 44px on touch.
- Test 200% zoom, screen readers, forced colors, reduced motion, and keyboard-only navigation.
- Do not hide focus or use hover as the only route to essential information.

## 12. Performance

- Server-render the initial leaderboard shell and meaningful content where architecture permits.
- Avoid layout shift in ranks, avatars, and numeric columns.
- Use vector brand assets and appropriately sized raster fallbacks.
- Virtualize only when row count and measured device performance require it; pagination remains the default public-ledger pattern.
- Motion and presence updates must not cause full-table reflow.

## 13. Mock-up and implementation workflow

Page design proceeds through visible review:

1. Define the exact route, data, states, and decisions the screen must support.
2. Produce two or more visually distinct mock-ups where a meaningful design choice exists.
3. Show desktop and mobile compositions.
4. Review hierarchy, density, branding, copy, privacy, and accessibility with the project owner.
5. Refine the selected mock-up.
6. Implement only after explicit visual approval.
7. Validate against the mock-up at target viewport sizes before merge.

The approved first-screen composition is recorded in `LEADERBOARD_FIRST_BASELINE.md`. Its general direction and implementation measurements are canonical; it is not yet a production component API or application route. The earlier bento Storybook prototype is superseded history.

## 14. Screen composition grammar

Merged from `design.md`. This section constrains how approved screens are composed. It does not define product behavior, entitlements, or data semantics — those belong to `docs/product/PRODUCT_SPEC.md` and `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`.

### 14.1 Composition rules

- Treat the desktop product as one continuous composition, not a grid of dashboard cards.
- Reserve bordered containers for genuinely independent objects: dialogs, notifications, the compact social rail, isolated controls.
- The leaderboard is the dominant object; the social rail is secondary and collapsible.
- The first screen must immediately answer: who is winning, by how much, where am I, and what changed.
- Remove decorative analytics that do not support a clear user question.
- Avoid a generic hero-plus-card-grid SaaS composition.
- Prefer open sections, hairline dividers, direct label-and-value pairs, full-width visualizations, and compact contextual rails over repeated statistic cards, analytics tiles, and nested bordered panels.
- Light is the launch theme, with indigo as a scarce signal. No dark theme is approved.
- The intended qualities — not the exact layouts — are those of a highly polished technical product surface: quiet hierarchy, tight information architecture, strong typographic rhythm, minimal chrome, precise alignment, restrained motion, considered exceptional states, and keyboard-friendly controls.
- Before approving a screen, remove at least one unnecessary visual element and confirm the screen becomes clearer rather than emptier.

### 14.2 Global navigation

A quiet top navigation carrying: Rankings, Friends, Boards, Search, Notifications, Profile.

### 14.3 Ranking controls

- Period: Today, Week, Month, Season, Year, All time.
- Scope: Global, Friends, Private boards, Organizations, Countries. Country scope is post-launch and must not appear as a launch-ready surface.
- Metric: Token Burn, Estimated Cash Burn.

These controls appear once per screen. Do not duplicate them in multiple locations.

### 14.4 Leaderboard header

Establishes, in one region: scope and period, total network Token Burn, estimated network Cash Burn, live participant count, the current user's rank, and the metric sort.

### 14.5 Leaderboard table

Functional column reference: Rank, User, Tokens Burned, Estimated Cash Burn, Models, Agents, Country, Streak, Movement.

- Right-align numeric values and use tabular figures.
- Make rank numerals typographically prominent; give rows generous vertical room.
- Distinguish the top three subtly. No metallic badges or medals.
- Reduce the visual weight of flags, model marks, and agent counts.
- Pin and emphasize the current user's row.
- Show movement as `↑ 4`, `↓ 2`, `NEW`, or `—`.
- Show live state only during an active qualifying agent session.
- Put secondary identity detail beneath the username rather than adding columns: `Active in Codex`, `12-day streak`, `Just overtook a friend`.

### 14.6 Social rail

Collapsible, never a permanent dashboard sidebar.

- Collapsed: friend avatars, active indicators, one meaningful event, overtake alert.
- Expanded: friend activity, requests, rival comparisons, active sessions.

It never exposes project names, files, paths, or transcript-derived detail.

### 14.7 Profile

Opens with identity and competitive position: username, handle, country, active agent state, global rank, Token Burn, Estimated Cash Burn, streak, agents used.

Tabs: Overview, History, Agents, Models, Boards.

Content: one full-width burn timeline, rank history, agent distribution, model distribution, records, streaks, recent milestones. Not four identical statistic cards.

Independently hideable by the user: Estimated Cash Burn, model breakdown, agent breakdown, activity history, presence, friend list, country, board participation. Private boards may expose exact burn, rank only, relative comparison, agent mix, or presence.

### 14.8 Presence

Extends §8. Presence is active only while a qualifying agent session is active. States: Active, Idle, Offline, Private. Example copy: `Vedant is active in Codex`, `Arham just overtook you`, `Riya entered the weekly top 10`. The privacy limits in §8 apply unchanged.

### 14.9 Privacy and integrity surface

- The word `verified` is banned from user-facing copy. Use Standard, Hardened, and Imported, and explain them plainly in place.
- The strongest permitted user-facing statement is: *The process that can read your transcripts cannot access the internet. The process that accesses the internet cannot read your transcripts.*
- Privacy reads as a product property, not compliance copy.

### 14.10 Mobile

Extends the mobile layout rules in §4, which own gutters and touch targets. Mobile is recomposed, not compressed: a dedicated leaderboard row layout, a sticky period and metric switcher, the current-user position always reachable, the social rail as a bottom sheet, large burn values still legible, secondary columns inside expandable rows, and full keyboard and screen-reader support.

### 14.11 Social competition, held back

Steam-like mechanics are integrated with restraint: friends currently in an agent session, overtake notifications, weekly rank changes, friend comparison, private boards, and organization boards. Country boards are post-launch. Competition emerges from data, movement, presence, and rivalry — never from a gaming dashboard, flashy decoration, or manufactured hype.

### 14.12 Charts

Charts answer a question or do not ship. Preferred: stepped burn timeline, rank-history line, agent/model horizontal distribution bars, daily activity heat strip, overtake and personal-record annotations. No donut charts on the leaderboard, and no generic dashboard filler.

## 15. Quality bar

Merged from `design.md`. A screen is not finished until all of these hold:

1. Consistent tabular alignment.
2. Designed empty states.
3. Long-name and huge-number handling.
4. Responsive behavior at 320px, 768px, 1280px, and ultrawide.
5. Hover, focus, loading, offline, error, private, and hidden states.
6. Non-color status indicators.
7. Visible keyboard focus.
8. Geometry-matched skeletons.
9. Normalized provider and tool marks.
10. Consistent copy voice.
11. Locale-aware dates, numbers, and currencies.
12. Contextual privacy explanations.
13. The current user is always easy to find.
14. Mobile recomposition.
15. No decorative filler sections, visible TODOs, dead buttons, or fake interactions.

Reject or revise any output containing excessive rounded cards, generic donut charts, default framework appearance, unnecessary gradients, glassmorphism, empty marketing slogans, random metric tiles, inconsistent spacing, overused pills, fake metallic rank badges, oversaturated accent usage, weak hierarchy, repeated component templates, placeholder copy, or decorative sections without product value.

## 16. Design review checklist

Merged from `design.md`. Before approving a screen:

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

## 17. Superseded values recorded from `design.md`

`design.md` was an earlier draft of this document and of `BRAND.md`. Its narrative content is merged above. Its numeric and identity claims **disagree** with the approved system, and both claims are recorded here rather than one being silently dropped. **The approved column governs.** Nothing may cite the `design.md` column as authority.

| Concern | Approved (`BRAND.md` / this file) | `design.md` draft claim |
|---|---|---|
| Page background | Canvas `#F4F2ED` | `#F7F7F5` |
| Primary text | Ink `#171714` | `#111113` |
| Secondary text | Muted `#716F68` | `#6B6B73` |
| Hairline | `#DEDAD1` | `#E7E7E4` |
| Accent indigo | Electric indigo `#5847E8` | `#5856E8` |
| Indigo secondary | Indigo dark `#4636C9` (accessible text) | `#4947D6` (hover) |
| Indigo soft | `#EFEDFF` | `#F0EFFF` |
| Positive | `#18794E` | `#14804A` |
| Warning | `#96651B` | `#A56400` |
| Negative / critical | Negative `#B84B44` | Critical `#C9362B` |
| Radii | 7px controls, 9px compact, 12px callouts, 16px primary ledger (§6) | main 6–10px, button 7–8px |
| Largest type | Display 40–48px | network total 64–80px, profile burn 40–48px |
| Motion | 160ms default, 120ms fast feedback (§10) | 180–240ms row movement |
| Product typeface | Inter only, self-hosted `InterVariable.woff2` | "Inter, Geist, or Instrument Sans" |
| Logo direction | Approved Ledger Wordmark; a crossed `x`, letter manipulation, and standalone symbols are explicit misuse | "explore a custom `x`, crossing signals, overtaking motif" |
| Cash metric name | Estimated Cash Burn, always labelled estimated | "Cash Burn" |

The `design.md` palette and radii were never adopted by `packages/ui/src/tokens.source.json`; the approved values are the ones that exist in code. The `design.md` logo exploration predates owner approval of the Ledger Wordmark and is rejected exploration, not an open option.
