# ADR-010: Always-on daemon lifecycle

Status: accepted
Date: 2026-07-23
Decision: D-061

## Context

VibeMaxxing depends on observing qualifying agent activity when it occurs. A foreground application, menu-bar item, tray icon, terminal session, browser tab, or manually started process is not reliable enough. Users routinely close shells, log out of websites, lose network access, sleep and wake laptops, and allow foreground applications to be reclaimed. A collector that is not persistently supervised creates silent gaps, weakens evidence continuity, and makes the product feel unreliable.

The requirement described as “running 24/7” cannot literally cover a powered-off machine, OS shutdown, suspended hardware that executes no code, explicit uninstall, a user disabling the OS background item, or an unrecoverable platform failure. The product must therefore define and prove the strongest truthful guarantee.

## Decision

`vibemaxxing-daemon` is an always-on, OS-supervised, per-user background service.

Its desired state is `enabled` immediately after successful installation and registration. While the host OS can schedule the relevant user service context, the daemon must be running or in an OS-managed restart transition. It automatically starts at the earliest supported lifecycle point, restarts after crashes or hangs, resumes after sleep and network loss, survives desktop-shell closure, and remains resident when collection or synchronization is paused.

The daemon is the stable lifecycle owner. The collector, sync process, adapters, shell, local dashboard, and updater are supervised dependants and may restart independently without terminating the daemon.

## Always-on semantics

The guarantee applies while all of the following are true:

- the machine is powered on and the OS is able to schedule processes;
- the VibeMaxxing service remains installed and enabled;
- the OS has not disabled the registered background item or service;
- the required user service context exists for the selected platform mode;
- no explicit uninstall or durable service-disable operation is in progress.

The daemon must remain resident in degraded or recovery mode rather than exit when:

- no user is authenticated to VibeMaxxing;
- the network is unavailable;
- collection is paused;
- synchronization is paused;
- an adapter is unsupported or crashing;
- a source permission is missing or revoked;
- the key store is locked;
- local storage is full or read-only;
- local state is corrupt and requires recovery;
- the installed version is security-blocked;
- an update failed and rollback is required.

In those states the daemon continues to expose health, diagnostics, privacy inspection, export, update, rollback, recovery and uninstall controls as safely applicable.

## Lifecycle controls

The ordinary product does not expose “quit daemon” as a normal action.

- Closing or quitting the menu-bar/tray shell closes only the shell.
- `pause collection` stops new source observation but leaves the daemon running.
- `pause sync` stops network submission but leaves the daemon and collector policy state running.
- `restart daemon` requests an orderly supervised restart.
- Temporary stop is reserved for installer, updater, uninstaller, test harness and explicit advanced maintenance flows.
- A durable `disable background service` operation is separate from pause, requires explicit confirmation, is visible in status, and reduces product functionality until re-enabled.
- Uninstall unregisters the OS service only after local export/deletion choices and pending-state warnings are handled.

## Two-level supervision

### OS supervisor

The platform service manager owns the daemon process and restarts it after abnormal termination.

The daemon must not fork into the background, self-daemonize, or escape the platform supervisor. It handles graceful termination signals, persists durable state before exit, and returns meaningful exit classifications for service-manager diagnostics.

### Daemon supervisor

The daemon supervises collector, sync, adapter and helper processes.

- Child heartbeats are monotonic and authenticated over local IPC.
- A child is considered unresponsive only after a configurable grace period and at least two missed probes.
- The daemon first requests graceful shutdown, then force-terminates after a bounded deadline.
- Child restarts use bounded exponential backoff with jitter.
- A crash-looping child enters `degraded` or `quarantined-component`; the daemon remains alive.
- Restart counters reset only after a sustained healthy interval.
- One failing adapter cannot restart unrelated adapters or the daemon.
- The daemon never sacrifices privacy isolation merely to recover a component.

## Platform decisions

### macOS

- Register a per-user LaunchAgent through `SMAppService`.
- Configure the launchd job to be kept alive continuously and loaded for each login.
- The service is separate from the menu-bar application.
- The shell checks `SMAppService.status` and shows a persistent repair action if the user disables the background item in System Settings.
- A LaunchDaemon or privileged helper is not introduced merely to continue across logout. Such a component requires a separate ADR because it changes privilege, privacy and user-session access.
- After logout the per-user agent is not running; it automatically returns at the next login. This is reported as `session-bound`, not falsely described as machine-wide uptime.

### Windows

- Prefer an OS-managed per-user background service registered for automatic start in the user context.
- Where the supported packaging model cannot provide an appropriate per-user service, use an OS-managed scheduled startup task with equivalent single-instance, restart and health semantics.
- Configure recovery actions to restart after failure with bounded delays and a nonzero failure-reset interval; never reboot the computer as a VibeMaxxing recovery action.
- The tray process is independent and may exit without affecting collection.
- A machine-wide Windows Service running before login is optional and requires a separate privilege/privacy decision because most source data belongs to a user session.

### Linux

