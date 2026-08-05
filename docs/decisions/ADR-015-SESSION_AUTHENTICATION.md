# ADR-015: Session authentication

Status: accepted
Date: 2026-08-06
Decision: D-028, D-036, D-055, D-081

## Context

This number was reserved for the session authentication scheme and left empty, which is why ADR-016 was authored before it. `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` unit PF-039 names this file as its first deliverable. Leaving it empty had a cost beyond a gap in a sequence: the repository holds two incompatible descriptions of how an authenticated request works, and neither one can be implemented while the other stands.

`docs/security/AUTHENTICATION_AND_RECOVERY.md` specifies secure, HTTP-only, same-site cookies for web, explicit native-device session tokens for CLI and daemon clients, short-lived access tokens with bounded refresh, rotation on refresh, replay detection, per-session revocation and revoke-all.

`packages/schemas/openapi-v1.yaml` declares one `securitySchemes` entry — `bearerAuth`, `type: http`, `scheme: bearer`, `bearerFormat: opaque` — applied globally, with no cookie scheme, no OAuth2 flows, no scopes, and no refresh operation among its paths.

Those are two different architectures. A browser client cannot present a bearer header it was never issued, and a daemon cannot hold a browser cookie. `packages/schemas/state-machine-registry-v1.json` already carries the shape the contract implies and the API cannot express: `web-session-family` and `native-session-family` each have `active`, `rotating`, `replay-detected`, `revoked` and `expired`, and `replay-detected` has no persistence owner today.

The surrounding decisions are fixed and this ADR works within them. D-028 makes OAuth the primary account-access mechanism with passkeys and hardware credentials as optional stronger factors. D-036 fixes GitHub to a GitHub App using web and device authorization and X to OAuth 2.0 authorization code with PKCE. D-055 fixes GitHub and X as the launch providers. D-081 adds a 90-day minimum provider-account age, which requires the authorization exchange to read and persist a provider-reported account creation timestamp. D-015 already establishes revocable Ed25519 device keys with sequence and hash continuity, so the native client holds a signing key before it holds a session.

Being deliberately multi-provider is the security fact that shapes the rest. A client that talks to more than one authorization server is exposed to the mix-up attack, in which an attacker induces the client to send an authorization code issued by one provider to a different provider's token endpoint. PKCE does not stop it. The control that does is RFC 9207, which returns an `iss` parameter in the authorization response for the client to compare against the provider it started the transaction with.

### Citations this ADR pins deliberately

- **RFC 9700, *Best Current Practice for OAuth 2.0 Security*** is the normative OAuth reference used here. It is a published BCP that updates RFC 6749, RFC 6750 and RFC 6819. `https://www.rfc-editor.org/info/rfc9700`
- **"OAuth 2.1" is not cited anywhere in this repository as a normative reference.** `draft-ietf-oauth-v2-1` remains an Internet-Draft, at revision -15 dated 2026-03-02, and has not reached the IESG. An Internet-Draft is a working document that may be updated, replaced or obsoleted at any time, so a normative contract that cites it cites a moving target. RFC 9700 carries substantially the same requirements in a stable document. `https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/`
- **RFC 9207, *OAuth 2.0 Authorization Server Issuer Identification***, Proposed Standard. `https://www.rfc-editor.org/info/rfc9207`
- **RFC 8628, *OAuth 2.0 Device Authorization Grant***, for the GitHub App device path named by D-036. `https://www.rfc-editor.org/info/rfc8628`
- **RFC 6819**, threat model and security considerations, for the session-fixation and token-substitution classes. `https://www.rfc-editor.org/info/rfc6819`
- **W3C Web Authentication Level 2 is the stable Recommendation** and is the normative citation for the optional passkey factor. **Web Authentication Level 3 is a Candidate Recommendation, not a Recommendation**; where a Level 3 behaviour is relied upon, the citation is the dated Candidate Recommendation Snapshot of 2026-05-26 and never the undated `/TR/webauthn-3/` URL, because the undated URL tracks a document that is still subject to change.

