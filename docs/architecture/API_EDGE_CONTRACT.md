# API Edge Contract: Limits, Versioning and Client Obligations

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-232, D-233, D-234

## What this document owns, and what it does not

`docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` states the *rules* of the public API edge: that rate limits exist per account, device, IP risk bucket and endpoint class; that responses carry limit headers without revealing abuse thresholds; that every state-changing endpoint defines idempotency semantics. Those rules have been in place since P-1140D and none of them carries a number, so none of them is implementable.

This document owns the numbers and the client-side obligations that follow from them:

- the rate-limit classes, their per-principal quotas, and what happens when a quota is exceeded;
- the API version and deprecation policy, including how long a deprecated surface survives;
- the client retry, backoff and retry-budget obligations, and which operations are safe to retry.

It does not own idempotency. `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` and `packages/schemas/state-machine-registry-v1.json` own it jointly, SR-012 records that it is semantically open, and PF-049 is repairing the machine artifacts. This document cites that contract to determine retry safety and deliberately does not restate its semantics.

It does not own origin validation. `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md` owns that for both the public API and the loopback surfaces.

Numeric quotas that a deployment can tune live in `packages/schemas/policy-defaults-v1.json`. A number that appears here and also appears there is the registry's number; this document explains where it came from.

## Rate limiting

### Why these numbers

Every quota below is derived from a load the product actually generates, not from a round number. The derivation matters because a limit set above the real load protects nothing and a limit set below it breaks the product.

The reference population is the invite-only private beta of D-180. The owner issues every invite personally, so the ring is bounded by how many invitations one person sends; the planning figure used here is **200 participants, one enrolled device each**, which is the `invite_outstanding_max` quota rather than a chosen number. The deployment shape is a single small managed container against a single managed PostgreSQL instance, so the aggregate admission ceiling is set from what that shape sustains rather than from what the product would like. That shape was originally fixed by the sub-100-USD ceiling of D-093; D-093 is superseded by D-360, which sets the ceiling at the measured steady-state monthly cost of the configuration selected under D-361. The deployment shape the quotas below are derived from is unchanged by that amendment, and the quotas are therefore unchanged.

Derived steady-state load at that population:

| Source | Derivation | Requests/second |
|---|---|---:|
| Claim submission | 200 devices x 1 batch per 60 s | 3.3 |
| Presence heartbeat | 200 devices x 1 per 30 s (`presence_heartbeat_seconds`) | 6.7 |
| Leaderboard reads | 200 clients x 1 per 60 s (`public_cache_stale_seconds` makes anything faster a cache hit) | 3.3 |
| Authenticated reads | 200 clients x 2 per 60 s | 6.7 |
| **Total** | | **20** |

The aggregate admission ceiling is set at **200 requests per second**, ten times derived steady state, which is the headroom that absorbs a synchronized reconnect after an outage without also absorbing a scripted flood.

### Principal classes

A quota is charged to exactly one principal. The principal is resolved in this order and the first match wins, so an authenticated request is never also charged to its IP address and a device is never also charged to its account:

1. `device` — an enrolled device presenting a valid device-bound session.
2. `account` — an authenticated session with no device binding, which is every hosted-web request.
3. `enrolment` — an in-flight OAuth transaction or device-authorization code, keyed by the transaction identifier rather than by any identity, because no identity exists yet.
4. `address` — an unauthenticated request, keyed by the client address prefix: the full IPv4 address, or the /64 for IPv6.

The /64 grouping for IPv6 is deliberate. A single residential IPv6 allocation is routinely a /64 or larger, so charging per-address would let one client rotate through a practically unlimited address space and defeat the limit entirely.

### Quotas

Each class is a token bucket: `rate` refills continuously, `burst` is the bucket depth, and a request costs one token unless stated. Burst is set at twice the sustained rate for interactive classes so a client that has been idle can issue a short run of requests without being throttled, and at the sustained rate for expensive classes where there is no legitimate burst.

| Operation class | Principal | Sustained rate | Burst | Applies to |
|---|---|---:|---:|---|
| `public-read` | `address` | 60 / minute | 120 | global leaderboard, public profiles |
| `authenticated-read` | `account` | 120 / minute | 240 | `/me`, `/rank/me`, authorized board views, notifications |
| `claim-ingest` | `device` | 6 / minute | 12 | `/claim-challenges`, `/claim-batches` |
| `presence` | `device` | 4 / minute | 8 | presence heartbeat |
| `social-mutate` | `account` | 30 / hour | 30 | friend requests, blocks, rivals, board invitations |
| `board-create` | `account` | 5 / day | 5 | board and community creation |
| `auth-start` | `address` | 10 / hour | 10 | OAuth start and callback, device-authorization start, private-beta invite redemption |
| `device-poll` | `enrolment` | 1 per 5 seconds | 1 | device-authorization polling |
| `subject-rights` | `account` | 5 / day | 5 | export requests, deletion requests |
| `appeal` | `account` | 5 / day | 5 | appeals against moderation outcomes |
| `report` | `account` | 20 / day | 20 | moderation reports |

