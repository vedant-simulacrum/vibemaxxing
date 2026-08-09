# Component Inventory

This file is the single registry for the UI system: what exists, what is only proposed, and how each implemented component may be used. It distinguishes current implementation from future intent so that coding agents do not hallucinate available components.

It absorbed the former `COMPONENTS.md` on 2026-08-06. The rules a component must satisfy to enter this registry are owned separately by `COMPONENT_STANDARD.md`; the layer model and dependency direction are owned by `UI_ARCHITECTURE.md`. This file does not restate either.

## Lifecycle

`proposed → approved-design → implemented → stable → deprecated`

- **Proposed**: identified need; no approved API or visuals.
- **Approved-design**: rendered states and API reviewed; implementation allowed.
- **Implemented**: code, documentation, stories, and tests exist.
- **Stable**: used successfully across approved product contexts.
- **Deprecated**: retained temporarily with replacement guidance.

## Current inventory

| Layer | Canonical name | Status | Intended responsibility |
|---|---|---|---|
| Tokens | Brand and foundation tokens | Implemented | Color, typography, spacing, shape, elevation, layout, focus, motion |
| Primitive | Wordmark | Implemented | Product attribution and home navigation using the approved outlined mark |
| Primitive | Icon | Implemented | One stroke system and accessible treatment |
| Primitive | IconButton | Implemented | Familiar icon-only actions with accessible names |
| Primitive | ProductButton | Implemented | Neutral, primary, and danger product actions |
| Primitive | ProductIconButton | Implemented | Compact product actions with a required accessible label |
| Primitive | Text | Proposed | Approved typography roles and truncation |
| Primitive | Stack / Inline | Proposed | Token-bound layout composition |
| Component | ChoiceGroup | Implemented | Scope, period, and metric selection for finite single choice |
| Component | Avatar | Implemented | Builder and group identity fallback |
| Component | EvidenceBadge | Implemented | Hardened, Standard, and Imported evidence labels |
| Component | Progress | Implemented | Rank progress and bounded quantitative status |
| Component | ProviderLogo | Implemented | Governed local provider and model-family marks from `assets/providers` |
| Component | ProductPanel | Implemented | Canonical purpose-named product surface |
| Component | ProductTabs | Implemented | Local tab navigation with tab semantics |
| Component | ProductAvatar | Implemented | Governed people imagery and presence |
| Component | ProductModel | Implemented | Model identity composed with a governed provider mark |
| Component | ProductStateBoundary | Implemented | Loading, empty, error, offline, stale, privacy, restriction, and quarantine states |
| Component | ProductNotice | Implemented | Persistent informational, warning, and danger explanations in place |
| Component | ProductDialog | Implemented | Focus-managed modal tasks |
| Component | Notice | Proposed | Generic informational, warning, error, and privacy messages |
| Component | Dialog | Proposed | Generic focus-managed modal tasks |
| Product pattern | RankMovement | Implemented | Direction, magnitude, label, and non-color meaning |
| Product pattern | ProductMovement | Implemented | Rank movement on product screens, non-color-readable |
| Product pattern | PresenceIndicator | Implemented | Privacy-safe active-agent presence |
| Product pattern | MetricValue | Implemented | Token and estimated-cash formatting with exact-value access |
| Product pattern | LedgerRow | Implemented | Responsive leaderboard record hierarchy |
| Product pattern | ProductUserIdentity | Implemented | Name, handle, governed avatar, and presence as one hierarchy |
| Product pattern | ProductFriendRow | Implemented | Approved friends-table row composition |
| Product pattern | ProductBoardStandingRow | Implemented | Approved board-standings row composition |
| Product pattern | ProductActivityEventRow | Implemented | Typed competitive-event row rhythm |
| Product pattern | ProductTrendChart | Implemented | Credited Token Burn trend and rival comparison, with accessible summary |
| Product pattern | ProductSparkline | Implemented | Compact rival direction cue supplementing exact text |
| Product pattern | ProductRankChart | Implemented | Weekly rank movement summary |
| Template | ProductShell | Implemented | Shared product header, navigation, search, account trigger, and mobile navigation |

**Unresolved naming overlap, recorded rather than silently resolved.** `Notice` and `Dialog` remain proposed as generic components while `ProductNotice` and `ProductDialog` are implemented. The two registries merged into this file disagreed on whether these are one concept at two lifecycle stages or two distinct components. Until an owner decides, treat the `Product*` names as the only usable exports and do not implement the generic names as duplicates.

## Implemented component usage contracts

The executable state catalogue lives in Storybook under `packages/ui`; the curated brand reference lives at `/style-guide`. Both consume public components exported from `@vibemaxxing/ui`.

