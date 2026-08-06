# Origin Validation and Loopback Surface Controls

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-230, D-231, D-440

## Why this document exists

Before it was written, the strings `cors`, `Access-Control` and `cross-origin` did not appear anywhere in this repository, and neither did `DNS rebinding`. That absence spanned two surfaces that fail in different ways:

- **The public API.** ADR-015 requires that "every state-changing request additionally requires either an `Origin` header matching an exact allowlisted origin or a double-submitted CSRF token bound to the session record". PF-039 landed half of that: `packages/schemas/openapi-v1.yaml` now declares a `csrfToken` security scheme carrying `X-VibeMaxxing-CSRF`, and every state-changing cookie-authenticated operation requires it. The other half was still missing — no document said which origins are allowlisted, and the OpenAPI document declares no `Origin` parameter and no preflight response, so the origin arm of that requirement had no implementable form.
- **The loopback surfaces.** `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md` describes `local-dashboard` as a "loopback-only control UI protected by an ephemeral local session token", and `docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` describes an unauthenticated loopback OTLP receiver. Both are HTTP servers reachable from a browser on the same machine. Binding to loopback is a network control and a browser is not on the network — it is already inside the machine, and it will send requests to `127.0.0.1` on behalf of whatever page the participant happens to be reading.

This document owns origin validation for both. It does not own local IPC over Unix sockets, named pipes or XPC — `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md` owns that, and its peer-credential model is a different and stronger control that no browser can reach.

## Part one: the public API

### Allowed origins

Cross-origin requests to the API are permitted from an exact allowlist. Wildcards are never used, `Access-Control-Allow-Origin: *` is never sent, and an origin is never reflected from the request without first being matched against the list.

| Origin | Purpose | Credentials |
|---|---|---|
| `https://vibemaxxing.dev` | the hosted web application | yes |
| `https://www.vibemaxxing.dev` | canonical redirect target | yes |
| `http://localhost:3000` | local development only, present only in the `local` environment build | yes |

There is no third-party origin, no partner origin and no embedding origin. The API exists to serve one first-party web application and a native client that is not a browser and therefore has no origin at all.

Subdomains are not wildcarded. `__Host-` cookie prefixes under ADR-015 already prevent a sibling subdomain from setting the session cookie; permitting a sibling subdomain as an origin would give back most of what that prefix was chosen to remove.

The `local` entry is compiled out of the production build rather than configured off. A configuration flag that admits `localhost` is one environment-variable mistake away from admitting it in production, and an attacker who can reach the production API from a page on the participant's own machine has a credentialed cross-origin channel.

### Preflight

`Access-Control-Allow-Methods` is `GET, POST, DELETE`. `Access-Control-Allow-Headers` is `Content-Type, Idempotency-Key, If-Match`. `Access-Control-Expose-Headers` is `Retry-After, RateLimit, RateLimit-Policy, X-Request-Id`. `Access-Control-Allow-Credentials` is `true`. `Access-Control-Max-Age` is `600` seconds — ten minutes is long enough to remove the preflight from an interactive session and short enough that revoking an origin takes effect within a coffee break.

A preflight for an origin that is not on the list returns `204` with no `Access-Control-*` headers at all, rather than an error. The browser then blocks the request itself. Returning an error body would tell a probing page whether the origin is known.

### State-changing requests

Origin validation is a second control and not the only one. Every state-changing request is validated in this order, and all applicable checks must pass:

1. **`Origin` must be present and must match the allowlist exactly**, scheme, host and port. A state-changing request with no `Origin` header from a cookie-authenticated session is refused; every browser sends `Origin` on `POST` and `DELETE`, so its absence means the request did not come from one.
2. **A double-submitted CSRF token bound to the session record**, as ADR-015 requires. This is the `csrfToken` scheme in `packages/schemas/openapi-v1.yaml`, carried in `X-VibeMaxxing-CSRF` and compared against the value stored with the session. The token rotates with the session.
3. **`SameSite=Lax` on the session cookie**, which ADR-015 sets, which stops cross-site `POST` before the request is dispatched.

Three overlapping controls is deliberate. `SameSite` is enforced by the browser and a browser bug removes it. `Origin` is a header and a request that is not from a browser can set it to anything, which is why it is not sufficient alone against a native attacker. The CSRF token is bound to server state and is the only one of the three an attacker cannot produce without already reading a response from the allowlisted origin. Each covers the others' failure.

