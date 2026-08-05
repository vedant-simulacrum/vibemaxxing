# Component Standard

This file owns the rules a component must satisfy. It does not list components: the registry of what exists, at which lifecycle stage, with which usage contract, is owned by `COMPONENT_INVENTORY.md`.

## Admission test

A new reusable component is justified only when at least one is true:

- it owns a distinct semantic or accessibility role;
- it owns repeatable interaction behavior;
- it appears in multiple approved contexts;
- it is a product-domain pattern whose consistency affects comprehension or trust.

Visual similarity alone does not justify one component, and minor visual difference does not justify duplication.

## Required contract

Every implemented component documents:

| Field | Requirement |
|---|---|
| Purpose | One sentence describing the user job |
| Use when / do not use when | Prevents semantic misuse |
| Anatomy | Named internal parts and slots |
| Props | Typed, minimal, semantic API with defaults |
| Variants | Named, finite, and visually approved |
| States | Default, hover, focus, active, disabled, loading, empty, error as applicable |
| Content rules | Length, truncation, labels, numerals, localization |
| Responsive behavior | Reflow and minimum viable content |
| Accessibility | Element semantics, name, keyboard behavior, focus, announcements |
| Tests | Behavior plus applicable accessibility and visual coverage |
| Status | One lifecycle stage from `COMPONENT_INVENTORY.md`, recorded there rather than here |

## Component file contract

Larger components use this co-located shape when separate files improve ownership:

```text
ComponentName/
  ComponentName.tsx
  ComponentName.module.css
  ComponentName.stories.tsx
  ComponentName.test.tsx
  ComponentName.docs.mdx
  index.ts
```

Simple primitives may share a module while the library is small. Their public exports, usage contract, executable catalogue coverage, and tests remain mandatory. Product patterns should move to co-located folders as their fixtures or behavior grow.

## Story coverage

Storybook is the required executable component catalogue. Every public component has stories for meaningful variants and difficult states, including long text, zero and extreme values, keyboard focus, loading, error, reduced motion, narrow viewport, and high zoom where relevant. Stories use realistic fixtures without private data and import only the public `@vibemaxxing/ui` implementation.

The `/style-guide` route is a curated brand reference, not a substitute for isolated stories. It may show representative compositions but is not required to duplicate every engineering state.

## Accessibility baseline

- Start with the correct native HTML element.
- Follow WAI-ARIA Authoring Practices only when native semantics are insufficient.
- Keyboard behavior and visible focus are contractual, not optional polish.
- Color never carries meaning alone.
- Automated checks must fail CI for known violations; manual checks remain required for semantics and usability.

## Variant rules

- Name variants by purpose (`primary`, `quiet`, `danger`), not appearance (`purple`, `small-shadow`).
- Size variants are allowed only when target size and density requirements remain accessible.
- Prefer slots for structured content and props for state or short labels.
- Never expose raw CSS values as props.
- Do not add a variant to reproduce a single screenshot without a recurring semantic need.

## Deprecation

Deprecated components remain documented with their replacement and migration path. New use is blocked before the old export is removed.
