# Current UI Audit and Migration

Status: audit of the current reference implementation; not approval to redesign the page

## Current strengths

- Brand and UI foundation documents exist.
- CSS and TypeScript foundation tokens exist in `@vibemaxxing/ui`.
- The current prototype already exposes repeated concepts such as icons, wordmark, ledger rows, tabs, avatars, evidence, presence, and metric values.
- Responsive and reduced-motion behavior has been considered.

## Current gaps

| Gap | Risk | Required correction |
|---|---|---|
| No dedicated style-guide directory before this change | Agents cannot discover one governing workflow | Use `docs/style-guide/README.md` as the entry point |
| Reusable UI lives in the page module | Other routes will copy or fork it | Extract only after approved component mock-ups |
| Many raw colors, sizes, shadows, and spacing values remain in page CSS | Near-duplicate visuals accumulate | Complete semantic tokens, then prohibit raw values |
| CSS and TypeScript tokens are separately handwritten | Values can drift | Introduce one canonical token source and generated outputs |
| No component stories or executable catalogue | States and variants remain implicit | Add Storybook with the first approved component set |
| No component behavior, accessibility, or visual regression gates | AI-generated changes can silently break shared UI | Add story-based testing and CI gates |
| No public component exports yet | Reuse cannot be enforced through package boundaries | Add exports as approved components are implemented |

## Safe migration sequence

1. Approve desktop and mobile mock-ups for the target page and its reusable elements.
2. Confirm the first component inventory and APIs from those mock-ups.
3. Introduce a canonical token file with reference and semantic aliases; generate CSS and TypeScript.
4. Install and configure the executable component catalogue.
5. Implement primitives first, then components, patterns, and templates.
6. Replace prototype-local implementations route by route without changing product behavior unintentionally.
7. Add CI gates for raw values, forbidden deep imports, stories, accessibility, behavior, and visual diffs.
8. Mark inventory entries stable only after reuse in more than one approved context.

## Enforcement backlog

The following controls are specified but not yet implemented:

- lint rule or style check rejecting unapproved raw visual values;
- package-boundary rule preventing application-local shared primitives;
- token generation and drift check;
- Storybook build and story coverage check;
- automated accessibility and interaction tests;
- approved visual-regression baseline;
- duplicate-component review in the pull-request template.

Keeping these items explicit prevents documentation from being mistaken for enforcement.
