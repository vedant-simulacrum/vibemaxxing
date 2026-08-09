# The VibeProof v1 shadow profile, and why it is not the canonical one

**This document is not the canonical wire profile.** `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` owns canonical encoding, COSE, limits and state transitions, and `packages/schemas/vibeproof-claim-v1.cddl` owns every payload and integer label. What this file owns is the *other* profile: the eleven-field shadow grammar in `protocol/vibeproof-v1.cddl`, its status, and the condition under which it is retired.

Until this revision it claimed the canonical role while describing the shadow. Everything below the first paragraph was the shadow codec — an eleven-key outer map, a three-key token map, a 1024-byte input limit, a client-selected evidence class, and "COSE signing and verification are intentionally out of scope" — presented under a filename that says canonical profile, in the same directory as the document that actually owns canonical encoding. Two files answered one question and the wrong one was easier to find.

## What the two profiles actually are

| | Normative | Shadow |
| --- | --- | --- |
| Grammar | `packages/schemas/vibeproof-claim-v1.cddl`, 26 rules | `protocol/vibeproof-v1.cddl`, 11 fields plus 8 helper rules |
| Claim shape | 31 integer labels, closed map | 11 integer labels |
| Token accounting | `token-categories`, 7 categories | `token-totals`, 3 |
| Signing | COSE_Sign1, tag 18, Ed25519 `alg -19`, external AAD `VIBEMAXXING/VIBEPROOF/V1` | none |
| Evidence class | assigned by the server verifier | `evidence-class` carried by the client |
| Vectors | `conformance/vibeproof/v1/` | `conformance/protocol/vibeproof-v1-vectors.json` |

The evidence-class row is the one that matters beyond field counts. A client-selected evidence class contradicts the binding product rule that public evidence status and competitive eligibility are assigned by the server verifier and never selected by the client, so the shadow grammar is not a simplification of the normative one — it decides something the normative one refuses to let the client decide.

## Status and retirement

D-096 accepted that the Rust and Go implementations are rewritten against the normative profile and the exact-byte vectors, and that the shadow profile and its vector corpus are retired once both implementations and their conformance suites consume the normative authority. That has not happened. `crates/vibeproof-core/`, `apps/api/cmd/api/protocol_fixtures.go`, `conformance/protocol/vibeproof-v1-vectors.json` and the `shadow-codec-parity` eval suite all consume the shadow profile and are each classified `exploratory-prototype` in `conformance/p1140f/artifact-authority-v1.json`.

`protocol/vibeproof-v1.cddl` itself is not in that registry. Four consumers of a grammar are quarantined and the grammar is not, so `validate_artifact_quarantine.py` reports five quarantined artifacts and the file they all agree about is not one of them. Adding a row for it requires the file to carry a quarantine notice — `scripts/repository/validate_artifact_quarantine.py` reads the notice out of the artifact itself — and `protocol/` is outside the paths `PF-002` may write. The row and the notice belong to the unit that owns that tree; this document records the hole rather than leaving it implicit in a count.

## Rollback

If a canonical-profile defect is found, stop accepting the affected protocol version, retain claims for investigation, and release a versioned replacement with new vectors. Never reinterpret old bytes under a changed profile. Accounting or pricing fixture defects quarantine affected totals until deterministic replay against a reviewed replacement fixture is complete.
