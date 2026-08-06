# `auth` conformance suite

Case prefix: `AU`. Subjects: `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That the OAuth, session and recovery behaviour specified in `docs/security/AUTHENTICATION_AND_RECOVERY.md` and ADR-015 holds against a recorded expectation, including the cases where it must refuse.

Authorities:

- `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md`
- `packages/schemas/openapi-v1.yaml` for the authentication operations
- `packages/schemas/state-machine-registry-v1.json` for the session and refresh-family machines

## Required cases

Positive: one complete authorization-code exchange, one device-authorization exchange, one refresh rotation, one recovery inside policy.

Negative, each of which must reject with a registered reason code:

- an authorization code replayed after use;
- a `state` value that does not match the transaction;
- an authorization code presented after its 60-second lifetime;
- a `state` presented after its 10-minute lifetime;
- a refresh handle presented a second time, which ADR-015 makes always an incident and which must revoke the whole family rather than the handle;
- a web session family past its 90-day absolute cap;
- a device-authorization code polled faster than the 5-second minimum interval in `docs/architecture/API_EDGE_CONTRACT.md`;
- a device-authorization code polled after its 15-minute expiry;
- a recovery attempt inside the cooling-off period;
- a request whose signing timestamp is outside the 300-second freshness bound.

## Status

**Nothing here executes.** This directory holds no fixture, no `manifest.json` and no runner. The `authentication-recovery` eval suite is `not_applicable` and names `apps/api/internal/auth` and `evals/fixtures/authentication-recovery.json` (new) as the paths whose absence justifies that status; it stays `not_applicable` until both exist. A README is not executable evidence and this one does not change any status.
