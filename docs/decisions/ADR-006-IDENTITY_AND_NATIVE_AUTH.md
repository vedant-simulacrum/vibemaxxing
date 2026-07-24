# ADR-006: Identity and Native Authorization

- Status: Accepted
- Date: 2026-07-19

## Decision

1. GitHub identity uses a GitHub App with user authorization, minimum permissions, expiring user tokens where available, and no repository-content permission for ordinary VibeMaxxing use.
2. Browser login uses OAuth authorization-code flow with state, PKCE where supported, exact redirect allowlists, and one-time callback codes.
3. Ordinary native CLI/daemon login uses external-browser Authorization Code + PKCE. OAuth device authorization is limited to explicitly registered limited-input or headless interactive profiles when the provider supports it. The daemon never receives the user's GitHub password.
4. X identity uses OAuth 2.0 Authorization Code with PKCE and the minimum identity scopes required to resolve the stable X user ID. OAuth 1.0a is not used unless a future required endpoint lacks OAuth 2.0 support.
5. GitHub and X are independent linked identities. Either may initiate an account when enabled; linking an identity requires a recent authenticated session and provider reauthorization.
6. Provider usernames and avatars are presentation metadata. Stable provider subject IDs are identity keys.
7. Passkeys are optional additional authenticators for account hardening and sensitive operations; they are never mandatory for baseline access.
8. Provider access tokens are encrypted, scoped minimally, rotated/refreshed only where needed, and deleted when the identity is disconnected. VibeMaxxing does not request repository access merely to establish identity.

## Account recovery

- Recovery may use another linked provider, an optional passkey, single-use recovery codes, or a documented human appeal.
- Linking, unlinking, merging, recovery, moderator privilege changes, mass deletion, and ownership transfer require recent authentication and risk checks.
- Removing the last usable identity requires adding another first or confirming full account deletion.
- Provider compromise triggers identity suspension, session revocation, device review, cooling-off, and appeal rather than silent reassignment.
- Provider rename does not change account ownership.
- Provider deletion or suspension does not delete VibeMaxxing data automatically.

## Session policy

- Web sessions use opaque random session IDs in Secure, HttpOnly, SameSite cookies.
- Session secrets are stored hashed server-side; rotation occurs after login, recovery, privilege changes, and suspicious activity.
- Access session target lifetime: 24 hours idle, 30 days absolute for ordinary users; privileged sessions are shorter.
- CSRF protection is mandatory for state-changing browser requests.
- When an eligible limited-input or headless profile uses device authorization, it produces a one-time enrollment grant bound to a device public key, account ID, nonce, and expiry. It is exchanged once for a revocable device credential.

## Failure behavior

Authorization denial, expired codes, slow-down responses, callback mismatch, revoked tokens, provider outages, and unavailable identity metadata must be explicit user-visible states. No failed OAuth flow may create a partial account without a resumable transaction record and expiry.

## Validation

Test callback fixation, state/PKCE bypass, replayed codes, device-code polling abuse, account-link confusion, provider-ID collision, provider rename, token revocation, last-identity removal, recovery takeover, CSRF, open redirects, session fixation, and concurrent merge races.
