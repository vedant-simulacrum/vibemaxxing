# GitHub Issue Generation Contract

Status: planning contract
Updated: 2026-07-19

`docs/planning/TASK_CATALOG.md` remains the phase and planning authority. `PR_SIZED_WORK_BREAKDOWN.md` remains the implementation-unit authority. GitHub issues are execution threads generated from those sources; they do not redefine requirements.

## Generation behavior

`scripts/repository/generate_issue_plan.py` parses numbered work units from the PR-sized breakdown and emits deterministic JSON records. It does not create issues or require network access.

After implementation is explicitly authorized, an operator or approved automation may create missing issues from that plan. Before creation it must search existing open and closed issues for the stable work-unit key and avoid duplicates.

## Required issue body

Every generated issue contains:

- stable key `IMP-###`;
- exact work-unit text;
- owning phase and dependency keys;
- linked decisions and contracts, added during issue triage;
- exclusions;
- schema and migration impact;
- privacy and security impact;
- tests and acceptance evidence;
- rollback requirements;
- implementation status distinct from planning status.

## Labels

Initial labels are `implementation`, one component label, and `blocked` until dependencies and phase approval permit work. Labels and milestones are operational metadata, not product authority.

## Thread discipline

Durable decisions discovered in issues or pull requests must be merged into the decision register, ADRs, schemas, or normative contracts. Closing an issue does not override a contract, and a contract change does not silently close an issue.
