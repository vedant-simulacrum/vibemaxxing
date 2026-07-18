# Research Basis

This system uses principles from official specifications and established design-system documentation. The sources inform the architecture; VibeMaxxing-specific decisions remain recorded in this repository.

## Findings and adopted decisions

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

Storybook treats a story as a captured component state and uses stories for documentation, interaction checks, accessibility checks, and visual comparison. VibeMaxxing will use stories as the component catalogue once component implementation is approved rather than maintaining screenshots or prose that can silently diverge from code.

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
