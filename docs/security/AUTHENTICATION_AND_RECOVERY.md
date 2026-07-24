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
