# Integrity Model

Updated: 2026-08-09
Status: normative planning direction; dimensional policy and schemas require P-1140B/C repair.

## Fundamental boundary

VibeMaxxing cannot universally prove genuine provider origin or uncompromised local execution on an unrestricted user-controlled machine. It can establish bounded, versioned facts about source capture, accounting, device signing, continuity, compatibility and server acceptance.

Do not use `verified` or `cheat-proof` as a blanket label.

## Consumer-facing states

### Standard

The server verifier accepted competitive usage under a named Standard profile. Accounting, privacy, compatibility and minimum continuity requirements passed, but one or more stronger source, device, process, checkpoint or attestation requirements were unavailable.

Standard is legitimate competitive usage and may contribute to global leaderboards.

### Hardened

The server verifier accepted competitive usage under a named Hardened profile after every required evidence dimension and certification check passed for the exact source/runtime/version/mode/platform/artifact tuple.

Hardened is a stronger evidence statement, not a different game and not a client setting.

### Imported

Historical usage loaded from mutable local records. Imported activity is private analytics only and never affects competitive rankings.

## Evidence ownership

The device submits evidence facts. The server verifier creates the authoritative appraisal.

A client claim may not self-award Standard or Hardened. The server appraisal records:

- source authority;
- capture binding;
- accounting authority;
- device-key protection;
- continuity strength;
- environment assurance;
- freshness and time uncertainty;
- compatibility/certification evidence;
- deterministic rule results;
- policy/profile version;
- acceptance, downgrade, quarantine or rejection outcome.

A stronger value in one dimension cannot silently compensate for an unmet mandatory requirement in another.

## Competitive policy

- Competitive ranking requires live or deterministically committed source activity, not historical mutable import.
- Certified local-model and delayed offline usage may be Standard or Hardened.
- Lack of network connectivity alone does not make usage ineligible.
- Long unanchored intervals, observation gaps, rollback uncertainty or weak key protection lower the applicable profile ceiling.
- Unknown source versions fail closed for Hardened and may downgrade only to an exercised compatible Standard profile.
- Generic estimates remain private unless a separately certified deterministic reconstruction profile explicitly permits competition.
- Standard and Hardened may both count globally; leaderboard views may filter Hardened-only.

## Continuity interpretation

Continuity must distinguish:

- local append-only event/claim commitment;
- previous server checkpoint receipt;
- current server challenge and submission freshness;
- device lineage and recovery state.

An upload-time challenge does not prove an offline event existed before the challenge. A local chain proves ordering but gains stronger retrospective resistance only through prior/following server checkpoints or platform-backed rollback-resistant state.

Continuity is scoped to the lineage, never to a device row. `AGENTS.md` states it as a binding rule and this section is where the mechanisms that carry it are listed: `device_sequences` holds one counter per lineage, `device_lineages` is the sole owner of `continuity_state`, and `claims`, `checkpoint_receipts` and `device_key_events` are all keyed and constrained on `lineage_id`. Scoping any one of them on the device row reintroduces the same defect, because a copied store enrols as a second device and then keeps a private counter, a private receipt chain or a private key history that nothing compares against the lineage's.

### Which acknowledged head wins

A lineage may present two acknowledged heads — a restore from a backup and the live device, most often. The newest wins: the receipt with the greater `accepted_through_claim_sequence` is authoritative, and the server never moves its head backwards. A device arriving with an older head is behind rather than correct, and rejoins by declaring a gap or requalifying; nothing about arriving late entitles it to roll the lineage back.

The ordering is over the sequence the server itself issued and never over a timestamp, because a clone controls its own clock and would otherwise win by setting it forward. Two receipts acknowledging the *same* head do not resolve at all: that is the `checkpoint-mismatch` detection basis below, and `unique (lineage_id, accepted_through_claim_sequence)` on `checkpoint_receipts` refuses the second write rather than storing a fork nobody counted.

### Device-key rotation and lost-key recovery

An ordinary rotation is dual authorized. `dual-authorized-rotation-v1` is two COSE_Sign1 envelopes over identical payload bytes: the outgoing key signs to prove continuity, the incoming key signs to prove control. Recent account authentication is a third gate at a different layer and is not a substitute for either half — a device that already holds both keys is the position a stolen laptop is in, and an account session alone is the position a phished attacker is in. `device_key_events` records all three as separate columns, with a check constraint that refuses a `rotated` row missing any of them.

Lost-key recovery is the case that cannot satisfy the pair, because the outgoing key is gone. It is a separate action rather than a rotation with a waiver: `recovered` requires an approved recovery case and *forbids* an outgoing-key signature, so a rotation cannot be admitted by asserting a recovery, and a party that can still sign with the old key cannot reach the recovery authority by claiming to have lost it. Recovery revokes the old key path, resets continuity or starts a new lineage, and requires requalification; a restored or cloned successor quarantines until resolved.

