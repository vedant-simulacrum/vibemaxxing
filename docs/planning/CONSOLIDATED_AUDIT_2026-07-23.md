# Consolidated repository audit

Updated: 2026-07-23

## Authority and scope

This document consolidates the post-validation audits performed against `main`, recent commits, issues, pull requests, normative contracts, planning schemas and the bounded Storybook/web prototype.

It is a planning artifact. It does not authorize product implementation, automated security/evaluation workflows, deployment, or launch. No finding below is evidence that an exploit exists in deployed software because no production backend, collector, protocol runtime, identity service, ranking service or updater exists.

## Executive conclusion

The repository is **not planning-contract complete**. The validated schemas prove that files parse and selected fixtures pass; they do not prove that the contracts are mutually complete, privacy-safe, interoperable or launch-ready.

The audit found a repeated failure pattern: prose promises a security, privacy, accounting or social invariant, while the machine contract either cannot represent it, permits contradictory states, or delegates the decision to an untyped string/JSON/byte field. Several accepted decisions remain directionally sound, but D-045's completion claim must be reopened.

The current implementation boundary remains:

- a fixture-backed hosted-web/Storybook prototype and design assets;
- planning-grade Markdown, OpenAPI, CDDL, Protobuf, JSON Schema and PostgreSQL DDL;
- no production implementation or executable security evidence.

## Consolidated critical findings

### 1. VibeProof and claim ingestion

1. The Token Burn formula assumes provider token categories are mutually exclusive; OpenAI cache/reasoning fields are breakdowns while Anthropic cache fields are additive. A provider/API-mode accounting profile must determine containment and canonical totals.
2. The complete COSE profile is absent: tag choice, protected labels, `kid` encoding, COSE_Key format, external AAD, unprotected headers and exact signed bytes are not frozen.
3. The claim extension map permits arbitrary binary values under arbitrary integer keys and an unbounded entry count. Protocol v1 should have no open-ended extension channel.
4. `application/cbor` is modeled as base64 text and no normative batch-envelope CDDL exists.
5. Batch atomicity, per-claim outcomes, challenge consumption, retries and durable batch replay results conflict.
6. `previous_claim_hash` is described as the previous accepted claim although offline multi-claim batches require a previous locally committed claim. The exact hashed object and domain separator are undefined.
7. Device-key rotation requires old/new authorization but has no transition payload, dual-signature wire format, persistence transaction or sequence boundary.
8. Client claims can self-assert the final `Standard`/`Hardened` state. Attester evidence, verifier appraisal and ranking eligibility must be separate objects.
9. Claims do not bind enough structural provenance to reproduce an evidence decision: capture mode, authority, profile versions, certification artifact, event commitment and policy versions are missing.
10. Client-side correction/supersession references lack authority and conflict with server-side append-only correction ledgers.
11. Numeric ranges differ across JSON, CBOR, JavaScript and PostgreSQL, permitting rounding, overflow or persistence failure.
12. Estimated counts can compete without a machine-enforced evidence ceiling. Generic estimates should remain private analytics; certified deterministic reconstruction needs a named lower profile.
13. Client wall-clock timestamps can select ranking and pricing periods without server-anchored uncertainty bounds.
14. Raw monotonic counters lack clock-domain, generation and suspend semantics; the JSON ordering conditional is ineffective.
15. A local commitment chain proves order, not pre-challenge existence, unless the server has previously acknowledged a chain head.

### 2. Device, native runtime and updater

16. New device enrollment can discard a quarantined/forked chain because device lineage, replacement reason, account-level integrity state and requalification are absent.
17. Device cloning and rollback cannot be solved universally by stable hardware identity without unacceptable privacy/platform trade-offs. Controls must combine lineage, server checkpoints, assurance ceilings and appealable account-level policy.
18. Local IPC sends opaque `normalized_event_json` bytes rather than a typed privacy-safe message, reopening an arbitrary-content channel between privileged processes.
19. Presence renewal is not bound to collector-observed qualifying activity; a web/session client could fabricate indefinite activity.
20. Presence audiences, privacy precedence, multi-device aggregation and immediate revocation are prose-only.
21. Hosted deletion scopes include `local`/`everything`, but a server cannot guarantee or safely authorize local destruction. Server deletion and per-device local deletion need separate state machines.
22. The native-to-web authenticated bridge has no single-use bootstrap protocol and risks bearer-token leakage or browser/daemon credential confusion.
23. The updater promises TUF, signing, transactional installation and rollback protection without a trust root, role policy, release-set manifest, compatibility graph, migration transaction or compromised-version evidence policy.
24. Adapter certification is bound to mutable names/versions rather than exact artifact digests, provenance and immutable result bundles.
25. The optional local SLM has no reproducible model/runtime/input/calibration contract. It must remain non-authoritative and disabled until it beats deterministic baselines under published false-positive limits.

