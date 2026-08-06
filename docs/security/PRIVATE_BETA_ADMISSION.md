# Private Beta Admission: Invite Codes

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-180, D-280, D-281, D-282, D-283, D-284, D-285, D-286, D-287, D-288

## What this document owns

D-180 fixes that private-beta access is by invite code issued directly by the owner, with no public signup, no open registration and no self-service waitlist. It also recorded that nothing specified the mechanism. This document is that mechanism, and it is the single normative owner of:

- the invite code's format, entropy, normalisation and storage;
- issuance, quota, expiry and revocation;
- redemption, and the constraints that make a single-use code single-use under concurrency;
- the order in which the admission gates are evaluated and which failure surfaces which reason code;
- what an invite proves and what it does not.

It does not own the schemas it describes. `packages/schemas/state-machine-registry-v1.json` owns the `invite-code` lifecycle, `packages/schemas/planning-schema.sql` owns `invite_codes` and `invite_redemptions`, `packages/schemas/openapi-v1.yaml` owns `redeemInvite`, `packages/schemas/reason-codes-v1.json` owns the three reason codes, and `docs/privacy/DATA_MAP.md` is the Article 30 record for the personal data the mechanism creates. Where this document and one of those disagree, the schema is correct and this document is the defect.

It does not own rate limiting. `docs/architecture/API_EDGE_CONTRACT.md` owns the classes and the numbers; this document binds redemption to a class that already exists rather than introducing one.

Nothing here is implemented. No code has been issued, no redemption has been executed, and no sweeper exists.

## What an invite proves, and what it does not

An accepted redemption proves exactly one thing: **the owner chose to admit this account.** It is admission control.

It is not proof of humanity. It is not a Sybil control on its own. A person who obtains two codes holds two admitted accounts, and nothing in the redemption path detects that. The invite is a Sybil control only to the strength of the issuer's own judgement about who they hand a code to, which is a human control and not a technical one, and it produces no verifiable property that any later process can check. Under D-100 no provider offers a usage-attestation path for an individual account, so admission cannot be upgraded into evidence about the person behind it. The technical load against duplicate identities is carried where it already sits: the one-active-ranked-identity rule of D-054, the duplicate and consolidation handling in `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`, and the confidence weight of ADR-020.

Stating this matters because an invite-only ring reads as a stronger integrity claim than it is. It bounds the population. It does not authenticate it.

## The code

**Format.** 125 bits drawn from a cryptographically secure random source, encoded in Crockford base 32 as 25 characters, displayed in five hyphen-separated groups of five. The Crockford alphabet excludes `I`, `L`, `O` and `U`, so the characters a person most often mistypes are never generated.

**Normalisation.** Before hashing, the server uppercases the input, removes hyphens and whitespace, and applies the Crockford confusable folding that maps `I` and `L` to `1` and `O` to `0`. The canonical form is the resulting 25-character string. The folding costs no entropy, because the folded characters are outside the generating alphabet; it exists so that a transcription error in exactly the characters people confuse is accepted rather than refused. `InviteRedemptionRequest.invite_code` accepts the display form with or without its hyphens and in any case.

**Storage.** The code is never stored. `invite_codes.code_hash` is SHA-256 over `'vibemaxxing-invite-v1' || 0x00 || canonical_code`, and the column is unique. A leaked database yields 32-byte digests and no usable code.

The digest is a plain hash rather than a memory-hard derivation, and that is a decision rather than an omission. A memory-hard derivation defends a low-entropy secret against offline search. This secret carries 125 bits, so an offline search is not the threat; what a slow derivation would cost is the redemption lookup, which must be an index probe on `code_hash` and would otherwise become a scan over every live code with one derivation per row. The domain separator is present so that a digest from this table can never be confused with a digest computed for another purpose over the same bytes.

**What the code is not.** It is not a bearer token for the API, it authenticates nothing, and presenting it never produces a session. It is redeemed by an already-authenticated account and its only effect is to write the redemption row.

