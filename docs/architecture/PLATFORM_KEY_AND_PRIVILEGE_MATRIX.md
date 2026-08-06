# Platform Key and Privilege Matrix

Status: normative planning contract
Updated: 2026-07-19

## Invariants

The collector may inspect source-local metadata required for normalization but has no network capability. The sync process may use the network but receives only fixed-schema safe records. The desktop shell has no source-content access. The daemon coordinates lifecycle and IPC but may not silently combine collector and sync privileges.

Every executable has an explicit capability manifest covering network, source observation, key use, local database access, update authority, diagnostics and IPC peers. A release fails closed when runtime privileges exceed its manifest.

## Process capability matrix

| Process | Network | Source/content observation | Device signing key | Local event store | Update authority |
|---|---|---|---|---|---|
| `vibeproof-collector` | forbidden | allowlisted adapter-specific read only | no direct export; signing request through bound local service only | write normalized events and commitments | none |
| `vibeproof-sync` | provider and VibeMaxxing allowlist only | forbidden | submit-signing capability only over authenticated IPC | read safe pending claims; write acknowledgements | none |
| `vibemaxxing-daemon` | no general outbound network | no transcript or tool-body access | enrollment, rotation and policy-mediated signing coordination | lifecycle/configuration/audit metadata | coordinate only |
| `vibemaxxing-cli` | login/update endpoints only when invoked | no implicit source scan | no raw key access | control and diagnostics through IPC | user-authorized install/update commands |
| `vibemaxxing-desktop-shell` | hosted-dashboard and login endpoints only | forbidden | no raw key access | status through IPC only | user consent UI only |
| updater helper | update endpoints only | forbidden | release-verification keys only | updater state only | atomic install/rollback within policy |

Crash reports, logs and diagnostics use an allowlist and never include prompts, responses, code, paths, repository names, filenames, tool bodies, credentials or arbitrary environment variables.

## Key protection classes by platform

A concrete release records the exercised class from `EVIDENCE_AND_ATTESTATION_PROFILES.md`; platform names do not imply a class automatically.

### macOS

- Prefer a non-exportable key generated through Security.framework with access control bound to the current user and application identity.
- Hardware-backed Secure Enclave use is optional where the required signing algorithm and deployment target are supported; absence must be disclosed.
- iCloud Keychain synchronization, backup restoration and migration behavior must be disabled or proven not to clone the competitive device key.
- LaunchAgent operation is per-user and unprivileged. Privileged helpers require a separate signed component, explicit installation and a narrower capability manifest.

### Windows

- Prefer non-exportable CNG/NCrypt keys, using platform or TPM-backed providers when exercised and available.
- DPAPI-wrapped exportable blobs are at most K3 and require clone/restore fixtures.
- Default operation is per-user. A Windows service or privileged helper is optional, separately installed and cannot grant source access to the networked sync process.
- Named-pipe ACLs bind the expected user SID and executable identity where available.

### Linux

- Prefer TPM2-backed non-exportable keys when explicitly configured and exercised.
- Secret Service storage is at most K3 unless the backend and migration behavior prove stronger properties.
- Encrypted application storage is K4 and cannot satisfy Hardened Source-Bound v1.
- Default operation uses a user systemd service when available; non-systemd fallback must preserve equivalent process separation and file permissions.
- Tray support is optional and must not be required for headless operation.

### WSL, containers and CI

- Default evidence ceiling is Standard unless a documented host-bound key, non-exportability property and rollback model pass conformance.
- Image, volume, home-directory and snapshot cloning are assumed possible.
- Ephemeral CI identities are separate device chains and cannot silently reuse an interactive user's key.

## Rollback and cloning contract

The local ledger stores an append-only pre-challenge commitment chain. The server stores the latest accepted sequence, prior hash and commitment checkpoint. Startup compares local state with the last server checkpoint before competitive collection resumes.

Restored state behind the server checkpoint enters recovery. Concurrent successors or reused commitment identifiers quarantine the device. Copying application files, virtual-machine snapshots, OS backups, credential migration or home directories never constitutes device transfer.

Required fixtures cover full-disk restore, home-directory restore, credential-store migration, VM snapshot rollback, cloned container volumes, concurrent clone submission, keychain unavailable, TPM/Secure Enclave reset, OS reinstall and downgrade to weaker key storage.

## Verified installation plans

An installation is a typed, ordered sequence of named operating-system operations and never a script. `packages/schemas/install-plan-v1.schema.json` is the record, `platform_install_plans` and `platform_install_operations` are the persistence owners, and D-389 records the choices.

Ten operations exist: `verify-release-signature`, `place-binary`, `register-service`, `set-autostart`, `grant-keystore-access`, `create-ipc-endpoint`, `register-privileged-supervisor`, `start-service`, `verify-health` and `remove-previous-version`. Eight reversals exist, and each operation either names the one a rollback runs or declares that it has none — because it changes nothing, as a verification does, or because its effect cannot be undone. A rollback that discovers the answer at run time is D-074's failure mode rather than its contract.

`verify-release-signature` is fixed at sequence 1 by the schema, in both directions: nothing else may occupy sequence 1, and it may occupy no other. No plan can place a filesystem write before the check that decides whether the release is genuine.

Every operation names its exact mechanism — `launchd-user`, `systemd-user`, `systemd-system`, `windows-service`, `windows-scheduled-task`. D-013 forbids claiming equal isolation strength across platforms, and a plan that left the mechanism implicit would be making that claim by omission. A plan containing `register-privileged-supervisor` carries `requires_privileged_consent`, because D-067 makes machine-wide supervision separately consented and least-privilege.

## IPC and authorization

All IPC uses restrictive ACLs, peer identity, executable/version binding where supported, challenge-response, message limits, rate limits, capability negotiation and replay protection. Sensitive actions require a user-presence or reauthentication policy: enrollment, key rotation, device removal, export, deletion, updater privilege changes and enabling optional elevated observation.

## Evidence ceilings

- K1/K2 plus C3/C4 and A2+ may qualify for Hardened Source-Bound v1 when every other profile requirement passes.
- K3 can qualify for Standard Live v1 but not Hardened after migration, restore or cloning uncertainty.
- K4 is Standard-only with explicit disclosure.
- K5/KU cannot enter competitive Hardened views.
- Unsupported platform capabilities lower the evidence profile; they do not silently weaken the profile definition.