Notes that each number depends on:

- **`claim-ingest` at 6 per minute** is six times the one-batch-per-minute steady rate. A device draining an offline backlog sends at most `batch_max_claims` = 500 claims per batch, so 6 batches per minute drains 3,000 claim-minutes per minute — a 24-hour backlog of 1,440 minutes clears in under 30 seconds. The limit therefore never delays a legitimate reconnect.
- **`presence` at 4 per minute** is twice the 30-second `presence_heartbeat_seconds` cadence, which allows one retry per interval without eating the next interval's allowance.
- **`social-mutate` at 30 per hour** is an anti-abuse number, not a capacity number. `ANTI_CHEAT_ATTACK_CATALOG.md` names rate limits as the control for Sybil farming (AC-A-022) and appeal spam (AC-A-045); 30 friend requests an hour is far beyond ordinary use and far below what makes mass solicitation worthwhile.
- **`device-poll` is an interval, not a bucket.** The device-authorization code expires after 15 minutes under ADR-015, and `DeviceAuthorizationStatus.retry_after_seconds` already caps a server-requested pause at 60 seconds. A 5-second minimum interval permits at most 180 polls against a code that lives 15 minutes, which is the ceiling; a poll arriving early returns `429` with `Retry-After` set to the remaining interval and does not consume the code.
- **`redeemInvite` is charged to `auth-start` rather than to an authenticated class.** It is an authenticated operation, so `authenticated-read` or `social-mutate` would be the ordinary reading, but the adversary against an invite code is an address cycling through accounts rather than an account, and only an address-keyed bucket bounds that. It is the admission flow, which is what this class already is. `docs/security/PRIVATE_BETA_ADMISSION.md` states the guessing arithmetic against this quota and adds a per-account lockout that this document does not own.
- **`subject-rights` is limited but never refused outright.** Article 12(5) of Regulation (EU) 2016/679 permits refusal only for manifestly unfounded or excessive requests, so the limit exists to stop automated hammering and not to gate the right. The first request from a principal in any 24-hour window is always admitted regardless of bucket state, and a throttled subject-rights request returns `429` with a `Retry-After` no greater than 3,600 seconds.

### Adaptive limits are separate and unpublished

The quotas above are the ordinary limits and they are published: a client may read them from this document and from the response headers. Separately, and consistent with the existing rule that responses must not reveal abuse thresholds, the edge may apply tighter adaptive limits to a principal under suspicion. Adaptive limits emit no headers, are not documented with a number anywhere in this repository, and a request refused by one is indistinguishable on the wire from a request refused by an ordinary limit.

That asymmetry is the point. A published ordinary limit lets an honest client pace itself; an unpublished adaptive limit denies an abusive client the feedback it needs to tune around the threshold.

### Response on breach

A request refused by a rate limit returns HTTP `429` with:

- `Retry-After`, an integer number of seconds, set to the time until one token is available, rounded up, minimum 1. The existing `RateLimited` response in `packages/schemas/openapi-v1.yaml` already requires this header.
- `RateLimit-Policy` and `RateLimit`, in the form of the IETF HTTP rate-limit header fields, for ordinary limits only. Omitted entirely for adaptive limits.
- A problem body whose `reason_code` is `RATE_LIMIT_EXCEEDED`, registered in `packages/schemas/reason-codes-v1.json` at registry version 1.3.0 with `http_status: 429`, `retryable: true` and `operation_classes: ["all"]`.

Until PF-045 landed that code, this requirement was unsatisfiable: the OpenAPI document required a `reason_code` on every problem body and the registry held no rate-limit code, so a `429` could not carry a registered reason at all. D-245 records what remains unclosed after that repair — the registry still has no code for a clock rollback or a future timestamp, and fifteen codes still name a `vibeproof-v1` state machine that is not registered, which D-224 records as a partial repair.

Exceeding the aggregate admission ceiling is a different condition and returns `503` with `Retry-After`, because it is a statement about the service and not about the client. Load shedding refuses expensive work before durable mutation, as the authoritative state contract already requires.

## API versioning and deprecation

### The version

The API is versioned in the URL path. `/v1` is the only version and `packages/schemas/openapi-v1.yaml` declares it. There is no version header, no content-type parameter and no query parameter; a client that wants a different major version requests a different path.

