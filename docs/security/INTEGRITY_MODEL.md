# Integrity Model

Updated: 2026-07-19
Status: normative planning contract

## Consumer-facing states

### Standard

Live competitive VibeProof collection satisfying `Standard Live v1` or a later accepted Standard profile.

### Hardened

Live competitive collection satisfying a named, versioned Hardened profile. `Hardened` is never awarded merely because one evidence dimension is stronger than Standard.

### Imported

Historical usage loaded from mutable local records. Imported activity is private analytics only and does not affect competitive rankings.

Avoid the word `verified`. Public UI exposes the simple state plus the profile ID, expiry and inspectable evidence breakdown.

## Independent evidence dimensions

The normative dimensions, classes and profile thresholds are owned by `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`:

- source authority;
- capture binding;
- accounting authority;
- device-key protection;
- continuity and rollback strength;
- environment assurance;
- freshness;
- exact compatibility evidence.

No dimension is inferred from another. Provider-reported usage observed locally is not provider-signed evidence. Device attestation does not prove source accounting. A server challenge proves submission freshness, not that an offline event existed before the challenge.

## Ranking policy

- Competitive rankings require live activity and a non-expired Standard or Hardened profile.
- Strongest integrity views require a named Hardened profile, official signed build, exact exercised adapter/runtime/model tuple, source recognition, continuity, accounting profile, duplicate-domain controls and every required clone/replay/privacy fixture.
- Unknown source or model versions fail closed for Hardened and may downgrade only to an explicitly exercised compatible Standard tier.
- Any observation gap breaks Hardened continuity for the affected interval.
- Imported, expired, unsupported and quarantined claims never silently contribute to active competition.
- Profile changes are prospective; accepted historical claims retain the profile and policy version under which they were accepted unless an explicit correction or disqualification record is issued.

## Fundamental claim boundary

VibeProof establishes canonical claim signing, registered-key possession, server challenge handling, continuity and policy acceptance. It does not universally establish provider origin, an uncompromised user-controlled machine, non-cloning, or truthful source output. Public descriptions must preserve this boundary.
