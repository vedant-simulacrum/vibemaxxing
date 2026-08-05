# UI System Architecture

Renamed from `docs/style-guide/ARCHITECTURE.md` on 2026-08-06 so it can no longer be confused with `docs/architecture/ARCHITECTURE.md`, which covers the system architecture of the product and has nothing to do with the UI layer model.

This file owns the UI system's layer model, dependency direction, ownership boundary, and documentation architecture.

## System layers

| Layer | Examples | Owned by |
|---|---|---|
| Tokens | color, type, spacing, radius, motion | `packages/ui/src/tokens.source.json` |
| Primitives | Button, Link, Text, Icon, Stack | `packages/ui/src/primitives/` |
| Components | Tabs, Avatar, StatusTag, Dialog | `packages/ui/src/components/` |
| Product patterns | LedgerRow, RankMovement, EvidenceBadge | `packages/ui/src/patterns/` |
| Templates | LeaderboardShell, ProfileShell | `packages/ui/src/templates/` |
| Pages | route data and composition only | `apps/*` |

Folders for unapproved component layers are created when the first approved implementation enters them. Empty folders are not used as evidence of implementation. Which named components currently occupy each layer is recorded in `COMPONENT_INVENTORY.md`, not here.

## One-way dependency rule

Dependencies flow downward:

`page → template → pattern → component → primitive → token`

Lower layers never import higher layers. Applications may import public exports from `@vibemaxxing/ui`; they must not reach into internal package paths.

## Ownership boundary

`packages/ui` owns reusable presentation, interaction behavior, accessibility semantics, variants, and styling. Application routes own data loading, authorization, routing, analytics wiring, and page composition.

If the same visual/behavioral unit appears twice—or is expected to appear twice—it belongs in `packages/ui`. A one-off may remain local only when its semantics are page-specific and extraction would create a misleading generic API.

## Composition model

The system follows the same scalable progression used by visual builders:

- **Variables/tokens** hold reusable values.
- **Components** hold reusable structure and behavior.
- **Properties/props** expose controlled content and state.
- **Slots/children** allow bounded composition without duplicating markup.
- **Variants** represent a small, named set of legitimate appearances.
- **Templates** assemble stable page structure without owning route data.

Prefer composition to large boolean-prop matrices. `Card tone="warning"` is understandable; a component with unrelated `compact`, `dark`, `centered`, `borderless`, `marketing`, and `leaderboard` switches is several components hiding behind one name.

## Token architecture

Use three levels:

1. **Reference tokens**: literal brand values such as Indigo 500.
2. **Semantic tokens**: purpose such as `text.primary`, `border.default`, or `status.positive`.
3. **Component tokens**: exceptional values scoped to one component, defined by aliasing semantic tokens.

Components consume semantic tokens. Raw hex, arbitrary shadows, one-off radii, and unexplained spacing values are prohibited in component and page CSS. Data-driven inline styles are allowed only for genuinely variable values such as progress width or position.

## Public API

Each reusable unit has one named export from `@vibemaxxing/ui`. Consumers import from the package root or an explicitly documented subpath. Renaming or removing a public prop requires a migration note and a deprecation window unless the component has not shipped.

## State ownership

- Keep route/business state in the application.
- Keep local interaction state inside the component when it has no meaning outside the component.
- Support controlled state when applications must coordinate it.
- Do not add global context merely to avoid passing a small number of explicit props.
- Separate visual state from server state and permissions.

## Responsive behavior

Responsiveness is part of the component contract. Components define how their own content reflows; templates define page-level recomposition. Pages must not patch a shared component with route-specific media-query overrides.

## Documentation architecture

The UI system has three non-interchangeable layers, and none may substitute for another:

1. **`@vibemaxxing/ui` owns implementation.** Neither documentation surface holds a duplicate component implementation.
2. **Storybook owns isolated executable states**, controls, accessibility checks, and visual-regression baselines. Every public component has stories covering its meaningful variants, edge cases, responsive behavior, and interaction or accessibility states.
3. **`/style-guide` owns the curated brand and product-system narrative.** It explains the approved visual language and shows representative compositions using the same `@vibemaxxing/ui` exports.

Stories and `/style-guide` import the package public API. They never copy component markup or styling. A component is not implemented until its required Storybook states exist; appearing on `/style-guide` alone is insufficient. `npm run ui:check` enforces both directions.
