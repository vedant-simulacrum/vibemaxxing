# Authentication and Recovery

## Authentication

- Passkeys/WebAuthn are preferred.
- Allow multiple credentials per account.
- Store credential public keys, counters/metadata, transports, timestamps, and user-visible labels only.
- Never receive biometric data.
- Use discoverable credentials where product UX supports them.
- Require user verification for sensitive actions.

## Recovery

Recovery must not be weaker than normal authentication without compensating controls.

Required controls:

- Encourage a second passkey or hardware key.
- Optional single-use recovery codes with hashed server-side verifiers.
- Cooling-off period for high-risk recovery.
- Revoke or reauthorize existing sessions after recovery.
- Notify existing credentials/channels of changes.
- Rate limit and risk score recovery attempts.
- Maintain a privacy-safe credential event ledger.
- Support a documented human appeal path without exposing account activity.

Email-only reset is not an accepted default.
