# Native Client, Daemon, CLI, Menu-Bar, and Tray Architecture

Updated: 2026-07-23
Status: planning contract

## Product topology

The local product consists of:

- `vibemaxxing-daemon`: always-on lifecycle owner and local control plane;
- `vibeproof-collector`: transcript-private live observation and deterministic normalization;
- `vibeproof-sync`: networked safe-claim synchronization process with no transcript access;
- `vibemaxxing-cli`: installer, diagnostics, automation, and headless control;
- `vibemaxxing-desktop-shell`: macOS menu-bar and Windows/Linux tray UX;
- local audit/control UI;
- hosted VibeMaxxing web dashboard;
- signed updater and platform service integration.

Process separation must preserve the privacy boundary: a process that can inspect content cannot access the network, while the networked process cannot inspect content.

## Always-on requirement

Under D-061 and ADR-010, the daemon desired state is `enabled` after successful installation.

- The platform service manager starts it automatically at the earliest supported boot or login boundary.
- The platform service manager restarts it after abnormal termination.
- The daemon remains resident when collection is paused, sync is paused, the network is unavailable, authentication is missing, permissions are revoked, storage is blocked, an adapter is broken, or recovery is required.
- Closing, quitting, crashing, updating, or never opening the desktop shell does not stop the daemon.
- The shell is not a parent process, owner, watchdog, or source of truth for daemon lifecycle.
- Normal product UX does not expose `quit daemon`; it exposes `pause collection`, `pause sync`, `restart`, `repair background service`, and `uninstall` as separate actions.
- A durable service-disable action is advanced, explicit, confirmed, visible, and reversible.
- The daemon must not self-daemonize or detach from the OS supervisor.

The truthful boundary is that no process can run while the machine is powered off, the OS cannot schedule the user service, the service is disabled or uninstalled, or hardware is fully suspended. The product must distinguish `machine-wide`, `boot-persistent`, `session-bound`, and `ephemeral` lifecycle modes.

## Ownership

### Daemon

Owns process supervision, adapter registry, local account/device binding, health, local configuration, IPC routing, lifecycle, service-manager reconciliation, and upgrade coordination. It must not become a transcript-processing monolith.

The daemon remains alive in `degraded`, `recovery`, `security-hold`, and `update-required` states so diagnostics, privacy inspection, update, rollback, export, repair, and uninstall remain available.

### Collector

Owns source observation, privacy filtering, deterministic event normalization, local evidence continuity, and safe handoff. No network access.

### Sync

Owns challenge retrieval, claim submission, acknowledgements, retries, backoff, and server session renewal. It receives only safe fixed-schema data.

### CLI

Supports install, uninstall, start, restart, status, login, logout, adapter list/add/remove/diagnose, privacy audit, export, delete, update, rollback, logs, doctor, pause collection, pause sync, resume collection, resume sync, background-service status/repair/enable/disable, and headless operation. Commands require stable exit codes and machine-readable output.

A temporary daemon stop is reserved for installer, updater, uninstaller, test harness, or explicit advanced maintenance. `stop` must not be presented as the ordinary equivalent of pause.

### Desktop shell

Shows active/idle/offline/private state, supported adapters, sync health, daemon/service-manager health, privacy boundary, updates, account/device controls, and a link or authenticated bridge to the hosted dashboard. Closing the shell must never stop the daemon, collector, or sync process.

## Two-level supervision

### OS-level supervision

The OS service manager owns the daemon process.

- One service registration per installation and user context.
- Single-instance enforcement.
- Auto-start enabled after installation.
- Restart after abnormal exit.
- Graceful stop deadline followed by forced termination only when required.
- Exit classification and service-manager diagnostics.
- No host reboot as a recovery action.
- No unlimited hot restart loop.

### Daemon-level supervision

The daemon owns child processes.

- Authenticated monotonic heartbeat per child.
- At least two missed probes before an unresponsive decision.
- Graceful termination request before force kill.
- Bounded exponential restart backoff with jitter.
- Restart counter reset only after sustained health.
- Per-component crash-loop quarantine.
- Failing adapter isolation.
- Child generation IDs to reject stale IPC after restart.
- Durable state reconciled before a recovered child resumes work.

A child failure may degrade collection or sync, but must not terminate the daemon.

## Local versus hosted UX

Local UX owns installation, permissions, adapter discovery, privacy verification, device state, collection controls, daemon/service repair, diagnostics, outbound ledger inspection, local export/deletion, and update status.

Hosted web owns leaderboards, profiles, friends, rivals, boards, organizations, communities, social notifications, moderation, appeals, and server-side account settings.

No hosted page may require prompt, transcript, project, repository, path, or code access.

## State model

Lifecycle dimensions are independent.

### Service registration

`unregistered -> registering -> enabled -> disabled-by-user | disabled-by-policy | registration-error -> unregistering -> unregistered`

### Daemon health

`starting -> healthy -> degraded | recovery | security-hold | updating | rolling-back -> healthy`

Exceptional state: `failed-restart-pending`, owned by the OS supervisor and repair UX.

### Collection

`enabled | paused-by-user | paused-by-policy | permission-required | source-unavailable | storage-blocked`

### Sync

