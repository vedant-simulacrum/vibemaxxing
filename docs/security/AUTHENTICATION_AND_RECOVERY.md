# Authentication, Identity, Sessions, and Recovery

Updated: 2026-07-19
Status: normative planning contract

## Principles

- Account identity and activity integrity are separate. Social login does not prove device, source, or claim authenticity.
- Request the minimum provider permissions required for sign-in and account linking.
- Provider access and refresh tokens are encrypted at rest, redacted from logs, rotated, revoked and deleted when no longer required.
- Passkeys and hardware-backed credentials are optional stronger factors, not mandatory for ordinary accounts.
- High-impact recovery and identity changes require cooling-off, notifications, session review and auditable reason codes.
- OAuth implementations follow RFC 9700 and provider-specific current official requirements; provider deviations are documented rather than silently weakening the common baseline.

## Primary authentication

Supported primary providers:

- GitHub through a GitHub App.
- X/Twitter through OAuth 2.0 Authorization Code with PKCE.

GitHub web login uses the GitHub App web application flow. Native CLI and desktop onboarding use the GitHub App device flow when no safe browser callback is available. The native application is a public client: no GitHub App client secret or private key is embedded in distributed binaries. Server-side GitHub App credentials remain only in the hosted service secret boundary.

GitHub user access tokens use the minimum app permissions and expiring user-to-server tokens with refresh rotation when enabled and supported. Every completed authorization re-fetches and validates the provider subject before binding it to a VibeMaxxing transaction.

## OAuth transaction security

Every authorization transaction records a single-use server transaction ID, provider, intended account action, client instance, redirect target, creation/expiry and cryptographically random state. Requirements:

- authorization code flow only; no implicit flow;
- PKCE with `S256` whenever the provider supports it, and mandatory for public clients;
- exact pre-registered redirect URI matching; no wildcard or open redirect targets;
- state bound to the browser session and intended provider/action;
- issuer/provider binding to prevent mix-up;
- authorization code and device code are single-use and short-lived;
- browser completion cannot authorize an unbound daemon or CLI instance;
- device-flow polling honors provider intervals, expiry and `slow_down` behavior;
- access and refresh token rotation detects replay and revokes the affected token family or session;
- callback errors are generic to the user and contain no credentials, codes or provider tokens in logs or URLs;
- CSRF, login CSRF, account pre-hijacking, confused-deputy and provider-link substitution are negative fixtures.

Where a provider does not implement a standard protection, the provider profile records the compensating control and resulting assurance ceiling.

## Account model

An account may link multiple external identities. Store only the provider subject identifier, verified provider metadata required for display or recovery, timestamps, linkage state and minimal encrypted credentials when operationally required.

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

The link transaction binds both provider subjects, the current account, session, intent, state, expiry and reauthentication result. A provider callback may not select a different target account than the one bound at transaction creation.

Account merge must define ownership of usernames, devices, claims, boards, friendships, moderation state and deletion requests. Merge never duplicates competitive claims. The final remaining authentication provider cannot be unlinked until another recovery-capable method is confirmed.

## Optional stronger authentication tier

Optional factors may include passkeys, WebAuthn security keys or platform credentials. Require stronger reauthentication for:

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
- rotation on refresh and token-family replay detection;
- device/session labels and last-used timestamps;
- IP and user-agent data minimized and retained only under an explicit privacy policy;
- per-session revocation and revoke-all capability;
- notification on suspicious or recovery-related session changes.

Native authorization binds the user account, provider subject, local device identity, daemon instance and authorization transaction. Browser login completion returns only a one-time completion capability to the already bound local client; it does not expose provider credentials to the shell.

## Recovery

Preferred recovery order:

1. Another linked provider.
2. Optional enrolled passkey or hardware key.
3. Single-use recovery codes with hashed server-side verifiers.
4. Existing trusted session with risk controls.
5. Human appeal with cooling-off and limited restoration powers.

Recovery never silently transfers competitive identity based only on mutable profile information or support discretion.

Required controls:

- rate limits and abuse detection;
- cooling-off for high-risk recovery;
- notifications to existing providers, sessions and configured channels;
- revocation or reauthorization of existing sessions;
- explicit device-key review;
- privacy-safe credential event ledger;
- reason codes and appeal path;
- no access to prompts, source code, projects or local activity content during recovery.

## Provider compromise or loss

If a provider account is compromised, suspended, deleted or renamed:

- provider subject ID remains the linkage key;
- the user may recover through another linked method;
- high-risk identity changes enter a pending state;
- competitive activity may continue from already authorized devices under policy, but account-control changes are restricted;
- no new provider may be linked solely through an untrusted existing provider without reauthentication or recovery controls.

Provider revocation, token expiry, installation removal, permission reduction and account suspension are explicit events. They invalidate affected credentials and may require reauthorization without deleting the internal account.

## Authorization

Authentication does not imply authorization. Define explicit permissions for:

- public and private profiles;
- friendships and blocks;
- private boards;
- organization and community administration;
- moderation and appeals;
- device management;
- data export and deletion.

Every high-impact action is server-authorized, idempotent where relevant, logged with privacy-safe audit data and protected against CSRF, confused-deputy behavior, replay and stale sessions.

## Remaining implementation evidence

- X provider conformance against its current authorization, refresh and revocation behavior.
- Optional passkey library and browser/platform interoperability bakeoff.
- Account-merge UX and abuse simulations.
- Recovery false-positive and takeover simulations.
- GitHub App permission manifest and installation/user-token lifecycle fixtures.

## Primary references

- GitHub Docs, “Generating a user access token for a GitHub App.”
- GitHub Docs, “Refreshing user access tokens.”
- RFC 9700, “Best Current Practice for OAuth 2.0 Security.”
