# VibeMaxxing Style Guide

Status: governing structure approved; Leaderboard First direction and implementation specification approved

This directory is the entry point for every product-UI decision. It exists to keep human-written and AI-generated interfaces on the same system instead of allowing each page to invent its own controls, spacing, colors, and interaction patterns.

This file is navigation and process only. It states where each decision lives and the order in which work happens; it does not itself define brand values, layout rules, layer boundaries, or component contracts.

## Source-of-truth map

| Concern | Canonical source |
|---|---|
| Brand identity, logo, palette, voice | `BRAND.md` |
| Product layout, interaction, and screen-composition foundations | `UI_FOUNDATIONS.md` |
| Font provenance and licensing | `assets/brand/FONT_PROVENANCE.md` |
| Machine-readable CSS and TypeScript tokens | `packages/ui/src/` |
| Isolated component states, controls, and accessibility checks | `packages/ui/.storybook/` and `*.stories.tsx` |
| System layers, dependency direction, ownership, and documentation architecture | `UI_ARCHITECTURE.md` |
| Definition of a reusable component and its required contract | `COMPONENT_STANDARD.md` |
| AI/vibe-coding rules | `AI_UI_RULES.md` |
| What exists, at which lifecycle stage, with which usage contract | `COMPONENT_INVENTORY.md` |
| Governed asset resolution | `ASSET_SYSTEM.md` |
| Curated brand and product-system reference | `/style-guide` |
| Research and source rationale | `RESEARCH.md` |
| Current gaps and migration sequence | `MIGRATION.md` |
| Approved first-screen direction and execution specification | `LEADERBOARD_FIRST_BASELINE.md` |
| Superseded Storybook prototype history | `LEADERBOARD_BENTO_BASELINE.md` |

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

## Enforcement

A change that adds a public component without a story fails `npm run ui:check`. Removing either documentation surface — Storybook or `/style-guide` — also fails the check. The three non-interchangeable documentation layers and the system-layer table are defined in `UI_ARCHITECTURE.md`.

## Change rule

A design-system change updates its implementation, documentation, Storybook stories, tests, inventory entry, and the curated `/style-guide` when the change affects brand guidance. A page-level exception must be documented with an owner and removal condition; “the mock-up was slightly different” is not sufficient.
