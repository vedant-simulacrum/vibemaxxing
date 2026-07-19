# Research Basis

This system uses principles from official specifications and established design-system documentation. The sources inform the architecture; VibeMaxxing-specific decisions remain recorded in this repository.

## Findings and adopted decisions

### Interface polish comes from correct type roles, not a novelty font

Inter is designed for detailed user interfaces and provides optical sizing, contextual alternates, and tabular figures. The Leaderboard First baseline therefore keeps Inter Variable, enables its UI features, uses tabular Inter for comparable numeric columns, and limits monospace to ranks and model identifiers. This avoids turning the entire interface into a synthetic developer/editorial treatment.

Source: https://rsms.me/inter/

### Dense tables need an explicit typography and spacing contract

Carbon specifies 14px row and column-header typography for data tables and documents token-bound table spacing. VibeMaxxing adopts the same readable density class while locking its own row height, padding, column widths, alignment, and truncation order in the screen baseline.

Source: https://carbondesignsystem.com/components/data-table/style/

### A limited spacing rhythm is a quality control

Atlassian documents an 8px base unit and limited spacing scale as a foundation for consistent layouts and responsive behavior. VibeMaxxing retains a 4px sub-step for compact relationships but makes 8px the primary page-layout beat. Token-bound layout primitives keep those decisions reusable instead of allowing route-local padding drift.

Sources:

- https://atlassian.design/foundations/grid-beta/applying-grid
- https://atlassian.design/components/primitives/overview/

### Variables, components, and templates form a reusable ladder

Webflow describes scalable systems as variables, components, assets, and page templates, with component properties, slots, and variants providing controlled flexibility. VibeMaxxing adopts the same ladder in code: tokens, primitives, components, product patterns, templates, and pages.

Sources:

- https://webflow.com/webflow-way/design-systems
- https://webflow.com/webflow-way/design-systems/components
- https://help.webflow.com/hc/en-us/articles/41959932025235-Using-a-design-system-in-Webflow

### Tokens need a portable, machine-readable source

The Design Tokens Community Group specification defines an exchange format for reusable design decisions. VibeMaxxing will keep a canonical token source and generate platform outputs from it when the token pipeline is implemented; CSS and TypeScript must not drift as independent handwritten sources.

Source: https://www.designtokens.org/tr/2025.10/

### Components should be composed around data and user jobs

React recommends breaking interfaces into a component hierarchy, building reusable components, and passing data through explicit props. VibeMaxxing therefore separates reusable presentation and behavior from route data, and prefers composition over page-local duplication.

Sources:

- https://react.dev/learn/thinking-in-react
- https://react.dev/learn/passing-props-to-a-component

### The catalogue should be executable

Storybook treats a story as a captured component state and uses stories for documentation, interaction checks, accessibility checks, and visual comparison. VibeMaxxing uses Storybook as the mandatory isolated component catalogue. The `/style-guide` route remains a curated brand reference, and both surfaces consume the same shared implementation so screenshots or prose cannot silently become a parallel system.

Sources:

- https://storybook.js.org/docs/writing-docs
- https://storybook.js.org/docs/writing-tests
- https://storybook.js.org/docs/writing-tests/accessibility-testing
- https://storybook.js.org/docs/writing-tests/visual-testing

### Components need usage guidance, not only code

The GOV.UK Design System documents when to use and when not to use components, encourages reuse of established type and spacing scales, and treats styles, components, patterns, and templates as distinct layers. VibeMaxxing adopts the same requirement for purpose, non-use cases, content, accessibility, and responsive guidance.

Sources:

- https://design-system.service.gov.uk/
- https://design-system.service.gov.uk/styles/type-scale/
- https://design-system.service.gov.uk/styles/page-template/

## Vibe-coded project risks

The following risks are architectural inferences from the repository audit and the practices above:

- an agent optimizes for the current screenshot and invents near-duplicate controls;
- tokens exist but raw values remain easier to generate;
- component names are reused while their semantics and APIs drift;
- documentation lists components that were never implemented;
- only the happy path is generated because edge states are not catalogued;
- page CSS overrides shared components until reuse becomes nominal;
- a large “universal” component accumulates unrelated boolean props;
- visual consistency is reviewed manually but never regression-tested.

The inventory, admission test, one-way dependency rule, story contract, and automated gates directly address these failure modes.
