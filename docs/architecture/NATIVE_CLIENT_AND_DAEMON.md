# Native Client, Daemon, CLI, Menu-Bar, and Tray Architecture

Updated: 2026-07-19
Status: planning contract

## Product topology

The local product consists of:

- `vibemaxxing-daemon`: lifecycle owner and local control plane;
- `vibeproof-collector`: transcript-private live observation and deterministic normalization;
- `vibeproof-sync`: networked safe-claim synchronization process with no transcript access;
- `vibemaxxing-cli`: installer, diagnostics, automation, and headless control;
- `vibemaxxing-desktop-shell`: macOS menu-bar and Windows/Linux tray UX;
- local audit/control UI;
- hosted VibeMaxxing web dashboard;
- signed updater and platform service integration.

Process separation must preserve the privacy boundary: a process that can inspect content cannot access the network, while the networked process cannot inspect content.

## Ownership

### Daemon

Owns process supervision, adapter registry, local account/device binding, health, local configuration, IPC routing, lifecycle, and upgrade coordination. It must not become a transcript-processing monolith.

### Collector

Owns source observation, privacy filtering, deterministic event normalization, local evidence continuity, and safe handoff. No network access.

### Sync

Owns challenge retrieval, claim submission, acknowledgements, retries, backoff, and server session renewal. It receives only safe fixed-schema data.

### CLI

Supports install, uninstall, start, stop, restart, status, login, logout, adapter list/add/remove/diagnose, privacy audit, export, delete, update, rollback, logs, doctor, and headless operation. Commands require stable exit codes and machine-readable output.

### Desktop shell

Shows active/idle/offline/private state, supported adapters, sync health, privacy boundary, updates, account/device controls, and a link or authenticated bridge to the hosted dashboard. Closing the shell must not stop the daemon unless the user explicitly chooses stop collection.

## Local versus hosted UX

Local UX owns installation, permissions, adapter discovery, privacy verification, device state, collection controls, diagnostics, outbound ledger inspection, local export/deletion, and update status.

Hosted web owns leaderboards, profiles, friends, rivals, boards, organizations, communities, countries, social notifications, moderation, appeals, and server-side account settings.

No hosted page may require prompt, transcript, project, repository, path, or code access.

## Lifecycle states

`not-installed → installed-stopped → starting → running → degraded → updating → rollback → stopping → stopped → uninstalling → removed`

Additional states include permission-required, login-required, adapter-unsupported, local-state-recovery, keychain-locked, disk-full, offline, sync-backlog, and compromised-version-blocked.

Every transition requires defined initiator, preconditions, durable writes, timeout, rollback, user message, telemetry allowlist, and recovery path.

## Platform behavior

- macOS: launch agent or equivalent unprivileged service, menu-bar shell, Keychain, code signing and notarization.
- Windows: per-user service/background process where feasible, tray shell, named pipes, DPAPI or credential manager, signed installer.
- Linux: user-level systemd where available with non-systemd fallback, tray integration where desktop support exists, Secret Service or documented fallback.
- WSL, containers, CI, and headless environments: CLI/daemon only unless a graphical shell is explicitly supported.

Baseline operation must not require administrator/root privileges. Optional hardening may require explicit elevated setup and must produce a stronger evidence label rather than silently changing behavior.

## IPC

All local IPC requires peer identity, restrictive ACLs, challenge-response, protocol versioning, message size and rate limits, replay protection where relevant, explicit errors, and capability negotiation. Never rely only on socket path secrecy.

## Storage and keys

Define separate storage for configuration, normalized events, pending claims, accepted acknowledgements, audit ledger, adapter state, evidence continuity, and diagnostics. Sensitive keys use OS credential facilities where available. Database encryption, crash consistency, checkpoints, rollback detection, retention, export, and deletion require normative specifications.

## Offline and failure behavior

- Collection may continue offline within bounded encrypted storage limits.
- Sync retries use bounded exponential backoff and server acknowledgements.
- Disk-full behavior must stop safely without corrupting prior state.
- Sleep/resume, clock change, network change, process crash, OS restart, and partial upgrade require deterministic recovery.
- Corrupt state enters recovery/quarantine; it may not silently reset sequences or duplicate claims.

## Updates

Updates require signed metadata, TUF conformance, atomic installation, rollback protection, interrupted-download recovery, version compatibility checks, and consumer verification. Collector, sync, daemon, CLI, shell, adapters, schemas, and model/runtime assets may have different compatibility constraints but one coordinated release policy.

## Completion outputs

- process and privilege diagram;
- IPC schemas and state machines;
- platform capability matrix;
- CLI command contract;
- local storage schema;
- installer/uninstaller and update state machines;
- resource budgets;
- accessibility and platform UX requirements;
- failure, recovery, export, and deletion matrices.
