# @vibemaxxing/ui

Shared product foundations for the Competitive Ledger interface and the only canonical home for reusable product UI.

This package currently owns stable design tokens only. Components will be added after page-level mock-ups are visually reviewed and approved. This avoids prematurely encoding a component library around unapproved screens.

## Imports

```css
@import "@vibemaxxing/ui/tokens.css";
```

```ts
import { brand, layout, motion, radius, space } from "@vibemaxxing/ui/tokens";
```

Canonical product behavior and composition rules live in `docs/design/UI_FOUNDATIONS.md`.

The governing style-guide entry point is `docs/style-guide/README.md`. Its architecture, component standard, inventory, and AI-authoring rules must be read before adding UI. Application routes compose this package; they do not recreate its components locally.