This is chosen over header-based negotiation for a specific reason rather than by convention: the release-set model in the operations contract binds each client build to a declared supported API version range, and the daemon's `version-expired` state already exists to refuse operation outside it. A path version makes that binding a URL the client either has or does not have, which is inspectable in a log line and in a proxy configuration. Header negotiation would move the same fact into a place neither surfaces by default.

### What may change within `/v1`

Additive only. Within a major version the server may:

- add a new endpoint;
- add an optional request field;
- add a response field;
- add a member to an enumeration **only where the schema and the contract both already declare that enumeration open**;
- relax a validation constraint;
- add a new `reason_code`.

Within a major version the server may not remove or rename a field, make an optional request field required, narrow a type, change the meaning of an existing value, or add a member to a closed enumeration. A closed enumeration is one a client is entitled to exhaustively match on; the state vocabularies in `packages/schemas/state-machine-registry-v1.json` are closed, and adding a state to one is a major-version change.

Clients must ignore unknown response fields and must not fail on an unrecognised `reason_code`; a client that treats an unknown reason as a hard error converts an additive change into a breaking one on its own side.

### Deprecation

A deprecated endpoint or field carries:

- `Deprecation`, an HTTP-date at which deprecation took effect;
- `Sunset`, an HTTP-date at which the surface stops responding;
- a `Link` relation to this document;
- `deprecated: true` in the OpenAPI description of the operation or property.

The window between `Deprecation` and `Sunset` is **180 days minimum**. That number is set by the client update model rather than chosen: ADR-013 makes updates mandatory with a signed deadline, the operations contract permits bounded user deferral, and a client that is offline or deferring can be several release sets behind. 180 days is two full quarters, which is long enough that a participant who opens the application once a quarter still receives at least one build that no longer uses the removed surface before it disappears.

Three carve-outs shorten the window, each with a stated trigger:

- **Security.** A surface removed to close a vulnerability may be sunset with the emergency update deadline that ADR-013 already defines, with no minimum window. The removal is announced through the same private advisory path as the fix.
- **Never used.** A surface that no released client build has ever called may be removed immediately. "Released" means present in a release set; a surface used only by an unreleased branch is not in use.
- **Legally compelled.** A surface that must be removed to satisfy a legal obligation is removed on the obligation's timetable, and the reason is recorded in the changelog without the detail that would identify the requester.

A deprecation is announced in `CHANGELOG.md` at the release that introduces the `Deprecation` header, again in every release set within the window, and once more in the release that performs the removal.

### The major-version rule

A breaking change opens `/v2`. `/v1` and `/v2` then run concurrently for the same 180-day minimum, measured from `/v2`'s first release set. Running two major versions concurrently on a sub-100-USD deployment is expensive, which is a deliberate pressure toward the additive rule above rather than an accident of the budget.

## Retry, backoff and retry budgets

### Retry safety

Whether an operation may be retried is decided by exactly one property: whether repeating it can produce a second effect. Three classes exist.

**Always safe.** Every `GET`. A read has no effect to duplicate.

**Safe under an idempotency key.** Every mutation that carries `Idempotency-Key` — claim batches, device enrollment, board creation, invitations, exports and deletion requests among them. Retrying with the *same* key is safe; retrying with a new key is a second request and is not a retry.

This safety is contingent, and the contingency is only half met. The `x-idempotency-contract` block at the root of `packages/schemas/openapi-v1.yaml`, landed by PF-049 under D-225, now states the wire half in full: the key is scoped to `(principal_id, operation_id, idempotency_key)`, the committed response is recorded whole rather than as a digest, a replay returns it byte-identically and carries `Idempotency-Replayed`, a same-key-different-digest request is `409` with `IDEMPOTENCY_KEY_CONFLICT`, and a record aged past its 168-hour retention is `410` with `IDEMPOTENCY_RECORD_EXPIRED`.

**The persistence half is not repaired and SR-012 stays open.** `packages/schemas/planning-schema.sql` still stores a nullable `response_digest` with no response-body column and keys the ledger on the account alone. So the contract a client codes against is complete and the storage that would honour it is not, and a client must treat byte-identical replay as specified rather than as demonstrated until that closes. The idempotency contract, not this document, decides when it does.

Three retry rules follow directly from that block and are stated here because they are client obligations rather than server semantics: a `409` is never retried, because the key is spent against different bytes; a `410` is never retried under the same key, because the response no longer exists to replay and re-executing would be a second mutation; and a request that times out while a row is reserved is retried with the *same* key, because the reserved-recovery rule makes that the only way to learn the original outcome.

