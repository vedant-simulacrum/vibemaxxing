# Integrity Model

Updated: 2026-07-23
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