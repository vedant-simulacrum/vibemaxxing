# Native Runtime, Storage, and IPC Contract

Status: normative planning contract
Version: 2
Updated: 2026-07-23

## Processes

1. `vibeproof-collector`: transcript-capable, no network, reads approved local sources, emits fixed-schema normalized events.
2. `vibeproof-sync`: network-capable, cannot read source files or transcript storage, converts queued safe events into signed claims and syncs them.
3. `vibemaxxing-daemon`: always-on service supervisor and local control plane; owns lifecycle, service-manager reconciliation, health, local policy, and IPC routing but not transcript contents.
4. `vibemaxxing-cli`: installer and noninteractive control client.
5. `vibemaxxing-shell`: macOS menu-bar / Windows and Linux tray UI.
6. `local-dashboard`: loopback-only UI served by the daemon or embedded shell, protected by an ephemeral local session token.

Closing the shell never stops collection. Pausing collection or sync never stops the daemon. The CLI and shell are replaceable clients of the same versioned local control API.

## Continuous service contract

D-061 and ADR-010 are binding.

- Installation is not successful until the applicable OS service registration exists and its desired state is enabled.
- The daemon auto-starts at the earliest supported boot or user-login boundary.
- The daemon remains a foreground child of the platform supervisor and never self-daemonizes.
- Abnormal exit triggers OS-managed restart.
- The daemon remains resident while offline, logged out of VibeMaxxing, paused, permission-blocked, storage-blocked, recovering, updating, rolling back, or security-held.
- Child collector, sync, adapter, and helper processes may restart independently.
- A child crash loop degrades only the affected capability and cannot terminate the daemon.
- The ordinary UI exposes pause and restart, not quit.
- Explicit disable and uninstall are distinct durable operations with confirmation and visible status.

The uptime promise excludes powered-off hardware, full suspension where no code executes, OS shutdown, a disabled/uninstalled service, or an unavailable user-service context. Platform lifecycle mode is persisted and displayed as `machine-wide`, `boot-persistent`, `session-bound`, or `ephemeral`.

## Privileges

Baseline runs as the logged-in user without elevation. Installation may request elevation only for an explicitly approved platform integration, with explanation. Collector access is allowlisted per source. Hardened platform integrations are optional and separately consented.

A privileged machine-wide service is not introduced solely to improve marketing language around uptime. It requires a separate accepted ADR covering privilege, session access, privacy, and uninstall behavior.

## Supervision protocol

### Platform supervisor to daemon

The service manager owns:

- registration and automatic start;
- one running daemon instance per installation/user context;
- abnormal-exit restart;
- graceful stop deadline;
- exit classification and diagnostics;
- prevention of host reboot as an application recovery action.

The daemon owns:

- readiness notification;
- graceful termination and durable-state flush;
- watchdog/health response;
- monotonic process generation;
- classified exit code;
- restart-loop backoff metadata.

### Daemon to child

Each child registration binds:

- process role;
- process generation;
- build and artifact digest;
- protocol version;
- capability set;
- authenticated IPC identity;
- heartbeat interval and grace period;
- restart policy;
- resource budget.

The daemon requires two missed probes before declaring a child unresponsive, requests graceful shutdown, force-terminates after a deadline, and restarts with bounded exponential backoff plus jitter. Restart counters reset only after sustained health. Stale child generations cannot submit IPC messages after replacement.

## Local storage

SQLite WAL database with encrypted sensitive columns; SQLCipher may be used where packaging and performance are acceptable. Schema domains:

- metadata and schema migrations;
- service registration and lifecycle state;
- daemon and child process generations;
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

Every migration is transactional, forward-tested from all supported versions, rollback-safe when possible, and preceded by a local encrypted backup. Failed migration leaves the prior version operable or enters explicit recovery mode while the daemon remains available for repair/export/uninstall.

## Service-state persistence

Persist at minimum:

