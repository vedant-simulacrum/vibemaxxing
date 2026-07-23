# Cross-platform integration completeness audit

Updated: 2026-07-23
Status: normative planning audit; implementation remains unauthorized

## Scope

This audit evaluates whether the planned system works as one product across the currently declared environments:

- macOS desktop;
- Windows desktop;
- Linux desktop;
- Linux headless;
- WSL;
- containers;
- CI/ephemeral runners;
- remote/headless machines.

Browser-only access is a hosted-web surface, not a collection platform. Mobile operating systems and ChromeOS are not currently specified as collector platforms and require an explicit scope decision before they may be advertised.

“Supported” requires all mandatory launch capabilities for that platform profile. A feature may not be called supported merely because the binary starts.

## Universal capability contract

Every supported collector platform must provide:

1. install, upgrade, rollback and uninstall;
2. an always-on OS-supervised daemon or an explicitly disclosed weaker environment profile;
3. separate collector and networked sync trust domains;
4. authenticated typed local IPC;
5. protected device keys with a declared protection class;
6. encrypted durable local state;
7. crash-consistent event, commitment and queue writes;
8. offline collection and later synchronization;
9. adapter discovery, capability probing and support ceilings;
10. deterministic privacy filtering and outbound inspection;
11. pause collection and pause sync without stopping the daemon;
12. diagnostics, recovery, export and local deletion;
13. signed/provenance-bound updates with rollback resistance;
14. accessibility-appropriate control UX or headless CLI parity;
15. complete lifecycle, failure and resource tests.

A platform missing a mandatory capability is `experimental`, `analytics-only`, `headless-limited`, or `unsupported`; it is not silently treated as equivalent.

## Shared component contract

The following logic must be shared rather than reimplemented independently per platform:

- normalized accounting types;
- accounting profile engine;
- deterministic integrity rules;
- commitment-chain logic;
- VibeProof canonical encoding and signing;
- privacy allowlist and canary scanner;
- device-lineage state machine;
- durable queue semantics;
- adapter manifest validation;
- reason codes and diagnostics model;
- update release-set verification;
- CLI command semantics.

Platform modules implement only OS integration:

- service registration/supervision;
- key storage and attestation inputs;
- IPC transport and peer identity;
- filesystem permissions and secure locations;
- sleep/resume/session notifications;
- packaging, signatures and installer behavior;
- menu-bar/tray/desktop integration.

## Platform capability matrix

| Capability | macOS | Windows | Linux desktop | Linux headless | WSL | Containers | CI/ephemeral |
|---|---|---|---|---|---|---|---|
| Lifecycle owner | per-user LaunchAgent via `SMAppService` | per-user OS-managed background service; scheduled task fallback only when required | `systemd --user`; desktop autostart fallback | `systemd --user` or system supervisor in explicit headless mode | systemd user service when enabled; session supervisor fallback | foreground daemon under container supervisor | foreground daemon bound to job lifetime |
| Across logout | not guaranteed in per-user mode; returns at login | depends on selected per-user service profile | with user lingering | supervisor-dependent | environment-dependent | restart-policy-dependent | no; ephemeral by definition |
| Shell | menu bar | tray | tray where desktop supports it | none | optional host/guest CLI | none | none |
| Control parity | shell + CLI | shell + CLI | shell + CLI | CLI | CLI; host bridge only if explicitly implemented | CLI/API socket | CLI |
| Key backend | Keychain/Secure Enclave capability classified | CNG/TPM with DPAPI/credential fallback class | TPM/Secret Service/kernel keyring capability class | TPM/keyring/file-wrapped fallback class | guest key backend; no silent host inheritance | injected or generated workload key under explicit policy | short-lived generated key |
| IPC | XPC or Unix-domain socket with peer checks | named pipe with explicit DACL and peer identity | Unix-domain socket with peer credentials | Unix-domain socket | Unix-domain socket in guest | Unix-domain socket | local pipe/socket |
| Packaging | signed/notarized app bundle and helper assets | signed installer and binaries | signed distro packages plus portable fallback policy | signed packages/archive | Linux package path | signed image and manifest | pinned tool artifact |
| Update | coordinated signed app/service update | coordinated installer/service update | package/channel or built-in updater with one trust root | same as Linux headless profile | guest update | immutable image replacement preferred | job-pinned version replacement |
| Evidence ceiling | capability-derived | capability-derived | capability-derived | capability-derived | host/guest uncertainty lowers ceiling | workload/host uncertainty lowers ceiling | ephemeral profile; board policy may exclude |

No cell is an implementation claim. Each must be converted into code and exercised evidence before support publication.

## macOS completion contract

### Required implementation