`enabled | offline | backoff | paused-by-user | auth-required | server-blocked | security-hold`

### Shell

`closed | starting | open | crashed`

Shell state has no transition that changes service registration or daemon desired state.

## Platform behavior

### macOS

- Per-user LaunchAgent registered through `SMAppService`.
- launchd job configured for continuous keep-alive and login loading.
- Separate menu-bar application.
- Shell reports `SMAppService.status` and provides repair instructions when disabled in System Settings.
- App signing and notarization apply to daemon, shell, helpers, and updater.
- Per-user mode is session-bound across logout; it automatically resumes at next login.
- No LaunchDaemon or privileged helper solely to claim 24/7 uptime. Machine-wide mode requires a separate ADR.

### Windows

- OS-managed per-user background service where supported; otherwise an OS-managed scheduled startup task with equivalent single-instance, restart, and health semantics.
- Automatic start in the relevant user context.
- Recovery actions restart the service with bounded delays.
- Never configure automatic host reboot as recovery.
- Tray shell remains independent.
- Machine-wide pre-login service requires a separate privilege/privacy decision.

### Linux

- `systemd --user` service where available.
- `Restart=always` plus application-level bounded crash-loop backoff.
- Offer and detect user lingering where supported to start at boot and continue after logout.
- Report `linger-enabled`, `session-bound`, `linger-unavailable`, or `authorization-required` honestly.
- Non-systemd fallback uses desktop/session autostart plus a single-instance supervisor and is assigned a weaker lifecycle grade.

### WSL, containers, CI, and headless environments

- CLI/daemon only unless a graphical shell is explicitly supported.
- Use the strongest native supervisor available.
- Container process remains foreground; container restart policy is deployment-owned.
- Ephemeral environments are labeled `ephemeral` and do not claim persistent uptime.

Baseline operation must not require administrator/root privileges. Optional hardening may require explicit elevated setup and must produce a stronger evidence label rather than silently changing behavior.

## IPC

All local IPC requires peer identity, restrictive ACLs, challenge-response, protocol versioning, message size and rate limits, replay protection where relevant, explicit errors, capability negotiation, child generation binding, and deadlines. Never rely only on socket path secrecy.

## Storage and service records

Define separate storage for configuration, normalized events, pending claims, accepted acknowledgements, audit ledger, adapter state, evidence continuity, diagnostics, and lifecycle supervision.

The lifecycle record includes:

- service-registration identifier and mode;
- desired enabled/disabled state;
- current process generation and build digest;
- last successful start and clean stop;
- last monotonic heartbeat;
- classified exit/restart reason;
- daemon and child restart counters;
- service-manager status;
- Linux lingering status;
- disabled-background-item state;
- current degraded/recovery reason codes.

It contains no prompt, transcript, path, repository, or source content.

Sensitive keys use OS credential facilities where available. Database encryption, crash consistency, checkpoints, rollback detection, retention, export, and deletion require normative specifications.

## Offline and failure behavior

- Collection may continue offline within bounded encrypted storage limits.
- Sync retries use bounded exponential backoff and server acknowledgements.
- Network loss changes sync state; it does not restart or terminate the daemon.
- Disk-full behavior blocks collection safely while daemon diagnostics remain available.
- Sleep/resume, clock change, network change, process crash, OS restart, and partial upgrade require deterministic recovery.
- Corrupt state enters recovery/quarantine; it may not silently reset sequences or duplicate claims.
- Key-store lock, permission loss, unsupported source, and auth expiry are degraded states, not daemon-exit conditions.

## Updates

Updates require signed metadata, TUF conformance, atomic installation, rollback protection, interrupted-download recovery, version compatibility checks, and consumer verification.

The updater must preserve service registration, acquire a maintenance lease and single-instance lock, drain durable writes, replace binaries atomically, and return lifecycle ownership to the OS supervisor. A new build passes startup, IPC, storage, migration, and privacy self-checks before the previous known-good build is removed.

Collector, sync, daemon, CLI, shell, adapters, schemas, and model/runtime assets may have different compatibility constraints but one coordinated release policy.

## Availability and recovery targets

Planning targets requiring executable evidence:

- successful installer completion implies service registration and enabled desired state;
- daemon readiness p95 <= 5 seconds after service-manager launch;
- abnormal-exit restart p95 <= 10 seconds and p99 <= 60 seconds excluding OS throttling;
- hung-child replacement <= 90 seconds;
- resume reconciliation begins <= 5 seconds after wake notification;
- update handoff causes < 30 seconds daemon unavailability;
- local daemon availability >= 99.9% while the applicable OS/user service context is available;
- zero silent loss of durably queued claims across restart.

## Completion outputs

- process, privilege, and supervision diagram;
- OS service-manager manifests/configuration;
- IPC schemas and state machines;
- lifecycle mode/capability matrix;
- daemon and child watchdog contract;
- CLI command contract;
- local storage and service-record schema;
- installer/uninstaller and update state machines;
- resource and availability budgets;
- accessibility and platform UX requirements;
- failure, recovery, export, and deletion matrices;
- reboot, logout/login, sleep/resume, crash-loop, disabled-service, disk-full, corrupt-state, interrupted-update, and uninstall evidence.
