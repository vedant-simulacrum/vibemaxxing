# Cross-platform integration completeness audit

Updated: 2026-07-23
Status: normative planning audit; implementation remains unauthorized

## Scope

The accepted launch platform families are:

- macOS desktop on Apple silicon and Intel;
- Windows desktop and applicable Windows Server profiles on native x64 and ARM64;
- Linux desktop, headless and remote profiles;
- WSL;
- containers;
- CI and ephemeral runners.

Android, iOS, iPadOS and ChromeOS are out of scope. There is no native collector, companion, control or launch application for those operating systems. Hosted web remains an ordinary browser surface and does not create a native-platform support claim.

“Supported” means an exact exercised platform tuple is published in the support registry. It does not mean every historical OS release, arbitrary derivative distribution or custom kernel is supported.

## Exact platform-profile identity

Every support claim binds:

`os_family + os_release_range + architecture + distribution/package profile + environment_kind + lifecycle_mode + key_protection_class + adapter/source version + collector/release-set version`.

Support states are:

- `certified-hardened`;
- `certified-standard`;
- `compatible-unverified`;
- `analytics-only`;
- `unsupported`.

Only the first two are public certified support. Compatible-unverified profiles cannot be marketed as exercised.

## Universal capability contract

Every supported collector profile must provide:

1. install, repair, upgrade, rollback and uninstall;
2. an OS/orchestrator-supervised daemon, or an explicitly disclosed job-lifetime profile for CI;
3. separate collector and networked sync trust domains;
4. authenticated typed local IPC;
5. protected device/environment keys with a declared protection class;
6. encrypted durable local state where persistence exists;
7. crash-consistent event, commitment and queue writes;
8. offline collection and later synchronization where the environment persists;
9. adapter discovery, capability probing and support ceilings;
10. deterministic privacy filtering and exact outbound inspection;
11. pause collection and pause sync without stopping the daemon;
12. diagnostics, recovery, export and local deletion;
13. mandatory signed automatic updates or immutable replacement under ADR-013;
14. accessibility-appropriate control UX or headless CLI parity;
15. complete lifecycle, failure, privacy and resource tests.

A profile missing a mandatory capability is explicitly downgraded or unsupported.

## Shared component contract

The following logic is shared across platforms:

- normalized accounting types;
- accounting-profile engine;
- deterministic integrity rules;
- commitment-chain logic;
- VibeProof canonical encoding and signing;
- privacy allowlist and canary scanner;
- device-lineage state machine;
- durable queue semantics;
- adapter-manifest validation;
- reason codes and diagnostics model;
- release-set verification;
- CLI command semantics.

Platform modules implement only:

- service registration and supervision;
- key storage and optional attestation inputs;
- IPC transport and peer identity;
- filesystem permissions and secure locations;
- sleep/resume/session notifications;
- packaging, signatures and installer behavior;
- menu-bar/tray/desktop integration;
- optional privileged lifecycle supervision under ADR-012.

## Platform capability matrix

| Capability | macOS | Windows | Linux desktop | Linux headless/remote | WSL | Containers | CI/ephemeral |
|---|---|---|---|---|---|---|---|
| Architectures | arm64, x86_64 | native x64, native ARM64 | x86_64, aarch64 launch; others only after certification | x86_64, aarch64 launch; others only after certification | guest architecture supported by certified distro profile | certified image architectures | certified runner architectures |
| Lifecycle owner | per-user LaunchAgent; optional constrained LaunchDaemon/helper | per-user background service/task; optional constrained Windows Service | systemd-user primary; non-systemd templates/fallbacks | user or machine supervisor by explicit profile | systemd-user when enabled; host-dependent fallback | foreground daemon under orchestrator | process bound to job/workflow lifetime |
| Across logout | per-user returns at login; privileged profile may continue | profile-specific; machine-wide optional | lingering offered/recommended; weaker fallback disclosed | supervisor-dependent | host/WSL lifetime-dependent | restart-policy-dependent | not applicable after job end |
| Control surface | menu bar + CLI + local dashboard | tray + CLI + local dashboard | tray where supported + CLI + local dashboard | CLI + local dashboard | CLI; explicit host bridge only if implemented | CLI/local orchestration channel | CLI/action output |
| Key backend | Keychain/Secure Enclave capability class | CNG/TPM; DPAPI fallback class | TPM/Secret Service/kernel keyring; encrypted fallback | TPM/keyring/encrypted fallback | guest-specific backend | workload/injected key under policy | short-lived job key |
| IPC | XPC or Unix socket with peer checks | named pipe with DACL and peer identity | Unix socket with peer credentials | Unix socket | Unix socket in guest | Unix socket/local channel | local pipe/socket |
| Packaging | signed/notarized Universal 2 or architecture artifacts | signed native x64/ARM64 installer and binaries | deb/rpm/Arch/Alpine/Nix/portable profiles | package/archive/service templates | independent Linux package path | signed immutable image | pinned signed tool/action artifact |
| Update | mandatory coordinated automatic update | mandatory coordinated automatic update | mandatory repository/built-in update under one release-set policy | mandatory unattended/channel policy | independent guest update | immutable image replacement | current pinned artifact required |
| Default evidence ceiling | capability-derived | capability-derived | capability-derived | capability-derived | Standard unless stronger profile certified | Standard unless stronger profile certified | Standard unless stronger profile certified |

