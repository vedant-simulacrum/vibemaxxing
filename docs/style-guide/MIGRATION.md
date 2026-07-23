# Current UI Audit and Migration

Status: first reference-page migration completed; not approval to redesign the page

## Current strengths

- Brand and UI foundation documents exist.
- CSS and TypeScript foundation tokens exist in `@vibemaxxing/ui`.
- The current prototype already exposes repeated concepts such as icons, wordmark, ledger rows, tabs, avatars, evidence, presence, and metric values.
- Responsive and reduced-motion behavior has been considered.

## Completed migration

| Previous gap | Completed correction |
|---|---|
| No governing style-guide directory | Added the required `docs/style-guide/` entry point and contracts |
| Reusable UI lived in the page module | Extracted implemented UI to public `@vibemaxxing/ui` exports |
| Raw component colors | Replaced with canonical UI tokens and added a rejecting check |
| Handwritten CSS and TypeScript token copies | Added one 83-token source and deterministic generator/check |
| No executable catalogue | Added mandatory Storybook stories and retained `/style-guide` as the curated brand reference |
| No reuse enforcement | Added checks for page-local recreations, inline styles, raw colors, stale tokens, and catalogue coverage |
| Live-text wordmark reconstruction | Replaced with the approved outlined SVG asset |
| `/style-guide` and Storybook responsibilities could drift | Made Storybook the required isolated catalogue, retained `/style-guide` as the curated brand reference, and added an automated parity gate |

## Migration performed

1. Preserved the current reference composition without a visual redesign.
2. Extracted its repeatable primitives, components, and product patterns.
3. Migrated the page to public package imports.
4. Centralized component CSS in the UI package.
5. Added canonical token generation, mandatory Storybook stories, and the curated `/style-guide` reference.
6. Added automated architectural and catalogue-parity checks and retained build/type/lint validation.

## Current enforcement

- Approved screens are composed as hosted application routes without changing their synthetic-fixture maturity.
- Shared screen-level rows, identity, charts, icon controls, notices, dialogs, shell, and exceptional states live in `@vibemaxxing/ui`.
- Browser checks exercise keyboard entry, search-dialog behavior, Escape dismissal, and WCAG A/AA rules.
- The state matrix covers all nine exceptional states on all five approved screens.
- The UI checker scans active application and UI source for raw colors, direct assets, direct Lucide imports, private component recreation, missing routes, missing states, and missing workflow gates.
- The pull-request template requires reuse, asset, responsive, state, accessibility, and baseline review.

AST-backed linting can replace focused repository checks when the implementation toolchain owns a canonical lint package. This is an enforcement-strength improvement, not a missing product behavior.
