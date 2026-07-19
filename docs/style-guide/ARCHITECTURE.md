# UI System Architecture

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