- Install a `systemd --user` service where systemd user managers are available.
- Use `Restart=always`; the application supplies bounded crash-loop backoff so service-level restart limits need not permanently disable the product.
- Offer user lingering when supported so the user manager can start at boot and continue after logout. Installation must report whether lingering is enabled, unavailable or requires authorization.
- Without lingering, report the lifecycle as `session-bound` and start automatically at the next login.
- Non-systemd fallback must use an OS desktop/session autostart mechanism plus a single-instance supervisor and must disclose its weaker restart guarantee.

### WSL, containers, CI and remote/headless environments

- Use the strongest native supervisor available in that environment.
- Ephemeral environments may be explicitly classified as `ephemeral` rather than pretending to provide continuous uptime.
- Container restart policy is deployment-owned; the daemon must still remain foreground and supervisor-compatible.

## Startup, recovery and availability targets

Planning targets, subject to implementation evidence:

- registration completed during installation before installation is reported successful;
- automatic start at supported boot/login boundary;
- daemon readiness p95 within 5 seconds after service-manager launch;
- abnormal-exit restart p95 within 10 seconds and p99 within 60 seconds, excluding platform throttling;
- hung-child detection and replacement within 90 seconds;
- sleep/resume health reconciliation begins within 5 seconds of resume notification;
- network reconnection triggers sync scheduling without daemon restart;
- update handoff target below 30 seconds of daemon unavailability;
- at least 99.9% daemon availability while the OS/user service context is available, measured locally without content-bearing telemetry;
- zero silent loss of durably queued claims due to restart.

These are evidence targets, not current implementation claims.

## State model

Service registration, daemon health, collection, synchronization and shell state are independent dimensions.

### Registration

`unregistered | registering | enabled | disabled-by-user | disabled-by-policy | unregistering | registration-error`

### Daemon

`starting | healthy | degraded | recovery | updating | rolling-back | security-hold | stopping-for-maintenance | failed-restart-pending`

### Collection

`enabled | paused-by-user | paused-by-policy | permission-required | storage-blocked | source-unavailable`

### Sync

`enabled | offline | backoff | paused-by-user | auth-required | server-blocked | security-hold`

### Shell

`closed | starting | open | crashed`

Shell state never changes daemon desired state.

## Persistent service record

Local durable state records:

- installation and service-registration IDs;
- selected platform lifecycle mode;
- desired service state;
- last successful start and clean stop;
- process generation;
- current build digest;
- last heartbeat monotonic counter;
- restart count and classified reason;
- child health and restart counters;
- platform service-manager status;
- whether Linux lingering is enabled;
- whether the OS/user disabled the background item;
- current degraded/recovery reason codes.

No record includes prompt, transcript, source path or repository content.

## Update and rollback behavior

- The updater never leaves the service unregistered during an ordinary version replacement.
- Update uses an explicit maintenance lease and single-instance lock.
- The old daemon drains durable writes and hands control back to the OS supervisor or atomic replacement mechanism.
- A new version must pass startup, IPC, storage and privacy self-checks before the previous known-good version is removed.
- Failure triggers rollback without changing device lineage or silently discarding queued claims.
- Security-blocked versions enter minimal safe mode when possible, retaining update, export and uninstall access.

## Failure safety

Always-on does not mean uncontrolled restart storms.

- The daemon uses bounded memory, CPU, file descriptors and log volume.
- Repeated child failures degrade the component rather than hot-looping.
- Repeated daemon failures are surfaced through the OS service manager and shell/installer repair tooling.
- The product must not request a host reboot to recover itself.
- A watchdog may restart a hung process but may not bypass database, migration, privacy, signature or version checks.
- Recovery never resets sequence, commitment or device lineage silently.

## Required implementation evidence

Before launch, exercise at minimum:

- closing and crashing the shell;
- normal daemon restart and kill -9 termination;
- repeated daemon crash with platform throttling;
- collector, sync and single-adapter crash loops;
- hung child and hung daemon detection;
- login, logout and subsequent login;
- OS reboot;
- sleep, hibernate where supported, and resume;
- network loss and reconnection;
- permission revocation;
- key-store lock;
- disk full and read-only storage;
- corrupt local database;
- interrupted update and rollback;
- security-blocked version;
- OS background item/service disabled by the user;
- Linux linger enabled and unavailable paths;
- uninstall with queued unsynchronized claims;
- no duplicate claim or continuity reset after every recovery path.

Each platform test records service-manager configuration, timestamps, process generations, restart reasons, durable queue invariants, privacy-canary result and user-visible status.

## Consequences

- Background persistence is a core product requirement and launch gate.
- The daemon consumes a small continuous resource budget even when no agent is active.
- The shell cannot be the service owner.
- Platform lifecycle strength is disclosed honestly.
- macOS and some Windows/Linux configurations are session-bound unless a separately approved machine-wide mode exists.
- Users retain the OS-level ability to disable or uninstall the service; the product detects and clearly reports this rather than attempting to bypass user control.
