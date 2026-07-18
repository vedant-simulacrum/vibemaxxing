# PR-Sized Implementation Work Breakdown

Status: normative implementation planning
Updated: 2026-07-19

Each item must be independently reviewable, tested, reversible where possible, and linked to the owning contract.

## Foundation

1. Pin Rust, Go, Node and package-manager toolchains; add clean-checkout verification.
2. Add schema workspaces for CDDL, OpenAPI, Protobuf, JSON Schema and SQL migrations.
3. Add generated-code reproducibility and breaking-change checks.
4. Add privacy-canary fixture framework and deny-by-default telemetry allowlist.

## VibeProof and accounting

5. Implement normalized event types and accounting-policy versioning.
6. Implement deterministic Token Burn reconciliation and golden vectors.
7. Implement claim model, canonical CBOR encoder and CDDL validation.
8. Implement COSE signing/verifying with Ed25519 and protected-header enforcement.
9. Implement challenge, sequence, expiry, previous-hash and correction state machines.
10. Add malformed, resource-limit, fuzz and cross-language verifier suites.

## Native runtime

11. Implement encrypted local schema and migrations.
12. Implement collector/sync process separation.
13. Implement bounded authenticated IPC and version negotiation.
14. Implement durable queue, acknowledgement, crash recovery and disk-full behavior.
15. Implement device enrollment, key rotation, revocation and clone/fork handling.
16. Implement CLI install/status/pause/resume/export/delete/diagnose commands.
17. Implement macOS menu bar and Windows/Linux tray control shells.
18. Implement signed packaging, autostart, atomic updater and uninstall verification.

## Adapter system

19. Implement adapter manifest validator and registry loader.
20. Implement normalized adapter SDK and source precedence engine.
21. Implement generic ACP/OTel/proxy/wrapper adapters.
22. Implement initial certified major-agent adapters selected from the registry.
23. Add version probes, privacy-negative tests, upgrade-break tests and compatibility publication.

## Identity and server

24. Implement GitHub App authorization and native device flow.
25. Implement X OAuth 2.0 PKCE and linked-identity state machine.
26. Implement sessions, optional passkeys, recovery, merge and provider-loss flows.
27. Implement PostgreSQL identity/device/challenge schema.
28. Implement claim ingestion transaction, uniqueness, sequence head and rejected-summary handling.
29. Implement transactional outbox and aggregation worker.
30. Implement period rollover, corrections and deterministic rebuild.
31. Implement leaderboard queries, keyset pagination, current-user rank and evidence filters.

## Product and social

32. Implement profiles, usernames, privacy defaults and blocks.
33. Implement friends, rivals, movement and overtake events.
34. Implement boards, organizations, communities and permission matrix.
35. Implement country cohorts and privacy thresholds.
36. Implement presence leases and multi-device behavior.
37. Implement notification grouping, hysteresis, quiet hours and delivery preferences.
38. Implement moderation cases, reversible actions, appeals and restoration.
39. Implement export, deletion and aggregate correction workflows.

## Web and native UX

40. Implement onboarding and native pairing.
41. Implement global/friends/group/country leaderboards.
42. Implement profile/activity/agent/cash views.
43. Implement social, board and notification surfaces.
44. Implement device, adapter, privacy, export and deletion settings.
45. Implement moderation and appeal surfaces.
46. Complete accessibility, responsive, offline and all exceptional states.

## Operations and launch

47. Implement deployment environments, secrets, migrations and promotion.
48. Implement observability allowlist, canary blocking and incident dashboards.
49. Implement backup/restore, DR, rollback and key-compromise automation.
50. Restore CI, security, dependency, eval, provenance and consumer verification gates.
51. Run independent security/privacy review and red-team campaign.
52. Run complete launch gate and publish open-source repository.

## PR acceptance contract

Every PR names decisions and contracts, lists privacy/security impact, contains tests and migrations, documents rollback, updates generated artifacts reproducibly, and provides evidence. Placeholder-only PRs do not close work.