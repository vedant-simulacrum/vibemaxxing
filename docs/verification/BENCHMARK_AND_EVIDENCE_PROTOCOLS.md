# Benchmark and Evidence Protocols

Status: normative planning evidence
Updated: 2026-07-19

## Hardware classes

Test low, typical, and high desktop classes on supported macOS, Windows, and Linux versions. Record CPU, RAM, storage, power source, OS, architecture, agent, adapter, runtime, and dataset versions.

## Native budgets

- Idle daemon CPU: median below 0.5% on typical hardware.
- Active collection CPU: p95 below 3% excluding optional local analysis.
- Daemon RSS: target below 150 MiB; any platform exception requires evidence.
- Cold control-surface readiness: p95 below 2 seconds.
- Resume recovery: p95 below 5 seconds.
- Local durable write: p99 below 50 ms under normal load.
- Queue survives crash, sleep, network loss, disk pressure and retry without duplication.
- Battery test: no more than 3% additional drain over an eight-hour representative workload on supported laptops.

## Server and ranking budgets

- Claim acceptance p95 below 250 ms and p99 below 750 ms at approved launch load.
- Idempotent duplicate response p95 below 150 ms.
- Leaderboard reads p95 below 300 ms uncached and 150 ms cached.
- Presence propagation p95 below 10 seconds.
- Minute aggregate freshness below 90 seconds under normal load.
- Complete ledger rebuild must reproduce checksummed aggregates exactly.
- Duplicate storms, retries and failover must never increase scores.

## Privacy evidence

Seed unique canaries in prompts, responses, paths, repository names, tool payloads and credentials. Scan claims, IPC available to the networked process, logs, traces, metrics, crash reports and packets. Acceptance requires zero canary occurrence and zero unallowlisted free-text field.

## Adapter evidence

For every certified version: synthetic sessions, real consenting sessions transformed into safe fixtures, category reconciliation, retries, streaming, failures, nesting, version detection, upgrade breakage, unsupported mode, duplicate capture and privacy-negative tests.

## Integrity evidence

Measure false acceptance, false rejection, false quarantine, detection latency and appeal overturn rate by attack class and environment. Deterministic controls must be evaluated before statistical methods. SLM acceptance requires statistically material lift beyond simpler baselines within CPU, memory, battery and reproducibility budgets.

## UX evidence

Chromium, Firefox and WebKit; keyboard-only; screen reader; 200% zoom; reduced motion; high contrast; mobile widths; slow network; offline; empty/error/private/quarantined/deleted states. Core Web Vitals must remain within current good thresholds at launch test time.

## Operations evidence

Run backup restore, regional/service failover tabletop, migration rollback, key rotation, compromised-key response, TUF malicious metadata, interrupted installation, downgrade attempt, expired metadata and clean consumer verification.

## Reproducibility

Every result records commit, fixture, schema, policy, model, runtime, hardware and command version. Raw evidence is immutable; summaries reference hashes. A pass cannot rely on skipped tests, missing tools, `not_applicable` without owner, or manually edited artifacts.