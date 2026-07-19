# Competitive Ledger UI Foundations

Status: approved foundations; Leaderboard First baseline approved for final reference review

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

The governing reuse architecture, component contract, inventory, and AI-authoring rules live in `docs/style-guide/`. That directory is the required entry point before any component or page implementation.

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

The approved first-screen composition is recorded in `docs/style-guide/LEADERBOARD_FIRST_BASELINE.md`. Its general direction and implementation measurements are canonical; it is not yet a production component API or application route. The earlier bento Storybook prototype is superseded history.