## Decision

Sessions are server-side records addressed by opaque handles. There are two families, matching the two machines already in the state registry, and one issuance path shared between them.

### Token format

Every access and refresh handle is 256 bits from a cryptographically secure random source, encoded base64url without padding, and carries no encoded claims. Handles are stored as SHA-256 digests server-side, so a database read does not yield a usable credential. A handle is a lookup key into a session record holding the account, the session family, the family generation counter, the issued and last-used timestamps, the expiry, the device enrollment where one applies, and the revocation state.

Self-contained tokens are rejected for this role. The repository requires per-session revocation, revoke-all, and replay detection with immediate effect; a self-contained token remains valid until its own expiry regardless of server state, which makes immediate revocation unachievable without a server-side lookup that removes the reason to use a self-contained token in the first place.

The existing `bearerAuth` declaration with `bearerFormat: opaque` is therefore correct as far as it goes and is retained. What is wrong is that it is the only scheme and that it is applied globally.

### Web session family

The browser holds two cookies, both `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`, and both using the `__Host-` prefix so they cannot be set by a sibling subdomain or scoped to a wider domain:

- `__Host-vm_session` carries the access handle. It is valid for 15 minutes from issue.
- `__Host-vm_refresh` carries the refresh handle. It is valid for 30 days from issue and the family is capped at 90 days absolute from first authentication, after which reauthentication with the provider is required.

`SameSite=Lax` rather than `Strict` is chosen because the OAuth redirect returns by top-level navigation, which `Lax` permits and `Strict` blocks for the cookie carrying the transaction binding. Every state-changing request additionally requires either an `Origin` header matching an exact allowlisted origin or a double-submitted CSRF token bound to the session record; the cookie attribute is not treated as the whole cross-site defence.

### Native session family

CLI, daemon and interactive-shell clients present the access handle in an `Authorization: Bearer` header under the retained `bearerAuth` scheme. The access handle is valid for 15 minutes; the refresh handle is valid for 30 days sliding with no absolute cap, because a headless daemon that silently stops collecting after 90 days is a worse outcome than a long-lived binding to a revocable enrolled key.

Native handles are sender-constrained. A bearer handle alone is not sufficient to authenticate a native request. Each request carries a `VibeProof-Device-Proof` header holding a COSE_Sign1 detached signature, produced by the enrolled Ed25519 device key of D-015, over a canonical binding of the HTTP method, the request path with query, the SHA-256 digest of the body, the session handle digest, a millisecond timestamp and a 128-bit nonce. The server rejects a proof whose timestamp is outside a 300-second window, whose nonce it has already seen inside that window, or whose signing key is not the key bound to that session record. A stolen handle without the device key is unusable, which is the property RFC 9700 asks for from a sender-constrained token, obtained here from a primitive the product already ships rather than from a second one.

This reuses the deterministic COSE and Ed25519 stack that D-011 and D-090 already make launch-blocking, so it introduces no new cryptographic dependency.

### Binding to device enrollment

A native session record names exactly one `device-enrollment` aggregate and one device public key. The binding is established during native authorization, is immutable for the life of the session record, and is checked on every request.

Browser login completion never authorizes an unbound local process. Native authorization runs as a distinct transaction: the daemon generates the enrollment key, presents the enrollment public key and a user-visible verification code, the browser leg authorizes that exact code and key, and the token exchange returns a session bound to that key. A native session cannot be created by any path that does not carry an enrollment key.

When a device enrollment leaves `active` — to `quarantined`, `revoked` or `deleted` — every native session bound to it moves to `device-revoked` on the next request or on the revocation event, whichever comes first. `device-revoked` exists in `native-session-family` and does not exist in `web-session-family`, which is correct: a web session is bound to a browser, not to an enrolled device.

### Refresh and rotation

