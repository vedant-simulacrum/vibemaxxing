# Native Runtime, Storage, and IPC Contract

Status: normative planning contract
Version: 1

## Processes

1. `vibeproof-collector`: transcript-capable, no network, reads approved local sources, emits fixed-schema normalized events.
2. `vibeproof-sync`: network-capable, cannot read source files or transcript storage, converts queued safe events into signed claims and syncs them.
3. `vibemaxxing-daemon`: service supervisor and local control plane; owns lifecycle, health, local policy, and IPC routing but not transcript contents.
4. `vibemaxxing-cli`: installer and noninteractive control client.
5. `vibemaxxing-shell`: macOS menu-bar / Windows and Linux tray UI.
6. `local-dashboard`: loopback-only UI served by the daemon or embedded shell, protected by an ephemeral local session token.

Closing the shell never stops collection. Stopping collection is an explicit action. The CLI and shell are replaceable clients of the same versioned local control API.

## Privileges

Baseline runs as the logged-in user without elevation. Installation may request elevation only to register a system service or platform integration, with explicit explanation. Collector access is allowlisted per source. Hardened platform integrations are optional and separately consented.

## Local storage

SQLite WAL database with encrypted sensitive columns; SQLCipher may be used where packaging and performance are acceptable. Schema domains:

- metadata and schema migrations;
- adapter installations/capabilities;
- normalized safe events;
- source checkpoints;
- sessions and parent-child relationships;
- claim queue and acknowledgements;
- device key metadata;
- audit ledger;
- local settings and consent;
- optional local-only analytics.

Transcript-bearing temporary data, if required by an adapter or analyzer, uses a separate store unavailable to sync and deleted according to the shortest configured retention. It is never included in backups by default.

Every migration is transactional, forward-tested from all supported versions, rollback-safe when possible, and preceded by a local encrypted backup. Failed migration leaves the old version operable or enters explicit recovery mode.

## Crash consistency

Source checkpoint, normalized event, dedup fingerprint, and claim-queue insertion commit atomically. Claims are removed only after durable server acknowledgement. WAL checkpoints are bounded. On crash, startup replays incomplete transactions and verifies the local hash chain.

Disk-full behavior pauses capture before corruption, surfaces a persistent warning, preserves acknowledged state, and never drops accepted-but-unsynced records silently. Corruption triggers read-only recovery, backup restore, or export-and-reset; it does not fabricate continuity.

## IPC

Local protocols use length-prefixed Protobuf messages over Unix-domain sockets or Windows named pipes.

Required envelope: protocol version, message ID, request type, timestamp, process nonce, challenge response, body length, and optional correlation ID.

Controls:

- OS peer identity and filesystem/DACL permissions;
- mutual application-level challenge-response;
- per-process ephemeral nonce;
- 1 MiB message limit and bounded nesting;
- request deadlines and cancellation;
- per-peer rate limits and connection caps;
- no arbitrary file paths or free-text transcript content on sync-facing channels;
- explicit version negotiation; incompatible peers fail closed with upgrade guidance.

The collector-to-daemon channel accepts normalized safe events only. The daemon-to-sync channel accepts signed-claim material only. The shell/CLI channel exposes health, settings, adapter status, safe aggregates, permissions, audit ledger, update and lifecycle commands.

## Device enrollment

The daemon generates an Ed25519 key in OS secure storage when possible, then obtains a one-time account-bound enrollment grant through browser or device-flow authorization. Enrollment binds account, device public key, platform, app build, nonce, and expiry. Server returns a revocable device ID and initial challenge.

Device transfer creates a new device identity. Keys are never exported as the default flow. Clone detection compares sequence/hash continuity and attestation/process evidence without using stable hardware fingerprints as user identity.

## Platform behavior

### macOS

LaunchAgent for user service; signed/notarized app bundle; Keychain; Unix socket or XPC where stronger identity is needed; menu-bar shell; optional Endpoint Security only for Hardened mode and only with explicit permission.

### Windows

Per-user service or scheduled startup task; DPAPI/CNG key protection; named pipes with explicit DACLs and client identity; tray shell; optional AppContainer/ETW/process evidence for Hardened mode.

### Linux

User systemd service when available with desktop autostart fallback; Secret Service or kernel/keyring-backed storage; Unix sockets with peer credentials; tray through StatusNotifier/AppIndicator where supported; Landlock/seccomp/no-new-privileges where available.

### WSL, containers, CI, remote environments

Each runtime receives an explicit environment identity. Host and guest capture domains are mutually exclusive or reconciled to prevent duplication. Ephemeral CI devices use short-lived keys and board policies may exclude them. Hardened evidence is unavailable where platform guarantees cannot be established.

## Lifecycle commands

`install`, `start`, `stop`, `status`, `doctor`, `login`, `logout`, `adapter list/add/remove/doctor`, `privacy inspect`, `claims inspect`, `sync`, `pause`, `resume`, `update`, `rollback`, `export`, `delete`, and `uninstall`.

Commands support JSON output, noninteractive operation, stable exit codes, and dry-run where destructive. Destructive deletion requires explicit scope and confirmation unless a signed noninteractive policy is supplied.

## Updates and rollback

Updater verifies platform signature, TUF metadata, hashes, provenance where available, compatibility, and disk space before atomic install. It retains one known-good version and database backup. Failed health check rolls back binaries and, where safe, schema. Security revocations may block known-compromised versions while preserving export/deletion access.

## Performance budgets

Idle daemon <= 100 MiB total RSS across baseline processes; idle CPU <= 0.5% average; no periodic wake more frequent than 30 seconds absent active sessions; active collection target <= 2% CPU excluding source tool cost; local event-to-visible-state p95 <= 2 seconds; startup p95 <= 3 seconds; disk growth bounded by retention and compaction policies.

## Privacy verification

The local UI displays every outbound claim field before sync, aggregate bytes sent, destination, device ID, adapter/evidence state, and rejection history. Packet-capture tests and canary scanning prove forbidden content never crosses the boundary.