**Not safe.** Mutations with no idempotency key: OAuth start and callback, device-authorization start, poll and exchange, and challenge creation. Each is a step in a stateful exchange where a second attempt legitimately advances or invalidates state. A client that fails one of these restarts the exchange from the beginning rather than retrying the step.

`packages/schemas/openapi-v1.yaml` already carries this distinction as the `x-idempotency` extension, and the exception list in `scripts/repository/validate_planning_coverage.py` is the same set. A client determines retry safety from the specification, never by guessing from the method.

### Backoff

A client that retries uses exponential backoff with full jitter:

```
delay = random_between(0, min(cap, base * 2 ** attempt))
```

with `base` = 1 second, `cap` = 60 seconds, and `attempt` counting from zero. Full jitter — a uniform draw over the whole interval rather than the interval plus a small perturbation — is chosen because the failure mode this defends against is synchronized retry after a shared outage, and only full jitter spreads a fleet that all failed at the same instant across the whole window. Adding jitter to a fixed delay leaves the fleet clustered.

`Retry-After`, when the server sends it, overrides the computed delay whenever it is larger. A server that has told the client when to come back knows something the client does not.

Attempt ceilings:

| Caller | Maximum attempts | On exhaustion |
|---|---:|---|
| Hosted web, interactive request | 3 | surface the failure to the participant |
| Native client, read | 5 | surface a degraded view |
| Native client, keyed mutation | 6 | return the item to the durable queue |
| Daemon claim queue | unbounded, capped delay | after 24 hours of continuous failure enter `offline` and stop retrying until connectivity changes |

The daemon's claim queue is the one unbounded case, and it has to be: dropping a queued claim loses accepted local activity that the participant earned, and the append-only ledger has no way to recreate it. It is bounded in delay rather than in attempts — at the 60-second cap that is 1,440 attempts a day — and after 24 hours it stops attempting and reports `offline` rather than continuing to burn battery on a service that is not coming back on its own. `NATIVE_CLIENT_AND_DAEMON.md` already defines `offline` and `backoff` as daemon states; this is the transition rule between them.

### Retry budget

Attempt ceilings alone do not prevent a retry storm, because every client obeying its own ceiling still multiplies total load by that ceiling exactly when the service is least able to absorb it. Each client therefore also enforces a budget: **retries may not exceed 10% of successful requests over a trailing 60-second window, with a floor of 3 retries** so that a client which has issued almost nothing can still retry at all.

When the budget is exhausted the client fails fast — it does not queue, does not sleep and does not retry — and reports the failure to its caller. The budget refills as successes accumulate, so a client recovers automatically as the service does.

10% is the ratio at which a retrying fleet adds a tenth to the offered load rather than a multiple of it. Under the aggregate admission ceiling of 200 requests per second against derived steady state of 20, a fleet in full retry adds 2 requests per second, which the ceiling absorbs without shedding.

### Circuit breaking

After **20 consecutive failures** against the same host, a client opens a circuit for **60 seconds**, during which it issues no requests and fails immediately. It then admits a single probe request; a success closes the circuit and a failure reopens it for another 60 seconds.

20 is set above the longest legitimate failure run a healthy service produces. A rolling deployment under the expand-and-contract policy of ADR-018 runs two versions simultaneously and can refuse requests during the version-gate check; 20 consecutive refusals is longer than that window and shorter than an outage.

### What a client must not do

- Retry a non-idempotent mutation.
- Retry a `4xx` other than `429`. A `400`, `401`, `403`, `404`, `409`, `410`, `415` or `422` is a statement about the request, and repeating it produces the same answer.
- Retry faster than `Retry-After`.
- Reset its backoff on a `429`. A `429` means the client is going too fast; treating it as a fresh start is how a client converts a throttle into a loop.
- Generate a new idempotency key for a retry.

## Evidence

Nothing here is implemented. No rate limiter exists, no client implements this backoff, no deprecation has ever been issued, and there is no measurement behind the derived load table beyond the arithmetic shown. The quotas are planning figures derived from a planning population, and the first real traffic is expected to move them. The conformance obligations that would make them evidence are:

- a load scenario that drives a single principal at ten times its class limit and asserts that other principals are unaffected. This is now specified operation by operation as `ratelimit-breach` in `evals/load/load-scenarios-v1.json`, with every rate resolved back to a policy key in `packages/schemas/policy-defaults-v1.json`, and it has not been written as a script or run. A specified scenario is not a satisfied obligation;
- a client-side test that asserts backoff, jitter distribution, budget exhaustion and circuit state transitions against a fault-injecting server;
- a deprecation fixture that asserts the header set and the 180-day minimum.
