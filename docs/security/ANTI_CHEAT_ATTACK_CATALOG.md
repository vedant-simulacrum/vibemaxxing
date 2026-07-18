# VibeMaxxing Anti-Cheat Attack Catalog

Updated: 2026-07-19
Status: planning template

Use one record per materially distinct attack. Do not merge attacks that require different controls or produce different user consequences.

## Required record fields

| Field | Meaning |
|---|---|
| ID | Stable identifier such as `AC-A-001` |
| Name | Short attack name |
| Class | fabrication, replay, identity, time, source, client, server, collusion, supply-chain, SLM, privacy |
| Description | Exact attacker action |
| Prerequisites | Required access, tooling, privileges, or coordination |
| Target | Adapter, collector, IPC, local state, claim, sync, API, database, ranking, account, updater |
| Expected gain | How rankings or evidence could be manipulated |
| Standard exposure | Feasibility against Standard evidence |
| Hardened exposure | Feasibility against Hardened evidence |
| Prevention | Deterministic controls that stop the attack |
| Detection | Signals that identify attempted or successful abuse |
| Residual risk | What remains possible after controls |
| False-positive risk | Legitimate behavior likely to resemble the attack |
| Policy action | Accept, downgrade, reject, quarantine, review, revoke, restore |
| Reason codes | Machine-readable policy reasons |
| User explanation | Safe and understandable explanation |
| Appeal route | Evidence and process for appeal |
| Test design | Fixtures, mutations, races, or red-team steps |
| Success criterion | Measurable control requirement |
| Owner | Planning or engineering owner |
| Status | proposed, researched, specified, tested, accepted-risk |

## Seed attack inventory

1. Edited token fields in mutable local records.
2. Fully fabricated source events.
3. Valid claim replay.
4. Concurrent duplicate submission.
5. Session or claim copied from another user.
6. Host and nested/guest agent double counting.
7. Backdated events crossing ranking periods.
8. Clock rollback and future timestamp manipulation.
9. Sequence rollback.
10. Previous-claim-chain truncation or fork.
11. Device-state cloning to a second machine.
12. VM or filesystem snapshot restore.
13. Modified collector or verifier.
14. Modified adapter emitting forged normalized events.
15. Source/model/version impersonation.
16. Unsupported source version presented as supported.
17. Official-build signature or update metadata substitution.
18. Device-key theft and reuse.
19. Account takeover through OAuth identity compromise.
20. Colluding accounts amplifying boards, presence, or rank movement.
21. Synthetic event generator mimicking legitimate sessions.
22. Repeated session fingerprints across accounts or devices.
23. Ingestion race exploiting uniqueness or transaction boundaries.
24. Aggregator replay or outbox duplication.
25. Pricing dataset substitution affecting Estimated Cash Burn.
26. SLM prompt injection through adversarial transcript text.
27. SLM model, weights, runtime, or policy substitution.
28. Denial of service through oversized or pathological local input.
29. Privacy exfiltration introduced as an integrity feature.
30. Moderator or insider abuse of quarantine and appeal controls.

## Catalog rule

A launch-blocking attack may not be marked resolved by prose alone. It requires an explicit control design, negative tests, measurable success criteria, residual-risk statement, and appeal behavior.