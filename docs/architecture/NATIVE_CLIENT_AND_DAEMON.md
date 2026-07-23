# Native Client, Daemon, CLI, Menu-Bar, and Tray Architecture

Updated: 2026-07-23
Status: planning contract

## Product topology

The local product consists of:

- `vibemaxxing-daemon`: always-on lifecycle owner and local control plane;
- `vibeproof-collector`: transcript-private live observation and deterministic normalization;
- `vibeproof-sync`: networked safe-claim synchronization process with no transcript access;
- `vibemaxxing-cli`: installer, diagnostics, automation and headless control;
- `vibemaxxing-desktop-shell`: macOS menu-bar and Windows/Linux tray UX;
- local audit/control UI;
- hosted VibeMaxxing web dashboard;
- mandatory signed updater and platform service integration;
- optional privileged lifecycle supervisor under ADR-012.

There is no Android, iOS, iPadOS or ChromeOS native product.

Process separation preserves the privacy boundary: a process that can inspect content cannot access the network, while the networked process cannot inspect content.

## Always-on requirement

Under D-061 and ADR-010, daemon desired state is `enabled` after successful installation.

- The platform service manager starts it at the earliest supported boot/login boundary.
- The platform service manager restarts it after abnormal termination.
- The daemon remains resident when collection or sync is paused, network/auth/permissions/storage are unavailable, an adapter is broken or recovery is required.
- Closing, crashing, updating or never opening the desktop shell does not stop the daemon.
- The shell is not a parent, owner or watchdog.
- Ordinary UX exposes pause/restart/repair/uninstall, not casual daemon quit.
- A durable service-disable action is advanced, explicit, confirmed and visible.
- The daemon does not self-daemonize or escape the OS supervisor.

No process runs while hardware is powered off, fully suspended or unavailable to the relevant service context. Lifecycle modes are `machine-wide`, `boot-persistent`, `session-bound`, `host-dependent`, `orchestrator-dependent` and `ephemeral`.

## Ownership

### Daemon

Owns supervision, adapter registry, local account/device binding, health, configuration, IPC routing, service-manager reconciliation and update coordination. It cannot become a transcript-processing monolith.

The daemon remains alive in `degraded`, `recovery`, `security-hold`, `update-required` and `blocked-version` states so diagnostics, privacy inspection, update, rollback, export, repair and uninstall remain available.

### Collector

Owns source observation, privacy filtering, deterministic event normalization, local continuity and safe handoff. No network access.

### Sync

Owns challenges, claim submission, acknowledgements, retries, backoff and server-session renewal. It receives fixed-schema safe data only.

### CLI

Supports install, uninstall, status, login/logout, adapters, privacy audit, export/delete, update/rollback, logs, doctor, collection/sync pause/resume, background-service status/repair/enable/disable, privileged-profile status and headless operation. Commands have stable exit codes and machine-readable output.

### Desktop shell

Shows collection/sync/daemon state, exact support profile, lifecycle mode, update deadline, privacy boundary, account/device controls and repair actions. Closing it never stops daemon, collector or sync.

### Optional privileged supervisor

Under ADR-012, a separate machine-wide component may register, start, monitor, update and recover approved user-scoped services. It cannot inspect source content, hold ordinary user claim keys, intercept provider traffic, merge users or open remote-control ports.

## Two-level supervision

### OS/orchestrator supervision

- One service registration per installation/profile.
- Single-instance enforcement.
- Auto-start enabled after install.
- Restart after abnormal exit.
- Bounded graceful-stop and forced-stop deadlines.
- Classified exit diagnostics.
- No host reboot as first recovery action.
- No unlimited hot restart loop.

### Daemon child supervision

- authenticated monotonic heartbeat;
- at least two missed probes before unresponsive classification;
- graceful stop before force kill;
- bounded exponential backoff with jitter;
- restart counters reset only after sustained health;
- per-component crash-loop quarantine;
- adapter isolation;
- child generation IDs rejecting stale IPC;
- durable-state reconciliation before resume.

A child failure may degrade collection or sync but cannot terminate the daemon.

## State model

### Service registration

`unregistered | registering | enabled | disabled-by-user | disabled-by-policy | registration-error | unregistering`

### Daemon health

`starting | healthy | degraded | recovery | security-hold | update-required | updating | rolling-back | blocked-version | failed-restart-pending`

### Collection

`enabled | paused-by-user | paused-by-policy | permission-required | source-unavailable | storage-blocked | update-blocked`

### Sync

`enabled | offline | backoff | paused-by-user | auth-required | server-blocked | security-hold | version-expired`

### Shell

`closed | starting | open | crashed`

### Privileged supervisor

`absent | installing | enabled | degraded | update-required | removing`

Shell state has no transition that changes daemon desired state.

## Accepted platform profiles

### macOS

- Apple silicon `arm64` and Intel `x86_64` are launch requirements.
- Per-user LaunchAgent through `SMAppService` is default.
- launchd continuous keep-alive and login loading.
- separate menu-bar application.
- signed/notarized Universal 2 or architecture-specific compatible release set.
- Keychain/Secure Enclave capability classification.
- XPC or Unix-socket peer validation.
- per-user mode is session-bound across logout.
- optional constrained LaunchDaemon/helper may strengthen supervision under ADR-012.

