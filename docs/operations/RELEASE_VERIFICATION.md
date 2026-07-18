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