| Component | Use when | Do not use when | Contract highlights |
|---|---|---|---|
| `Wordmark` | Product attribution and home navigation | A compact app-icon context requires the `vm` mark | Uses approved outlined SVG; accessible home label |
| `Icon` | A familiar action or status needs visual support | The icon would replace unfamiliar language | Decorative SVG is hidden from assistive technology |
| `IconButton` | A familiar compact action has an accessible name | A text label would be clearer | Required label, focus, disabled, and expanded states |
| `ChoiceGroup` | A finite list selects exactly one scope or mode | Content is navigation between distinct tab panels | Typed values, visible selected state, `aria-pressed` |
| `Avatar` | Builder/group initials need a consistent fallback | A brand/app icon is required | Finite approved tints and stable dimensions |
| `RankMovement` | Rank direction and magnitude are shown | A generic percentage change is shown | Accessible direction, number, and neutral state |
| `EvidenceBadge` | Evidence level is Hardened, Standard, or Imported | General product status is shown | Text always carries meaning; shield supplements Hardened |
| `PresenceIndicator` | Privacy-safe active-agent presence is shown | Project, file, prompt, or task context would be exposed | Announces “Active in”; never accepts private context |
| `MetricValue` | Credited Token Burn, Token Burn on the participant's own surface, or Estimated Cash Burn is displayed | Unrelated currency or generic metrics are shown | Metric-specific formatting and explicit estimated label |
| `Progress` | A bounded value from 0–100 is meaningful | The value is indeterminate | Clamps input and exposes native progressbar values |
| `LedgerRow` | A public leaderboard record is displayed | A generic data table row is sufficient | Composes rank, identity, presence, evidence, metric, and action |
| `ProductShell` | A hosted product surface needs the canonical header and navigation | A standalone marketing or native surface is being composed | Owns wordmark, primary navigation, search, and account trigger |
| `ProductAvatar` | Governed people fixtures or future identity images are shown | Initial-only fallback is sufficient | Resolves only through `assetRegistry`; supports presence and accessible labels |
| `ProductButton` | A product action uses neutral, primary, or danger emphasis | An icon-only control is appropriate | One tone contract, native disabled behavior, stable dimensions |
| `ProductPanel` | A purpose-named product region needs the canonical surface treatment | A decorative generic card would be created | Semantic `section` with an optional accessible label |
| `ProductTabs` | Distinct panels share a local view switcher | A finite non-navigation choice is being made | Tablist/tab semantics and controlled selection |
| `ProductMovement` | Product screens show rank movement | A generic percentage change is shown | Direction and magnitude remain non-color-readable |
| `ProductModel` | A model name and governed provider mark appear together | Provider identity is unknown | Provider marks resolve only through `ProviderLogo` |
| `ProductStateBoundary` | A product surface is loading, empty, failed, offline, stale, private, blocked, restricted, or quarantined | The ready surface is shown | Shared copy, status semantics, privacy-safe explanations, and recovery actions |
| `ProductIconButton` | A compact product action has a familiar icon and accessible name | Visible text is clearer | Requires an accessible label and supports expanded/controls state |
| `ProductDialog` | Search, confirmation, or another blocking task needs modal focus | A route or inline panel is more appropriate | Modal semantics, focus containment, Escape dismissal |
| `ProductNotice` | A product state needs persistent contextual explanation | A blocking failure requires `ProductStateBoundary` | Info, warning, and danger tones retain visible text |
| `ProductUserIdentity` | Name, handle, governed avatar, and presence travel together | Only an avatar or fallback is needed | One identity hierarchy and governed fixture resolution |
| `ProductFriendRow` | Friends tables show the approved identity, presence, rank, burn, model, and actions | A generic person row is sufficient | Reuses identity, movement, model, and action contracts |
| `ProductBoardStandingRow` | Board standings show the approved member columns | A non-ranking membership list is shown | Current-user state and rank remain explicit |
| `ProductActivityEventRow` | Competitive events share the approved ledger rhythm | Arbitrary social feed content is shown | Typed title/detail/trailing structure and unread label |
| `ProductTrendChart` | Credited Token Burn trend or rival comparison is shown | Exact analytical inspection is required | Accessible summary; code-native data graphic |
| `ProductSparkline` | A compact rival direction cue supplements exact text | It would be the only data representation | Requires an accessible label |
| `ProductRankChart` | Weekly rank movement is summarized | Exact point inspection is required | Accessible summary and non-interactive SVG |

`ProviderLogo` is implemented but is consumed through `ProductModel` rather than placed directly, so it carries no independent placement contract.

## Shared state coverage

Storybook renders default, selected, disabled, positive, negative, neutral, Hardened, Standard, Imported, present, absent, token, cash, zero, complete, long-content, and ledger states. The product catalogue also executes loading, empty, error, offline, stale, private, blocked, restricted, and quarantined states.

Every approved product screen has explicit desktop, tablet, and mobile stories. The separate product-state matrix executes all nine exceptional states for all five approved screens. CI captures all three breakpoints, runs browser accessibility and keyboard checks, and compares captures with governed committed render baselines.

## Approved fidelity prototypes

| Screen | Status | Executable reference | Boundary |
|---|---|---|---|
| Leaderboard First baseline | Approved fidelity prototype | `packages/ui/src/concepts/leaderboard-first.tsx` and `references/leaderboard-first-approved.png` | Canonical desktop Storybook recreation; production extraction remains intentionally separate |
| Public profile, rival comparison, friends, activity, board standings | Implemented prototype | `packages/ui/src/concepts/product-storyboards.stories.tsx` | Shared product patterns, governed assets, responsive stories, difficult states, and visual baselines; non-production under P-1104 |
| Leaderboard bento prototype | Deprecated | `packages/ui/src/concepts/leaderboard-bento.stories.tsx` | Superseded fixture-only prototype; must not drive new implementation |

The earlier Competition Slice directions are rejected exploration artifacts and are not approved sources for product implementation.

The current reference page consumes the implemented entries from `@vibemaxxing/ui`. Remaining proposed entries are not available for reuse and must not be invented locally.

## Updating the inventory

An entry changes status only when the lifecycle requirements defined in `COMPONENT_STANDARD.md` are actually satisfied. When implementation begins, add its import path, owner, story location, and replacement information where relevant. A component that reaches `implemented` must appear in both tables above.
