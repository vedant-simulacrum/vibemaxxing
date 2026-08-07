# vibeproof-core — exploratory prototype, quarantined

**This crate is not the VibeProof v1 protocol.** It is an exploratory prototype that
implements an eleven-field shadow payload predating the normative schema, and it is
quarantined under P-1140F-1 until it is rewritten against that schema.

The normative authority is `packages/schemas/vibeproof-claim-v1.cddl`, owned by
`docs/architecture/VIBEPROOF_V1_PROTOCOL.md`. Where this crate and the CDDL disagree,
the CDDL is correct and this crate is the defect.

## Known incompatibilities with the normative schema

- unsigned 11-field payload
- client-selected evidence class
- client-selected billable total
- does not consume normative COSE vectors

## Prohibited uses

Output from this crate may not be used for:

- claim-ingestion
- ranking
- verifier-appraisal
- normative-conformance
- support-claim

Its evidence ceiling is `fixture-consistent`: its tests prove it agrees with its own
fixtures, and nothing more. Agreement with `apps/api/cmd/api/protocol_fixtures.go` is
not conformance either — both consume the same shadow schema, so they agree with each
other about something the protocol does not say.

## Why it still exists

Deleting it would discard a working deterministic-encoding prototype and the pricing
arithmetic in `tests/accounting_pricing.rs`, which are the input to the D-012 CBOR/COSE
crate bakeoff. It is kept as a research artifact and fenced rather than removed.

`conformance/p1140f/artifact-authority-v1.json` is the authority for this file's status.
`scripts/repository/validate_artifact_quarantine.py` checks that this notice still
matches that record; edit the record, not this list.
