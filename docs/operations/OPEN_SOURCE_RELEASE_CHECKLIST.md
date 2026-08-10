# Open-source release checklist

Status: normative planning checklist; no item is evidence that the release happened
Owner: this document owns the per-release open-source obligations. `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` owns the operations contract and the launch scope; `docs/planning/REPOSITORY_OPERATIONS.md` owns the retroactive publication audit. This file owns neither and duplicates neither.

## What this is for

`docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` carried this as a `planned-missing` row for the whole planning phase, against D-040 and a decision that no longer holds. The obligations were named in four words — "license/dependency review, security policy, contribution path and public docs" — and nothing said what would satisfy them or who had.

The row cited D-033, which said the repository is private during planning and becomes public before launch. D-540 superseded it: the repository has been public since it was created. A checklist inheriting that citation would have been written as a pre-publication gate, which is the framing D-541 records as the reason the audit was never performed at all.

A checklist that omits the item already known to be unmet is dishonest, so the first entry below began as the finding the D-541 audit actually produced rather than a template row. A checklist that records an item as unmet without reading the artifact is wrong in the other direction, which is what happened to three of these and is noted under the table.

## The repository is already public

D-541 records that publication was never treated as an event: the repository has been public since 2026-07-18, so nothing here is a gate that runs before publication. Every item is owed retroactively and is checked against a repository that is already readable by anyone.

The retroactive audit is performed and recorded in `REPOSITORY_OPERATIONS.md`. Four of its five limbs are clean. This checklist inherits the fifth.

## Items

Each item names what would satisfy it, not what it hopes is true. An item is `met` only when the artifact it names exists and says what the item requires.

| # | Item | State | What satisfies it |
|---|---|---|---|
| 1 | LGPL attribution for the `sharp-libvips` binaries | **met** | `NOTICE` names all fourteen LGPL-licensed packages across both lockfiles, their versions, libvips' source and the licence texts, and records that they are used unmodified and resolved from npm rather than vendored. It states what it does not settle: the Combined Work obligations attach on distribution, and nothing is distributed yet. |
| 2 | Dependency licence inventory is complete and current | **met** | The D-541 audit resolved every declared dependency across `requirements-planning.txt`, both npm lockfiles, `Cargo.lock` and `go.mod`. No GPL or AGPL; one LGPL family, which is item 1. Recorded in `docs/planning/REPOSITORY_OPERATIONS.md`. |
| 3 | Security policy | **met** | `SECURITY.md` names GitHub private vulnerability reporting as the channel, commits to acknowledging within 3 business days, assessing within 5 and updating every 7 for active high-severity reports, and carries a supported-versions statement. |
| 4 | Contribution path | **met** | `CONTRIBUTING.md` states the repository is in planning contract repair with implementation gated behind P-1104, sets pull-request requirements, and requires DCO sign-off with no CLA. |
| 5 | Public documentation entry point | **met** | `README.md` opens "Status: authorized to build, nothing built", states that the gate was opened with its preconditions unmet, and says there is no daemon, adapter, collector, OAuth, database or API. It is blunt to a human reader, not only to an agent. |
| 6 | Release-set manifests are authenticated targets | unmet | `packages/schemas/release-set-v1.schema.json` requires the eight per-component fields and refuses a manifest signed by the root role or targeting a component path, with seven negative examples. Satisfied when a real release set is produced under it, which is implementation-session work. |
| 7 | Signing keys and TUF root | unmet, deliberately | No key, keypair or TUF root exists in this repository and none may be created during planning. Listed so its absence is recorded rather than discovered. |

Five of seven are met. The first version of this table recorded all seven as unmet, and three of those were wrong: `SECURITY.md`, `CONTRIBUTING.md` and `README.md` already existed and already said what their items require. Asserting a gap without reading the artifact is the same error as asserting coverage without reading it, and it is worth recording here because this checklist exists to stop exactly that.

## What this checklist is not

No item here is implementation evidence. Item 6's schema exists and no release set has been produced under it; item 7 is deliberately unmet. A green row would mean the artifact exists and says the right thing, never that a release ran.

## The other two planned-missing rows

Both stay `planned-missing`, with the reason recorded in the inventory rather than here.

- **Deployment and operations** is gated after P-1104 and no deployment automation may exist during planning. The row's own dependency says so.
- **Local development environment** lands with the first service under D-264. Its declared normative owner, `docs/engineering/LOCAL_DEVELOPMENT.md`, does not exist — which is what `planned-missing` means, and is the reason the row is not a defect.