- signed/notarized application bundle;
- independent menu-bar shell and per-user LaunchAgent;
- `SMAppService` registration, status, repair and unregister flows;
- service remains alive after shell exit;
- Keychain access groups and key accessibility policy;
- Secure Enclave capability detection without assuming availability;
- XPC or Unix socket peer validation and protocol negotiation;
- explicit Full Disk Access or source-specific permission UX only where an adapter requires it;
- sleep/wake, fast-user-switching, logout/login and network-change handling;
- atomic app/helper update and rollback;
- user-visible handling when Background Items is disabled;
- complete uninstall of service registration, binaries and selected local data.

### Required tests

- Apple silicon and Intel where both remain supported;
- clean install, upgrade from every supported previous version and uninstall;
- shell crash, daemon crash, child crash and launchd restart throttling;
- login/logout, fast user switching, sleep/wake and reboot;
- Keychain locked, migrated, restored and denied;
- source permission grant/revoke while active;
- background item disabled/re-enabled;
- interrupted update and failed health-check rollback;
- privacy canaries across unified logging, crash reports and IPC.

## Windows completion contract

### Required implementation

- signed installer, binaries and uninstaller;
- per-user background service where supported by packaging architecture;
- OS-managed scheduled startup fallback with equivalent single-instance and repair semantics;
- tray shell independent from daemon lifecycle;
- named pipes with explicit user/service DACLs, local-only restriction and peer identity;
- CNG/TPM key generation and non-exportability classification;
- DPAPI or credential-manager fallback classification;
- session change, lock/unlock, sleep/hibernate/resume and network-change handling;
- service recovery actions without machine reboot;
- atomic update, rollback and in-use binary replacement strategy;
- multi-user machine isolation;
- complete uninstall and pending-claim warning.

### Required tests

- supported client and server Windows editions selected by the platform baseline;
- x64 and ARM64 where advertised;
- standard user and administrator-installed paths;
- UAC elevation boundary and non-elevated daily operation;
- tray crash, daemon crash, service manager restart and crash loops;
- user switch, lock/unlock, sleep, hibernate and reboot;
- TPM present/absent/cleared and DPAPI profile changes;
- antivirus/endpoint protection interference and locked files;
- named-pipe cross-user and anonymous-access rejection;
- update rollback and installer repair;
- privacy canaries across Event Log, crash dumps and installer logs.

## Linux desktop completion contract

### Required implementation

- package policy for declared distributions and architectures;
- `systemd --user` service with explicit linger status;
- non-systemd desktop autostart fallback classified as weaker;
- tray integration only where a supported desktop protocol exists;
- Secret Service, TPM and kernel-keyring capability selection;
- Unix socket ownership, mode and peer credential checks;
- Wayland/X11-independent core behavior;
- desktop permission and portal handling where applicable;
- package-manager and built-in update interaction policy;
- clean uninstall across package formats.

### Required tests

- every advertised distribution/version/architecture combination;
- GNOME, KDE and headless behavior where advertised;
- systemd user manager with linger enabled/disabled/unavailable;
- no graphical session, locked session and logout/login;
- Secret Service present/locked/absent;
- read-only home, disk full, inode exhaustion and permission changes;
- Unix socket ownership and namespace attacks;
- suspend/resume and network-manager changes;
- package upgrade/rollback and partial transaction recovery;
- privacy canaries across journal, core dumps and package logs.

## Linux headless and remote completion contract

Headless mode must not depend on a tray, browser remaining open or desktop keyring.

Required:

- noninteractive install and configuration;
- machine-readable CLI output and stable exit codes;
- explicit secure key backend and fallback warning;
- browser/device authorization that binds the exact daemon instance;
- remote terminal disconnection does not stop the supervised daemon;
- service health, privacy inspection, export, update and uninstall through CLI;
- no implicit opening of remote network control ports.

Tests include SSH disconnect, reboot, user-session absence, keyring absence, automated provisioning, log rotation and recovery without GUI.

## WSL completion contract

WSL is a distinct guest environment, not equivalent to Windows-native collection.

Required:

- guest-specific device and evidence identity;
- explicit source ownership between Windows host and WSL guest;
- duplicate-domain reconciliation preventing host/guest double counting;
- systemd-enabled and systemd-disabled lifecycle paths;
- clear disclosure that WSL lifetime may depend on host WSL lifecycle;
- no silent use of Windows credentials or device keys;
- path and IPC boundaries that do not leak source content across host/guest;
- separate install/update/uninstall state from the Windows app.

Tests include WSL shutdown/restart, distribution export/import/clone, host reboot, guest clock change, shared-file access and duplicate source execution visible to both host and guest.

## Containers completion contract

Container support is a headless environment profile.

Required:

- foreground, non-self-daemonizing process;
- read-only root filesystem compatibility where practical;
- explicit writable state volume;
- non-root operation;
- secrets delivered through an approved mechanism and never baked into images;
- health/readiness endpoints exposed only through local/container orchestration channels;
- immutable-image update preferred over self-update;
- explicit host/source observation model and evidence ceiling;
- no access to Docker/container runtime socket by default.

