# Decision-to-implementation traceability

Updated: 2026-07-23
Status: normative planning traceability; implementation remains unauthorized

A decision is technically covered only when it has a normative owner, implementation work unit, machine or state ownership where applicable, platform behavior, and executable acceptance evidence.

The complete matrix is split only to keep repository writes reliable:

- `D-001-D-020.md`
- `D-021-D-040.md`
- `D-041-D-061.md`
- `D-062-D-069.md`
- `D-070-D-099.md`
- `D-100-D-199.md`
- `D-200-D-299.md`
- `D-300-D-399.md`
- `D-400-D-499.md`
- `D-500-D-599.md`
- `D-600-D-699.md`

Each decision appears exactly once. Superseded decisions must have no active implementation path. Accepted decisions are directions, not proof that software exists or works. Provisional and research-required decisions cannot support production claims until their evidence gates close.

The shards are generated from `conformance/planning/decision-traceability-v1.json` by `scripts/repository/generate_planning_docs.py`; editing a table by hand fails the drift check. That JSON is the second matrix PF-063 called for: P-1140E froze structural traceability at D-001..D-069, and widening `range(1, 70)` would make a closed program's evidence set mutable, so coverage of the whole register is owned by the P-1140F track instead.

`validate_planning_artifacts.py` now fails when a decision has no row, when a row names a decision the register does not hold, when an implementation-bearing row leaves any of the five cells empty, and when two live decisions carry the same text. That last check exists because the register held fifteen byte-identical pairs — D-320 through D-334 repeating D-380 through D-394 — with no `supersedes` marker on either copy.

A row that is not implementation-bearing still appears, carrying the reason. Leaving it out would make coverage unreadable: an absent row and a deliberately excluded one would look the same, and only one of them is a defect. An implementation-bearing decision that no work unit owns records `unassigned` with an `owner_gap_reason`, so the gap is counted rather than filled with a plausible name.

The validator must also fail if Android, iOS, iPadOS or ChromeOS native work appears without a new accepted decision superseding D-066.