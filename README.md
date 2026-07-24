# VibeMaxxing

VibeMaxxing is a privacy-preserving competitive leaderboard and Steam-like social layer for AI-agent activity, built around local-first accounting and the planned VibeProof integrity protocol.

## Status

The repository is in **planning alignment and contract repair**.

A July 23 audit found contradictions between earlier “planning complete” declarations, newer product decisions, privacy requirements, anti-cheat research, draft schemas and the implementation handoff. Product implementation has not begun and remains blocked by P-1140F plus explicit approval under P-1104.

One fixture-backed hosted-web/Storybook slice exists as a runnable prototype. It is not a production frontend, backend integration, protocol implementation, launch evidence or authorization to continue implementation.

Current planning conclusions:

- local-model and delayed offline usage can count competitively when deterministically captured by a certified source profile;
- Standard and Hardened claims can both contribute to public leaderboards;
- Imported history never enters competition;
- the server verifier, not the client, awards public evidence status;
- prompts, outputs, code, paths, repositories, tool contents and raw logs never reach VibeMaxxing servers;
- country leaderboards are post-launch;
- the SLM detector is post-launch research and is not a launch dependency;
- current protocol and event schemas are planning placeholders until P-1140F repairs and validates their remaining semantic findings.

## Start here

1. [`AGENTS.md`](AGENTS.md) — sole initialization and operating manual.
2. [`docs/project/PROJECT.md`](docs/project/PROJECT.md) — product and architectural authority.
3. [`docs/project/STATUS.md`](docs/project/STATUS.md) — current phase, readiness and allowed work.
4. [`docs/project/DOCUMENTATION.md`](docs/project/DOCUMENTATION.md) — canonical documentation and schema ownership map.
5. [`docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`](docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md) — current cross-repository reconciliation.
6. [`docs/planning/DECISION_REGISTER.md`](docs/planning/DECISION_REGISTER.md) and [`TASK_CATALOG.md`](docs/planning/TASK_CATALOG.md).
7. Run `python3 scripts/repository/doctor.py` from a clean checkout.

## Structure

- `docs/project/` — project authority, status and documentation map.
- `docs/planning/` — decisions, tasks, audits, alignment and planning validation.
- `docs/research/` — evidence inputs; research does not override accepted decisions.
- `docs/product/`, `docs/architecture/`, `docs/security/`, `docs/privacy/` — normative contracts being reconciled under P-1140.
- `docs/integrations/` — universal compatibility, certification and T20 planning contracts.
- `docs/decisions/` — accepted ADRs.
- `docs/implementation/` — inactive implementation handoff and dependency-ordered work breakdown.
- `packages/schemas/` — planning-grade schemas; not production-proven and blocked where marked inconsistent.
- `conformance/` — planning registries and fixtures; empty or planned certifications are not support evidence.
- `scripts/repository/` — read-only repository and planning validators.
- `apps/web/` — bounded fixture-backed prototype.
- `crates/`, `apps/`, `packages/` — current seeds and approved future implementation areas; see `docs/implementation/REPOSITORY_LAYOUT.md` before assuming a path exists.

## Core rules

- No prompt, transcript, code, path, repository name, tool content, credential, embedding, summary, classification or personal insight may reach VibeMaxxing servers.
- Token Burn is the default raw metric; Estimated Cash Burn is always explicitly estimated.
- Historical imports never enter active competition.
- Competitive support requires exercised exact-version, mode, platform and artifact certification evidence.
- OAuth account control is not proof of one unique human.
- Deterministic controls own accounting, signatures, replay, duplicates, continuity and hard eligibility.
- Models and statistical detectors are secondary signals and cannot independently rewrite totals or permanently ban users.
- Internal delivery may be staged, but public launch targets the complete core social product except country leaderboards.
- Specifications, mocks, fixtures and runnable prototypes are not implementation or launch evidence.
