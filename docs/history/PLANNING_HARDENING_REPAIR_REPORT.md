# Planning-Hardening Repair Report

Updated: 2026-07-19
Status: repairs committed; clean-checkout execution pending

## Repaired findings

| Audit finding | Repair |
|---|---|
| Planning completeness overstated | D-038 superseded by D-042; project, status, README, AGENTS, handoff and task catalog moved to planning-hardening |
| Required schemas absent | Added JSON Schemas, CDDL, Protobuf, OpenAPI, planning SQL, reason registry, policy registry and observability allowlist under `packages/schemas/` |
| Broken adversarial registry path and action vocabulary | Added canonical schema-backed registry; normalized actions/reason codes; removed `anti-cheat-cases.json` |
| Agent registry unable to represent exercised support | Added schema and exact certification records; empty certifications explicitly mean no product-level support |
| Future paths presented as current | Added `REPOSITORY_LAYOUT.md`; handoff now links current versus future tree |
| Batch/challenge/partial-acceptance ambiguity | ADR-007 selects one challenge per atomic batch and prohibits partial acceptance |
| Sequence-gap recovery undefined | ADR-007 defines bounded signed gap declarations, downgrade and re-enrollment conditions |
| Unicode handle rules undefined | ADR-008 selects Unicode 16.0, NFKC, full case fold, script and confusable rules |
| Scattered configurable defaults | Added versioned policy registry with values, bounds, owners and retroactivity; reconciled defaults document |
| License contradiction | ADR-009 and `LICENSES.md` select Apache-2.0 code, CC BY 4.0 docs/specs and DCO/no CLA |
| Placeholder CODEOWNERS | Replaced with current repository owner and sensitive path ownership |
| Thin contributing/security policies | Expanded contribution, DCO, schema, privacy, review and private vulnerability-reporting requirements |
| Repository checks validated legacy structure only | Added `scripts/repository/doctor.py`; compatibility policy delegates to it |
| Workflows were no-op or unpinned | Removed no-op security/release workflows; pinned checkout in planning validator |
| Work breakdown disconnected from issues | Added deterministic offline issue-plan generator and issue-generation contract |
| Historical PASS remained authoritative | Replaced final exit audit with an explicit supersession notice |
| Placeholder schema/protocol READMEs | Replaced with source-of-truth and generation guidance |
| Country/RPO defaults contradicted contracts | Numeric values now resolve through policy registry and operations targets |

## Static verification performed

- Re-read canonical authority, status, handoff and schema inventory after edits.
- Searched repository index for stale `technical planning complete`, `implementation-ready`, `anti-cheat-cases.json`, `AGPL` and placeholder CODEOWNER strings; no results were returned.
- Manually reconciled adversarial actions with the reason-code registry.
- Verified the agent registry uses existing family IDs and contains no fabricated certification results.
- Verified obsolete no-op workflows and registry were deleted.

## Remaining executable validation

The current environment does not have the GitHub CLI and could not clone the private repository, so the following evidence remains pending:

1. Run `python3 scripts/repository/doctor.py` from a clean checkout.
2. Run the manual/pull-request planning workflow.
3. Parse JSON Schemas with a Draft 2020-12 validator.
4. Parse CDDL with the selected planning validator.
5. Compile Protobuf files and run future Buf lint/breaking checks.
6. Validate OpenAPI 3.1.
7. Parse planning SQL in a disposable PostgreSQL database, without treating it as migration evidence.
8. Perform an independent context-free re-audit.

Until those pass, P-1120, P-1126 and P-1128 remain open and implementation remains unauthorized.
