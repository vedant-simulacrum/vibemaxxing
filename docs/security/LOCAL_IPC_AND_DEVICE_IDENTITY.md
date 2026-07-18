# Local IPC and Device Identity

## Security goals

- The transcript-capable process cannot use the network.
- The network-capable process cannot read transcripts.
- Only the intended local peer can submit safe claims.
- Replays, stale handshakes, oversized messages, role confusion, and endpoint hijacking are rejected.

## Common protocol

Every connection must perform:

1. kernel peer-identity validation;
2. protocol-version and role negotiation;
3. server-generated random challenge;
4. response bound to the process-start nonce and device/application key where available;
5. monotonic per-connection message sequence;
6. strict message-size and rate limits;
7. explicit close on unknown fields or schema violations.

Do not send transcript text, filenames, paths, prompts, code, or semantic findings through this channel.

## Linux

- Use a pathname Unix-domain `SOCK_SEQPACKET` or stream socket in a private runtime directory.
- Directory mode should normally be `0700`; socket mode should be least privilege.
- Verify peer credentials using `SO_PEERCRED`; use `SO_PASSCRED` where per-message credentials add value.
- Refuse peers with unexpected UID/GID and validate executable/build identity where feasible.
- Avoid the abstract namespace for the primary trust boundary.

## Windows

- Create named pipes with an explicit security descriptor.
- Restrict the DACL to the intended logon SID and required service identities.
- Reject remote clients and cross-session access.
- Do not rely on the permissive default descriptor.
- Prefer identification-level client inspection; use impersonation only for a documented need and always revert safely.

## macOS

- Prefer XPC between signed app/helper components.
- Validate the audit token and expected code-signing requirement for the connecting peer where supported.
- Keep entitlements minimal and separate network and transcript privileges.
- For developer CLI builds, use a private Unix-domain socket plus the common handshake, while labeling it as a weaker development mode.

## Device identity

- Generate a device key during registration.
- Prefer non-exportable hardware-backed storage; provide an encrypted software fallback.
- Store only the public key and metadata server-side.
- Device keys sign device-registration and claim-chain operations; they are not account-recovery credentials.
- Rotation, revocation, compromise response, and stale-device expiry must be explicit and testable.