## Issuance

Issuance is owner-only and is an operator action, not an HTTP operation.

The owner runs the operations tool, which draws 125 bits, renders the display form once to the terminal, writes `invite_codes` with `state = 'issued'`, and discards the plaintext. The tool never writes the code to a file, a log or the database. If the owner loses the displayed value before sending it, the code is revoked and a new one is issued; there is no recovery path, because a recovery path would require storing the code.

**No administrative API operation exists, and none is added here.** `packages/schemas/openapi-v1.yaml` contains no administrative surface at all: every operation is either public or authenticated as an ordinary participant, and there is no role, scope or moderator session anywhere in the document. Adding an issuance operation would mean inventing that authorization model for one endpoint, and an authorization model invented for one endpoint is the kind of thing that is later reused by three. The owner is the only issuer, has direct database access under D-091, and does not need an API to reach it.

**Quota.** At most `invite_outstanding_max` codes may be in state `issued` at any moment; the default is 200, which is the private-beta population `docs/architecture/API_EDGE_CONTRACT.md` derives its rate limits from. There is no per-code use quota, because there is no multi-use code.

The quota is enforced by the issuing tool and **is not a database constraint**, which is a real asymmetry with the single-binding rule below and is recorded rather than glossed. PostgreSQL cannot express "at most N rows in this state" without a trigger or a counter table, and a trigger that exists only to bound the owner's own issuance rate is a moving part with no adversary. The consequence is that a mistake by the owner can exceed the quota and nothing will stop it. The guessing arithmetic below is stated against the quota, so exceeding it weakens that arithmetic in proportion and does not break it.

**Single-use only. Multi-use codes are rejected.** A multi-use code is a shareable link: one forward and invite-only becomes open registration, silently, with no event anyone would notice. Expressing the owner's quota as the number of codes issued rather than as a use count on one code also makes the ring size equal to the number of rows in a table, which is a quantity that stays true without anyone re-reading a configured number.

## Expiry and revocation

**Expiry** is `invite_code_expiry_days` from issue, default 14. The owner sends every invite to a person they have already contacted directly, so a code unused after two weeks is far more likely to be a message that never arrived than an acceptance still in flight. The window also bounds the standing set of live codes, which is the quantity the guessing arithmetic depends on. A sweeper moves an unredeemed code from `issued` to `expired` through `beta-invite-expire`; `invite_codes_expiry_idx` is the partial index it reads.

**Revocation** applies to an `issued` code only, through `beta-invite-revoke`. A redeemed code cannot be revoked. Withdrawing a participant's access after they have been admitted is a restriction of their account under the `account-lifecycle` machine, decided and appealed under the moderation contract; routing it through the invite would give one aggregate authority over another's lifecycle and would leave the account in a state no machine describes.

Both `expired` and `revoked` are terminal. Neither returns the code value to circulation: the row and its `code_hash` uniqueness survive, so the same 125-bit value can never be issued twice even by accident.

## Redemption

`POST /invites/redeem`, `redeemInvite`. It is authenticated as an ordinary account, requires recent authentication, carries an `Idempotency-Key` under the document's idempotency contract, and returns `InviteRedemption`.

Recent authentication is required because redemption is irreversible and spends a scarce resource the owner issued by hand. In the ordinary flow the participant authenticated seconds earlier, so the requirement costs nothing; what it buys is that a session stolen and used weeks later cannot burn an invite.

### The transaction

One serializable transaction:

1. normalise and hash the presented code;
2. select the `invite_codes` row by `code_hash` for update;
3. insert `invite_redemptions (invite_code_id, account_id, redeemed_at)`;
4. update the code row to `state = 'redeemed'`, set `redeemed_at`, increment `revision`;
5. commit.

### Why two concurrent redemptions cannot both succeed

Because the outcome is unrepresentable, not because the worker is careful.

