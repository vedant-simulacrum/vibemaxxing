# Implemented Components

The executable examples live at `/style-guide`. Public components are exported from `@vibemaxxing/ui`.

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

## Shared state coverage

The catalogue renders default, selected, disabled, positive, negative, neutral, Hardened, Standard, Imported, present, absent, token, cash, and responsive ledger states. Loading, empty, error, offline, restricted, and quarantined states remain pattern-level work because the current reference page does not yet implement those product states.
