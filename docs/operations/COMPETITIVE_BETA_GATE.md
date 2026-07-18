# Competitive Beta Gate

The gate is machine-generated from evidence artifacts. Documentation cannot satisfy it.

## Mandatory pass evidence

- three certified production adapter reports;
- accounting conformance across all certified adapters;
- privacy canary scan across claims, telemetry, logs, crash artifacts, and profiles;
- replay, duplicate-race, state-cloning, clock-rollback, and cross-adapter double-count tests;
- collector performance results on macOS, Windows, and Linux;
- PostgreSQL ranking benchmark and ledger rebuild;
- onboarding study meeting time and comprehension thresholds;
- Cash Burn pricing provenance verification;
- release consumer-verification test;
- deletion and backup-restore exercise;
- incident and moderation tabletop exercise.

## Output

`artifacts/evals/competitive-beta-go-no-go.json`

Status is `pass` only when every mandatory artifact exists, has schema version, has `status: pass`, is within freshness policy, and is tied to the current commit or an explicitly accepted immutable release candidate.
