# Native Client, Daemon, CLI, Menu-Bar, and Tray Architecture

Updated: 2026-07-19
Status: normative planning contract

## Product topology

The local product consists of:

- `vibemaxxing-daemon`: lifecycle owner and local control plane;
- `vibeproof-collector`: transcript-private live observation and deterministic normalization;
- `vibeproof-sync`: networked safe-claim synchronization process with no transcript access;
- `vibemaxxing-cli`: installer, diagnostics, automation and headless control;
- `vibemaxxing-desktop-shell`: macOS menu-bar and Windows/Linux tray UX;
- local audit/control UI;
- hosted VibeMaxxing web dashboard;
- signed updater and platform service integration.

Process separation preserves the privacy boundary: a process that can inspect content cannot access the network, while the networked process cannot inspect content. The normative process capabilities, platform key classes and rollback requirements live in `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`.

## Ownership

### Daemon

Owns process supervision, adapter registry, local account/device binding, health, local configuration, IPC routing, lifecycle and upgrade coordination. It does not become a transcript-processing monolith and has no unrestricted outbound network capability.

### Collector

Owns source observation, privacy filtering, deterministic event normalization, pre-challenge local commitments and safe handoff. No network access.

### Sync

Owns challenge retrieval, claim submission, acknowledgements, retries, backoff and server session renewal. It receives only safe fixed-schema records and cannot read source files, prompts, responses, tool bodies or arbitrary collector diagnostics.

### CLI

Supports install, uninstall, start, stop, restart, status, login, logout, adapter list/add/remove/diagnose, privacy audit, export, delete, update, rollback, logs, doctor and headless operation. Commands require stable exit codes and machine-readable output.

### Desktop shell

Shows active/idle/offline/private state, supported adapters, sync health, privacy boundary, updates, account/device controls and a link or authenticated bridge to the hosted dashboard. Closing the shell does not stop the daemon unless the user explicitly chooses stop collection. The shell has no source-content or raw-key access.

## Capability enforcement

Every executable ships with a versioned capability manifest. Runtime enforcement and conformance verify:

- permitted network destinations;
- permitted source/process/file observation;
- key operations and prohibition on raw-key export;
- local database tables or queues accessible to the process;
- IPC peers, methods, message sizes and rate limits;
- updater and privilege-escalation authority;
- diagnostics and telemetry allowlists.

A release fails closed when observed privileges exceed the manifest. Optional elevated observation is a separate signed component with explicit installation, user consent, removal and a stronger evidence profile; it never silently changes baseline behavior.

## Local versus hosted UX

Local UX owns installation, permissions, adapter discovery, privacy verification, device state, collection controls, diagnostics, outbound ledger inspection, local export/deletion and update status.

Hosted web owns leaderboards, profiles, friends, rivals, boards, organizations, communities, countries, social notifications, moderation, appeals and server-side account settings.

No hosted page requires prompt, transcript, project, repository, path or code access.

## Lifecycle states

`not-installed -> installed-stopped -> starting -> running -> degraded -> updating -> rollback -> stopping -> stopped -> uninstalling -> removed`

Additional states include permission-required, login-required, adapter-unsupported, local-state-recovery, keychain-locked, disk-full, offline, sync-backlog and compromised-version-blocked.

Every transition defines initiator, preconditions, durable writes, timeout, rollback, user message, telemetry allowlist and recovery path.

## Platform behavior

- macOS: per-user LaunchAgent or equivalent unprivileged service, menu-bar shell, Security.framework/Keychain, code signing and notarization.
- Windows: per-user background process by default, tray shell, named pipes, CNG/NCrypt or documented weaker fallback, signed installer.
- Linux: user-level systemd where available with non-systemd fallback, tray integration where desktop support exists, TPM2/Secret Service or documented fallback.
- WSL, containers, CI and headless environments: CLI/daemon only unless a graphical shell is explicitly supported; Standard is the default evidence ceiling until clone and key properties are exercised.

Baseline operation does not require administrator/root privileges. Platform product names do not imply a key-protection class; backup, sync, migration and restore behavior are exercised and recorded.

## IPC

All local IPC requires peer identity, restrictive ACLs, challenge-response, protocol versioning, message size and rate limits, replay protection where relevant, explicit errors and capability negotiation. Never rely only on socket path secrecy.

Enrollment, key rotation, device removal, export, deletion, updater privilege changes and optional elevated observation require explicit user-presence or reauthentication policy.

## Storage and keys

Separate storage exists for configuration, normalized events, local commitments, pending claims, accepted acknowledgements, audit ledger, adapter state, evidence continuity and diagnostics.

Sensitive keys use the strongest exercised platform facility. The release records K1-K5/KU from `EVIDENCE_AND_ATTESTATION_PROFILES.md`; OS credential storage alone does not establish non-exportability. Database encryption, crash consistency, checkpoints, rollback detection, retention, export and deletion are normative requirements.

## Offline and failure behavior

- Collection may continue offline within bounded encrypted storage limits.
- C3/C4 events are committed to an append-only chain before future server challenges are known.
- Startup compares local continuity with the last server checkpoint before competitive collection resumes.
- Sync retries use bounded exponential backoff and server acknowledgements.
- Disk-full behavior stops safely without corrupting prior state.
- Sleep/resume, clock change, network change, process crash, OS restart and partial upgrade have deterministic recovery.
- Corrupt, restored-behind or forked state enters recovery/quarantine; it may not silently reset sequences or duplicate claims.
- Device transfer uses key rotation or new enrollment, never file, home-directory, credential-store, VM or volume copying.

## Diagnostics and privacy

Crash reports, logs and support bundles are schema allowlisted. They never contain prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project/repository names, credentials, arbitrary environment variables, embeddings, summaries, classifications or personal insights. Collection and sync diagnostics are separated so joining them cannot reconstruct forbidden content.

## Updates

Updates require signed metadata, TUF conformance, atomic installation, rollback protection, interrupted-download recovery, version compatibility checks and consumer verification. Collector, sync, daemon, CLI, shell, adapters, schemas and model/runtime assets may have different compatibility constraints but one coordinated release policy.

## Completion outputs

- process and privilege diagram and machine-readable capability manifests;
- IPC schemas and state machines;
- platform key, backup, migration and capability matrix;
- CLI command contract;
- local storage and commitment schema;
- installer/uninstaller and update state machines;
- resource budgets;
- accessibility and platform UX requirements;
- failure, clone, rollback, recovery, export and deletion matrices.
