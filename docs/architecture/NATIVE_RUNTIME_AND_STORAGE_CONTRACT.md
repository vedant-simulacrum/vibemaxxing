# Native Runtime, Storage, and IPC Contract

Status: normative planning contract
Version: 4
Updated: 2026-08-06
Decisions: D-231

## Processes

1. `vibeproof-collector`: transcript-capable, no network, reads approved local sources and emits fixed-schema normalized events.
2. `vibeproof-sync`: network-capable, cannot read source files or transcript storage, finalizes and submits safe claims.
3. `vibemaxxing-daemon`: always-on service supervisor and local control plane; owns lifecycle, health, local policy, service-manager reconciliation and IPC routing but not transcript contents.
4. `vibemaxxing-cli`: installer and noninteractive control client.
5. `vibemaxxing-shell`: macOS menu-bar and Windows/Linux tray UI.
6. `local-dashboard`: loopback-only control UI protected by an ephemeral local session token. Loopback binding is a network control and a browser on the same machine is not on the network, so the dashboard is also a cross-site request forgery and DNS-rebinding surface; `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md` owns the `Host` allowlist, `Origin` rules, token handling and expiry that make the binding a boundary.
7. optional `vibemaxxing-machine-supervisor`: separately installed privileged lifecycle component under ADR-012; it cannot inspect source content or hold ordinary user claim keys.

Closing the shell never stops collection. Pausing collection or sync never stops the daemon. The CLI, shell and dashboard are replaceable clients of the same versioned local control API.

There is no Android, iOS, iPadOS or ChromeOS native process, package, collector, companion or control application.

## Continuous service contract

D-061 and ADR-010 are binding.

- Installation is not successful until the applicable service registration exists and desired state is enabled.
- The daemon starts at the earliest supported boot or login boundary for the declared lifecycle profile.
- The daemon remains a foreground child of the platform supervisor and never self-daemonizes.
- Abnormal exit triggers supervisor-managed restart.
- The daemon remains resident while offline, unauthenticated, paused, permission-blocked, storage-blocked, recovering, updating, rolling back, security-held or version-blocked.
- Collector, sync, adapter and helper processes restart independently.
- A child crash loop degrades only that capability.
- Ordinary UX exposes pause and restart, not quit.
- Explicit disable and uninstall are separate durable operations.

Lifecycle modes are:

- `machine-wide`;
- `boot-persistent`;
- `session-bound`;
- `host-dependent`;
- `orchestrator-dependent`;
- `ephemeral`.

The uptime promise excludes powered-off hardware, full suspension where no code executes, OS shutdown, disabled/uninstalled services and unavailable service contexts.

## Privilege contract

The default profile runs as the logged-in user without elevation.

ADR-012 permits an optional machine-wide privileged supervisor only when:

- installation and consent are separate from the default per-user path;
- capabilities are limited to service registration, supervision, bounded health, signed update coordination, approved directory/ACL setup and repair/uninstall;
- it cannot read source files, prompts, transcripts, code, repositories or adapter-private stores;
- it cannot hold ordinary user claim keys, intercept provider traffic, install kernel anti-cheat or open remote-control ports;
- every user retains separate local storage, keys, lineage and claim chain;
- cross-privilege IPC is typed, authenticated, ACL-bound, replay-resistant and generation-bound;
- disabling or removing privileged mode does not silently delete or merge user state.

Privilege does not award Hardened evidence by itself.

## Supervision protocol

### Platform supervisor to daemon

The service manager owns:

- registration and automatic start;
- one daemon per installation/profile;
- abnormal-exit restart;
- graceful-stop deadline;
- exit classification;
- restart throttling;
- prevention of host reboot as the default recovery action.

The daemon owns:

- readiness notification;
- graceful termination and durable-state flush;
- watchdog response;
- monotonic process generation;
- classified exit code;
- restart-loop metadata.

### Daemon to child

Each child registration binds:

- process role and generation;
- build/artifact digest;
- protocol version;
- capability set;
- authenticated IPC identity;
- heartbeat/grace policy;
- restart policy;
- resource budget.

Two missed probes are required before unresponsive classification. The daemon requests graceful shutdown, force-terminates after a deadline and restarts with bounded exponential backoff plus jitter. Counters reset only after sustained health. Stale generations cannot submit messages after replacement.

### Privileged supervisor to user daemon

The privileged channel exposes only:

- register/start/stop/restart status;
- installed and target release-set digest;
- bounded health state and reason code;
- update/rollback/repair/uninstall commands;
- user-session activation request where supported.

No normalized event, claim payload, source path, prompt, transcript or user credential crosses this boundary.

## Local storage

Use SQLite WAL with encrypted sensitive columns; SQLCipher may be selected where packaging and performance are acceptable.

Schema domains include:

- metadata and migrations;
- exact platform-profile identity;
- service registration and lifecycle state;
- privileged-supervisor registration state;
- daemon and child generations;
- adapter installations/capabilities;
- normalized safe events;
- source checkpoints;
- sessions and parent-child relationships;
- commitments, pending claims and acknowledgements;
- device/environment key metadata;
- audit ledger;
- update policy, deadline and rollback state;
- settings and consent;
- optional local-only analytics.

Transcript-bearing temporary data uses a separate store unavailable to sync and excluded from backups by default.

Every migration is transactional, forward-tested from all supported versions, preceded by an encrypted backup and rollback-safe where possible. Failure leaves the prior version operable or enters explicit recovery while update, export and uninstall remain available.

## Service-state persistence

Persist at minimum:

- installation ID;
- exact support tuple: OS family/release, architecture, distribution/package, environment kind, lifecycle mode, key-protection class and release-set version;
- service-registration ID and desired state;
- OS/orchestrator status;
- privileged-profile state and supervisor artifact digest;
- last successful daemon start and clean stop;
- daemon/child process generations;
- current build and adapter digests;
- heartbeat and classified restart reason;
- restart counters and child health;
- Linux lingering/init state;
- disabled-background-item state;
- update channel, class, signed deadline, target digest and rollback state;
- degraded/recovery reason codes.

Writes changing service state, privilege mode, update state or uninstall progress are transactional and crash recoverable.

## Crash consistency

Source checkpoint, normalized event, dedup fingerprint, deterministic rule result, local commitment and claim-queue insertion commit atomically. Claims are removed only after durable server acknowledgement.

On crash, startup replays incomplete transactions and verifies local continuity. Disk-full behavior pauses capture before corruption and never silently drops accepted-but-unsynced records. Corruption enters read-only recovery, backup restore or export-and-reset without fabricating continuity.

## IPC

Local protocols use length-prefixed generated Protobuf messages over Unix-domain sockets, XPC where selected on macOS or Windows named pipes.

Required envelope:

- protocol major/minor;
- message ID;
- sender role and process generation;
- monotonic send counter;
- deadline;
- process nonce and challenge response;
- body length;
- optional correlation ID.

Controls:

- OS peer identity and filesystem/DACL permissions;
- mutual challenge-response;
- per-process nonce and generation binding;
- 1 MiB maximum and bounded nesting;
- request deadlines/cancellation;
- per-peer rate and connection limits;
- no arbitrary paths or free text on sync/privilege channels;
- explicit negotiation; incompatible peers fail closed with upgrade guidance.

Collector-to-daemon accepts only typed safe events. Daemon-to-sync accepts only typed claim material. Shell/CLI channels expose health, lifecycle, platform profile, update status, settings, adapter state, safe aggregates, permissions, audit and lifecycle commands.

## Device and environment enrollment

The daemon generates an Ed25519 key in the strongest available supported backend and obtains a one-time account-bound enrollment grant. Enrollment binds:

- account;
- public key;
- device/environment lineage;
- exact platform profile;
- collector/release-set digest;
- native session;
- nonce and expiry.

Device transfer creates a new lineage. Keys are not exported by default. Clone detection uses continuity and bounded platform/environment signals without treating stable hardware identifiers as public human identity.

CI uses short-lived job identities. Containers bind workload/state-volume identity. WSL owns guest lineage separate from Windows-native lineage.

## Platform behavior

### macOS

- Apple silicon `arm64` and Intel `x86_64` are launch profiles.
- Current macOS major and two preceding majors are target policy where architecture support exists.
- Per-user LaunchAgent through `SMAppService` is default.
- Signed/notarized Universal 2 or architecture-specific compatible artifacts.
- Keychain/Secure Enclave capability classification.
- XPC or Unix socket with peer identity.
- Background-item disable state is visible and repairable.
- Optional constrained LaunchDaemon/helper under ADR-012.

### Windows

- Native x64 and native ARM64 are launch profiles.
- Maintained desktop and applicable Server/headless profiles.
- Per-user OS-managed service or scheduled-task fallback with equivalent semantics.
- CNG/TPM with DPAPI fallback classification.
- Named pipes with explicit DACL/client identity.
- Optional constrained Windows Service under ADR-012.
- Host reboot is never the first recovery action.

### Linux

- Launch prebuilt architectures: x86_64 and aarch64.
- Package profiles: deb, rpm families, Arch, Alpine/musl, Nix and signed portable glibc/musl archives.
- `systemd --user` primary; lingering offered/recommended with explicit authorization.
- OpenRC, runit, s6 and dinit templates for certified headless profiles.
- Desktop autostart is weaker/session-bound.
- GNOME, KDE, Xfce, Cinnamon, MATE and LXQt are tested where advertised; core behavior is Wayland/X11 independent.
- TPM, Secret Service, kernel-keyring and encrypted fallback classes.
- Optional constrained system supervisor under ADR-012.

### WSL

