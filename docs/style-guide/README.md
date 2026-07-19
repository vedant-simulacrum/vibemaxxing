# VibeMaxxing Style Guide

Status: governing structure approved; leaderboard bento baseline approved for Storybook fidelity work

This directory is the entry point for every product-UI decision. It exists to keep human-written and AI-generated interfaces on the same system instead of allowing each page to invent its own controls, spacing, colors, and interaction patterns.

## Source-of-truth map

| Concern | Canonical source |
|---|---|
| Brand identity, logo, palette, voice | `docs/design/BRAND.md` |
| Product layout and interaction foundations | `docs/design/UI_FOUNDATIONS.md` |
| Font provenance and licensing | `assets/brand/FONT_PROVENANCE.md` |
| Machine-readable CSS and TypeScript tokens | `packages/ui/src/` |
| Isolated component states, controls, and accessibility checks | `packages/ui/.storybook/` and `*.stories.tsx` |
| Component ownership and composition | `ARCHITECTURE.md` |
| Definition of a reusable component | `COMPONENT_STANDARD.md` |
| AI/vibe-coding rules | `AI_UI_RULES.md` |
| Approved, proposed, and deprecated UI | `COMPONENT_INVENTORY.md` |
| Implemented component usage contracts | `COMPONENTS.md` |
| Curated brand and product-system reference | `/style-guide` |
| Research and source rationale | `RESEARCH.md` |
| Current gaps and migration sequence | `MIGRATION.md` |
| Approved first-screen baseline and execution specification | `LEADERBOARD_BENTO_BASELINE.md` |

## Required order of work

Before writing UI code:

1. Search the component inventory and `packages/ui`.
2. Reuse an existing component unchanged when it represents the same job.
3. Add a documented variant or slot when the job is the same but the content or emphasis differs.
4. Compose existing components into a pattern or template when the job spans several components.
5. Propose a new component only when the semantics, behavior, or accessibility contract is genuinely different.
6. Add or update its Storybook stories before using it in a product route.
7. Show the rendered Storybook states for visual approval before treating it as canonical.

Pages consume the system. Pages do not become a second design system.

## Documentation surfaces

Storybook and `/style-guide` are complementary and must never substitute for one another:

- **Storybook is the engineering source for executable component states.** Every public component has isolated stories covering its meaningful variants, edge cases, responsive behavior, and interaction or accessibility states.
- **`/style-guide` is the curated brand reference.** It explains the approved visual language and shows representative compositions using the same `@vibemaxxing/ui` exports.
- **`@vibemaxxing/ui` is the implementation source.** Neither documentation surface owns a duplicate component implementation.

A change that adds a public component without a story fails `npm run ui:check`. Removing either documentation surface also fails the check.

## System layers

| Layer | Examples | Owned by |
|---|---|---|
| Tokens | color, type, spacing, radius, motion | `packages/ui/src/tokens.source.json` |
| Primitives | Button, Link, Text, Icon, Stack | `packages/ui/src/primitives/` |
| Components | Tabs, Avatar, StatusTag, Dialog | `packages/ui/src/components/` |
| Product patterns | LedgerRow, RankMovement, EvidenceBadge | `packages/ui/src/patterns/` |
| Templates | LeaderboardShell, ProfileShell | `packages/ui/src/templates/` |
| Pages | route data and composition only | `apps/*` |

Folders for unapproved component layers are created when the first approved implementation enters them. Empty folders are not used as evidence of implementation.

## Change rule

A design-system change updates its implementation, documentation, Storybook stories, tests, inventory entry, and the curated `/style-guide` when the change affects brand guidance. A page-level exception must be documented with an owner and removal condition; “the mock-up was slightly different” is not sufficient.
