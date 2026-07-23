# GitHub Issue Generation Contract

Status: planning contract
Updated: 2026-07-23

`docs/planning/TASK_CATALOG.md` owns planning phases and gates. `PR_SIZED_WORK_BREAKDOWN.md` owns future implementation units. Generated issue plans and GitHub issues are non-authoritative execution metadata.

## Stable keys

Implementation issue keys are the stable work-unit headings already present in the work breakdown, such as:

- `F-01` for foundation contracts;
- `P-06` for protocol vectors;
- `N-18` for mandatory-update coordination;
- `O-30` for the out-of-scope platform guard;
- `PL-01` for a post-launch track.

Do not generate a parallel `IMP-###` numbering system. Renumbering by list position is prohibited because it silently changes issue identity when units are inserted or reorganized.

## Generator behavior

`scripts/repository/generate_issue_plan.py`:

1. parses `## Epic <ID> — <title>` headings;
2. parses `### <ID>-<NN> <title>` work-unit headings;
3. rejects duplicate keys;
4. rejects a work-unit prefix that does not match its epic;
5. requires contiguous source-ordered numbering within each epic;
6. records source line, component, phase gate and artifact maturity;
7. writes deterministic schema-version-2 JSON with the source SHA-256;
8. performs no network calls and creates no GitHub issues.

The generated JSON is produced on demand or into a temporary validation path. It need not be committed, and an old generated file must never be treated as current authority.

## Phase gates

- Ordinary work units remain blocked by `P-1104-explicit-implementation-approval`.
- `PL-*` units remain blocked by `post-launch-explicit-approval`.
- Generating an issue plan does not authorize implementation.

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

Initial labels are `implementation`, one component label and `blocked`. Labels and milestones are operational metadata and do not alter product authority.

## Thread discipline

Durable findings from issues or pull requests must be merged into the decision register, ADRs, schemas or normative contracts. Closing an issue does not override a contract, and changing a contract does not silently close an issue.
