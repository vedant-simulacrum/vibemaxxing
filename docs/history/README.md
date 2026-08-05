# Planning history

Point-in-time reports that are no longer authority. They are retained because the repository's own discipline requires that superseded conclusions stay visible rather than disappear — several of these documents record claims that were later retracted, and that record is the evidence trail for why the current contracts read as they do.

**Nothing in this directory is normative.** Do not cite it to justify a decision, close a finding, or establish state. Current authority lives in:

- `docs/project/STATUS.md` — phase and permitted work
- `docs/project/DOCUMENTATION.md` — the single normative-owner map
- `docs/planning/DECISION_REGISTER.md` — decisions D-001..D-077
- `docs/planning/TASK_CATALOG.md` — gates and programs
- `conformance/p1140f/*.json` — machine-readable semantic state

## Contents

| File | What it was | Why it is here |
|---|---|---|
| `FINAL_PLANNING_EXIT_AUDIT.md` | Declared planning complete | Explicitly superseded by D-042; the PASS verdict was retracted |
| `PLANNING_HARDENING_VALIDATION_REPORT.md` | Validation of the hardening pass | Self-declared historical evidence, superseded as current authority |
| `PLANNING_HARDENING_REPAIR_REPORT.md` | Repairs from the same pass | Spent; its open items were absorbed into the P-1140 programs |
| `TRACEABILITY_AND_DRY_RUN_AUDIT.md` | Claimed complete traceability coverage | Self-declared historical; the coverage conclusion is void |
| `T20_PLANNING_COMPLETION_REPORT.md` | Declared the T20 cohort planned | Self-declared historical; D-046 is provisional and the registry has zero slots |
| `MOCK_IMPLEMENTATION_HANDOFF_REVIEW.md` | Review of the handoff draft | Point-in-time, 2026-07-19 |
| `CONSOLIDATED_AUDIT_2026-07-23.md` | First repository-wide audit | Superseded by `REPOSITORY_ALIGNMENT_2026-07-23.md`, then by P-1140E and P-1140F |
| `LAUNCH_POLICY_DECISIONS_2026-07-23.md` | Launch policy decisions | Fully absorbed into `DECISION_REGISTER.md` |
| `INDEPENDENT_ARCHITECTURE_REVIEWS.md` | One-off architecture review record | Point-in-time, 2026-07-19; formerly the sole file in `docs/reviews/` |
| `REPOSITORY_ALIGNMENT_2026-07-23.md` | Canonical P-1140A authority alignment audit and reconciliation record | Spent: P-1140A–E are all `complete-planning`; its decisions are owned by `DECISION_REGISTER.md` and its gates by `TASK_CATALOG.md`. Its canonical authority hierarchy was merged into `docs/project/DOCUMENTATION.md` before the move |
| `MACHINE_CONTRACT_REPAIR_SPEC.md` | Normative P-1140B–E machine-contract repair requirements | Spent: its exit condition was reached; the repaired contracts live in `packages/schemas/` and are indexed by `SCHEMA_AND_INTERFACE_INVENTORY.md` |

The first nine had zero inbound references from any document, script, workflow, or registry when they were moved here on 2026-08-05.

The last two were moved on 2026-08-06 and, unlike the first nine, did have live inbound references. Those references — the `AGENTS.md` initialization order, the `docs/project/DOCUMENTATION.md` initialization order and file map, and `TRACEABILITY_AND_DRY_RUN_AUDIT.md` — were repaired in the same change. Neither file is referenced by any script, workflow, or machine registry.

## Related historical material kept in place

`docs/research/` holds dated research waves that its own `README.md` already classifies as historical evidence, partially superseded. They stay where they are because `AGENTS.md` directs agents to `docs/research/README.md` to locate primary evidence for an active decision.
