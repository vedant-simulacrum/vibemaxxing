# `release` conformance suite

Case prefix: `RL`. Subjects: `rust`, `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That a client verifying a release set behaves as ADR-013 and the operations contract require, and in particular that it refuses each of the five update-system attacks by name rather than by accident.

Authorities:

- `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
- `docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md`
- `packages/schemas/release-set-v1.schema.json`
- `packages/schemas/platform-profile-registry-v1.json` for the exact tuple a release set claims to support

## Required cases

Positive: one well-formed release set accepted, with artifact digests, source commit, SBOM, provenance, supported version ranges and update class present.

Negative, one per attack the operations contract requires clients to defend against, so the case list maps one-to-one onto the stated threat:

- **rollback** — metadata offering an earlier version than the client has already installed;
- **freeze** — valid but stale metadata replayed past its expiry;
- **mix-and-match** — targets from one snapshot combined with a different snapshot's metadata;
- **fast-forward** — a version number inflated beyond the range the root delegation permits;
- **endless data** — a target whose declared length is exceeded by the stream.

Plus: expired timestamp metadata; expired snapshot metadata; a targets delegation signing outside its delegated path; a threshold not met; a client past a signed update deadline attempting a competitive operation; and an installation rolled back without resetting lineage or losing queued claims.

## Status

**Nothing here executes.** No fixture, no `manifest.json`, no runner. The `release-verification` eval suite is `not_applicable` and names `crates/vibeproof-verifier/src/lib.rs` (new) and `evals/fixtures/release-verification.json` (new) as the paths whose absence justifies that status. No TUF metadata has ever been generated, no key exists, and no release set has been produced. A README is not executable evidence and this one does not change any status.
