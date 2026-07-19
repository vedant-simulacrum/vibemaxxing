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
| Primitive | IconButton | Proposed | Familiar icon-only actions with accessible names |
| Primitive | Text | Proposed | Approved typography roles and truncation |
| Primitive | Icon | Proposed | One stroke system and accessible treatment |
| Primitive | Stack / Inline | Proposed | Token-bound layout composition |
| Component | Tabs | Proposed | Scope, period, and metric selection where semantics match |
| Component | Avatar | Proposed | Builder and group identity fallback |
| Component | StatusTag | Proposed | Evidence and system state labels |
| Component | Progress | Proposed | Rank progress and bounded quantitative status |
| Component | Notice | Proposed | Informational, warning, error, and privacy messages |
| Component | Dialog | Proposed | Focus-managed modal tasks |
| Product pattern | RankMovement | Proposed | Direction, magnitude, label, and non-color meaning |
| Product pattern | EvidenceBadge | Proposed | Hardened, Standard, and Imported evidence |
| Product pattern | PresenceIndicator | Proposed | Privacy-safe active-agent presence |
| Product pattern | LedgerRow | Proposed | Responsive leaderboard record hierarchy |
| Product pattern | MetricValue | Proposed | Token and estimated-cash formatting with exact-value access |
| Template | LeaderboardShell | Proposed | Ledger-first page structure and contextual rail |

The current reference page contains local prototypes of several proposed entries. They are not canonical shared components. They must be reviewed through mock-ups, then extracted or replaced deliberately rather than copied into another route.

## Updating the inventory

An entry changes status only when its lifecycle requirements are actually satisfied. When implementation begins, add its import path, owner, story location, and replacement information where relevant.