`invite_redemptions.invite_code_id` is the **primary key**. Two concurrent redemptions of one code attempt two inserts of the same key; exactly one commits and the other takes a unique violation, whatever isolation level the transaction ran at and whether or not the row lock in step 2 was taken. The lock makes the losing transaction fail early and cleanly; the key is what makes it fail at all.

`invite_redemptions.account_id` is **unique**. One account cannot accumulate redemptions, so a participant who obtains two codes cannot stack them, and a retry that races itself cannot produce a second row.

Neither property is stated anywhere as a rule a service must obey, which is deliberate: a rule stated in prose is enforced by whoever read it, and these two are enforced by the database.

The state column is a consequence rather than the control. The check constraints on `invite_codes` bind the state to the timestamp set — a `redeemed` row has `redeemed_at` and no `retired_at`, a `revoked` row has `revoked_at`, a `retired` row has both `retired_at` and `redeemed_at` — so a row cannot claim one lifecycle while recording another.

### Failures

| Condition | Status | Reason code |
|---|---:|---|
| Code unknown, expired, revoked, or already redeemed by any account | 422 | `INVITE_CODE_NOT_REDEEMABLE` |
| The calling account already holds a redemption | 409 | `INVITE_ALREADY_REDEEMED` |
| An authenticated account with no redemption calls a gated operation | 403 | `INVITE_REQUIRED` |

**One code covers four conditions on purpose.** Distinguishing "no such code" from "expired" from "revoked" from "already redeemed" turns the endpoint into an oracle over the code space and tells the holder of one code things about the ring they were not told: that a forwarded code was already spent discloses that someone else was invited, and a live-versus-absent distinction is the signal a search would optimise against. The four are one answer and the answer is the same.

**One code is deliberately distinguishable, and it is safe.** `INVITE_ALREADY_REDEEMED` is a statement about the caller's own account, which the caller can observe anyway by being admitted. It exists so that a participant who retries a redemption they already completed is told what happened rather than told their code is bad.

## The admission gate

An account with no `invite_redemptions` row is authenticated and not admitted. Every authenticated operation answers 403 with `INVITE_REQUIRED`, with six exceptions:

- `redeemInvite`, which is how the state is left;
- `getMe`, so the participant can see what the controller holds, which is Article 15;
- `requestExport` and `requestDeletion`, which are Articles 20 and 17;
- `listSessions` and `revokeAllSessions`, so a participant who signed in by mistake can end it.

The exceptions are not a convenience. Articles 15, 17 and 20 of Regulation (EU) 2016/679 do not wait on an admission decision, and a product that took a person's provider identity and then refused them the routes to see or erase it would be creating a data subject with no rights.

`updateMe` is deliberately **not** exempt, which is the one place a rights argument is answered with a product one. The only fields an un-admitted account could rectify are the handle and the display name, and the handle is a scarce competitive name that `account_handles` holds uniquely. Admitting `updateMe` before redemption would let anyone who can complete an OAuth exchange reserve handles they will never compete under, which is precisely the thing an admission boundary exists to stop. An account with no redemption holds a handle it was assigned and nothing else to correct, and Article 16 becomes reachable the moment it is admitted.

`INVITE_REQUIRED` binds to the `authenticated` operation class in `packages/schemas/reason-codes-v1.json`, which says the code may appear on an authenticated operation; this list is which ones it does not.

`AccountProfile.admitted` carries the state, so a client renders the redemption screen without first provoking a 403. It is a boolean and not a lifecycle: the `invite-code` machine has five states and the account is told none of them.

## Gate order

Three checks stand between a person and an admitted account. They are separate, they are evaluated in a fixed order, and the order is not the cheapest-first one.

**1. Age floor, D-103, before the authorization flow starts.** The minimum age is 16 everywhere. It is a self-declared affirmation presented before `startGitHubAuth` or `startXAuth` is called, and no date of birth is collected or stored, which is the whole point of a uniform floor. **A refusal surfaces no reason code**, because the flow does not start: no provider request is made, no transaction row is written, and nothing about the person reaches the server. A gate that refuses by never asking is the only one of the three that costs the refused person no disclosure at all, which is why it is first.

