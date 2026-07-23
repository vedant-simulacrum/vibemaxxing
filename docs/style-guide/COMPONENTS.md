# Implemented Components

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
| `MetricValue` | Token Burn or Estimated Cash Burn is displayed | Unrelated currency or generic metrics are shown | Metric-specific formatting and explicit estimated label |
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

## Shared state coverage

Storybook renders default, selected, disabled, positive, negative, neutral, Hardened, Standard, Imported, present, absent, token, cash, zero, complete, long-content, and ledger states. The product catalogue also executes loading, empty, error, offline, stale, private, blocked, restricted, and quarantined states.

Every approved product screen has desktop and mobile stories, with a shared 1024px tablet contract. CI captures all three breakpoints and compares the desktop output with the governed committed render baseline.
