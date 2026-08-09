# GitHub Issue Generation Contract

Status: planning contract
Updated: 2026-08-09

`docs/planning/TASK_CATALOG.md` owns planning phases and gates. `PR_SIZED_WORK_BREAKDOWN.md` owns future implementation units. Generated issue plans and GitHub issues are non-authoritative execution metadata.

## Stable keys

Implementation issue keys are the stable work-unit headings already present in the work breakdown, in `<EPIC>-<NNN>` form — `PF-001`, `F-001`, `N-016` and the rest. `PR_SIZED_WORK_BREAKDOWN.md` owns the list; do not restate it here.

Do not generate a parallel `IMP-###` numbering system. Renumbering by list position is prohibited because it silently changes issue identity when units are inserted or reorganized.

## Generator behavior

`scripts/repository/generate_issue_plan.py`:

1. parses `## Epic <ID> — <title>` headings;
2. parses `### <EPIC>-<NNN> <title>` work-unit headings, in the same three-digit form the stable keys use;
3. rejects duplicate keys;
4. rejects a work-unit prefix that does not match its epic;
5. requires contiguous source-ordered numbering within each epic;
6. copies each unit's `Files:`, `Acceptance:`, `Depends:`, `Est:` and `Status:` into its record, and refuses to emit a record it cannot fill;
7. records source line, component, phase gate, gate state and artifact maturity;
8. exits non-zero when its own reading of any unit's status differs from `scripts/repository/validate_work_unit_status.py`'s;
9. writes deterministic schema-version-3 JSON with the source SHA-256;
10. performs no network calls and creates no GitHub issues.

Field *enforcement* belongs to `validate_work_unit_status.py` under D-201, not here. The generator's refusal is narrower and different in kind: an issue whose acceptance criterion is blank misdescribes the unit it was generated from, so the record is not written at all.

The two readers are deliberately independent. They match different heading patterns over the same document, so a heading that lost its title, or one whose prefix is wider than the validator's pattern admits, is seen by one and not the other. Neither reader can detect that alone; the disagreement check is what makes it visible, and it fails the generator rather than producing a plan built on the difference.

The generated JSON is produced on demand or into a temporary validation path. It need not be committed, and an old generated file must never be treated as current authority.

## Phase gates

`conformance/p1140f/gate-authorization-v1.json` is the sole authority for gate state. Each record names the gate its unit sits behind and the state that gate currently holds; neither value is written down here or in the generator.

- The gate is derived from the epic prefix: `PF-*` units sit behind `P-1140F`, every other epic behind `P-1104`. No list of units is maintained.
- `phase_gate_state` is copied from the record. A record is labelled `blocked` when that state is not one under which the gate's work may proceed, and an unrecognised state blocks: releasing a unit the owner has not is the failure that matters.
- P-1104 is `authorized-open` as recorded on 2026-08-05. Implementation records are therefore no longer labelled `blocked` — which is a fact about the gate, not about any unit's readiness.
- Generating an issue plan does not authorize implementation, and a record's gate state is a restatement of the authorization record rather than evidence of anything.

## Required issue body after approval

Every created execution issue contains:

- the exact stable work-unit key and title;
- owning epic and dependencies;
- mapped decisions, ADRs, contracts and schemas;
- exclusions and platform profiles;
- privacy, security, migration and compatibility impact;
- tests, fixtures, benchmarks and executable evidence required;
- rollback or disable path;
- implementation status distinct from planning status.

Before creating an issue, the operator must search open and closed issues for the stable key and avoid duplicates.

## Labels

Initial labels are one track label — `implementation`, or `planning-repair` for a `PF-*` unit — one component label derived from the epic title, and `blocked` only while the unit's gate state says so. Labels and milestones are operational metadata and do not alter product authority.

## Thread discipline

Durable findings from issues or pull requests must be merged into the decision register, ADRs, schemas or normative contracts. Closing an issue does not override a contract, and changing a contract does not silently close an issue.
