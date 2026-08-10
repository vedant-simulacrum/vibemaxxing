# Open-source release checklist

Status: normative planning checklist; no item is evidence that the release happened
Owner: this document owns the per-release open-source obligations. `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` owns the operations contract and the launch scope; `docs/planning/REPOSITORY_OPERATIONS.md` owns the retroactive publication audit. This file owns neither and duplicates neither.

## What this is for

`docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` carried this as a `planned-missing` row for the whole planning phase, against D-040 and a decision that no longer holds. The obligations were named in four words — "license/dependency review, security policy, contribution path and public docs" — and nothing said what would satisfy them or who had.

The row cited D-033, which said the repository is private during planning and becomes public before launch. D-540 superseded it: the repository has been public since it was created. A checklist inheriting that citation would have been written as a pre-publication gate, which is the framing D-541 records as the reason the audit was never performed at all.

A checklist whose items are all unchecked is honest. A checklist that omits the item already known to be unmet is not, so the first entry below is the finding the D-541 audit actually produced rather than a template row.

## The repository is already public

D-541 records that publication was never treated as an event: the repository has been public since 2026-07-18, so nothing here is a gate that runs before publication. Every item is owed retroactively and is checked against a repository that is already readable by anyone.

The retroactive audit is performed and recorded in `REPOSITORY_OPERATIONS.md`. Four of its five limbs are clean. This checklist inherits the fifth.

## Items

Each item names what would satisfy it, not what it hopes is true. An item is `met` only when the artifact it names exists and says what the item requires.

| # | Item | State | What satisfies it |
|---|---|---|---|
| 1 | LGPL attribution for the `sharp-libvips` binaries | **unmet** | `@img/sharp-libvips-*` prebuilt binaries are pinned under `LGPL-3.0-or-later` in `apps/web/package-lock.json` and `scripts/brand/package-lock.json`, and `LICENSES.md` states the NOTICE and attribution review they require has not happened. Satisfied by a NOTICE file carrying the required attributions and the written-offer or corresponding-source statement LGPL §4 requires, or by removing the dependency. |
| 2 | Dependency licence inventory is complete and current | unmet | Every declared dependency in `requirements-planning.txt`, the npm lockfiles, `Cargo.lock` and `go.mod` resolved to a licence, with no unlicensed entry. The D-541 audit found no GPL or AGPL and one LGPL family, which is item 1. |
| 3 | Security policy | unmet | A `SECURITY.md` naming a reporting channel, a response expectation the owner can actually meet, and the supported-version statement. It must not claim a support window the project does not staff — an unstaffed promise is worse than none. |
| 4 | Contribution path | unmet | A `CONTRIBUTING.md` stating whether external contributions are accepted at all. "Not currently accepting contributions" is a complete answer and is preferable to silence, which reads as an open door. |
| 5 | Public documentation entry point | unmet | A reader arriving at the repository can tell what the project is, what state it is in, and that no component is implemented or launch-ready. `README.md` and `AGENTS.md` both exist; this item is whether they say the phase plainly to someone who is not an agent. |
| 6 | Release-set manifests are authenticated targets | unmet | `packages/schemas/release-set-v1.schema.json` requires a TUF role reference, target path, architecture, hash, provenance reference, native signature reference, compatibility tuple and update class per component, and refuses a manifest signed by the root role or targeting a component path. Satisfied when a real release set is produced under it, which is implementation-session work. |
| 7 | Signing keys and TUF root | unmet, deliberately | No key, keypair or TUF root exists in this repository and none may be created during planning. This item is listed so its absence is recorded rather than discovered. |

## What this checklist is not

No item here is implementation evidence. Item 6's schema exists and no release set has been produced under it; item 7 is deliberately unmet. A green row would mean the artifact exists and says the right thing, never that a release ran.

## The other two planned-missing rows

Both stay `planned-missing`, with the reason recorded in the inventory rather than here.

- **Deployment and operations** is gated after P-1104 and no deployment automation may exist during planning. The row's own dependency says so.
- **Local development environment** lands with the first service under D-264. Its declared normative owner, `docs/engineering/LOCAL_DEVELOPMENT.md`, does not exist — which is what `planned-missing` means, and is the reason the row is not a defect.