**2. Provider account age, D-081, at the OAuth callback.** A linked provider account must be at least 90 days old, measured from the provider-reported creation timestamp, which arrives during the authorization exchange. Failure is 422 `PROVIDER_ACCOUNT_TOO_NEW` at `completeGitHubAuth`, `completeXAuth` and `linkIdentity`. This gate already exists and this document does not change it.

**3. Invite redemption, D-180, after authentication.** Evaluated last, on an account that exists.

### Why the invite is last

The invite check is the cheapest of the three and it runs last anyway.

If a code could be presented before authentication, the response would be a pure function of the code and the endpoint would be a free oracle: an attacker probes the space at whatever rate the edge allows, learns nothing per attempt but pays nothing either, and a per-account lockout has no account to attach to. Requiring an authenticated account first makes every guess cost one completed OAuth exchange against a provider account that is itself at least 90 days old, so the price of a guessing campaign is a supply of aged GitHub or X accounts rather than a supply of HTTP requests. That is a far worse trade for the attacker and it is bought entirely by ordering.

### What each failure discloses

The order also decides what each refusal leaks, and the analysis runs in both directions.

`PROVIDER_ACCOUNT_TOO_NEW` is reachable by anyone with a provider account, invited or not, because it is evaluated before the invite is ever considered. It therefore says nothing about the invite ring — it does not reveal that a beta exists, that the caller was invited, or that anyone was. It does reveal that the caller's provider account is under 90 days old, which is a fact about an account the caller controls and can read on the provider's own profile page.

`INVITE_REQUIRED` is reachable only by an authenticated principal, so it is a statement to a person about their own account rather than a statement about a stranger's. No unauthenticated party can use this surface to learn whether an account exists, because the surface refuses them before it looks.

`INVITE_CODE_NOT_REDEEMABLE` discloses nothing about any account, by construction, and nothing about the code beyond the fact that it did not work.

Reversing the order would break all three of those properties at once. An invite check placed first would have to answer an unauthenticated caller, which means answering with the existence or non-existence of a code, and an account-age check placed after an invite check would tell a code holder that their provider account, specifically, is what stopped them — which is a fact about a person the ring can then be reasoned about from.

## Guessing, rate limits and lockout

Three controls, and the first one does most of the work.

**Entropy.** 125 bits. At most `invite_outstanding_max` = 200 codes are live at once, so a uniformly random guess hits a live code with probability about 200 / 2^125, which is roughly 5 × 10^-36.

**Rate limit.** Redemption is charged to the **`auth-start`** class of `docs/architecture/API_EDGE_CONTRACT.md`: 10 per hour, burst 10, keyed on the `address` principal — the full IPv4 address or the IPv6 /64. It is bound to that class rather than to `authenticated-read` or `social-mutate` because the adversary here is an address cycling through accounts rather than an account, and `auth-start` is already the admission-flow class and already keyed the right way. No new number is introduced.

At 10 attempts an hour, one address makes about 87,600 attempts a year. Against 200 live codes in a 2^125 space that is a probability near 4 × 10^-31 of hitting anything in a year of continuous, uninterrupted guessing. The rate limit is not what makes the search hopeless; the entropy is. The rate limit is what stops the search from costing the service anything while it fails.

**Lockout.** After `invite_redemption_failure_lockout_attempts` = 5 consecutive failed redemptions, an account cannot attempt redemption for `invite_redemption_lockout_hours` = 24. Five is set from what a person transcribing a code needs rather than from what an attacker can afford: the confusable folding already absorbs the common transcription errors, so a participant who has typed it wrong five times has the wrong string rather than a typo, and the person who sent them the code is the owner, who is reachable because the ring is 200 people and one maintainer.

The lockout counter is **edge-side state, held with the rate-limit buckets, and is not a persistence owner**. It has no table in `packages/schemas/planning-schema.sql` and no row in `packages/schemas/data-disposition-v1.json`, exactly as the token buckets do not, because it is a counter that may be lost on restart with no consequence beyond a locked-out participant becoming unlocked early.

