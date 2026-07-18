# Contributing to VibeMaxxing

The repository is private and in planning-hardening. External contribution processes become active before public release, but all changes already follow this contract.

## Start

1. Read `AGENTS.md`.
2. Read `docs/project/STATUS.md` and `docs/project/DOCUMENTATION.md`.
3. Identify the owning task, decision, ADR, and normative contract.
4. Do not begin product implementation without an explicit phase change.

## Change types

- Documentation correction: update the single normative owner; do not add a competing summary.
- Behavioral or architectural change: update the decision register and create or amend an ADR.
- Schema change: update the authoritative schema first, compatibility rule, examples, validation, and migration plan.
- Adapter change: identify exact source version, mode, platform, privacy risks, evidence ceiling, conformance suite, and maintainer.
- Dependency change: record purpose, owner, license, security posture, update path, overlapping alternatives, and removal plan.

## Pull request requirements

Every PR must include:

- task and decision IDs;
- contracts and schemas changed;
- privacy and security impact;
- compatibility and migration impact;
- rollback or reversal plan;
- tests or planning validations actually run;
- generated artifacts and reproducibility impact;
- unresolved risks.

Mocks, placeholders, skipped checks, empty fixtures, and unexecuted tests are not implementation evidence.

## Commits and DCO

All contributions use the Developer Certificate of Origin. Add a `Signed-off-by: Name <email>` line to each commit. A CLA is not currently required.

## Privacy and fixtures

Never include real prompts, transcripts, code, repository names, paths, credentials, tokens, personal data, or private user data. Use synthetic fixtures. Security-sensitive abuse thresholds and exploit material may require private handling even after the repository becomes public.

## Reviews

Changes to protocol, privacy, security, accounting, identity, release, governance, or canonical project authority require CODEOWNER review. Material disagreement is resolved through the decision register and an ADR, not only in a comment thread.
