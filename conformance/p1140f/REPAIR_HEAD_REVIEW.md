# P-1140F Repair Head Review

Status: `reviewed`
Updated: 2026-08-12

This record captures the reviewed planning-contract head. It is not a security
certification, a runtime test, or a P-1104 authorization, and closing a finding on this
head means the recorded contradiction is gone from the documents rather than that any
behaviour is correct.

## Exact review target

- Commit: `46bf2fa47963261d48fa80a6980de85d80cfaad8`
- Clean-checkout CI: [Planning checks run 31606983374](https://github.com/vedant-simulacrum/vibemaxxing/actions/runs/31606983374) — passed on that exact commit, including PostgreSQL-backed structural DDL validation, which does not execute locally.
- Finding registry SHA-256: `7791b82d637d9c022bbd88d11650113153512c4f17acf540da69957f299f663c`
- Artifact registry SHA-256: `5a4c90b29348f600fb342a97c3221319014b21b98bd5324eba360ad89f5a269d`
- Review boundary: planning-contract semantics only. Do not infer runtime security, platform certification, deployment readiness, or P-1104 authorization.

Both registry digests were computed from the two files as they stand at the reviewed
commit. No validator computes or verifies them — the schema checks only that they are
sixty-four hex characters — so they are a recorded claim a reader can reproduce with
`git show <commit>:<path> | shasum -a 256`, not a machine-derived fact.

## Superseded target

This record previously pinned `e1320a6730a62a7345ad44d149a9344d3d17c1c9` with the status
`pending-independent-semantic-review`. That head is superseded, not reviewed: it was the
repaired P-1140E structural head, and the thirteen semantic findings SR-005 through SR-017
were opened against it afterwards. It is named here rather than deleted because SR-016
cites this file at that digest, and a record that quietly drops the head it used to claim
is the drift that finding exists to catch.

## Verdict

**PASS-WITH-EXCEPTIONS**, for SR-005 through SR-017, recorded by the CTO under delegated
owner authority.

The registry spells this as `review_verdict: "pass"` with the three limitations below,
because `review-target-v1.schema.json` admits `pending`, `pass` and `fail` and nothing
else. Adding a fourth value would have meant amending two schemas and the authority
validator to record something the limitations already say in full. The exceptions are
the verdict; they are not commentary on it.

## Limitations

1. **This review is not independent.** It was performed under delegated owner authority by
   the same agent that performed the repairs. SR-016 is the finding about review-record
   integrity, so this verdict is an instance of the thing that finding governs. The
   mechanical criteria — artifact coverage, evidence format, unit status — are
   machine-checked and cannot be talked around; the judgement about whether a repair is
   adequate is not.
2. **These are contract repairs.** Nothing in this repository is implemented, so no finding
   is closed on runtime evidence. A closed finding means the recorded contradiction is gone
   from the documents, never that the behaviour is correct.
3. **D-012, D-043 and D-046 remain open decisions** with stated missing evidence. They are
   not findings and do not block the gate, and each names what would close it.

## What the mechanical half actually checked

- `validate_repair_task_binding.py` — every serving unit of every finding has landed, and
  every closure-evidence entry names a unit that serves that finding at a commit this
  checkout resolves.
- `validate_finding_artifact_coverage.py` — every conflicting artifact of every settled
  finding is either touched by a commit the finding cites or carries a recorded reason it
  needed no change. The claim scope is file-level: a cited commit touching the file is not
  proof it repaired the fragment, and a recorded reason is a claim a reviewer must read.
- `validate_work_unit_status.py` — every `landed` unit's `Evidence:` lines were executed,
  not parsed.
- `validate_p1140f_authority.py` — every severity the registry can carry has a recorded
  ceiling, and the review cannot pass while any finding is open at any severity.

None of that is the review. It is the floor the review stands on.

## Severity

D-300 is accepted as proposed: nine findings at P0, three at P1, one at P2. The gate record
carries a ceiling for each severity — `open_p0_baseline` 9, `open_p1_baseline` 3,
`open_p2_baseline` 1 — which is a partition of the thirteen the single P1 ceiling held,
not a relaxation of it. Before this change a regrade would have moved nine findings out of
the only severity anything counted and improved the number by emptying it.

## What remains

The gate state in `conformance/p1140f/gate-authorization-v1.json` is unchanged and remains
the owner's alone. No agent has flipped it, and this record does not flip it.
