# VibeMaxxing

VibeMaxxing is a privacy-preserving competitive leaderboard and Steam-like social layer for AI-agent activity, built on the local-first VibeProof accounting and integrity protocol.

## Status

Technical planning is complete at validated contract level. The repository remains in planning mode; product implementation has not begun and requires explicit user approval under P-1104.

## Start here

1. [`AGENTS.md`](AGENTS.md) — canonical initialization and operating rules.
2. [`docs/project/PROJECT.md`](docs/project/PROJECT.md) — authoritative product, privacy and stack direction.
3. [`docs/project/STATUS.md`](docs/project/STATUS.md) — current readiness and allowed work.
4. [`docs/project/DOCUMENTATION.md`](docs/project/DOCUMENTATION.md) — canonical documentation and schema map.
5. Run `python3 scripts/repository/doctor.py` from a clean checkout.

The implementation handoff remains inactive until explicit user approval.

## Structure

- `docs/project/` — project authority, status and documentation map.
- `docs/planning/` — decisions, tasks, validation evidence and planning audits.
- `docs/product/`, `docs/architecture/`, `docs/security/`, `docs/privacy/` — normative behavioral contracts.
- `docs/decisions/` — accepted ADRs.
- `docs/implementation/` — future handoff, work units, current/target tree and issue-generation contract.
- `packages/schemas/` — validated planning-grade JSON Schema, CDDL, Protobuf, OpenAPI, SQL and policy artifacts.
- `conformance/` — schema-backed compatibility and adversarial planning registries.
- `scripts/repository/` — repository doctor, validators and deterministic generators.
- `crates/`, `apps/`, `packages/` — current seeds and approved future implementation areas; see `REPOSITORY_LAYOUT.md` before assuming a path exists.

## Core rules

- No prompt, transcript, code, path, repository name, tool content, credential, embedding, summary, classification or personal insight may reach VibeMaxxing servers.
- Token Burn is the default raw metric; Cash Burn is always explicitly estimated.
- Historical imports never enter active competition.
- Agent support requires exercised exact-version/mode/platform certification evidence.
- Public launch is comprehensive; staged internal delivery does not reduce scope.
- Planning artifacts are not implementation evidence.