Requests authenticated by a bearer credential rather than a cookie — every native client request — are exempt from checks 1 and 2 and are not exempt from anything else. A cross-site request cannot attach a bearer credential the attacking page does not hold, so cross-site request forgery does not apply to them.

## Part two: the loopback surfaces

### The threat

A daemon listening on `127.0.0.1` is reachable by every process on the machine, including the participant's browser. Two attacks follow, and neither requires the attacker to be on the participant's network.

**Cross-site request forgery against loopback.** A page at `https://attacker.example` issues a form post or a `fetch` with `mode: "no-cors"` to `http://127.0.0.1:<port>/…`. The request is dispatched. The attacker cannot read the response — the same-origin policy still holds — but for a control API that does not matter, because pausing collection, revoking a device or triggering an export are effects that do not need a readable response to be damaging.

**DNS rebinding.** The attacker serves `evil.example` with a very short DNS time-to-live, first resolving to their own address so the page loads, then re-resolving to `127.0.0.1`. Subsequent requests from that page are, as far as the browser is concerned, same-origin with `evil.example` — so the same-origin policy no longer protects the response, and the attacker reads it. This defeats every control that depends on the attacker being unable to read: an ephemeral session token displayed by the dashboard, a device list, a claim history. Rebinding is the reason "loopback-only" is not by itself a security boundary against a browser, and it is why the OTLP receiver's current stated mitigation set — loopback bind and peer credentials — is incomplete against this specific adversary.

Peer credentials do not help here either. The peer *is* the participant's own browser, running as the participant, which is exactly the identity the check would approve.

### Required controls

Every HTTP server bound to a loopback interface in this product — `local-dashboard`, the adapter-one OTLP receiver, and any future loopback surface — applies all of the following. They are cheap, they are independent, and each closes something the others do not.

**1. `Host` header allowlist.** The request's `Host` must be exactly `127.0.0.1:<port>`, `[::1]:<port>`, or `localhost:<port>`. Any other value, including any name that resolves to a loopback address, is refused with `403` before routing. This is the control that defeats DNS rebinding: a rebound request still carries `Host: evil.example`, because the browser sends the name it was given and not the address it resolved to. A server that ignores `Host` cannot distinguish the two; a server that checks it cannot be rebound.

**2. `Origin` header rules.** For a state-changing request the `Origin` must be absent, or exactly `http://127.0.0.1:<port>`, `http://[::1]:<port>` or `http://localhost:<port>`. Absent is permitted because the native shell and CLI are not browsers and send no origin; any *other* value means a web page is talking to the daemon and the request is refused with `403`.

**3. No credentials in a browser-reachable form.** The dashboard's session token is never stored in a cookie. It is delivered as a URL fragment when the shell opens the dashboard, held in memory by the page, and sent in a request header. A cookie would be attached automatically by the browser to a forged cross-site request; a header will not be. This is the control that makes forgery fail even if the first two are somehow bypassed.

**4. A random high port, recorded in the local state directory.** The listening port is chosen at daemon start from the ephemeral range and written to a file readable only by the owning user. A fixed well-known port is the single fact an attacking page needs to target the surface without probing; a random port makes it enumerate roughly sixteen thousand possibilities against a server that refuses on `Host` anyway.

**5. Bind verification before listening.** The receiver resolves its configured bind address and refuses to start if the result is not a loopback address. `ADAPTER_ONE_CLAUDE_CODE_OTEL.md` already requires this for the OTLP receiver; it applies to every loopback listener, and there is no configuration path that binds a routable interface.

**6. No CORS headers, ever.** A loopback surface sends no `Access-Control-Allow-Origin`, no `Access-Control-Allow-Credentials` and answers no preflight with an allow. There is no legitimate cross-origin consumer of the local control API. A preflight receives `403`.

**7. Idle expiry.** The dashboard session token expires **900 seconds** after the last request on it, and unconditionally **3,600 seconds** after issue. The idle number matches `challenge_expiry_seconds`, which is the existing repository figure for a short-lived local credential; the absolute number bounds the window in which a token left in a browser tab's memory remains useful. Closing the dashboard revokes the token immediately.

**8. Local rate limit.** 60 requests per minute per token, and 10 per minute for a request that has no valid token. The second number bounds a probing page: at 10 attempts a minute, enumerating a sixteen-thousand-port range takes over a day, by which time the daemon has restarted onto a different port.