### 3. Authentication, identity and sessions

26. OAuth establishes control of provider accounts, not one unique human. The current uniqueness constraint only prevents reuse of the same provider subject and cannot enforce one-human-one-ranking-identity across accounts/providers.
27. Google is named in ranked-identity policy but absent from the authentication SQL/OpenAPI/provider contract.
28. OAuth transaction persistence stores only hashes and cannot recover the original PKCE verifier or bind issuer, redirect URI, client configuration, browser/native instance and intended action.
29. Refresh-token rotation, token-family lineage, replay detection, revoke-all and separate web/native sessions exist only in prose.
30. Handle rename cooldowns, redirects, non-reuse, deletion privacy and Unicode-policy migration need an append-only assignment/reservation ledger.
31. Export requests lack typed scope, coherent snapshot, manifest, recent authentication, encrypted delivery, revocable short-lived download grants and purge receipts.
32. Idempotency headers are required but no transactional idempotency ledger, fingerprinting, key scope, response replay or expiry semantics exist.

### 4. Accounting, pricing and ranking

33. Pricing tables cannot represent units, denominators, region, service tier, batch/flex/priority mode, thresholds, cache duration/storage, modality, tools or stacking.
34. A client may name a pricing dataset even though Estimated Cash Burn must be a server-derived interpretation.
35. Model aliases lack immutable event-time resolution, so historical prices can change during rebuilds.
36. Cost interpretations do not retain rule-level line items, matched conditions, rounding or component provenance.
37. Ranking promises model/agent/evidence filters, but OpenAPI, aggregates and snapshots do not carry a canonical ranking-view identity.
38. `first_reached_score_at` has no deterministic semantics after negative corrections, repeated score crossings, filters or rebuilds.
39. Country affiliation is mutable, semantically undefined and historically unversioned; cohort privacy and country-board binding are prose-only.
40. Public country ranking should use prospective, season-frozen ranking affiliation rather than imply nationality or live location.
41. Moderation actions and appeals cannot identify exact claims, views, periods or ledger effects, nor deterministically reverse them.

### 5. Social and public-product contracts

42. Board ownership has conflicting authorities (`boards.owner_account_id` and owner memberships), while board/org/community governance transitions are absent.
43. Friendships are undirected but stored as ordered pairs, permitting duplicate reverse edges and crossed requests.
44. Notifications/outbox payloads and preferences are unrestricted JSON, so privacy fields, deduplication, hysteresis, block reauthorization, quiet hours and retractions are not enforceable.
45. External avatar URLs create either third-party viewer tracking or SSRF. Use controlled upload/provider import, re-encoding and internal asset IDs.
46. Public profile, claim, presence, pricing and several other endpoints return generic open-ended resources, undermining field-level authorization and interoperability.
47. API resource governance is absent: payload/compute limits, quotas, concurrency, polling cadence, `429`, `Retry-After`, outstanding-object ceilings and load shedding are unspecified.

## Decisions that can be closed now

These are recommended defaults and do not require implementation authorization:

- Keep D-006: forbidden content never crosses the device boundary. Remove hosted request-path evidence from launch profiles.
- Keep Standard/Hardened as public labels, but award them only through server verifier appraisals.
- VibeProof v1 has no generic extension map and uses one fully specified COSE profile.
- Token Burn uses versioned provider/API accounting profiles and only mutually exclusive canonical totals.
- Estimated counts are private unless a deterministic reconstruction profile is explicitly certified; estimates never receive Hardened.
- Estimated Cash Burn is server-derived from immutable usage facts and versioned pricing rules.
- Competitive time uses server-anchored intervals; client wall time is diagnostic only.
- Device chains are append-only local continuity chains; ranking effects are separate server ledger decisions.
- Offline intervals without a prior/following server checkpoint have an explicit lower assurance ceiling.
- New/recovered device chains do not inherit Hardened and must requalify.
- OAuth-only launch language is “one active ranked identity per detected/resolved person,” not verified unique humans.
- Presence is server-derived from signed collector activity and then projected per viewer/audience.
- The SLM is optional, abstaining and non-authoritative until benchmarked.
- Server deletion never directly authorizes local deletion.
- Adapter certification is digest-addressed and bound to provenance plus immutable conformance results.
- Ranking, snapshots, cursors, corrections and caches use a canonical `ranking_view_id`.
- Country is prospective ranking affiliation, frozen for a season; it is not a claim of nationality.

