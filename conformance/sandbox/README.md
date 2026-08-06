# `sandbox` conformance suite

Case prefix: `SB`. Subjects: `rust`, `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That the process boundaries and the loopback surfaces hold: that a component which must not reach the network cannot, that a component which must not read transcripts cannot, and that a web page on the participant's own machine cannot drive the local control API.

Authorities:

- `docs/security/PLATFORM_ISOLATION.md`
- `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`
- `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`
- `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
- `packages/schemas/local-control-v1.proto`

## Required cases

Process boundary:

- the transcript-capable collector attempting an outbound connection, refused;
- the network-capable sync component attempting to open transcript storage, refused;
- a privileged supervisor attempting to read source content or hold an ordinary claim key, refused;
- a local IPC message from a peer whose kernel-reported credentials do not match the expected role, refused;
- a local IPC message replayed with a stale connection nonce or an out-of-order sequence, refused.

Loopback origin controls, one per rule in `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`:

- a request with a rebinding-shaped `Host` header — a routable name resolving to a loopback address — refused with `403`;
- a state-changing request with a foreign `Origin`, refused with `403`;
- a preflight from a non-allowlisted origin receiving no `Access-Control-*` header;
- a dashboard session token used after its 900-second idle expiry, refused;
- a dashboard session token used after its 3,600-second absolute expiry, refused;
- an unauthenticated probe exceeding 10 requests per minute, refused;
- a listener configured with a routable bind address, asserted to refuse to start rather than to bind.

## Status

**Nothing here executes.** No fixture, no `manifest.json`, no runner, and none of the components under test exists: there is no collector, no sync process, no daemon, no dashboard. The `sandbox-enforcement` eval suite is `not_applicable` and names `crates/vibeproof-collector/src/lib.rs` (new) and `evals/fixtures/sandbox-enforcement.json` (new) as the paths whose absence justifies that status. A README is not executable evidence and this one does not change any status.