### The OTLP receiver keeps its own honest caveat

`docs/integrations/ADAPTER_ONE_CLAUDE_CODE_OTEL.md` states plainly that the receiver is an unauthenticated localhost endpoint and that any process able to reach the socket can mint token counts. The controls here do not change that. They stop a *web page* from reaching it; they do not stop a *local process* from doing so, and no loopback control can, because a local process running as the participant is indistinguishable from the participant. That residual exposure remains recorded where it already is, and this document does not weaken it by implying otherwise.

## The machine surface

Everything above is now readable by a generator. `packages/schemas/origin-policy-v1.json` is the machine owner and `packages/schemas/origin-policy-v1.schema.json` constrains it. It carries the three origins, the preflight values, the ordered state-changing checks with the reason code each failure answers, the bearer exemption, and one entry per loopback listener binding all eight controls by name. `scripts/repository/validate_planning_artifacts.py` validates it.

The public API's half is projected into `packages/schemas/openapi-v1.yaml` under D-440, because a middleware generator reads the API document and not a security contract beside it. Three things appear there: an `x-origin-policy` block at the document root, a `components/parameters/Origin` header parameter whose enum is the allowlist, and a `components/responses/Preflight` component declaring the six `Access-Control-*` headers an allowlisted origin receives. Every value in the block is compared field by field against the policy record, in the same way the reason registry's recorded operation classes are derived from the document and compared rather than trusted — a hand-maintained second copy keeps passing after the thing it describes changes shape.

The `Origin` parameter is declared by exactly the operations whose security includes `csrfToken`, and by no others. That is the state-changing cookie-authenticated set PF-039 already marked, so the origin arm of the ADR-015 requirement binds to the same twenty-two operations by construction rather than by a second hand-maintained list. The parameter is declared optional, because OpenAPI cannot make a parameter required under one security alternative and absent under another and a bearer-authenticated native request sends no origin at all; the conditional rule lives in the policy record, whose `origin-exact-match` check records `missing_header` as `refuse`.

Preflight is not declared as an `options` operation on every path. No CORS implementation routes a preflight to an operation — the edge answers it before routing — so declaring one per path would record a mechanism that does not exist. The response component is declared once and the extension block names it.

The loopback listeners have no OpenAPI presence at all, because they are not the public API. Their refusal vocabulary — `LOOPBACK_HOST_NOT_ALLOWED`, `LOOPBACK_ORIGIN_NOT_ALLOWED`, `LOOPBACK_PREFLIGHT_REFUSED`, `LOOPBACK_TOKEN_EXPIRED`, `LOOPBACK_RATE_LIMIT_EXCEEDED` — lives in the policy record and deliberately not in `packages/schemas/reason-codes-v1.json`, which requires every wire-visible code to bind to a declared API operation and would therefore have to invent operations that do not exist. The validator fails if one of these codes is ever added there.

One figure is recorded as a tension rather than resolved. Control 8 sets ten requests a minute for a request carrying no valid token. Every request to the OTLP receiver is unauthenticated by construction, so that probe limit is the receiver's whole limit and it bounds legitimate export as well as probing. A 60-second exporter interval fits inside it and a burst does not. Raising the number for that listener needs its own decision, because the same number is what makes port enumeration take a day.

## Evidence

Nothing here is implemented. No server validates a `Host` header, no dashboard exists, no CORS configuration exists, and the conformance obligations that would turn these rules into evidence do not yet run. A schema that validates is not a control that runs. They are:

- a fixture set that drives each loopback listener with a rebinding-shaped request (`Host: evil.example`, loopback destination) and asserts `403`;
- a fixture set that drives each state-changing loopback route with a foreign `Origin` and asserts `403`;
- a preflight fixture for the public API asserting that a non-allowlisted origin receives no `Access-Control-*` header;
- a test that the `local` origin entry is absent from a production build artifact rather than merely disabled.

These belong to the `sandbox` conformance suite, whose harness contract is `docs/verification/CONFORMANCE_HARNESS.md`. That suite now declares a manifest at `conformance/sandbox/manifest.json` recording `fixture_state` as `empty`, naming `packages/schemas/origin-policy-v1.json` as its reason authority, and naming `OS-002` as the unit that owes the fixtures. The suite still holds no fixture, and an empty suite with a manifest is a countable gap rather than a closed one.