- Globally competitive by default at verifier-awarded evidence level.
- Guest-specific lineage and keys.
- Windows/WSL duplicate-domain reconciliation.
- systemd-enabled and disabled lifecycle paths.
- host-dependent lifetime disclosure.
- independent install/update/uninstall.
- Standard default ceiling unless a stronger WSL profile is certified.

### Containers

- Globally competitive certified profiles.
- Foreground non-self-daemonizing process under orchestrator.
- Non-root signed/provenance-bound images.
- Explicit state volume and read-only root compatibility where practical.
- No runtime socket by default.
- Immutable image replacement.
- Replica/state-volume duplicate prevention.
- Standard default ceiling unless stronger controlled execution is certified.

### CI/ephemeral

- Globally competitive by default.
- Short-lived job/workflow identity and key.
- Deterministic retry, cache and matrix duplicate domains.
- No continuity assumption without protected state.
- No daemon after job termination.
- Current pinned artifact required.
- Standard default ceiling unless a stronger runner profile is certified.

## Lifecycle commands

User-facing commands:

`install`, `status`, `doctor`, `login`, `logout`, `adapter list/add/remove/doctor`, `privacy inspect`, `claims inspect`, `sync`, `pause collection`, `resume collection`, `pause sync`, `resume sync`, `restart daemon`, `background-service status/repair/enable/disable`, `privileged-service status/install/remove`, `update status/check/apply`, `rollback`, `export`, `delete`, and `uninstall`.

Temporary daemon stop exists only for installer/updater/uninstaller/test/advanced maintenance. Durable disable, privileged installation/removal, deletion and uninstall require explicit scope and confirmation unless governed by an approved signed noninteractive policy.

## Session and environment transitions

- Sleep/hibernate does not fabricate a stop event.
- Resume creates a new monotonic generation when needed and reconciles source state.
- Network loss sets sync offline; collection continues within storage/compatibility limits.
- Network restoration schedules sync without daemon restart.
- Logout behavior follows lifecycle mode.
- OS reboot returns at the next supported lifecycle boundary.
- WSL shutdown, container termination and CI job end produce explicit environment termination state.
- Service unavailability is visible and never interpreted as successful collection.

## Mandatory updates and rollback

ADR-013 is binding.

Update classes:

- `emergency-security-integrity`;
- `required-compatibility`;
- `routine-product`.

Every signed update policy includes current/minimum version, target release-set digest, deadline, allowed deferral, affected capabilities and blocked-version behavior.

The updater:

- verifies platform signature, TUF metadata, digests, provenance and compatibility;
- preserves service registration;
- acquires a maintenance lease and single-instance lock;
- drains durable writes;
- replaces only required components atomically;
- returns lifecycle ownership to the supervisor;
- runs startup, IPC, migration, storage and privacy checks;
- retains a known-good version and backup;
- rolls back on failure without resetting lineage or dropping queued claims.

Competitive profiles cannot permanently disable required updates. A version past deadline may lose new collection, claim finalization or sync, but retains diagnostics, update, export and uninstall where safe.

Containers update through immutable image replacement. CI uses current pinned artifacts and server-enforced expiry rather than a persistent updater.

## Performance and availability budgets

Planning targets:

- idle process set <= 100 MiB RSS;
- idle CPU <= 0.5% average;
- no periodic wake more frequent than 30 seconds absent active sessions except bounded health probes;
- active collection <= 2% CPU excluding source-tool cost;
- local event-to-visible state p95 <= 2 seconds;
- daemon readiness p95 <= 5 seconds;
- abnormal-exit restart p95 <= 10 seconds and p99 <= 60 seconds excluding supervisor throttling;
- hung-child replacement <= 90 seconds;
- resume reconciliation begins <= 5 seconds;
- ordinary update handoff < 30 seconds daemon unavailability;
- daemon availability >= 99.9% while its service context exists;
- zero silent loss of durable queued claims.

## Required validation

For every advertised exact platform tuple exercise:

- install/service registration and repair;
- shell close/crash;
- daemon graceful/forced restart and crash-loop throttling;
- collector/sync/adapter crash loops and hangs;
- login/logout/reboot/sleep/hibernate where applicable;
- network loss/reconnection;
- permission and key-store failure;
- disk full/read-only/corrupt storage;
- mandatory update deadlines, interrupted update and rollback;
- blocked-version safe mode;
- service disabled by user/policy;
- privileged supervisor cross-user, substitution and uninstall paths where offered;
- WSL export/import/clone and host/guest duplication;
- container volume clone/replica duplication;
- CI retry/cache/matrix duplication and expired artifact rejection;
- uninstall with unsynchronized queue;
- no duplicate claim, silent gap, sequence reset or privacy-canary egress.

## Privacy verification

The local UI exposes every outbound claim field, aggregate bytes, destination, device/environment lineage, adapter/evidence state, exact support tuple, lifecycle mode, privilege mode, update deadline and rejection history. Packet-capture and canary tests prove forbidden content never crosses local, network or privileged boundaries.