- installation ID;
- service-registration ID and platform mode;
- desired service state;
- OS service-manager status;
- last successful daemon start;
- last clean daemon stop;
- daemon process generation;
- current build digest;
- last monotonic heartbeat;
- classified restart reason;
- daemon and child restart counters;
- per-child health state;
- Linux lingering state;
- disabled-background-item state;
- degraded/recovery reason codes.

Writes that change desired service state, update state, or uninstall progress are transactional and crash recoverable.

## Crash consistency

Source checkpoint, normalized event, dedup fingerprint, and claim-queue insertion commit atomically. Claims are removed only after durable server acknowledgement. WAL checkpoints are bounded. On crash, startup replays incomplete transactions and verifies the local hash chain.

Disk-full behavior pauses capture before corruption, surfaces a persistent warning, preserves acknowledged state, and never drops accepted-but-unsynced records silently. The daemon stays available in `storage-blocked`. Corruption triggers read-only recovery, backup restore, or export-and-reset; it does not fabricate continuity.

## IPC

Local protocols use length-prefixed Protobuf messages over Unix-domain sockets, XPC where selected on macOS, or Windows named pipes.

Required envelope:

- protocol major/minor;
- message ID;
- sender role;
- sender process generation;
- monotonic send counter;
- deadline;
- process nonce;
- challenge response;
- body length;
- optional correlation ID.

Controls:

- OS peer identity and filesystem/DACL permissions;
- mutual application-level challenge-response;
- per-process ephemeral nonce;
- process-generation binding;
- 1 MiB message limit and bounded nesting;
- request deadlines and cancellation;
- per-peer rate limits and connection caps;
- no arbitrary file paths or free-text transcript content on sync-facing channels;
- explicit version negotiation; incompatible peers fail closed with upgrade guidance.

The collector-to-daemon channel accepts normalized safe events only. The daemon-to-sync channel accepts signed-claim material only. The shell/CLI channel exposes health, lifecycle mode, service-manager status, settings, adapter state, safe aggregates, permissions, audit ledger, update and lifecycle commands.

## Device enrollment

The daemon generates an Ed25519 key in OS secure storage when possible, then obtains a one-time account-bound enrollment grant through browser or device-flow authorization. Enrollment binds account, device public key, platform, app build, daemon installation ID, nonce, and expiry. Server returns a revocable device ID and initial challenge.

Device transfer creates a new device identity. Keys are never exported as the default flow. Clone detection compares sequence/hash continuity and attestation/process evidence without using stable hardware fingerprints as user identity.

## Platform behavior

### macOS

- Register a per-user LaunchAgent through `SMAppService`.
- Configure launchd for automatic login loading and continuous keep-alive.
- Use signed/notarized app and service components.
- Store keys in Keychain/Secure Enclave where supported.
- Use Unix socket or XPC with authenticated peer identity.
- Menu-bar shell remains independent.
- If the user disables the background item in System Settings, report `disabled-by-user` and provide repair steps.
- Per-user mode is session-bound at logout and resumes automatically at next login.

### Windows

- Prefer an OS-managed per-user background service.
- If packaging constraints prevent that, use an OS-managed scheduled startup task with equivalent single-instance, restart, and health behavior.
- Configure automatic start and recovery restart with bounded delays.
- Never configure machine reboot as recovery.
- Use DPAPI/CNG key protection and named pipes with explicit DACLs/client identity.
- Tray shell remains independent.

### Linux

- Use a `systemd --user` service where available.
- Configure `Restart=always`; application backoff prevents unbounded crash loops.
- Offer and detect user lingering where supported.
- Persist/report `linger-enabled`, `session-bound`, `linger-unavailable`, or `authorization-required`.
- Use Secret Service or kernel/keyring-backed storage and Unix sockets with peer credentials.
- Non-systemd fallback uses desktop/session autostart plus single-instance supervision and receives a weaker lifecycle grade.

### WSL, containers, CI, remote environments

Each runtime receives an explicit environment identity. Host and guest capture domains are mutually exclusive or reconciled to prevent duplication. Ephemeral CI devices use short-lived keys and board policies may exclude them. Hardened evidence is unavailable where platform guarantees cannot be established.