Revocation is the one transition with no key authorization at all, since the key being revoked may be exactly the one that is lost or in someone else's hands. Recent account authentication is therefore the whole of its authority, and the constraint says so.

Recovery is exhaustible and exhaustion is permanent. Under D-561, a participant who has lost every enrolled device and every recovery code has no reachable path back: the ranked identity is retired terminally and there is no appeal transition. `docs/security/AUTHENTICATION_AND_RECOVERY.md` owns that rule and the enrolment surface that must state it; it is named here because it is the boundary condition of this section — the recovery authority above is finite, and continuity that cannot be re-established is not restored by a support decision.

### Fork and clone resolution

A lineage fork is the case where two device installations present continuations of one lineage generation. D-072 states the outcome and D-383 records the aggregate that carries it.

| Concern | Owner |
|---|---|
| Lifecycle | the `lineage-fork-case` machine |
| Persistence | `lineage_fork_cases` and `lineage_fork_branches` |
| Record | `packages/schemas/fork-resolution-v1.schema.json` |
| Revision model | `lineage_fork_cases.revision` |
| Transaction boundary | `fork-case-and-branches` while quarantining and selecting, `fork-case-and-lineage` when the survivor resumes |
| Reversal | `reversed`, reached only through an appeal, which releases the quarantine and restores the branch's claims |

The states are `detected`, `quarantined`, `survivor-selected`, `requalifying`, `resumed`, `unresolved`, `appealed` and `reversed`. Only `resumed` and `reversed` are terminal; `unresolved` is not, because a denied appeal returns the case to it and a later appeal is still possible.

Three properties are constraints rather than procedure:

- a resumed generation is strictly greater than the fork generation, so a resolution cannot replay the fork it resolved and cannot be read as a merge of two commitment chains;
- one survivor exists per case, enforced by a partial unique index, so two operators cannot select two;
- one open case exists per lineage generation.

Claims accepted at or before the fork generation are untouched, because a fork says nothing about work already accepted. Post-fork claims on a quarantined branch are held by `quarantines` and are not deleted: the resolution is appealable, and an appeal needs the evidence a deletion would have destroyed. Every branch is recorded including the ones that lost, for the same reason.

Detection is deterministic — a duplicate sequence continuation, a divergent commitment chain, a duplicate installation identity, or a checkpoint mismatch. None of the four is a statistical inference, which D-053 confines to a local advisory detector.

They are checked in a fixed order, and duplicate installation identity is first. A copied store presents a duplicated installation identity at enrolment, before it presents a conflicting sequence, so waiting for the collision accepts one more generation of claims from a store already known to be duplicated. Checkpoint mismatch is last because it is the only one observable from the acknowledged heads alone rather than from a submission.

A malformed submission is refused, not quarantined. One naming a commitment head the lineage never held, or a sequence that is neither the next nor one already issued, identifies no branch and opens no case; it resolves to `CLAIM_GAP_DECLARATION_REQUIRED` or `CLAIM_SEQUENCE_UNEXPECTED` and the lineage continues. Conflating the two would make every decoding error a fork.

`conformance/vibeproof/v1/fork-and-rotation-vectors.json` states what a decoder must conclude for each of these, and `validate_lineage_fork_and_rotation` in `scripts/repository/validate_planning_artifacts.py` recomputes every disposition rather than reading it. Two of its five lineages fork nothing — a control that accepts four submissions in a row, and one whose two malformed submissions are refused — because every other assertion in the corpus is otherwise satisfied by a resolver that quarantines all input. Nothing in the product reads that file; it says what an implementation must do and is not evidence that one does.

## Environment interpretation

Signed builds, process binding, OS key protection and attestation are independent evidence inputs. None alone proves token accounting.

Hardened must remain attainable for certified local sources without requiring cloud-provider receipts, but every named profile must disclose its actual source, device and environment requirements.

## Detector boundary

Deterministic controls are authoritative for accounting, schema, signature, replay, duplicate, continuity and hard eligibility.

Statistical and model-based detectors:

- consume privacy-safe aggregate/structural features by default;
- cannot alter token totals;
- cannot award a stronger profile;
- cannot permanently ban independently;
- begin in shadow/advisory mode;
- require registered versions, calibration and appealable reason codes.

The SLM is post-launch research only. A future raw-local-record mode requires a separately approved sandbox and may emit only bounded registered anomaly classes; no raw content or content-derived identifier may leave the device.