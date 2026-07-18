# Collector Performance and Power Research Contract

## Representative matrix

- Apple Silicon macOS: current and previous major OS.
- Intel macOS where still supported.
- Windows 11 x86-64.
- Windows on Arm where supported.
- Ubuntu LTS x86-64.
- Linux Arm64 where supported.
- Low-resource environment: 2 cores / 4 GiB.

## Workloads

- installed but idle
- supported agent absent
- agent open but inactive
- light interactive session
- long high-token session
- parallel agents
- rapid process restarts
- offline network
- sync backlog
- suspicious-session challenge verification
- optional local semantic analysis

## Required measures

- idle and active CPU
- RSS and peak memory
- wakeups/timers
- disk writes and database growth
- network bytes
- startup and shutdown latency
- event throughput
- p50/p95/p99 normalization latency
- claim size
- dropped events
- battery/energy impact
- thermal behavior

## Measurement principles

- record hardware, OS, power mode, compiler, build, and background load;
- separate measurement-tool overhead from collector overhead;
- use repeated runs and report distributions, not one number;
- compare against an agent-only baseline;
- test on battery and AC where applicable;
- expensive semantic verification is not continuously enabled by default.

## Initial blocking budgets

- idle CPU p95 <= 0.5% of one core;
- idle RSS p95 <= 80 MiB;
- no periodic wakeup faster than required by an active adapter;
- startup p95 <= 500 ms on supported modern hardware;
- deterministic normalization p99 <= 10 ms per event;
- zero dropped qualifying events at the supported throughput target;
- no unbounded local database or log growth;
- no measurable battery regression above the approved study threshold during idle use.

Budgets must be recalibrated from evidence; changes require an ADR and before/after results.