Tests include restart policy, volume restore/clone, image rollback, abrupt kill, resource limits, network partition, read-only filesystem and multi-replica duplicate prevention.

## CI and ephemeral runner completion contract

CI mode must be explicitly ephemeral.

Required:

- short-lived device key and session;
- no assumption of continuity across jobs;
- deterministic import versus competitive eligibility policy;
- board-level ability to exclude CI;
- noninteractive install and teardown;
- secret minimization and log redaction;
- no background process expected after job termination.

Tests include retrying jobs, restored caches, duplicated workspaces, concurrent matrix jobs and leaked-log canaries.

## Cross-component integration sequences

The following sequences require end-to-end tests on every applicable platform profile.

### Installation

`verify package -> install binaries -> create secure directories -> register service -> create/obtain device key -> start daemon -> health handshake -> launch optional shell -> begin adapter discovery`

A failed step rolls back or enters a visible repairable state. Installation cannot report success while service registration failed.

### Startup

`OS supervisor launch -> single-instance lock -> storage migration -> integrity check -> device/key load -> IPC listeners -> child supervision -> adapter probe -> sync scheduling -> ready`

The daemon does not mark ready before durable state and privacy boundaries are valid.

### Collection

`source observation -> typed IPC -> normalization -> accounting profile -> deterministic rules -> privacy scan -> atomic local commit -> queue`

No network-capable process receives source content.

### Synchronization

`native session -> challenge -> claim finalization/signing -> outbound preview/audit -> submission -> atomic server appraisal/receipt -> durable acknowledgement -> projection event`

An exact retry returns the prior result. Conflicting reuse cannot add score.

### Update

`metadata refresh -> release-set compatibility -> artifact download -> signature/provenance verification -> disk/migration preflight -> maintenance lease -> atomic replacement -> health/privacy checks -> commit or rollback`

Service registration, queued claims, device lineage and export/uninstall access survive failure.

### Uninstall

`warn about pending claims -> offer sync/export/delete choices -> stop children -> unregister service -> revoke or retain server device per explicit choice -> delete selected local state -> remove binaries -> produce local receipt`

Uninstall must not claim server deletion unless the separate server workflow succeeds.

## Cross-platform invariants

- The same normalized event and claim bytes produce the same meaning everywhere.
- Token arithmetic is checked and deterministic across Rust, Go, TypeScript presentation and PostgreSQL.
- Platform key strength changes evidence dimensions, not token totals.
- Platform lifecycle limitations are visible and never silently called Hardened.
- Unsupported source/platform combinations fail closed for stronger evidence and remain diagnosable.
- A shell crash cannot stop collection.
- A sync crash cannot expose raw source data.
- An adapter crash cannot restart unrelated adapters.
- A failed update cannot reset device lineage or commitments.
- Restore/clone uncertainty cannot silently retain Hardened.
- Privacy canaries are forbidden from logs, crash reports, telemetry, notifications, support bundles and server records.

## Platform release gates

A platform profile becomes public only after:

1. its capability matrix is complete;
2. installation, startup, supervision, update, rollback and uninstall pass;
3. all local trust boundaries pass adversarial IPC and filesystem tests;
4. key storage and migration behavior is classified;
5. source adapters have exact platform certifications;
6. resource and battery budgets pass;
7. accessibility or headless control parity passes;
8. privacy canaries pass in platform-native logs and crash facilities;
9. clone, restore, sleep and reboot continuity tests pass;
10. support and recovery documentation is complete;
11. no P0/P1 platform-specific blocker remains;
12. the support registry publishes the exact tested platform profile.

## Current audit conclusion

Nothing is currently production-complete on any collector platform. The repository now contains implementation ownership and evidence requirements, but executable daemon, collector, sync, adapter, installer and platform evidence do not yet exist.

The fixture-backed web prototype does not satisfy any platform collector gate.

## Scope questions requiring explicit product answers

The following cannot be inferred safely and must be decided before platform baselines freeze:

1. Are Intel Macs required at public launch, or Apple silicon only?
2. Is Windows ARM64 required at launch, or x64 only initially?
3. Which Linux distributions, versions, desktop environments and CPU architectures receive first-class packages?
4. Must Linux collection continue across logout through lingering by default, even when enabling linger requires additional user authorization?
5. Are WSL, containers and CI competitively eligible globally by default, board-policy-controlled, or analytics-only initially?
6. Are ChromeOS, iOS, iPadOS and Android explicitly out of scope, or should any become collector platforms?
7. Is a machine-wide privileged service ever acceptable for pre-login/across-logout collection, or must all desktop collection remain per-user?
8. Is auto-update mandatory by default, or may users choose notify-only/manual channels?
