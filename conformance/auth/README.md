# `auth` conformance suite

Case prefix: `AU`. Subjects: `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That the OAuth, session and recovery behaviour specified in `docs/security/AUTHENTICATION_AND_RECOVERY.md` and ADR-015 holds against a recorded expectation, including the cases where it must refuse.

Authorities:

- `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- `docs/decisions/ADR-015-SESSION_AUTHENTICATION.md`
- `packages/schemas/openapi-v1.yaml` for the authentication operations
- `packages/schemas/oauth-provider-registry-v1.json` for the provider capability record the mix-up vectors are decided against
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

## What is here now

`provider-mixup-vectors-v1.json` holds sixteen callback observations under PF-005: two accepted baselines, one per launch provider, and fourteen refusals. Each refusal differs from its provider's baseline in exactly one field, which is what makes the recorded reason code attributable to one discriminator rather than to a generally malformed callback. The seven discriminators are transaction single use, transaction lifetime, the provider-specific callback path, exact redirect match, issuer identification, state binding and PKCE method. `manifest.json` declares one case per vector.

## Status

**No harness runner executes this suite against a subject.** `runner.state` is `absent` and `OS-009` owns it. The vectors above are decided inside this repository by `scripts/repository/validate_oauth_identity_contract.py`, which evaluates each callback against `packages/schemas/oauth-provider-registry-v1.json` and compares the decision with the recorded expectation. That is a planning check and not conformance: there is no Go subject running the same decision, and cross-implementation agreement is the thing conformance is for.

Nine of the transaction shapes listed above are still unwritten — the refresh-handle replay, the 90-day family cap, the device-code polling bounds and the recovery cooling-off case among them. The `authentication-recovery` eval suite stays `not_applicable`: it names `apps/api/internal/auth` and `evals/fixtures/authentication-recovery.json` (new) as the paths whose absence justifies that status, and neither exists. Nothing in this directory changes it. An earlier version of this section said the directory held no `manifest.json`, which was already untrue when it was written.