## User decisions required

1. **Identity claim:** Should public language promise a strongly enforced one-person policy, or do you want verified unique humans with materially stronger identity proofing and privacy trade-offs?
2. **Launch evidence:** Should global competition permit Standard claims at launch, or should the main public leaderboard require Hardened and leave Standard to separate boards?
3. **Offline competition:** Should unanchored offline activity be Standard-only, private-only, or excluded entirely from active competition?
4. **Country feature:** Keep self-declared, season-frozen ranking affiliation, or remove country leaderboards from launch?
5. **Social launch scope:** Must organizations, communities, private boards, presence, notifications and moderation all ship at first public launch, or can the public launch contract be narrowed?
6. **SLM:** Retain it as a post-launch research track, or remove it from launch architecture until deterministic controls have executable evidence?
7. **Protocol correction strategy:** Is a protocol-breaking VibeProof v1 rewrite acceptable now, before implementation, rather than preserving the current planning schema?

## Reopened planning program

The following dependency order replaces the claim that P-1104 is the only remaining planning gate:

1. **P-1140A — authority reset and launch-scope freeze.** Reconcile status, decisions, task catalog, open issues/PRs and user decisions.
2. **P-1140B — core trust and accounting contracts.** Freeze evidence/appraisal separation, accounting profiles, pricing rules, time anchors, device lineage and privacy boundaries.
3. **P-1140C — VibeProof v1 wire protocol.** Freeze COSE, CDDL, batch, continuity, checkpoint, rotation, numeric limits, provenance and conformance vectors.
4. **P-1140D — identity, API, ranking and social state machines.** Repair OAuth/session/idempotency, ranking views, moderation/corrections, presence and relationship governance.
5. **P-1140E — cross-contract validation.** Add planning-only negative fixtures and repository checks proving prose, schemas and registries agree. This does not enable product security/eval automation.

P-1104 remains blocked until P-1140A–E are complete and explicit user implementation approval is given.

## Highest-impact file map

The findings primarily require eventual changes to:

- `docs/project/STATUS.md`
- `docs/planning/DECISION_REGISTER.md`
- `docs/planning/TASK_CATALOG.md`
- `docs/security/THREAT_MODEL.md`
- `docs/security/INTEGRITY_MODEL.md`
- `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`
- `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
- `docs/privacy/PRIVACY_CONTRACT.md`
- `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
- `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
- `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
- `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
- `packages/schemas/vibeproof-claim-v1.cddl`
- `packages/schemas/normalized-event.schema.json`
- `packages/schemas/adapter-manifest.schema.json`
- `packages/schemas/local-control-v1.proto`
- `packages/schemas/openapi-v1.yaml`
- `packages/schemas/planning-schema.sql`
- `packages/schemas/reason-codes-v1.json`

## Primary references

- RFC 9700, OAuth 2.0 Security Best Current Practice.
- RFC 9052 and RFC 9053, COSE structures and algorithms.
- RFC 8949 and RFC 8610, CBOR and CDDL.
- RFC 8628, OAuth device authorization grant.
- RFC 9207, authorization-server issuer identification.
- RFC 9449, DPoP sender-constrained tokens.
- RFC 9334 and RFC 9711, RATS architecture and entity attestation token concepts.
- The Update Framework specification.
- SLSA provenance specification.
- OWASP API Security Top 10 and application logging guidance.
- Unicode UAX #31 and UTS #39.
- Official provider usage and pricing documentation for OpenAI, Anthropic and Google.

## Repository-state note

Issue #12 and open PR #17 correctly reopened part of the hardening surface, but PR #17 is documentation-only, non-mergeable in its current state and does not repair the machine contracts listed above. The recent merged work is primarily the bounded UI prototype and visual system. Neither is launch evidence for the backend, protocol, identity, ranking or native runtime.
