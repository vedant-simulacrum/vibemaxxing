# @vibemaxxing/ui

Shared product foundations for the Competitive Ledger interface and the only canonical home for reusable product UI.

This package owns the canonical design tokens and reusable interface components. Components are added only after their visual states are reviewed and approved.

## Imports

```css
@import "@vibemaxxing/ui/tokens.css";
```

```ts
import { tokens } from "@vibemaxxing/ui/tokens";
```

Canonical product behavior and composition rules live in `docs/design/UI_FOUNDATIONS.md`.

## Component development

Storybook is the required isolated component catalogue:

```sh
npm run storybook
npm run storybook:build
```

Every public component must have meaningful stories before product use. The application `/style-guide` route is the curated brand reference; it imports these same components and does not replace Storybook.

The approved fixture-only leaderboard recreation lives under `Approved baseline/Leaderboard bento` in Storybook. Its exact visual and extraction contract is documented in `docs/style-guide/LEADERBOARD_BENTO_BASELINE.md`. It is a fidelity prototype, not an application route or stable public API.

The governing style-guide entry point is `docs/style-guide/README.md`. Its architecture, component standard, inventory, and AI-authoring rules must be read before adding UI. Application routes compose this package; they do not recreate its components locally.

`src/tokens.source.json` is canonical. Run `npm run tokens:generate` after changing it and `npm run tokens:check` in validation. Never edit `tokens.css` or `tokens.ts` directly.
