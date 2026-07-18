# Platform Isolation Contract

## Required process split

`vibeproof-private` may read approved local evidence but has no network capability.

`vibeproof-sync` may use the network but cannot read transcript/session roots or local semantic outputs.

They communicate through a versioned fixed-schema IPC channel containing safe claims only.

## Portable baseline

- Separate executables and identities where practical.
- Explicit inherited-handle closure.
- Absolute path allowlists.
- No arbitrary plugin loading.
- No shell execution in the private process.
- Resource ceilings.
- IPC peer authentication.
- Negative tests for network, DNS, forbidden paths, process execution, and credential stores.

## macOS

Preferred controls:

- App Sandbox for compatible components.
- App-group container for narrowly shared state.
- Security-scoped user-approved file access.
- Separate signed helper when required capabilities conflict with the GUI sandbox.
- Entitlement inspection in CI for release artifacts.

## Linux

Preferred controls:

- Landlock filesystem policy.
- Seccomp syscall policy.
- Namespaces and cgroups where available.
- No-new-privileges.
- Read-only mounts and explicit writable state roots.

## Windows

Preferred controls:

- AppContainer or less-privileged AppContainer.
- Explicit filesystem capability grants.
- Denied network capability for the private process.
- Named-pipe ACLs for IPC.
- Job objects for process and resource containment.

Experimental sandbox APIs may be evaluated but cannot be the sole production dependency until stable.

## Evidence states

- Standard: portable process split and tested policy.
- Hardened: verified platform-native kernel enforcement.
- Imported: historical/non-live evidence, never active-rank equivalent.
