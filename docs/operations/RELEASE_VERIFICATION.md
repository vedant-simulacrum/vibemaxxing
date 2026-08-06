# Release Verification

A release is incomplete until an independent consumer path verifies it.

## Required artifacts

- Native binaries for supported targets.
- Checksums.
- SBOM.
- Build provenance attestation.
- Sigstore bundle/signature.
- Platform-native signature/notarization where applicable.
- TUF update metadata.
- Verification instructions.

## CI consumer test

A clean job must:

1. Download artifacts from the public release endpoint.
2. Bootstrap from the pinned trusted root.
3. Verify TUF metadata and rollback/freeze protections.
4. Verify checksum.
5. Verify Sigstore identity, issuer, signature bundle, and transparency-log inclusion.
6. Verify macOS or Windows native signature where relevant.
7. Run `--version` and a safe self-test.
8. Reject wrong identity, altered bytes, expired metadata, downgraded versions, and missing evidence.

Generating attestations without this verification job is not sufficient.

## TUF roles and trusted client state

Step 3 above names the rollback and freeze protections. `packages/schemas/tuf-trust-v1.schema.json` is what they are, and D-390 records the choices.

The security properties of TUF are client-side, so the record that matters is the client's own view rather than the repository's. `tuf_metadata` holds one row per device per role: the trusted version, its digest, the version and digest it replaced, the signature count, the threshold and the expiry.

Three refusals are named attacks and not error conditions:

| Refusal | Attack |
|---|---|
| metadata at or below the trusted version | rollback |
| metadata past its expiry, or a client past its own trust window | freeze |
| fewer signatures than the role's threshold | key compromise |

A check constraint makes a row recording fewer signatures than its threshold unrepresentable, so a client that accepted metadata it should have refused cannot record having done so.

Root and targets keys are offline; timestamp and snapshot are online. The four expiry cadences D-239 fixes are policy keys — `tuf_root_expiry_days` at 365, `tuf_timestamp_expiry_days` at 1, `tuf_snapshot_expiry_days` at 7 and `tuf_targets_expiry_days` at 90 — so the numbers resolve rather than living in prose.

Two limits are recorded rather than absorbed. D-091 leaves the project with one maintainer, so a root threshold above one is unsatisfiable and the policy says one rather than describing a checklist as equivalent. And no reason code exists for a local refusal: the reason registry has three transports and all of them are server-side, so the refusal column stays unpopulated until a local transport exists.

## Compatibility graph

`packages/schemas/compatibility-graph-v1.schema.json` and `compatibility_edges` answer which build may talk to which, per interface. D-391 records why there are six of them rather than one version number: a client can be current on the HTTP API and behind on the local IPC contract at the same moment.

Ranges are closed on the left and open on the right, so an empty range cannot be written. `breaking` is recorded and never derived, because D-234 makes adding a member to a closed state vocabulary a major-version change and no arithmetic over two numbers can detect that. A sunset without a deprecation notice is refused unless it names one of D-234's three carve-outs, which turns the 180-day window into a constraint rather than an intention.
