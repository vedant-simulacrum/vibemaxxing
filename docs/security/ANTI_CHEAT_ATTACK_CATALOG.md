# VibeMaxxing Anti-Cheat Attack and Control Catalog

Updated: 2026-07-19
Status: planning control matrix

This catalog defines attack classes, primary deterministic controls, policy outcomes, residual risks, and required validation. Detailed fixtures live in `conformance/adversarial/anti-cheat-cases.json`.

## Policy actions

- `accept`
- `accept_idempotently`
- `downgrade_standard`
- `exclude_claim`
- `quarantine_session`
- `quarantine_score`
- `require_stronger_evidence`
- `human_review`
- `revoke_device`
- `restrict_ranking`
- `restore_after_appeal`

An SLM or heuristic may recommend only downgrade, quarantine, stronger evidence, or review. It may not rewrite totals or permanently ban by itself.

## Attack/control matrix

| ID | Attack | Primary controls | Default outcome | Residual risk and required validation |
|---|---|---|---|---|
| AC-A-001 | Edit token fields in mutable source records | live observation, source conformance, deterministic normalization, signed claim | exclude or Imported | privileged source tampering remains; mutation fixtures |
| AC-A-002 | Fully fabricate source events | source/process binding, version probes, challenge timing, continuity | quarantine | sophisticated emulation remains; synthetic-generator campaign |
| AC-A-003 | Replay valid claim | nonce/challenge, sequence, claim ID, uniqueness | accept idempotently or reject replay | distributed race; concurrent replay tests |
| AC-A-004 | Concurrent duplicate submission | unique constraints, serializable acceptance boundary, idempotency key | one accept, rest idempotent | transaction bugs; duplicate storm test |
| AC-A-005 | Copy claim/session from another account | account/device binding, signatures, subject binding | reject and review | stolen key remains; cross-account fixture |
| AC-A-006 | Host/guest/nested-agent double counting | provenance graph, parent/child IDs, source precedence | exclude duplicate branch | incomplete parent metadata; nested-agent matrix |
| AC-A-007 | Backdate into prior period | server challenge time, bounded skew, receipt time, late-event policy | exclude or late-policy | offline legitimate activity; period-boundary simulation |
| AC-A-008 | Future timestamp or clock rollback | monotonic sequence, server time, clock-state tracking | downgrade/quarantine | sleep/resume drift; platform clock tests |
| AC-A-009 | Sequence rollback | durable sequence state, server high-water mark | reject/quarantine | state loss; crash/restore campaigns |
| AC-A-010 | Claim-chain truncation or fork | previous-claim commitment, fork detection | quarantine device chain | deliberate permanent offline fork; recovery protocol tests |
| AC-A-011 | Clone device state to second machine | non-exportable keys where available, server branch detection, device continuity | quarantine/revoke | platforms without hardware binding; clone lab |
| AC-A-012 | VM/filesystem snapshot restore | server high-water state, challenge freshness, anti-rollback state | reject/quarantine | offline queue rollback; snapshot campaigns |
| AC-A-013 | Modified collector/verifier | signed builds, measured version, updater integrity, process evidence | downgrade/restrict | root user can patch runtime; signed/unsigned matrix |
| AC-A-014 | Modified adapter emits forged normalized events | adapter signing/provenance, conformance probes, source binding | suspend adapter/quarantine | malicious community maintainer; supply-chain tests |
| AC-A-015 | Source/model/version impersonation | source-specific probes, model enum provenance, registry allowlist | downgrade/exclude | closed tools may expose weak identity; version fixtures |
| AC-A-016 | Unsupported version presented as supported | exact version detection, capability probe expiry | fail closed/downgrade | version spoofing; upgrade matrix |
| AC-A-017 | Adapter downgrade to weaker capture path | strongest-source selection, downgrade reason, continuity break | Standard or exclude | attacker disables stronger path; downgrade campaign |
| AC-A-018 | Mixed-version downgrade | per-event adapter/source version, session invariant | split/downgrade session | legitimate upgrade mid-session; transition tests |
| AC-A-019 | Build signature/update metadata substitution | TUF, threshold signatures, expiry, rollback/freeze defense | block update/restrict | signing-key compromise; malicious metadata suite |
| AC-A-020 | Device-key theft and reuse | secure storage, rotation, revocation, anomaly checks | revoke/review | malware with user access; key-theft simulation |
| AC-A-021 | OAuth account takeover | provider reauth, optional strong factor, session/device review | restrict account changes | provider compromise remains; recovery tabletop |
| AC-A-022 | Sybil account farming | rate limits, provider/account age signals, graph analysis, board rules | restrict/review | privacy-preserving uniqueness is limited; Sybil simulation |
| AC-A-023 | Colluding accounts manipulate boards/rank movement | graph/cohort analysis, board audit, notification hysteresis | quarantine/review | legitimate teams resemble collusion; cohort tests |
| AC-A-024 | Board owner/admin collusion | immutable admin audit, separation of score computation, appeals | revoke admin/review | social governance abuse; insider scenarios |
| AC-A-025 | Synthetic event generator mimics sessions | source-bound evidence, sequence invariants, statistical/SLM residual checks | quarantine | high-quality emulation; red-team generator tournament |
| AC-A-026 | Repeated fingerprints across accounts/devices | privacy-safe fingerprints, graph analysis | review/quarantine | common automation templates; false-positive calibration |
| AC-A-027 | Partial event suppression | continuity markers, expected lifecycle invariants | downgrade/quarantine | source may omit legitimately; omission fixtures |
| AC-A-028 | Observation-gap induction | continuity heartbeats, gap state, Hardened eligibility rules | break Hardened continuity | OS suspension and upgrades; gap simulations |
| AC-A-029 | Ingestion uniqueness race | transaction boundary, unique constraints, idempotent response | one accept | database failover edge cases; race benchmark |
| AC-A-030 | Outbox/worker replay | outbox IDs, processed-event ledger, idempotent aggregate deltas | idempotent | operator repair mistakes; replay/rebuild tests |
| AC-A-031 | Aggregate or rebuild divergence | append-only claims, deterministic rebuild, reconciliation hashes | halt publication/rebuild | nondeterministic code; differential rebuild test |
| AC-A-032 | Pricing dataset substitution | signed/versioned dataset, provenance, effective date | reject estimate version | compromised publisher; substitution vectors |
| AC-A-033 | Local gateway/proxy forges provider/model | gateway identity tier, provider evidence separation | Generic/Standard only | gateways can fabricate labels; gateway conformance |
| AC-A-034 | Local inference server forges usage | deterministic local tokenizer where possible, server provenance | lower evidence | tokenizer mismatch; cross-tokenizer research |
| AC-A-035 | Presence farming without qualifying activity | live qualifying-session state, expiry, source heartbeat | expire/quarantine | low-rate fake heartbeats; presence abuse test |
| AC-A-036 | Notification/overtake manipulation | derived events from canonical ranks, hysteresis, deduplication | suppress/repair | correction churn; timeline simulations |
| AC-A-037 | Country-board manipulation | change limits, coarse evidence, cohort thresholds | hide/review | country proof remains weak; privacy/abuse study |
| AC-A-038 | SLM prompt injection | bounded structural input, no tools/network, constrained output | ignore model signal/review | model still misclassifies; adversarial corpus |
| AC-A-039 | SLM/model/runtime substitution | signed assets, pinned runtime, measured versions | disable detector/downgrade | local root substitution; asset-tamper tests |
| AC-A-040 | Detector evasion/low-and-slow manipulation | multi-window rules, graph analysis, red-team updates | review | adaptive attackers; longitudinal benchmark |
| AC-A-041 | Detector/cohort poisoning | robust baselines, trusted calibration sets, holdouts | disable/recalibrate | subtle poisoning; poisoning experiments |
| AC-A-042 | Oversized/pathological local input | strict parser/resource limits, timeouts, streaming bounds | reject input/degrade | platform DoS; fuzz/resource suite |
| AC-A-043 | Privacy exfiltration disguised as integrity | fixed schema, no-network analyzer, allowlists, canaries | block release | accidental fields; continuous privacy-negative tests |
| AC-A-044 | Moderator/insider abuse | least privilege, dual control, append-only audit, appeals | revoke/review/restore | colluding insiders; audit tabletop |
| AC-A-045 | Appeal spam or evidence fabrication | rate limits, signed case records, bounded evidence | restrict appeal channel | denial of service; workflow load test |
| AC-A-046 | Adapter maintainer compromise | signed commits/releases, review, emergency disable, reproducible builds | suspend adapter | upstream compromise; supply-chain exercise |
| AC-A-047 | Conformance-fixture gaming | hidden/private holdouts, mutation generation, independent review | withhold certification | overfitting remains; rotating test corpus |
| AC-A-048 | WSL/container/CI duplicate identity | host/guest provenance, environment IDs, parent relation | exclude duplicate | unusual topology; environment matrix |
| AC-A-049 | Remote development environment duplication | source/session ownership and device/environment mapping | split or exclude | cloud workspace cloning; remote-env tests |
| AC-A-050 | Deletion/recreation to evade restrictions | tombstoned abuse keys with privacy limits, provider/device linkage policy | retain restriction/review | privacy and legal limits; lifecycle review |

## Evidence-tier qualification

Hardened eligibility requires live capture, supported exact version, official or approved signed adapter/build, uninterrupted continuity, source recognition, protocol conformance, and platform hardening where available. Any observation gap, unsupported version, modified component, rollback, or unresolved fork breaks Hardened continuity.

Standard eligibility requires live supported capture, deterministic accounting, valid signatures, sequence/replay/duplicate checks, and privacy-negative conformance. Imported data never ranks.

## Appeals

Every exclusion, downgrade, quarantine, restriction, or revocation requires a stable reason code, safe user explanation, retained privacy-safe evidence, review authority, appeal window, restoration semantics, and audit trail. Restoration must correct derived ranks and notifications deterministically.

## Completion and validation

No launch-blocking attack is resolved by prose. Each requires fixtures or attack procedures, measurable success criteria, false-positive analysis, residual-risk acceptance, and named ownership. Active thresholds, exploit fingerprints, and unpublished incident details remain outside public Git.