Use the strongest native supervisor available. In containers the daemon remains foreground and container restart policy is deployment-owned.

## Lifecycle commands

User-facing commands:

`install`, `status`, `doctor`, `login`, `logout`, `adapter list/add/remove/doctor`, `privacy inspect`, `claims inspect`, `sync`, `pause collection`, `resume collection`, `pause sync`, `resume sync`, `restart daemon`, `background-service status`, `background-service repair`, `background-service enable`, `background-service disable`, `update`, `rollback`, `export`, `delete`, and `uninstall`.

Temporary `stop daemon` exists only for installer/updater/uninstaller/test/advanced-maintenance interfaces and is not presented as an ordinary daily action.

Commands support JSON output, noninteractive operation, stable exit codes, and dry-run where destructive. Durable disable, deletion, and uninstall require explicit scope and confirmation unless a signed noninteractive policy is supplied.

## Sleep, network, and session transitions

- Sleep/hibernate writes no fabricated stop event.
- Resume creates a new monotonic generation when required, validates child health, reconciles source state, and schedules sync.
- Network loss sets sync `offline`; collection continues within storage bounds.
- Network restoration schedules sync without restarting the daemon.
- Login starts the user service automatically.
- Logout behavior follows the declared lifecycle mode.
- OS reboot restarts the service at the next supported lifecycle boundary.
- User-service unavailability is visible and never silently interpreted as successful collection.

## Updates and rollback

Updater verifies platform signature, TUF metadata, hashes, provenance, release-set compatibility, and disk space before atomic install.

- Preserve service registration across ordinary replacement.
- Acquire a maintenance lease and single-instance lock.
- Drain and persist durable writes.
- Stop only the minimum required components.
- Install atomically.
- Return lifecycle ownership to the OS supervisor.
- Require new build startup, IPC, migration, storage, and privacy self-checks.
- Retain one known-good version and database backup.
- Roll back on failed health check.
- Security-blocked versions retain update, export, repair, and uninstall access in minimal safe mode where possible.

## Performance and availability budgets

- Idle daemon/process set <= 100 MiB total RSS target.
- Idle CPU <= 0.5% average target.
- No periodic wake more frequent than 30 seconds absent active sessions, except bounded health probes required by the supervision policy.
- Active collection target <= 2% CPU excluding source-tool cost.
- Local event-to-visible-state p95 <= 2 seconds.
- Daemon readiness p95 <= 5 seconds after service-manager launch.
- Abnormal-exit restart p95 <= 10 seconds and p99 <= 60 seconds, excluding platform throttling.
- Hung-child replacement <= 90 seconds.
- Resume reconciliation begins <= 5 seconds after wake notification.
- Update handoff causes < 30 seconds daemon unavailability.
- Daemon availability target >= 99.9% while the applicable OS/user service context is available.
- Disk growth is bounded by retention and compaction policies.
- Zero silent loss of durably queued claims due to restart.

## Required validation

Exercise on every supported platform/mode:

- install and service registration;
- shell close and shell crash;
- daemon graceful restart;
- daemon forced termination;
- repeated crash and service-manager throttling;
- collector, sync, and adapter crash loops;
- hung child and hung daemon;
- login/logout/login;
- reboot;
- sleep/hibernate/resume;
- network loss/reconnection;
- permission revocation;
- key-store lock;
- disk full/read-only storage;
- corrupt database;
- interrupted update and rollback;
- security-blocked version;
- background service disabled by user;
- Linux linger enabled/unavailable;
- uninstall with unsynchronized queue;
- no duplicate claim, silent gap, sequence reset, or privacy-canary egress after recovery.

## Privacy verification

The local UI displays every outbound claim field before sync, aggregate bytes sent, destination, device ID, adapter/evidence state, service lifecycle mode, and rejection history. Packet-capture tests and canary scanning prove forbidden content never crosses the boundary.