No matrix cell is an implementation claim.

## macOS completion contract

### Baseline

- Apple silicon `arm64` and Intel `x86_64` are launch requirements.
- The current macOS major and two preceding majors are target policy, constrained by actual hardware support.
- Universal 2 artifacts are preferred where dependency chains permit them.
- Intel remains required on supported releases that boot on Intel.

### Required implementation

- signed/notarized app bundle;
- independent menu-bar shell and daemon;
- `SMAppService` LaunchAgent registration/status/repair/unregister;
- shell exit cannot stop daemon or children;
- Keychain access and Secure Enclave capability classification;
- typed XPC or Unix-socket peer validation;
- adapter-specific permission UX;
- sleep/wake, fast-user-switching, logout/login and network-change handling;
- mandatory atomic update and rollback;
- user-visible repair when Background Items are disabled;
- complete uninstall.

### Optional privileged profile

A separately approved LaunchDaemon/helper may strengthen across-logout or managed-machine supervision. It is lifecycle-only, cannot inspect source content and requires ADR-012 evidence.

### Required tests

Every advertised architecture/OS tuple must pass install, update, rollback, uninstall, shell/daemon/child crash, launchd throttling, login/logout, fast-user switching, sleep/wake, Keychain denial/migration, permission grant/revoke, background-item disable/repair and privacy-canary tests.

## Windows completion contract

### Baseline

- native x64 and native ARM64 are launch requirements;
- maintained Windows desktop profiles are supported;
- applicable maintained Windows Server/headless profiles are supported;
- daily operation is non-elevated after installation;
- legacy x86/ARM32 are not launch targets unless later required by a maintained profile.

### Required implementation

- signed native installers, binaries and uninstaller;
- per-user background service/task with equivalent repair semantics;
- independent tray shell;
- named pipes with user/service DACLs and peer identity;
- CNG/TPM non-exportable path and DPAPI fallback classification;
- session switch, lock/unlock, sleep/hibernate/resume and network-change handling;
- service recovery without automatic machine reboot;
- mandatory atomic update, rollback and in-use replacement strategy;
- multi-user isolation;
- pending-claim warning on uninstall.

### Optional privileged profile

A constrained Windows Service may provide machine-wide supervision. It cannot read ordinary user source content, merge users or bypass claim lineage.

### Required tests

Every advertised edition/build/architecture tuple must pass standard/admin install paths, UAC boundaries, native ARM64 operation, tray/daemon/service crash loops, user switching, sleep/hibernate/reboot, TPM presence/reset, DPAPI changes, endpoint-security interference, named-pipe cross-user rejection, update/rollback/repair and privacy-canary tests.

## Linux completion contract

### Baseline package ecosystems

Launch planning covers:

- Debian/Ubuntu-family deb repositories;
- Fedora/RHEL/Rocky/Alma-family rpm repositories;
- openSUSE/SLES-family rpm repositories;
- Arch-family packages;
- Alpine/musl packages;
- Nix flake/module integration;
- signed portable glibc and musl tarballs.

Exact maintained distro releases are published by the support registry. Derivatives remain compatible-unverified until exercised or explicitly proven identical.

### Architectures

- prebuilt launch targets: x86_64 and aarch64;
- armv7, riscv64, ppc64le, s390x and others remain experimental/source-compatible until the complete gate passes.

### Desktop and init profiles

First-class desktop testing covers GNOME, KDE Plasma, Xfce, Cinnamon, MATE and LXQt across Wayland/X11 where applicable. Core collection does not depend on a graphical environment.

- systemd-user is primary;
- lingering is offered and recommended with explicit authorization and status;
- OpenRC, runit, s6 and dinit templates cover non-systemd headless profiles;
- desktop autostart is a weaker session-bound fallback;
- missing tray support falls back to CLI plus local dashboard.

### Key storage

Capability order: TPM-backed/non-exportable key, Secret Service, kernel keyring, encrypted file-wrapped fallback. The fallback lowers assurance only.

### Required tests

Every advertised distro/version/architecture/package/init tuple must pass service lifecycle, linger enabled/disabled/unavailable, GUI/headless behavior, key backend present/locked/absent, read-only home, disk/inode exhaustion, socket namespace attacks, suspend/resume, network changes, package update/rollback/partial recovery, uninstall and privacy-canary tests.

## WSL completion contract

WSL is globally competitive by default but remains a distinct guest profile.

Required:

- separate guest device lineage and keys;
- explicit source ownership and deduplication between Windows and WSL;
- systemd-enabled and disabled paths;
- honest host-dependent lifecycle status;
- no silent Windows credential/key inheritance;
- independent install/update/uninstall;
- export/import/clone continuity downgrade;
- Standard default ceiling unless stronger WSL evidence is certified.

