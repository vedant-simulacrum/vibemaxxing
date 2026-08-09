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

### Provider configuration authority

`packages/schemas/oauth-provider-registry-v1.json` is the preconfigured provider-capability record. ADR-015 and `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` both make a control conditional on it — RFC 9207 issuer validation for a provider recorded as supporting it, the unique provider-specific redirect path for one that is not — and neither rule could be evaluated while the record existed only as a phrase. `packages/schemas/oauth-provider-registry-v1.schema.json` is its shape and `scripts/repository/validate_oauth_identity_contract.py` decides it.

| Concern | Owner |
|---|---|
| Provider row | `packages/schemas/oauth-provider-registry-v1.json` |
| Shape | `packages/schemas/oauth-provider-registry-v1.schema.json` |
| Vocabulary | one spelling of `github` and `x` across the registry, `linked_identities.provider`, `oauth_transactions.provider` and every `provider` enum in `packages/schemas/openapi-v1.yaml` |
| Mix-up corpus | `conformance/auth/provider-mixup-vectors-v1.json`, declared as cases in `conformance/auth/manifest.json` |

Each row carries the issuer, authorization and token endpoints, the reference the deployment reads the client identifier from, the exact redirect URI, the pinned PKCE method, the RFC 9207 and device-flow capabilities, the scope set, a monotonic revision and a bounded review date. The client identifier itself is never committed: it differs between the local build and production, so a literal would be wrong in one of them by construction.

Two properties are load-bearing rather than descriptive.

**A capability is an observation or it is not claimed.** Nothing in this repository has performed an authorization request against either provider, so both rows record `unverified` for RFC 9207 and for device flow, and the validator refuses a row that claims `supported` while its verification state says nothing was read. Recording `supported` without a reading would manufacture the very control ADR-015 relies on to close the mix-up attack. The consequence is deliberate: with the capability unverified, an absent `iss` is not a failure, and the binding that actually refuses a cross-provider callback is the unique provider-specific callback path.

**The `iss` parameter follows the capability, not the provider.** `/auth/github/callback` declared `iss` and `/auth/x/callback` did not, while `packages/schemas/reason-codes-v1.json` bound `OAUTH_ISSUER_MISMATCH` to both. The asymmetry read as a capability difference and rested on nothing. Both callbacks now declare it optionally, because both rows record the same capability, and the validator derives the requirement from the row: `supported` requires it, `unsupported` forbids it, `unverified` admits it as a comparison that is never required.

The mix-up corpus is decided rather than asserted. Each of the sixteen vectors is a callback observation the validator evaluates against the registry, and each of the fourteen refusals differs from its provider's accepted baseline in exactly one field, so a recorded reason code is attributable to one discriminator rather than to a generally malformed vector. The validator additionally mutates each discriminator itself against the committed registry, which is what catches a rule the evaluator stops applying even when every recorded vector still agrees with it.

### The OAuth transaction aggregate

The transaction is the only route by which a callback may change identity. `packages/schemas/planning-schema.sql`, table `oauth_transactions`, is the persistence owner; the `oauth-transaction` machine in `packages/schemas/state-machine-registry-v1.json` owns the lifecycle; `oauth_authorization_events` is the append-only ledger, and its `event_type` vocabulary is exactly that machine's transition identifiers.

| Concern | Owner |
|---|---|
| Lifecycle | the `oauth-transaction` machine |
| Persistence | `oauth_transactions`, `oauth_authorization_events` |
| Revision model | `oauth_transactions.revision`, monotonic |
| Transaction boundary | `oauth-and-session`: consuming the transaction and binding the session or the provider identity commit together |
| Expiry | `expires_at`; an unconsumed transaction reaches `expired` |
| Reversal | none. A consumed transaction is spent; a mistake is a new transaction |

The row records the provider, the provider-registry revision it agreed to, the issuer, the exact redirect, the pinned PKCE method, the state hash, the encrypted verifier, the intended action, the initiating account and web session, the recent-authentication instant, the result, the failure reason, the revision, the lifetime and the consumption instant. All of it is stored at creation and compared at callback. A callback-controlled value never selects the provider configuration, the issuer, the client configuration, the redirect URI or the token endpoint.

Four rules are check constraints because each is a race or an omission that application code loses:

- a `link-identity` transaction is startable only from an authenticated account and session under recent authentication, which is the reauthentication requirement above expressed where it cannot be skipped;
- a `link-identity` transaction never produces a session, so the linking flow cannot be used to mint browser access;
- a `consumed` transaction produced what its action names — a session for a sign-in, a linked identity for a link — so `consumed` cannot mean finished with no effect;
- a transaction that started on one account cannot finish on another, which is the silent reassignment `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` forbids.

**There is no standalone authorization-code path.** `linkIdentity` previously took a bare `authorization_code`, so identity could be mutated without reaching a transaction at all and therefore without verifying a redirect, a state, a PKCE verifier, a provider revision or a lifetime. Every control the transaction exists to apply was optional in practice. `linkIdentity` now names an `oauth_transaction_id`, and the two intended actions stop being the same operation at the callback: a sign-in callback consumes the transaction and mints access, while a link callback stops at `callback-received` and leaves the linking to `linkIdentity`, which is authenticated, CSRF-protected, recent-auth gated and idempotent — none of which a public callback can be. `unlinkIdentity` no longer shares that request body: it names the linked identity, because requiring an authorization code to remove a link is exactly wrong in the case where the provider account is what the participant has lost.

