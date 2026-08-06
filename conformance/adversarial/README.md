# `adversarial` conformance suite

Case prefix: `AV`. Subjects: `go`. Harness contract: `docs/verification/CONFORMANCE_HARNESS.md`.

## What this suite proves when it runs

That every attack in the catalogue produces the outcome the catalogue claims. This is the suite that turns the anti-cheat design from a table of intentions into a set of assertions.

Authorities:

- `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`, which is the case list
- `docs/security/THREAT_MODEL.md`
- `docs/security/INTEGRITY_MODEL.md`
- `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`
- `packages/schemas/reason-codes-v1.json` for the expected outcome of each rejection

## Required cases

**One per row of the attack catalogue.** The catalogue already states, for every attack, the control, the expected outcome and the confounder that must not be misclassified as the attack, which is a case definition in everything but format. A row with no case is an attack whose control has never been exercised.

The confounder column is not optional detail. Half of these controls are only correct if they *also* leave the legitimate case alone: offline activity that looks like backdating, sleep-and-resume drift that looks like clock rollback, a genuine device migration that looks like a clone. Each case therefore has a paired negative — the attack, rejected — and a paired positive — the confounder, accepted — and passing only the first is not passing.

Existing partial material: `conformance/adversarial/anti-cheat-registry-v1.json` and `conformance/adversarial/wave4-cases.json` map some attack identifiers to expected outcomes. They are a start and not a manifest; neither carries fixture digests, authority references or a negative-case declaration.

One known defect the manifest work will surface: `anti-cheat-registry-v1.json` maps `clock-rollback` to `CLAIM_SEQUENCE_UNEXPECTED`, and `packages/schemas/reason-codes-v1.json` registers no code for a clock rollback or a future timestamp. Either a code is registered or the mapping is wrong; a case cannot be written until that is decided.

## Status

**Nothing here executes.** No `manifest.json`, no runner, and no server to attack. The `adversarial-integrity` eval suite is `not_applicable` and names `apps/api/internal/appraisal` and `evals/fixtures/adversarial-integrity.json` (new) as the paths whose absence justifies that status. `docs/security/ADVERSARIAL_TABLETOPS.md` records paper exercises, which are design review and not conformance evidence. A README is not executable evidence and this one does not change any status.