Tests include WSL shutdown/restart, distribution export/import/clone, host reboot, guest clock changes, shared-file access and duplicate source execution visible to host and guest.

## Container completion contract

Containers are globally competitive by default under certified profiles.

Required:

- foreground non-self-daemonizing process;
- non-root image;
- explicit writable state volume;
- read-only root compatibility where practical;
- signed/provenance-bound image;
- no runtime socket by default;
- local/orchestrator-only health channels;
- immutable image replacement;
- replica/state identity and duplicate prevention;
- Standard default ceiling unless stronger controlled execution is certified.

Tests include restart policy, volume restore/clone, image rollback, abrupt kill, resource limits, network partition, read-only filesystem and multi-replica duplicate prevention.

## CI and ephemeral completion contract

CI is globally competitive by default at the verifier-awarded level.

Required:

- short-lived environment/device identity;
- no continuity assumption across jobs without protected state;
- workflow/run identity binding;
- deterministic retry and matrix-job duplicate domains;
- noninteractive setup/teardown;
- current pinned tool artifact under mandatory compatibility policy;
- secret minimization and privacy-safe logs;
- no daemon expected after job termination;
- Standard default ceiling unless stronger runner profile is certified.

Tests include retries, restored caches, duplicated workspaces, concurrent matrix jobs, expired tool rejection and leaked-log canaries.

## Optional privileged supervision

ADR-012 permits machine-wide supervision only when:

- per-user unprivileged mode remains the default;
- privilege is explicitly consented;
- supervisor capabilities are lifecycle-only;
- user lineages and stores remain isolated;
- typed authenticated IPC crosses the privilege boundary;
- cross-user, substitution, update/rollback, uninstall and privacy tests pass;
- privilege does not self-award Hardened.

## Mandatory automatic updates

ADR-013 applies to every competitive profile.

- Security/integrity updates may have short deadlines.
- Compatibility updates have a migration window.
- Routine updates allow bounded scheduling but cannot be disabled indefinitely.
- Active writes reach a durable checkpoint before ordinary restart.
- Blocked versions retain diagnostics, update, export and uninstall where safe.
- Containers replace immutable images.
- CI uses current pinned artifacts and server-enforced expiry.

## Cross-component integration sequences

### Installation

`verify package -> install binaries -> create secure directories -> register service -> create/obtain key -> start daemon -> health handshake -> launch optional shell -> adapter discovery`

Installation cannot report success while service registration or privacy-boundary initialization failed.

### Startup

`OS/orchestrator launch -> single-instance lock -> storage migration -> integrity check -> key load -> IPC listeners -> child supervision -> adapter probe -> sync scheduling -> ready`

### Collection

`source observation -> typed IPC -> normalization -> accounting profile -> deterministic rules -> privacy scan -> atomic local commit -> queue`

### Synchronization

`native session -> challenge -> claim finalization/signing -> outbound preview/audit -> submission -> atomic server appraisal/receipt -> durable acknowledgement -> projection event`

### Update

`metadata refresh -> compatibility graph -> artifact/image retrieval -> signature/provenance verification -> preflight -> maintenance lease -> atomic replacement -> health/privacy checks -> commit or rollback`

### Uninstall

`warn pending claims -> offer sync/export/delete -> stop children -> unregister service -> revoke/retain server device by explicit choice -> delete selected local state -> remove binaries -> local receipt`

## Cross-platform invariants

- Identical normalized facts and claim bytes have identical meaning everywhere.
- Token arithmetic is deterministic across Rust, Go, TypeScript presentation and PostgreSQL.
- Key strength changes evidence dimensions, not totals.
- Lifecycle limits are visible.
- Shell crashes cannot stop collection.
- Sync cannot read source content.
- Adapter failure cannot restart unrelated adapters.
- Failed update cannot reset lineage or commitments.
- Restore/clone uncertainty cannot silently retain Hardened.
- Privacy canaries never appear in logs, crash reports, telemetry, notifications, support bundles or server records.
- Out-of-scope mobile/ChromeOS native artifacts cannot enter launch packages or work units.

## Platform release gates

A profile becomes public only after:

1. exact tuple registration;
2. install/start/supervision/update/rollback/uninstall pass;
3. IPC/filesystem adversarial tests pass;
4. key storage/migration is classified;
5. adapters have exact certifications;
6. resource and battery budgets pass where applicable;
7. accessibility or headless parity passes;
8. privacy canaries pass in native logs/crash facilities;
9. clone/restore/sleep/reboot continuity tests pass;
10. mandatory-update behavior passes;
11. support and recovery docs exist;
12. no P0/P1 platform blocker remains.

## Current conclusion

Platform scope is now frozen by D-062 through D-068. Issue #26 can close.

Nothing is currently production-complete on any collector profile. The repository has requirements and implementation ownership, not executable daemon, collector, sync, adapter, installer or platform evidence. The Storybook prototype does not satisfy collector-platform gates.