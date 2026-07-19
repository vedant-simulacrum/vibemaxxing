# Component Inventory

This file is the human-readable registry for the UI system. It distinguishes current implementation from future intent so that coding agents do not hallucinate available components.

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
| Primitive | Button | Proposed | Actions and action links with semantic emphasis |
| Primitive | IconButton | Implemented | Familiar icon-only actions with accessible names |
| Primitive | Text | Proposed | Approved typography roles and truncation |
| Primitive | Icon | Implemented | One stroke system and accessible treatment |
| Primitive | Stack / Inline | Proposed | Token-bound layout composition |
| Component | ChoiceGroup | Implemented | Scope, period, and metric selection for finite single choice |
| Component | Avatar | Implemented | Builder and group identity fallback |
| Component | EvidenceBadge | Implemented | Hardened, Standard, and Imported evidence labels |
| Component | Progress | Implemented | Rank progress and bounded quantitative status |
| Component | Notice | Proposed | Informational, warning, error, and privacy messages |
| Component | Dialog | Proposed | Focus-managed modal tasks |
| Product pattern | RankMovement | Implemented | Direction, magnitude, label, and non-color meaning |
| Product pattern | PresenceIndicator | Implemented | Privacy-safe active-agent presence |
| Product pattern | LedgerRow | Implemented | Responsive leaderboard record hierarchy |
| Product pattern | MetricValue | Implemented | Token and estimated-cash formatting with exact-value access |
| Template | LeaderboardShell | Proposed | Ledger-first page structure and contextual rail |

## Approved fidelity prototypes

| Screen | Status | Executable reference | Boundary |
|---|---|---|---|
| Leaderboard First baseline | Approved-design | `docs/style-guide/references/leaderboard-first-approved.png` and `LEADERBOARD_FIRST_BASELINE.md` | General direction and measured specification approved; final responsive mock-up review required before production extraction |
| Leaderboard bento prototype | Deprecated | `packages/ui/src/concepts/leaderboard-bento.stories.tsx` | Superseded fixture-only prototype; must not drive new implementation |

The earlier Competition Slice directions are rejected exploration artifacts and are not approved sources for product implementation.

The current reference page consumes the implemented entries from `@vibemaxxing/ui`. Remaining proposed entries are not available for reuse and must not be invented locally.

## Updating the inventory

An entry changes status only when its lifecycle requirements are actually satisfied. When implementation begins, add its import path, owner, story location, and replacement information where relevant.
