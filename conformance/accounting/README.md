# `accounting` conformance suite

Case prefix: `AC`. Subjects: `rust`, `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

Twelve cases over thirteen files. One of them, `accounting-v1-fixtures.json`, is read by `scripts/ci/run_phase1_evidence.py`; the other twelve files are exercised only by the Python stages of `scripts/repository/validate_planning_artifacts.py`, which is one subject and not the two the manifest declares. No case here is cross-language conformance.

`reconciliation-vectors-v1.json` is evaluated under **every permutation** of each vector's readings, not under a sampled pair, so a reconciliation whose total depends on which reading arrived first fails here. Its readings carry what the source said and who read it and nothing about when it arrived, because a field a vector can carry is a field a tie can be broken on; `reconciliation-vectors-v1.invalid-arrival-order-field.json` is that refusal. No vector in either file names a certified tuple, because no binding in `producer-bindings-v1.json` is certified.
