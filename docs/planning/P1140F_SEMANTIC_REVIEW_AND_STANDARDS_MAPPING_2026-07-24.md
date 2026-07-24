# P-1140F Semantic Review and Standards Mapping

Status: `in-progress-planning`
Updated: 2026-07-24
Evidence maturity: manual planning review independent of the P-1140E validator; not a third-party audit, runtime proof, security certification, or implementation authorization

## Purpose

P-1140E proves structural repository consistency: registered decisions, references, state-machine identifiers, API operation coverage, platform-profile coverage, planned race cases, and clean-checkout validator execution. It does not prove that the contracts are semantically correct, standards-conformant, implementable, or secure.

P-1140F is the separate semantic-readiness gate. It reviews the frozen P-1140B through P-1140D contracts against primary standards and official platform documentation before P-1104 may be considered.

## Current result

- Structural P0 open: 0
- Structural P1 open: 0
- Semantic P0 open: 0
- Semantic P1 open: 4
- P-1104: blocked

No implementation may begin until all four semantic P1 findings are repaired in their normative owners, the repaired schemas and fixtures cross-resolve, and a clean-checkout planning run passes on the repair head.

## Open semantic P1 findings

### SR-001 — OAuth issuer verification is not capability-aware

`docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` requires every callback to verify issuer, while `packages/schemas/openapi-v1.yaml` callback operations carry only `code` and `state`. OAuth authorization-response issuer validation is only directly available when the authorization server supports the RFC 9207 `iss` response parameter and advertises that capability.

Required repair:

1. Add a provider-capability record containing immutable issuer, authorization endpoint, token endpoint, client identifier, exact redirect URI, PKCE requirements, and whether RFC 9207 authorization-response issuer identification is supported.
2. Require and validate callback `iss` only for providers that advertise support.
3. For providers without RFC 9207 support, bind each transaction to one preconfigured provider and token endpoint, use a unique redirect path per authorization server, and reject callbacks received on any redirect other than the one stored with the transaction.
4. Never select issuer, provider, client configuration, or token endpoint from callback-controlled values.
5. Add positive and mix-up/redirect-confusion fixtures for every launch provider.

Primary sources:

- https://www.rfc-editor.org/rfc/rfc9700.html
- https://www.rfc-editor.org/rfc/rfc8252.html
- https://www.rfc-editor.org/rfc/rfc9207.html
- https://www.rfc-editor.org/rfc/rfc8414.html
- https://www.rfc-editor.org/rfc/rfc7636.html

### SR-002 — Device authorization is over-broad

`packages/schemas/openapi-v1.yaml` currently exposes a generic `/auth/device/*` family and the implementation breakdown names normal native-device authorization. RFC 8628 is for devices with limited input or no suitable browser and explicitly does not replace browser-based native OAuth on capable devices.

Required repair:

1. macOS, Windows, and desktop Linux use the system browser with Authorization Code plus PKCE.
2. Device authorization is removed from the ordinary desktop path.
3. Device authorization may exist only for an explicitly registered limited-input or headless interactive profile whose provider supports RFC 8628.
4. CI and unattended automation use workload identity or another separately accepted non-human flow; they must not poll a human device code.
5. Device authorization must not be treated as device possession, device attestation, ranked-identity proof, or evidence-tier authority.

Primary sources:

- https://www.rfc-editor.org/rfc/rfc8252.html
- https://www.rfc-editor.org/rfc/rfc8628.html
- https://www.rfc-editor.org/rfc/rfc9700.html

### SR-003 — The interactive menu-bar/tray shell lacks an authoritative state machine

The native contract says daemon, shell, collector, and sync are independent, but the registry has no interactive-shell machine. The user-facing process is a separate lifecycle and security boundary: it displays state, initiates OAuth, controls pause/resume, requests updates, and talks to the daemon through authenticated local IPC.

Required repair:

1. Add one authoritative `interactive-shell` machine with persistence owner, states, transitions, actors, authentication, idempotency, audit, reversal, and transaction boundaries.
2. Cover absent/headless, starting, connected, daemon-unavailable, stale, paused, offline, degraded, auth-required, update-required, update-blocked, permission-repair, and exiting states.
3. Closing or crashing the shell never stops the OS-supervised daemon.
4. Collection pause, sync pause, daemon shutdown, uninstall, logout, and UI exit are distinct actions.
5. Define single-instance behavior, session/login changes, privacy-safe notifications, OAuth browser handoff, IPC peer verification, and CLI parity.
6. Add platform-specific mappings for macOS menu-bar/login-item/LaunchAgent, Windows notification-area shell plus supervised background process, and Linux desktop shell plus systemd-user/headless mode.

Primary sources:

- https://developer.apple.com/documentation/swiftui/menubarextra
- https://developer.apple.com/documentation/servicemanagement/smappservice
- https://learn.microsoft.com/en-us/windows/win32/shell/notification-area
- https://www.freedesktop.org/software/systemd/man/latest/systemd.user.html

### SR-004 — Platform source evidence is not immutable enough

The platform registry uses source URLs and verification dates, including mutable references. A future reviewer cannot prove which exact upstream text or repository revision supported a profile field.

Required repair:

1. Replace each source string with a typed source-evidence object.
2. Record source identifier, immutable version/release/commit, retrieval timestamp, content SHA-256, canonical URI, and the exact fields supported by that source.
3. Internal repository evidence must bind an exact commit SHA, never a moving branch.
4. Release/build evidence must bind artifact digest and provenance subject/materials.
5. Validators reject mutable-only evidence and duplicate or conflicting field authority.

Primary sources:

- https://slsa.dev/spec/v1.2/provenance
- https://slsa.dev/spec/v1.2/
- https://theupdateframework.io/spec/
- https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases

## Reviewed domains without a new semantic P1

### Deterministic evidence, replay, and device cloning

The P-1140B/C direction is sound at planning level: server-owned appraisal, deterministic CBOR/COSE, exact replay, conflicting-key rejection, monotonic checkpoint state, clone/fork quarantine, dual-signature rotation, and append-only corrections. This is not interoperability or security evidence. Independent Rust and Go codecs, malformed/resource tests, transactional replay tests, rollback simulations, and recovery drills remain implementation evidence.

Primary sources:

- https://www.rfc-editor.org/rfc/rfc8949.html
- https://www.rfc-editor.org/rfc/rfc9052.html
- https://www.rfc-editor.org/rfc/rfc9053.html
- https://www.rfc-editor.org/rfc/rfc8032.html

### Accounting and universal adapters

The repository correctly separates provider-reported, reconstructed, and local-runtime authority and requires immutable accounting profiles and support ceilings. Universal support remains a certification program, not an adapter-list claim. Every advertised product/source/version/platform/mode combination still requires real fixtures, upgrade-break tests, duplicate-domain tests, privacy canaries, and non-expired certification.

### Anti-cheat and SLM

Deterministic controls remain authoritative. Statistical or small-language-model detection remains local-only, advisory, post-launch research and may not modify totals, raise evidence tiers, or permanently ban. This staging is retained.

### Ranking, social, moderation, export, and deletion

No new P1 was identified in the current planning ownership model: immutable ranking views, append-only corrections, canonical friendship pairs, immediate block invalidation, viewer-specific presence, authorization recheck at notification delivery, reversible moderation effects, and distinct local/server deletion are coherent planning directions. Runtime race, privacy, rebuild, and abuse tests remain mandatory evidence.

### Release trust

TUF plus signed release sets and provenance is an appropriate direction. No release-security claim exists until a real repository, threshold keys, expiry/rollback/freeze tests, compromise recovery, immutable artifacts, and exercised installers/updaters exist.

Primary sources:

- https://theupdateframework.io/spec/
- https://slsa.dev/spec/v1.2/

## Closure criteria

P-1140F becomes `complete-planning` only when:

1. SR-001 through SR-004 are repaired in the architecture contract, OpenAPI, state-machine registry, platform-profile schema/registry, fixtures, validators, handoff, and work breakdown as applicable.
2. Provider-specific OAuth and native-shell fixtures exist and are schema-validated.
3. Source-evidence objects bind immutable revisions and digests.
4. The P-1140E structural validator passes without asserting semantic correctness.
5. A manual review record confirms zero open semantic P0/P1 findings on the exact repair head.
6. P-1104 remains a separate explicit user decision after this gate closes.
