# Independent Architecture Reviews

Status: planning review record
Updated: 2026-07-19

These reviews use separate failure-oriented lenses. They do not replace implementation evidence or external professional review where required.

## Privacy review

Pass with conditions. The split collector/sync boundary and fixed-schema claims are sound. Launch blockers: prove OS enforcement per platform, canary every telemetry path, and ensure crash reporting cannot serialize arbitrary local state.

## Cryptography and protocol review

Pass with conditions. Canonical CBOR/CDDL, COSE, Ed25519 device keys, protected headers, challenges, sequences and chaining form a coherent profile. Implementation must use audited libraries, exact-byte vectors, parser limits, algorithm-confusion tests and key-rotation drills. No custom cryptographic primitive is permitted.

## Database and distributed-systems review

Pass with conditions. Append-only accepted claims, uniqueness constraints, transactional outbox, idempotent workers and deterministic rebuild are appropriate. Launch blockers: benchmark partitioning, rollover, correction, rebuild, duplicate storms, failover and cache invalidation.

## Native desktop security review

Pass with conditions. Separate processes, OS peer identity, ACLs, challenge-response and bounded IPC are appropriate. Hardened status cannot be universal. Each OS needs an explicit capability matrix, signing path, autostart behavior, updater recovery and uninstall verification.

## Anti-cheat and red-team review

Pass as an honest risk-reduction design, not cheat-proofing. Deterministic controls correctly precede models. Launch blockers: executable campaign coverage, calibrated policy budgets, clone/fork handling, insider controls, appeal restoration and independent red-team testing.

## Product and social-system review

Pass with conditions. Token Burn and Steam-like competition are coherent. The system must prevent harassment through blocks, notification controls, discoverability defaults, private-board permissions and country cohort thresholds. Wasteful authentic use remains valid by product policy.

## Accessibility and design review

Pass with conditions. Competitive Ledger direction is distinctive and avoids generic dashboard aesthetics. All status must be non-color-only; tables require keyboard and screen-reader semantics; mobile layouts must preserve rank context; motion must be optional.

## Operations and incident review

Pass with conditions. Managed runtime plus PostgreSQL is a reasonable launch baseline. Launch blockers: restore evidence, RPO/RTO validation, key-compromise exercise, provider outage behavior, incident communication and privacy-safe observability.

## Open-source and supply-chain review

Pass with conditions. Apache-2.0 plus DCO is the planned default. Public release requires contributor governance, trademark policy, private security-advisory process, signing-key separation, reproducible release evidence and clear community-adapter trust labels.

## Consolidated result

No architecture-level contradiction blocks implementation. All conditions map to committed implementation or launch evidence. Future external reviewers may reopen decisions with concrete evidence, but no subsystem requires an unplanned architecture invention.