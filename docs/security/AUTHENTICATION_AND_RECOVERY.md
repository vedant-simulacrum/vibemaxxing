# Authentication, Identity, Sessions, and Recovery

Updated: 2026-07-19
Status: planning contract

## Principles

- Account identity and activity integrity are separate. Social login does not prove device, source, or claim authenticity.
- Request the minimum provider scopes required for sign-in and account linking.
- Provider access tokens must be encrypted, short-lived where possible, rotated, and deleted when no longer required.
- Passkeys and hardware-backed credentials are optional stronger factors, not mandatory for ordinary accounts.
- High-impact recovery and identity changes require cooling-off, notifications, session review, and auditable reason codes.

## Primary authentication

Supported primary providers:

- GitHub.
- X/Twitter.

The implementation decision between GitHub App and OAuth App must be finalized through current official documentation and a threat/permission comparison. Ordinary desktop native clients use external-browser Authorization Code + PKCE. Device authorization is restricted to registered limited-input or headless interactive profiles when the provider supports it; CI and unattended automation must not poll a human device code. Browser callback flows must bind state, PKCE where supported, redirect URI, client instance, and session.

## Account model

An account may link multiple external identities. Store only the provider subject identifier, verified provider metadata required for display or recovery, timestamps, linkage state, and minimal encrypted credentials when operationally required.

Do not use mutable usernames as identity keys. Provider subject IDs are stable linkage keys; display names and handles are attributes.

Required states:

- unregistered;
- registered with one provider;
- linked providers;
- optional stronger factor enrolled;
- provider disconnected;
- provider access lost;
- provider compromised;
- recovery pending;
- restricted;
- deletion pending;
- deleted.

## Account linking

Linking a new provider requires an active authenticated session and reauthentication with the existing provider or optional stronger factor. Prevent accidental linking to an existing VibeMaxxing account; require an explicit merge flow with conflict review.

Account merge must define ownership of usernames, devices, claims, boards, friendships, moderation state, and deletion requests. Merge must never duplicate competitive claims.

## Optional stronger authentication tier

Optional factors may include passkeys, WebAuthn security keys, or platform credentials. Require stronger reauthentication for:

- changing linked identities;
- exporting sensitive account data;
- deleting an account;
- transferring board or organization ownership;
- moderator or administrator actions;
- rotating critical recovery methods;
- restoring a quarantined high-value account where policy requires it.

No biometric data is received or stored by VibeMaxxing.

## Sessions

Sessions require:

- secure, HTTP-only, same-site cookies for web;
- explicit native-device session tokens for CLI/daemon clients;
- short-lived access tokens and bounded refresh tokens;
- rotation on refresh;
- replay detection;
- device/session labels;
- last-used timestamps;
- IP and user-agent data minimized and retained only under an explicit privacy policy;
- per-session revocation and revoke-all capability;
- notification on suspicious or recovery-related session changes.

Native authorization must bind the user account, local device identity, daemon instance, and authorization transaction. Browser login completion must not authorize an unbound local process.

## Recovery

Preferred recovery order:

1. Another linked provider.
2. Optional enrolled passkey or hardware key.
3. Single-use recovery codes with hashed server-side verifiers.
4. Existing trusted session with risk controls.
5. Human appeal with cooling-off and limited restoration powers.

Recovery must never silently transfer competitive identity based only on mutable profile information or support discretion.

Required controls:

- rate limits and abuse detection;
- cooling-off for high-risk recovery;
- notifications to existing providers, sessions, and configured channels;
- revocation or reauthorization of existing sessions;
- explicit device-key review;
- privacy-safe credential event ledger;
- reason codes and appeal path;
- no access to prompts, source code, projects, or local activity content during recovery.

### The recovery case aggregate

The controls above are requirements. The aggregate that carries them is the recovery case, and D-320 records the choices inside it.

| Concern | Owner |
|---|---|
| Lifecycle | the `recovery-case` machine in `packages/schemas/state-machine-registry-v1.json` |
| Persistence | `packages/schemas/planning-schema.sql`, table `recovery_cases` |
| Record | `packages/schemas/recovery-case-v1.schema.json` |
| Revision model | `recovery_cases.revision`, monotonic, incremented inside the transaction that changes the row; a conditional update naming a stale revision is refused |
| Transaction boundary | `recovery-session-and-device`: rebinding access, revoking every session family and quarantining every enrolled device commit together |
| Expiry | `expires_at`; an unfinished case moves to `expired` and the participant starts again |
| Reversal | none. An applied recovery is not undone; a wrongly applied one is answered by a new case, because the access it revoked cannot be un-revoked |

The states are `requested`, `verifying`, `cooling-off`, `applied`, `denied`, `cancelled` and `expired`. Four of them are terminal.

Three properties are check constraints rather than handler discipline, because each is a race an application-level check loses:

- applying before `cooling_off_ends_at` is unrepresentable, so the window cannot be skipped by a retry that arrives early;
- an applied case that did not revoke sessions and quarantine devices cannot be written, so the two effects cannot drift apart from the state that claims them;
- a partial unique index permits one live case per account, so an attacker cannot open a second case to outlast the notice on the first.

What a case verifies is a locally-held factor: a recovery code, an optional authenticator, or a signature from an enrolled device. Under D-100 no provider offers an individual-account attestation path, so `verified_factor_class` names none of them and no surface may present a recovery as provider-confirmed.

The error paths are `denied` with a reason code from `packages/schemas/reason-codes-v1.json`, `expired` when the case outlives its window, and `cancelled` by a participant who still holds access. A denied case records the code; the participant is told the outcome and not which factor failed, because that distinction tells an attacker which factor to attack next.

Nothing here resurrects an identifier a D-085 erasure destroyed. An erasure deletes the account row a case references, so an erased account has no case to recover and no pseudonym to re-bind.

## Provider compromise or loss

If a provider account is compromised, suspended, deleted, or renamed:

- provider subject ID remains the linkage key;
- the user may recover through another linked method;
- high-risk identity changes enter a pending state;
- competitive activity may continue from already authorized devices under policy, but account-control changes are restricted;
- no new provider may be linked solely through an untrusted existing provider without reauthentication or recovery controls.

## Authorization

Authentication does not imply authorization. Define explicit permissions for:

- public and private profiles;
- friendships and blocks;
- private boards;
- organization and community administration;
- moderation and appeals;
- device management;
- data export and deletion.

Every high-impact action must be server-authorized, idempotent where relevant, logged with privacy-safe audit data, and protected against CSRF, confused-deputy behavior, replay, and stale sessions.

## Open research

- GitHub App versus OAuth App permissions and lifecycle.
- X/Twitter sign-in protocol and long-term API constraints.
- Native device-flow support and secure fallback.
- Optional passkey library and browser/platform interoperability.
- Account-merge UX and abuse resistance.
- Recovery false-positive and takeover simulations.
