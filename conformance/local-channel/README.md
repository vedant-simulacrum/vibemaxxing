# Local channel conformance

Refusals on the IPC channel between a role process and the daemon.

`docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md` states that role confusion and stale
handshakes are rejected. Before PF-012 the protocol could do neither: `Envelope`
carried a single universal `oneof` holding every body, `sender_role` was a field the
sender filled in, and no reason code existed with which to refuse anything. The
document promised a property the wire format made structurally impossible to have.

`packages/schemas/local-control-v1.proto` now reaches each body only through its own
role's arm, so a collector encoding a deletion request is unrepresentable rather than
rejected. What remains detectable — a sender setting `sender_role` to one role and
selecting another role's arm, an unverified peer executable, a grant from before a
revocation — is what the three `local-channel` reason codes name.

This suite is separate from `conformance/sandbox`, whose reason authority is
`packages/schemas/origin-policy-v1.json`. A loopback refusal is an origin decision and
a local-channel refusal is a peer-identity decision; two different vocabularies do not
belong in one suite.

**No runner executes these vectors.** They state what the daemon must refuse. They are
not evidence that any daemon refuses it.
