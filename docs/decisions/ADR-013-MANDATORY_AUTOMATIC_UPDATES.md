# ADR-013: Mandatory automatic updates

Status: accepted
Date: 2026-07-23
Decision: D-068

## Context

VibeMaxxing relies on exact accounting semantics, signed adapters, privacy boundaries, source-version compatibility, replay protection and release provenance. Long-lived manual-update installations would fragment protocol behavior, leave compromised binaries active, and allow unsupported adapters or policies to keep producing claims.

The update mechanism differs by environment. Desktop applications may self-update; Linux packages may use repositories; containers should generally be replaced immutably; CI should use pinned tool artifacts. The product needs one policy without forcing one unsafe mechanism everywhere.

## Decision

Automatic updates are mandatory for supported competitive profiles.

Users may choose stable or explicitly supported preview channels, but may not permanently disable security and compatibility updates while continuing to submit competitive claims. A bounded deferral is allowed to finish active work and permit maintenance scheduling. Profiles that cannot update within policy transition to a restricted state that preserves local export, repair and uninstall but blocks new competitive submission when required.

## Update classes

### Emergency security or integrity update

- May carry an immediate or short mandatory deadline.
- May revoke known-compromised artifacts, adapters, keys or protocol versions.
- The client downloads and stages promptly.
- Active collection is allowed to reach a safe durable checkpoint before restart unless the installed version is actively leaking data or corrupting evidence.
- Failure to update by deadline blocks new sync or collection according to the signed policy.

### Required compatibility update

- Covers protocol, schema, source-version, pricing/accounting or server compatibility.
- Uses a published deadline and migration window.
- Local collection may continue only when the old profile remains semantically compatible and safely queueable.

### Routine product update

- Installs automatically within a bounded maintenance window.
- May be deferred temporarily but not disabled indefinitely.
- Never silently changes ranking/accounting semantics for already accepted claims.

## Trust model

- TUF-style metadata and project release-set policy protect root, targets, snapshot and timestamp roles.
- Every artifact is bound to digest, source commit, SBOM, provenance and compatibility metadata.
- Platform-native signatures/notarization are required in addition to project metadata where available.
- Clients defend against rollback, freeze, mix-and-match, endless-data and compromised-key scenarios.
- Root and high-impact release-key operations use threshold authorization and offline custody where practical.

## Environment mechanisms

### macOS

Signed/notarized app, daemon and helper artifacts update as one compatible release set. Installation is atomic, retains a known-good version, verifies service registration after replacement and rolls back after failed health/privacy checks.

### Windows

Signed native `x64` and `ARM64` artifacts use an atomic installer/service replacement strategy. In-use binaries, reboot requirements, service recovery and rollback are explicit. The updater never requests a reboot merely as its first recovery mechanism.

### Linux desktop and headless

Project repositories and built-in release metadata share one release-set authority. Package-manager integration must not allow an old daemon with a new schema or adapter set. Portable installations use the same signed metadata. Automatic security updates are enabled by default and required for competitive profiles.

### WSL

The guest installation updates independently from the Windows-native application and uses the Linux profile. Host and guest compatibility is checked where duplicate reconciliation or bridges exist.

### Containers

Immutable signed image replacement is mandatory; in-container self-update is not the normal mechanism. Orchestrators roll to a compatible release-set digest and retain rollback capability. A mutable stale container may be server-blocked after deadline.

### CI and ephemeral runners

Pinned action/tool artifacts are updated through dependency automation or centrally maintained workflow references. Expired versions are rejected by the server after the compatibility window. Jobs do not run a persistent background updater.

## Active-work safety

- Updates acquire a maintenance lease.
- Normal updates wait for atomic local writes to complete.
- Pending claims, device lineage, local commitments and checkpoint state survive replacement.
- Update does not discard an active session silently.
- The user sees a clear countdown when a restart is required.
- Emergency privacy updates may stop collection immediately when continued operation is unsafe.

## Restricted-version behavior

A blocked version retains, where safely possible:

- local status and diagnostics;
- privacy inspection;
- local export;
- update and rollback recovery;
- uninstall;
- access to already stored local data.

It may lose:

- new source collection;
- new claim finalization;
- synchronization;
- stronger evidence eligibility.

The reason and deadline are explicit and signed.

## Required evidence

Before launch, test:

- metadata expiry and freeze attacks;
- rollback and mix-and-match attempts;
- artifact and provenance tampering;
- interrupted downloads and disk exhaustion;
- update during active capture and queued sync;
- schema migration failure;
- failed startup/privacy health check and rollback;
- key rotation and compromised release signing;
- offline clients returning after the deadline;
- service registration preservation;
- container rollout and rollback;
- CI rejection of expired tools;
- export/uninstall on blocked versions.

## Consequences

- Notify-only/manual update mode is not a supported competitive configuration.
- Users retain channel choice and bounded scheduling, not permanent refusal.
- Automatic updates become part of platform certification and launch readiness.
- Release infrastructure and compromise recovery are launch-critical, not optional operations work.
