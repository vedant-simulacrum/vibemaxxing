# Metrics Specification

## Consumer-facing model

Expose two first-class metrics only:

1. Token Burn
2. Cash Burn

Avoid confusing users with multiple overlapping headline scores in V1.

## Internal accounting

Internally retain:

- Source-reported token categories
- Canonically measured visible activity
- Capture method
- Environment strength
- Duplicate/replay state
- Continuity state
- SLM risk result

These internal factors determine whether activity is accepted, provisional, imported, or quarantined. They should not become a mysterious public score.

## Genuine usage policy

Genuine model activity counts even when:

- It is repetitive
- It is inefficient
- It is wasteful
- It was run primarily to climb the leaderboard
- It uses large context windows
- It uses many subagents

Cheating is evidence falsification, not wastefulness.

## Cash pricing

- Maintain versioned pricing by provider, model, and effective date.
- Calculate current API-equivalent value.
- Clearly label estimates.
- Preserve the pricing version used for historical calculations.
- Recalculation policy must be explicit: either freeze historical values or show both then-current and current-equivalent estimates.

## Unknown and local models

- Token Burn may still count.
- Cash Burn is `—`, `Local compute`, or an explicitly optional local estimate.
- Do not treat missing cash data as zero spend.
