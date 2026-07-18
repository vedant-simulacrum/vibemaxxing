# ADR-009: Licensing and Contribution Model

Status: accepted for planning; final dependency and counsel review remains a release gate
Date: 2026-07-19

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
