# ADR-011: Universal platform support baseline

Status: accepted
Date: 2026-07-23
Decisions: D-062, D-063, D-064, D-065, D-066

## Context

VibeMaxxing must count qualifying AI-agent activity wherever users run agents. Restricting collection to one desktop operating system, one CPU architecture, or one execution environment would undermine the universal-competition thesis and create artificial ranking gaps.

“All Mac, all Windows and all Linux” cannot truthfully mean unsupported historical releases, abandoned distributions, obsolete 32-bit systems, or arbitrary custom kernels. The implementable commitment is broad native support governed by a rolling exact-profile registry. A profile is publicly supported only after its package, lifecycle, key-storage, adapter, privacy, recovery and update gates are exercised.

## Decision

Public launch includes competitive collection support for:

- macOS on Apple silicon `arm64` and Intel `x86_64`;
- maintained Windows desktop and applicable Windows Server releases on native `x64` and native `ARM64`;
- maintained Linux distributions across desktop, headless and remote use;
- WSL, containers and CI/ephemeral runners as globally eligible environment profiles by default.

Android, iOS, iPadOS and ChromeOS are out of scope. They are not collector, companion, control or launch platforms. Browser access remains available through the hosted web product on browsers those operating systems may provide, but no native application or platform-specific product promise is made.

## Exact support-profile identity

A public support profile is the immutable tuple:

`os_family + os_release_range + architecture + distribution/package profile + environment_kind + lifecycle_mode + key_protection_class + adapter/source version + collector/release-set version`.

The support registry publishes only exercised tuples. Compatibility inferred from a similar system is labelled `compatible-unverified`, not certified.

## Rolling lifecycle policy

- Maintained upstream operating systems and distributions are candidates for active support.
- End-of-life profiles receive a published sunset date and migration window.
- Security-critical unsupported profiles may be blocked from new competitive claims while preserving export, update and uninstall where technically possible.
- Protocol/accounting semantics remain identical across architectures.
- Platform capability changes evidence dimensions and ceilings, never token totals.

## macOS baseline

Launch support includes:

- Apple silicon `arm64`;
- Intel `x86_64`;
- the current macOS major release and the two preceding major releases, constrained by the architectures each release actually supports;
- signed and notarized Universal 2 artifacts where all dependencies permit them;
- architecture-specific artifacts when required, with identical protocol and accounting behavior.

Intel remains a launch requirement on supported macOS releases that boot on Intel hardware. Every published Mac tuple must exercise installation, LaunchAgent registration, Keychain behavior, background-item disable/repair, fast-user switching, sleep/wake, logout/login, update/rollback and uninstall.

## Windows baseline

Launch support includes:

- native `x64` binaries;
- native `ARM64` binaries;
- maintained Windows desktop editions suitable for the product;
- maintained Windows Server editions suitable for headless operation;
- graphical and headless profiles where applicable;
- non-elevated daily operation after installation.

Legacy 32-bit x86 and ARM32 are not launch targets unless a maintained Windows profile requires them and a later decision adds them.

Every published Windows tuple must exercise standard-user and administrator-assisted installation, multi-user isolation, CNG/TPM and DPAPI fallback behavior, lock/unlock, sleep/hibernate, service recovery, endpoint-security interference, native named-pipe authorization, update/rollback and uninstall.

## Linux baseline

The shared Rust core is distribution-agnostic. Packaging and native integration are profile-specific.

### First-class package ecosystems

Launch planning must provide and exercise:

- Debian/Ubuntu-family `.deb` repositories;
- Fedora/RHEL/Rocky/Alma-family `.rpm` repositories;
- openSUSE/SLES-family `.rpm` repositories;
- Arch-family packages;
- Alpine-family musl-compatible packages;
- Nix flake/module integration;
- signed portable glibc and musl tarballs.

Derivatives inherit only a compatible-unverified expectation until exercised as their own profile or explicitly covered by an identical runtime/package contract.

### Architectures

Launch prebuilt targets are:

- `x86_64`;
- `aarch64`.

Additional architectures such as `armv7`, `riscv64`, `ppc64le` and `s390x` remain source-compatible or experimental until reproducible builds and the complete platform gate pass. They are not silently advertised as launch-certified.

### Desktop and service integration

First-class desktop testing covers GNOME, KDE Plasma, Xfce, Cinnamon, MATE and LXQt across Wayland and X11 where applicable. The daemon and CLI remain independent of the graphical shell. When tray protocols are unavailable, CLI plus the loopback local dashboard provide control parity.

`systemd --user` is the primary user-service integration. Installation offers and recommends lingering so collection can continue across logout, with explicit authorization and status disclosure. OpenRC, runit, s6 and dinit service templates are maintained for non-systemd headless profiles. Desktop autostart is a weaker, session-bound fallback and is labelled accordingly.

Key-protection preference is TPM-backed/non-exportable key, Secret Service, kernel keyring, then encrypted file-wrapped fallback. The fallback lowers evidence dimensions but does not alter accounting.

## WSL profile

WSL is globally eligible by default as a distinct guest environment.

- It owns separate device lineage and keys.
- Windows-native and WSL source domains are reconciled to prevent double counting.
- WSL install/update/uninstall is independent of the Windows-native client.
- systemd-enabled and systemd-disabled lifecycle paths are supported.
- WSL lifetime is host-dependent and is never marketed as machine-independent always-on execution.
- export/import/clone operations change continuity and may lower evidence.
- Standard is the default competitive ceiling; Hardened requires an exercised WSL-specific profile.

## Container profile

Containers are globally eligible by default when using a certified profile.

- The daemon remains foreground under the container/orchestration supervisor.
- Images are non-root by default, signed, provenance-bound and compatible with an explicit writable state volume.
- Read-only roots are supported where practical.
- Container runtime sockets are not mounted by default.
- Replica identity, state ownership and duplicate domains prevent horizontal duplicate scoring.
- Immutable image replacement is the update mechanism.
- Standard is the default competitive ceiling unless a stronger controlled-execution profile is certified.

## CI and ephemeral profile

CI and ephemeral runners are globally eligible by default.

- Each job or bounded workflow receives a short-lived environment/device identity.
- Continuity is not assumed across jobs unless an explicitly protected continuity store exists.
- Retries, matrix jobs and restored workspaces use deterministic duplicate domains.
- Workflow/run identity and source-adapter digests bind the claim context without replacing source accounting.
- Logs and artifacts pass privacy-canary checks.
- Standard is the default competitive ceiling; Hardened requires a certified runner/execution profile.
- Boards may exclude CI or require a stronger minimum profile without changing global eligibility.

## Required support tiers

- `certified-hardened` — exact tuple passes stronger evidence gates.
- `certified-standard` — exact tuple passes competitive correctness, privacy and lifecycle gates.
- `compatible-unverified` — expected to run but not advertised as certified.
- `analytics-only` — explicitly excluded from active competition.
- `unsupported` — known incompatible, unsafe or out of policy.

## Consequences

- Cross-platform support is a launch requirement, not a later port.
- Public launch cannot ship only macOS, only Windows or only one Linux family.
- Native Windows ARM64, Intel Mac and Apple-silicon Mac require independent build and test lanes.
- Linux breadth is delivered through exact tested profiles rather than an unverifiable universal claim.
- WSL, containers and CI count globally but normally begin at Standard.
- No Android, iOS, iPadOS or ChromeOS implementation work is authorized.