Refresh is one-time-use. Presenting a refresh handle moves the family to `rotating`, atomically consumes the presented handle, and issues a new access and refresh pair in the same transaction with the family generation counter incremented. Refresh of a native session additionally requires a valid device proof from the bound key.

Presenting a refresh handle that has already been consumed is a replay. The family moves to `replay-detected`, every handle in the family — every generation, access and refresh alike — is revoked immediately, and the account owner receives a server-inbox security notice. This is RFC 9700's refresh-token replay-detection requirement, and it is why `replay-detected` needs a persistence owner rather than existing only in the registry.

Rotation is not a heuristic. Every refresh rotates, so a handle observed twice is always an incident and never an artifact of a benign race. A client that loses the response to a refresh must reauthenticate; the alternative — a grace window in which the old handle stays valid — is the exact condition under which replay detection stops detecting.

### Revocation

- A user may revoke one session, or all sessions, from any authenticated session.
- Revocation is immediate. It writes the revocation state on the session record, and because handles are lookups rather than assertions, the next request fails.
- Password-equivalent events — unlinking a provider, changing a recovery method, completing an account recovery, or a successful appeal that restores an account — revoke every session family for the account.
- A device enrollment leaving `active` revokes its bound native sessions.
- A sanction that restricts an account under D-084 does not by itself revoke sessions, because the sanctioned participant needs an authenticated session to read the private notice and file an appeal.

### The authorization exchange

Every provider authorization uses the authorization code grant, tracked by the existing `oauth-transaction` machine through `created`, `redirected`, `callback-received`, `consumed`, and terminating in `expired` or `failed`.

Binding requirements, all of which are enforced by the client leg and none of which are optional:

- **PKCE with `code_challenge_method=S256` only.** A transaction presenting `plain`, or presenting no challenge, moves to `failed`. The verifier is 43 to 128 characters from a cryptographically secure random source.
- **RFC 9207 issuer validation.** The client records the expected issuer when it creates the transaction and compares it against the `iss` returned in the authorization response. A mismatch moves the transaction to `failed` and the code is never sent to any token endpoint. Because both launch providers are known to the client at transaction creation, an authorization response arriving without an `iss` for a provider recorded as supporting it is also a failure rather than a fallback to unvalidated behaviour. This is the control that closes the mix-up attack, which PKCE alone leaves open, and it is load-bearing precisely because the product is multi-provider by decision.
- **Exact-string redirect URI matching.** The registered redirect URI is compared by exact octet equality. No prefix match, no wildcard, no path-suffix append, no scheme or port coercion.
- **Single-use authorization codes** with a 60-second lifetime, bound to the transaction, the client and the PKCE verifier. A second presentation of a code moves the transaction to `failed` and revokes anything issued from the first presentation.
- **`state` is bound to the browser session**, single-use, 128 bits of entropy, 10-minute lifetime, and is checked in addition to PKCE rather than instead of it.
- **No implicit grant, no resource-owner password credentials grant, and no bearer credentials in query strings**, per RFC 9700.

The GitHub App device authorization path of D-036 cannot use PKCE or a redirect URI, because RFC 8628 has neither. It is constrained instead by binding the device code to the enrolling device public key at initiation, displaying the user code and the enrollment fingerprint together for the user to compare, polling no faster than the interval the provider returns, and expiring the device code after 15 minutes. A device authorization that completes without a matching enrollment key produces no session.

The provider access token obtained by the exchange is used once, server-side, to read the provider account identifier and the account creation timestamp that D-081 requires, and is then discarded. No provider refresh token is retained, and no provider credential is stored at rest. Where a provider requires ongoing access for a later feature, that is a separate decision with its own custody analysis and is not authorized by this ADR.

### Optional stronger factors

Passkeys and hardware security keys remain optional additional factors under D-028, using Web Authentication Level 2 as the normative reference. They are required for reauthentication before the sensitive operations already listed in `docs/security/AUTHENTICATION_AND_RECOVERY.md` when the account has one enrolled. Where a Level 3 behaviour is relied upon, the dated 2026-05-26 Candidate Recommendation Snapshot is the citation, and a Level 3 behaviour is never a precondition for authenticating, because a Candidate Recommendation may change before it becomes a Recommendation.

