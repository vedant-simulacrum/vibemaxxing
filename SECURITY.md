# Security Policy

## Reporting

Report vulnerabilities through **[GitHub private vulnerability reporting](https://github.com/vedant-simulacrum/vibemaxxing/security/advisories/new)**. Do not open a public issue.

If that channel is unavailable to you, contact the repository owner through a private channel. Private reporting is enabled on this repository as of 2026-08-05; an earlier version of this file assumed the repository was private and directed reporters to a private message instead. The repository is public.

Do not include real prompts, transcripts, code, repository names, paths, API keys, credentials, access tokens, cookies, or user data. Use minimal synthetic reproduction material and encrypted attachments where necessary.

## Priority areas

- transcript or forbidden-data exfiltration;
- claim forgery, canonicalization, signature, replay, sequence, fork, or clone failures;
- adapter or source impersonation;
- device-key compromise and recovery;
- ranking, identity, social, moderation, or authorization manipulation;
- updater, release, dependency, build, or other supply-chain compromise;
- deletion, export, retention, backup, or recovery failures.

## Response targets

Planning-stage targets, not contractual promises:

- acknowledge credible reports within 3 business days;
- begin severity assessment within 5 business days;
- provide status updates at least every 7 days for active high-severity reports;
- coordinate disclosure after a fix or effective mitigation is available, unless active exploitation requires earlier notice.

Privacy-boundary violations are treated as highest severity until scoped.

## Supported versions

No production version is currently supported because product implementation has not begun. There is no deployed system, no release, and no binary to attack — reports at this stage concern the design and the specifications in `packages/schemas/` and `docs/`.

Before the first release, this file must list supported versions and an end-of-support policy.

Known and accepted at this stage, so you need not report them: the ranked metric is uncapped and a user who controls their own machine can inflate their own score; automated dependency scanning, SAST, and SBOM generation are deliberately disabled until implementation opens (`AGENTS.md`); and `main` has no branch protection. These are tracked, not overlooked.

## Safe harbor

A formal safe-harbor policy must be reviewed and published before public launch. Until then, do not perform testing against systems or data you do not own or have explicit permission to test.
