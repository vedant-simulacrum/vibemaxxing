# VibeMaxxing Style Guide

Status: governing structure approved in principle; component visuals still require mock-up approval

This directory is the entry point for every product-UI decision. It exists to keep human-written and AI-generated interfaces on the same system instead of allowing each page to invent its own controls, spacing, colors, and interaction patterns.

## Source-of-truth map

| Concern | Canonical source |
|---|---|
| Brand identity, logo, palette, voice | `docs/design/BRAND.md` |
| Product layout and interaction foundations | `docs/design/UI_FOUNDATIONS.md` |
| Font provenance and licensing | `assets/brand/FONT_PROVENANCE.md` |
| Machine-readable CSS and TypeScript tokens | `packages/ui/src/` |
| Component ownership and composition | `ARCHITECTURE.md` |
| Definition of a reusable component | `COMPONENT_STANDARD.md` |
| AI/vibe-coding rules | `AI_UI_RULES.md` |
| Approved, proposed, and deprecated UI | `COMPONENT_INVENTORY.md` |
| Research and source rationale | `RESEARCH.md` |
| Current gaps and migration sequence | `MIGRATION.md` |

## Required order of work

Before writing UI code:

1. Search the component inventory and `packages/ui`.
2. Reuse an existing component unchanged when it represents the same job.
3. Add a documented variant or slot when the job is the same but the content or emphasis differs.
4. Compose existing components into a pattern or template when the job spans several components.
5. Propose a new component only when the semantics, behavior, or accessibility contract is genuinely different.
6. Show the rendered new component and its states for visual approval before treating it as canonical.

Pages consume the system. Pages do not become a second design system.

## System layers

| Layer | Examples | Owned by |
|---|---|---|
| Tokens | color, type, spacing, radius, motion | `packages/ui/src/tokens.*` |
| Primitives | Button, Link, Text, Icon, Stack | `packages/ui/src/primitives/` |
| Components | Tabs, Avatar, StatusTag, Dialog | `packages/ui/src/components/` |
| Product patterns | LedgerRow, RankMovement, EvidenceBadge | `packages/ui/src/patterns/` |
| Templates | LeaderboardShell, ProfileShell | `packages/ui/src/templates/` |
| Pages | route data and composition only | `apps/*` |

Folders for unapproved component layers are created when the first approved implementation enters them. Empty folders are not used as evidence of implementation.

## Change rule

A design-system change updates its implementation, documentation, stories, tests, inventory entry, and migration notes together. A page-level exception must be documented with an owner and removal condition; “the mock-up was slightly different” is not sufficient.