## Required OpenAPI content

PF-039 carries the edit to `packages/schemas/openapi-v1.yaml`. This ADR states its exact content so that the edit is transcription rather than interpretation:

- `bearerAuth` is retained unchanged: `type: http`, `scheme: bearer`, `bearerFormat: opaque`.
- `sessionCookie` is added: `type: apiKey`, `in: cookie`, `name: __Host-vm_session`.
- `deviceProof` is added: `type: apiKey`, `in: header`, `name: VibeProof-Device-Proof`.
- The global `security` block is removed. Each operation declares its own requirement: browser operations require `sessionCookie`; native operations require `bearerAuth` and `deviceProof` together, expressed as a single requirement object so that neither satisfies the operation alone; public operations declare an empty requirement explicitly rather than inheriting one.
- A refresh operation exists, accepting the refresh handle from the `__Host-vm_refresh` cookie for browsers or from the request body for native clients, and returning rotated credentials.
- Session-listing, single-session revocation and revoke-all operations exist.
- The `replay-detected` and `device-revoked` states are representable on the session resource, and `packages/schemas/planning-schema.sql` carries the matching CHECK vocabulary in the kebab-case spelling D-079 requires.

## Consequences

- The contradiction between `docs/security/AUTHENTICATION_AND_RECOVERY.md` and `packages/schemas/openapi-v1.yaml` is resolved in favour of both being right about their own client: cookies for browsers, sender-constrained bearer handles for native clients, one issuance and revocation model behind them.
- `replay-detected` and `device-revoked` acquire a persistence owner, so two registry states stop being unreachable.
- Every authenticated request costs one server-side session lookup. This is a deliberate trade of throughput for immediate revocation, and it makes the session store a hot path that the ranking projections do not touch.
- Native clients acquire a per-request signing cost and a required clock within 300 seconds of the server. A daemon with a badly skewed clock cannot authenticate, which is a visible failure rather than a silent downgrade.
- Rotation without a grace window means a client that crashes between sending a refresh and persisting the response must reauthenticate. For the daemon this is a user-visible prompt, and it is accepted because a grace window defeats replay detection.
- The 90-day absolute cap on web families forces periodic reauthentication with the provider, which is also the point at which a revoked or renamed provider account is noticed.
- Storing the provider account creation timestamp under D-081 adds a personal-data field. It belongs in the data map, the export bundle and the erasure path, and those edits are owned by the privacy contract and the deletion unit rather than by this ADR.
- No claim of unique humanity follows from any of this. OAuth proves provider-account control, and a 90-day-old account is an older account and nothing more.

## What would cause this to be revisited

- **RFC 9700 is obsoleted or materially updated**, or `draft-ietf-oauth-v2-1` reaches RFC status, at which point the normative citation moves and the requirements are rechecked against the published text.
- **Web Authentication Level 3 reaches Recommendation**, at which point the dated snapshot citation is replaced by the Recommendation and Level 3 behaviours become available as preconditions rather than enhancements.
- **A launch provider withdraws or changes a flow** — RFC 9207 support, the GitHub App device path, or the account creation timestamp field — which reopens both this ADR and D-081.
- **Measured evidence that the per-request session lookup is the ranking-path bottleneck.** The response is a cache with a bounded revocation propagation delay, and adopting it requires stating that delay as a security property rather than as an implementation detail.
- **A measured rate of daemon reauthentication prompts caused by rotation without a grace window** that is high enough to damage collection continuity. The response is not a grace window; it is a durable client-side write of the refresh response before the old handle is discarded.
- **An observed replay that the 300-second proof window admits**, which narrows the window and tightens nonce retention.
- **A second maintainer joins**, which makes the dual-control obligations on session-signing and release keys satisfiable and reopens the key-custody assumptions this ADR inherits from D-091.
