# `protocol` conformance suite

Case prefix: `PR`. Subjects: `rust`, `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

One case over an unsigned eleven-field shadow codec whose authority class is `exploratory-prototype`. It is the only conformance directory any runner executes, and `evals/fixtures/protocol-conformance.json` names `conformance/vibeproof/v1/exact-byte-vectors.json` as its normative owner while running this directory instead. The suite has no negative case, so it cannot show that either subject rejects anything.
