# AI UI Authoring Rules

These rules are written for coding agents and apply to every UI change.

## Before generating code

1. Read this directory, starting with `README.md`, `BRAND.md`, and `UI_FOUNDATIONS.md`.
2. Search `packages/ui`, its public exports, and `COMPONENT_INVENTORY.md` for an existing solution.
3. List the components, patterns, and tokens the proposed screen will reuse.
4. Identify any missing state or variant before proposing a new component.
5. Add or update Storybook stories for every affected public component.
6. Stop for visual approval when the work introduces or materially changes a component appearance or page composition.

## Generation constraints

- Import reusable UI from `@vibemaxxing/ui`.
- Do not recreate a shared component inside an application route.
- Do not duplicate JSX and CSS to move faster.
- Do not introduce raw colors, arbitrary spacing, shadows, radii, type sizes, or motion values.
- Do not use inline styles except for data-driven values that cannot be expressed as a finite variant.
- Do not create ambiguous catch-all components such as `Card`, `Box`, or `Widget` without a precise contract.
- Do not add a new icon style, state color, or responsive breakpoint locally.
- Do not treat a screenshot as the component API; infer the underlying reusable jobs and states.
- Do not claim a component exists because it is listed as proposed.
- Do not use `/style-guide` coverage as a substitute for isolated Storybook stories.
- Do not implement a second component inside a story or `/style-guide`; both must import the package public API.

## Reuse decision

Use this order:

1. Existing component with existing props.
2. Existing component composed differently through an approved slot.
3. Existing component with one semantic, backwards-compatible variant.
4. New product pattern composed from existing components.
5. New primitive or component only after the admission test and visual review.

If changing an existing component would add unrelated responsibilities, create a separate component instead.

## Completion checklist

A UI task is incomplete until:

- all reusable elements are in the shared package;
- the inventory reflects their real status;
- stories show required states and variants;
- behavior, accessibility, and visual tests pass;
- responsive behavior is verified at agreed viewports;
- no duplicated component implementation or raw token value was introduced;
- documentation describes when to use and when not to use the result.

## Review questions

Reviewers and agents ask:

- Did we search before creating?
- Is this a new user job or only a new visual arrangement?
- Could a prop or slot solve it without weakening the API?
- Is the shared component being patched by page CSS?
- Are all states represented, not only the happy path?
- Would changing one token or component update every instance consistently?
