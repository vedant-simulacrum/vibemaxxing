# Repository Operations Policy

## Visibility

The repository is public and has been since 2026-07-18, so publication is not a later decision and this paragraph's precondition cannot be satisfied in advance. The secret, privacy, license, security and history audit it required is therefore owed retroactively rather than as a gate. All five limbs have now been performed and are recorded below under D-541. Treat every commit as published at the moment it is pushed.

### Retroactive publication audit

Performed 2026-08-09 against `2453f67` and restricted to refs that exist on the remote. This machine carries local-only `refs/conductor-checkpoints/*` refs that inflate `git rev-list --all` by roughly 140 commits; an unqualified scan would have reported working-copy artifacts as published history, so every history claim below was re-run against `--remotes=origin`.

- **Secret.** Performed. 1,829 blobs across all 918 commits scanned for AWS keys, Anthropic keys, GitHub tokens and classic PATs, private key headers, Slack tokens and Google API keys. Zero matches.
- **Privacy.** Performed. No third-party personal data: no third-party names, email addresses, IP addresses or hostnames. Two self-disclosures by the owner, recorded rather than removed because rewriting public history is the more damaging repair: the personal address `vk.work.official@gmail.com` is the committer on 33 commits including the initial import, which is a different address from the `vedant@simulacrum.world` the legal documents name as contact; and the owner's first name is used as sample data in shipped UI mockups. The gitignored agent-session and virtualenv directories, which do hold local paths and session material, are confirmed never committed.
- **License.** Performed, one gap open. No GPL, AGPL or LGPL source dependency. `apps/web/package-lock.json` and `scripts/brand/package-lock.json` each pin `@img/sharp-libvips-*` prebuilt binaries under `LGPL-3.0-or-later`, and `LICENSES.md` already states that the NOTICE and attribution review those require has not been done — this audit makes that concrete rather than hypothetical, and it is the one limb finding that remains open. The unfamiliar `zmij v1.0.23` in `Cargo.lock` was checked against crates.io and is legitimate: David Tolnay's Schubfach float-formatting crate, MIT, the same maintainer as the `serde_json` that depends on it.
- **Security.** Performed, clean. All three workflows use plain `pull_request` and never `pull_request_target`; `permissions: contents: read`; every third-party action pinned to a full commit SHA; no `${{ secrets.* }}` reachable from a pull-request trigger; no download-and-execute pattern in `scripts/`, the `Makefile` or `.github/`.
- **History.** Performed, clean. Largest blob is a governed 786 KB mockup. No vendored dependencies, archives or binaries were ever committed, and no agent-session material ever was. Forty-two files are deleted-but-reachable, of which the notable ones are `release.yml`, `security.yml` and `dependabot.yml` — consistent with those capabilities being deliberately unactivated — and a batch of superseded planning documents. Stale, not sensitive.

One limb of five was evidence about one limb of five, which is why D-541 recorded the gap rather than the reassurance. Five of five is now performed; the LGPL attribution review is the single obligation the audit leaves open, and it belongs to the open-source release checklist rather than here.

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

1. Obtain explicit user approval.
2. Enable required branch protections and checks.
3. Freeze the initial implementation task set and owners.
4. Confirm local development prerequisites and supported platforms.
5. Confirm no private or stale planning material will leak into public releases.

## Publication checklist

Before making the repository public:

- run secret and history scans;
- review threat and abuse details for safe disclosure;
- verify licenses and third-party notices;
- remove environment-specific probes and personal metadata;
- verify issue and security reporting policies;
- review all artifacts and commit history;
- document responsible disclosure and support boundaries.