### Windows

- Native x64 and native ARM64 are launch requirements.
- Maintained desktop and applicable Server/headless profiles.
- OS-managed per-user service or scheduled startup fallback with equivalent semantics.
- independent tray shell.
- named-pipe DACL and peer identity.
- CNG/TPM non-exportable key path with DPAPI fallback classification.
- optional constrained Windows Service under ADR-012.

### Linux

- Maintained desktop, headless and remote profiles on x86_64 and aarch64 at launch.
- systemd-user primary; lingering offered and recommended with explicit authorization.
- OpenRC, runit, s6 and dinit templates for supported non-systemd headless profiles.
- desktop autostart only as weaker session-bound fallback.
- GNOME, KDE, Xfce, Cinnamon, MATE and LXQt control compatibility where advertised.
- Wayland/X11-independent core.
- TPM/Secret Service/kernel-keyring/encrypted fallback classification.
- optional constrained system service under ADR-012.

### WSL

- Distinct guest lineage and keys.
- Globally competitive by default at verifier-awarded level.
- Host/guest duplicate reconciliation.
- systemd-enabled and disabled paths.
- host-dependent lifecycle disclosed.
- independent install/update/uninstall.
- Standard default ceiling unless stronger profile certified.

### Containers

- Globally competitive certified profile.
- Foreground process under orchestrator.
- non-root, signed, provenance-bound image;
- explicit state volume and read-only root compatibility where practical;
- no container runtime socket by default;
- immutable image replacement;
- replica/volume identity and duplicate prevention.

### CI/ephemeral

- Globally competitive by default.
- short-lived environment/device identity;
- workflow/run binding and deterministic retry/matrix duplicate domains;
- no background process expected after job end;
- current pinned artifact required;
- Standard default ceiling unless stronger runner profile certified.

## IPC

All local and privileged IPC requires peer identity, restrictive ACLs, challenge-response, protocol versioning, message/depth/rate limits, replay protection, explicit errors, capability negotiation, process-generation binding and deadlines. Socket-path secrecy alone is insufficient.

## Storage and service records

Separate storage exists for configuration, normalized facts, pending claims, acknowledgements, audit ledger, adapter state, continuity, diagnostics and lifecycle supervision.

Lifecycle records include:

- exact platform support tuple;
- service-registration ID and mode;
- desired state;
- process generation and build digest;
- last successful start/stop;
- heartbeat;
- classified exit/restart reason;
- daemon/child restart counters;
- service-manager and linger status;
- privileged-profile status;
- mandatory-update channel/deadline/version state;
- degraded/recovery reason codes.

No record contains prompt, transcript, path, repository or source content.

## Offline and failure behavior

- Collection may continue offline within bounded encrypted storage and compatibility policy.
- Sync retries use bounded backoff and durable acknowledgements.
- Network loss changes sync state without daemon restart.
- Disk full blocks collection safely while diagnostics remain.
- Sleep/resume, clock/network change, crash, OS restart and partial upgrade have deterministic recovery.
- Corruption enters recovery/quarantine without silent sequence reset.
- Key-store lock, permission loss, unsupported source and auth expiry are degraded states.
- WSL/container/CI lifecycle termination is classified and never misrepresented as native machine-wide persistence.

## Mandatory updates

Under ADR-013:

- competitive profiles cannot permanently disable required updates;
- security/integrity, compatibility and routine update classes have signed deadlines;
- users may choose supported channel and bounded maintenance timing;
- maintenance lease drains durable writes before ordinary restart;
- release-set compatibility covers daemon, collector, sync, CLI, shell, adapters, schemas and assets;
- new builds pass startup, IPC, storage, migration and privacy checks before old build removal;
- failed updates roll back without resetting lineage or losing queued claims;
- blocked versions retain diagnostics, update, export and uninstall where safe;
- containers replace immutable images;
- CI uses current pinned artifacts rather than a persistent updater.

## Availability targets

Planning targets requiring executable evidence:

- installer success implies service registration and enabled desired state;
- readiness p95 <= 5 seconds after supervisor launch;
- abnormal-exit restart p95 <= 10 seconds and p99 <= 60 seconds excluding OS throttling;
- hung-child replacement <= 90 seconds;
- resume reconciliation begins <= 5 seconds;
- ordinary update handoff causes < 30 seconds daemon unavailability;
- daemon availability >= 99.9% while the applicable service context exists;
- zero silent loss of durable queued claims.

## Completion outputs

- process/privilege/supervision diagram;
- service manifests for every exact profile;
- IPC schemas/state machines;
- platform tuple registry;
- watchdog contract;
- CLI contract;
- storage/service-record schema;
- privileged-profile contract;
- mandatory-update/rollback state machines;
- resource/availability/accessibility budgets;
- complete failure/recovery/export/deletion evidence matrix;
- negative evidence that no Android/iOS/iPadOS/ChromeOS native path exists.