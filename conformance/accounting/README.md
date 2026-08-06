# `accounting` conformance suite

Case prefix: `AC`. Subjects: `rust`, `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

Ten cases over eleven files. One of them, `accounting-v1-fixtures.json`, is read by `scripts/ci/run_phase1_evidence.py`; the other ten files are exercised only by the Python stages of `scripts/repository/validate_planning_artifacts.py`, which is one subject and not the two the manifest declares. No case here is cross-language conformance.
