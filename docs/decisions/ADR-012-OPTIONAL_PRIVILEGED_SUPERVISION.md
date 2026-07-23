# ADR-012: Optional privileged machine-wide supervision

Status: accepted
Date: 2026-07-23
Decision: D-067

## Context

The default VibeMaxxing runtime is per-user and unprivileged. Some users and managed environments require collection to survive logout, begin before an interactive login, or run on shared/headless machines. Achieving that on every operating system may require a machine-wide service or privileged installer action.

A privileged process must not become a shortcut around the privacy architecture. It must not gain transcript access, broad filesystem access, arbitrary process inspection, network interception, or kernel anti-cheat capabilities merely because it owns lifecycle supervision.

## Decision

VibeMaxxing may offer an optional machine-wide privileged supervision profile.

The default installation remains per-user and unprivileged. Machine-wide mode is opt-in, separately consented, independently packaged, and capability-limited. It exists to register, start, stop, monitor, update and recover user-scoped VibeMaxxing services; it does not perform accounting or inspect source content.

## Capability boundary

The privileged supervisor may:

- register and supervise approved VibeMaxxing service binaries;
- start user-scoped daemons at supported boot/login boundaries;
- expose bounded service health and version state;
- coordinate signed update replacement and rollback;
- create approved machine-level directories with least-privilege ACLs;
- broker explicit user-session activation without reading user source data;
- retain export, repair and uninstall paths for blocked versions.

It may not:

- read prompts, responses, transcripts, source code, repositories, paths or source-agent storage;
- hold device signing keys used for user claims unless a separately approved machine-owned deployment profile requires its own lineage;
- intercept provider traffic;
- install kernel extensions, drivers, endpoint-security hooks or packet filters by default;
- enumerate arbitrary processes or files beyond an adapter-specific separately accepted capability;
- weaken user isolation on multi-user systems;
- open remote-control ports;
- silently enroll users or sources.

## Identity and storage

- Each user retains a separate account, device lineage, local database and claim chain.
- Machine-wide service identity is not a ranked human identity.
- Shared-machine deployments never merge users into one claim chain.
- Privileged service state contains only installation, version, service-registration, health and update metadata.
- IPC between the privileged supervisor and per-user daemon is typed, authenticated, ACL-bound and replay-resistant.

## Platform profiles

### macOS

A LaunchDaemon or privileged helper may be offered for machine-wide lifecycle only. It requires explicit administrator approval and must not gain access to user content stores. The normal menu-bar and collector processes remain in the user session.

### Windows

A Windows Service may supervise per-user processes or run a separately defined headless machine profile. Service SID isolation, restricted tokens, explicit ACLs and session-bound IPC are required. Daily user interaction remains non-elevated.

### Linux

A system service may supervise headless or multi-user deployments. User content collection remains in user-scoped processes unless the deployment is an explicitly machine-owned source profile. systemd hardening or equivalent sandboxing is required where available.

## Installation and consent

- Per-user mode is the default recommendation.
- Machine-wide mode requires a separate installer choice and privilege prompt.
- The installer explains what remains running across logout and which data the privileged component can access.
- Status surfaces display the active lifecycle profile.
- Downgrading from machine-wide to per-user mode preserves user data and lineage where safe.
- Uninstall removes privileged registration only after dependent user services are stopped or migrated.

## Evidence and release gates

Before public support, each privileged profile must pass:

- least-privilege review;
- cross-user access tests;
- IPC spoofing/replay tests;
- service binary substitution tests;
- update and rollback under partial failure;
- login/logout, fast-user-switching and concurrent-user tests;
- privacy canaries in privileged logs, crash reports and support bundles;
- uninstall and downgrade tests;
- independent security review.

## Consequences

- Always-on behavior can be stronger in managed/headless deployments without making privilege mandatory.
- Privileged code becomes a separately audited high-risk component.
- Hardened evidence is not granted merely because machine-wide mode is enabled.
- Kernel anti-cheat and mandatory traffic proxying remain rejected.
