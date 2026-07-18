# Repository Operations Policy

## Visibility

Keep the repository private during planning unless the user explicitly chooses otherwise. Open-source publication is a later release decision and requires a secret, privacy, license, security, and history audit.

## Default branch

- Default branch: `main`.
- Planning changes may be committed directly only by the owner or through a reviewed planning branch.
- Product implementation should use short-lived branches and pull requests once that phase opens.

## Required protections before implementation

Configure `main` to require:

- pull requests;
- at least one approving review for normal changes;
- independent review for high-risk privacy, protocol, identity, auth, data, migration, deletion, or release changes;
- required CI, policy, schema, documentation, and eval checks;
- resolved review conversations;
- linear history or squash merges;
- no force pushes or branch deletion;
- signed commits where practical.

## Planning review contract

Each planning change must identify:

- task IDs from `TASK_CATALOG.md`;
- affected decision IDs;
- constraints and alternatives;
- privacy and security impact;
- interfaces, schemas, state machines, and failures changed;
- future evidence and acceptance gates;
- unresolved questions.

## Repository hygiene

- No secrets, tokens, credentials, private prompts, transcripts, local paths, or proprietary source content.
- No bootstrap archives, base64 transfer fragments, generated caches, or nested repository metadata.
- Keep manifests and checksums synchronized through a reproducible generator.
- Use pinned or lockfile-controlled toolchains before implementation.
- Keep generated evidence governed by `ARTIFACT_POLICY.md`.

## CI expectations during planning

Planning CI should validate:

- Markdown, YAML, and JSON syntax;
- internal links and required root files;
- task and decision ID uniqueness;
- references from tasks to valid decisions and specifications;
- schema validity;
- forbidden secret and privacy canaries;
- manifest freshness;
- explicit status for every eval and artifact.

It must not manufacture passing product evidence from missing implementations.

## Phase transition checklist

Before implementation begins:

1. Complete P-901 through P-903.
2. Obtain explicit user approval in P-904.
3. Enable required branch protections and checks.
4. Freeze the initial implementation task set and owners.
5. Confirm local development prerequisites and supported platforms.
6. Confirm no private or stale planning material will leak into public releases.

## Publication checklist

Before making the repository public:

- run secret and history scans;
- review threat and abuse details for safe disclosure;
- verify licenses and third-party notices;
- remove environment-specific probes and personal metadata;
- verify issue and security reporting policies;
- review all artifacts and commit history;
- document responsible disclosure and support boundaries.