## Deletion, erasure, and why an invite is never recycled

When an admitted account is deleted, or erased under Article 17, one transaction does both of the following:

1. the `invite_redemptions` row is **deleted**, because that row is the only stored edge between the issuer and the invitee and it is personal data about the invitee;
2. the `invite_codes` row moves from `redeemed` to `retired` through `beta-invite-retire`, which is terminal.

The order matters and the outcome is the point: **the edge disappears and the invite does not return to the pool.** If the redemption row were deleted without retiring the code, the code would become redeemable again, and deleting an account would become a way to recycle an invite — either by the participant themselves, or by anyone the code had been shared with before it was spent. If the code stayed in `redeemed` with no redemption row, the state would be a lie: `redeemed` means bound to exactly one account and there would be no account.

`retired` therefore means: this code was spent, the account that spent it no longer exists, and it can never be spent again.

The retained `invite_codes` row names the issuer, an issue time, an expiry, a redemption time, a retirement time and a 32-byte digest. It names **no invitee**. That is why the erasure does not need to reach it, and why `packages/schemas/data-disposition-v1.json` classifies it `non-personal` with an erasure action of `retain-unlinked` while `invite_redemptions` is `personal` with an erasure action of `delete`.

The retention of the code row is indefinite and that is deliberate: it is the record that a 125-bit value has been used, and deleting it would allow that value to be issued a second time.

## The issuer-to-invitee edge

An invite code links the owner to the invitee. That is a social-graph edge held by the controller and it is a processing activity in its own right, recorded in `docs/privacy/DATA_MAP.md` under Account and identity.

**Basis.** Article 6(1)(a) consent, as part of account creation, which is the purpose D-101 already binds to consent. It is not Article 6(1)(f): the edge exists to admit the participant to the product rather than to secure it, and D-101 confines the legitimate-interests basis to security and fraud prevention.

**Retention.** Life of the account. The row is deleted on account deletion and on erasure, as above.

**The issuer is not disclosed to the invitee.** `InviteRedemption` carries no issuer field and neither does any other response shape. Today there is exactly one issuer, so disclosing it would disclose nothing the participant does not already know — and that is precisely the argument against adding the field, because it is safe only because of a fact that is expected to change. A field whose privacy properties depend on the population being one is a field that becomes wrong the day a second issuer exists.

**There is no invite chain, and none is retained.** Participants cannot issue invites. The graph is depth one, owner to invitee, and `invite_redemptions` holds it as a single row per admitted account. Nothing accumulates across redemptions, no ancestry is recorded, and after an erasure nothing about the invitee survives in either table.

## Evidence

Nothing here is implemented and none of it has been executed.

- No invite code has been generated, and no generator exists.
- No redemption has run. The constraints were exercised serially against a real `postgres:16` while this document was written — a second redemption of one code, a second redemption by one account and a duplicate `code_hash` each raise a unique violation, and the state-to-timestamp checks each raise a check violation — but that was a throwaway probe, nothing in the repository re-runs it, and no statement was executed concurrently. The concurrency claim above therefore remains an argument from a primary key rather than a measured result. `conformance/p1140e/sql-race-plans-v1.json` records planned race cases for the equivalent constraints elsewhere in the schema and none has been executed.
- The expiry sweeper does not exist; `invite_codes_expiry_idx` is a declared target shape.
- The lockout counter does not exist and no rate limiter exists.
- `conformance/p1140e/state-machine-fixtures-v1.json` holds one positive and one negative transition case for `invite-code`. Neither is executed by any runner.

The conformance obligations that would turn this into evidence are a concurrency case that drives two redemptions of one code and asserts exactly one commits, a case that asserts all four unredeemable conditions produce the same response bytes, and a deletion case that asserts the code reaches `retired` and the redemption row is gone in the same transaction.