An ambiguous callback — one whose state matches no live transaction, whose transaction is already consumed, or whose transaction has expired — moves nothing and is refused with a registered reason code. The `state_hash` is unique, so two callbacks cannot both consume one transaction, and a partial unique index permits one live transaction per account, provider and action, so a returning callback has one stored state to match rather than a set.

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

### The linked identity aggregate

The linked provider identity is the second of the three aggregates AGENTS.md keeps apart: an account, a linked provider identity and a ranked identity are separate things with separate lifecycles, and this is the middle one. D-081 and the provider-loss section below are the rules it exists to carry.

| Concern | Owner |
|---|---|
| Lifecycle | the `linked-identity` machine in `packages/schemas/state-machine-registry-v1.json` |
| Persistence | `packages/schemas/planning-schema.sql`, table `linked_identities` |
| Client projection | `Identity.state` in `packages/schemas/openapi-v1.yaml` |
| Revision model | `linked_identities.revision`, monotonic |
| Transaction boundary | `identity-and-oauth-transaction` for a link, `identity-and-session` for an unlink or a compromise report |
| Reversal | `unlink-pending` returns to `linked`; `recovery-pending` returns to `linked` when the recovery is cancelled or denied. `unlinked` and `superseded` are terminal |

The eight states are `candidate`, `linked`, `unlink-pending`, `lost`, `compromised`, `recovery-pending`, `unlinked` and `superseded`. Two are terminal. The table previously held three — `linked`, `unlink-pending`, `unlinked` — and the aggregate bound no machine at all, under a recorded absence saying the enrollment flow owned its transitions and they were unspecified. Three states cannot express any of what the provider-loss section below requires, so that section described behaviour the schema had nowhere to put.

`provider_subject` is the durable linkage key while the binding is live, and is never a username. `provider_account_created_at` is the D-081 gate input, captured at link time from the provider; nothing persisted it before, so the 90-day gate had no stored value to be evaluated against.

**Unlinking was silently permanent, and the privacy commitment and the uniqueness constraint could not both be honoured.** `docs/privacy/DATA_MAP.md` retains both fields "until unlink or account erasure" and deletes the subject "immediately on unlink". `provider_subject` was `not null`, so that promise could be kept only by deleting the whole row — and the row could not be deleted, because a total `unique (provider, provider_subject)` meant the retained `unlinked` row blocked that provider account from ever being linked again, to this account or to any other. Both fields are now null exactly when the binding has ended, which turns the retention rule into a constraint rather than something a worker has to remember, and the uniqueness is partial over the six live states so that the rule it encodes — one live binding per provider subject, never a silent reassignment, which `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` states in prose — is visible where a reader looks rather than resting on how the engine treats nulls. A second partial index permits one live identity per account and provider.

**The last-authentication-method invariant is not a constraint, and this says so rather than implying one.** An account must always retain at least one usable authentication method, so an unlink is refused when it would remove the last. That is a count across sibling rows, which no `check` and no unique index can express, and inventing a counter column on `accounts` would make a cached number a second authority for a fact the rows already hold. It is therefore carried in two places that a validator can compare: the guard is named in the machine, as the action `request-unlink-unless-last-authentication-method` on the transition into `unlink-pending`, and it is stated here. `scripts/repository/validate_oauth_identity_contract.py` fails when either half goes missing. It is enforced inside the transaction that performs the unlink and it is a serialization requirement, not a convenience check.

The guard sits on the *request* rather than on the apply, because `unlinked` is terminal: there is no transition out of it, so an unlink that removed the last method would lock the account out permanently and irreversibly. `superseded` is reachable only by a worker acting on a later binding of the same subject; no participant action and no other account's moderator can drive a live identity into either terminal state.

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

Recovery must never silently transfer competitive identity based only on mutable profile information or support discretion.

### The set is finite and exhausting it is permanent

There is no fifth step. This list previously ended with "human appeal with cooling-off and limited restoration powers", and D-561 removed it: exhausting every enrolled device and every recovery code permanently ends the ranked identity, with no appeal transition and no support path that can restore it. The `recovery-case` machine below carries no transition that reaches an applied recovery from a `verified_factor_class` of `none`, which is that decision expressed as a reachability property rather than as guidance.

The reason is stated rather than implied. An appeal path that cannot be staffed by a solo operator is a promise the product would break under its first real load, and a wall stated in advance is kinder than a queue that never drains. It reopens if a funded support function exists to adjudicate recovery appeals.

Because it is unappealable it has to be disclosed before it can be triggered, not after. The enrolment surface renders the warning on the same view that issues the recovery codes — not in a help page, not on a later settings screen — so nobody can lose the set without having been told what losing it costs.

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

The controls above are requirements. The aggregate that carries them is the recovery case, and D-380 records the choices inside it.

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
