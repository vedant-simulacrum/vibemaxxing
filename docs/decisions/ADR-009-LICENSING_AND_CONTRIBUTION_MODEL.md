# ADR-009: Licensing and Contribution Model

Status: accepted for planning; final dependency and counsel review remains a release gate, and that gate is **unmet**
Date: 2026-07-19
Amended: 2026-08-06 to state the counsel gate as unmet and to extend its scope to the participant-facing legal documents

## Decision

- Original source code in this monorepo is licensed under Apache License 2.0.
- Protocol specifications, architecture documents, product documentation, diagrams, and examples are licensed under CC BY 4.0 unless a file states otherwise.
- Third-party code, generated artifacts derived from third-party sources, model assets, fonts, icons, fixtures, and datasets retain their original licenses and notices.
- Contributions use the Developer Certificate of Origin. No CLA is required initially.
- VibeMaxxing and VibeProof names and marks are not granted for confusing product branding by the code or documentation licenses; a separate trademark policy is required before public release.

The hosted application is not separately AGPL-licensed. A future copyleft change requires an explicit relicensing strategy, contributor-rights analysis, user approval, and a new ADR.

## Rationale

One code license avoids ambiguous boundaries between protocol, native, server, and web packages in a tightly integrated monorepo. Apache-2.0 provides explicit patent terms and is compatible with the intended open adapter and protocol ecosystem.

## Release conditions

Before repository publication:

- complete dependency and license scans;
- confirm attribution and NOTICE obligations;
- add full CC BY 4.0 and DCO texts or authoritative references;
- confirm contributor and trademark policy with qualified counsel where appropriate;
- resolve any dependency that cannot be distributed under the selected matrix.

## The counsel gate, and its current state

**No qualified counsel has reviewed anything in this repository. The gate is open and unmet, and no artifact may present it as satisfied.**

The gate's scope is wider than licensing. It covers, as one review:

- this ADR's licence matrix, contributor model and trademark position;
- `PRIVACY.md`, the participant-facing notice under Articles 13 and 14 of Regulation (EU) 2016/679;
- `TERMS.md`, including its liability limitations, its consumer-law carve-out and its governing-law clause;
- `docs/privacy/DATA_MAP.md`, which is also the Article 30 record of processing activities;
- ADR-021, which records the public-by-default risk acceptance and the legal analysis the three documents above derive from, and which states in its own text that it is reasoning rather than advice.

D-109 owns this gate together with the three other unmet legal preconditions: the mandatory data protection impact assessment, the unfilled controller legal name, address, supervisory authority and governing jurisdiction, and the absent named sub-processor list. ADR-017 records that engaging counsel is itself one of the conditions that would reopen the residency analysis.

Closing the gate means a named reviewer, a dated review, and a record of what changed as a result. A reading by the owner, however careful, is not it.
