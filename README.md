# VibeMaxxing

**A public leaderboard for AI-agent usage that never sees your code.**

Developers burn tokens all day and have no shared way to see it. VibeMaxxing ranks that activity — a Steam-like social layer over how much you actually run Claude Code, Codex, Gemini CLI, and friends — while keeping every prompt, file path, and repository name on your own machine.

A local daemon watches your agent, counts tokens, signs the count on-device, and sends **only fixed-schema aggregates** to the server. No prompts. No transcripts. No filenames. No content-derived hashes. That boundary is the product.

- **Token Burn** — the ranked metric. Raw accepted tokens.
- **Estimated Cash Burn** — an API-equivalent price interpretation, always labeled estimated, never real spend.

---

## Status: authorized to build, nothing built

Gate `P-1104` is **open** as of 2026-08-05 — implementation is authorized. It was opened deliberately with its preconditions unmet: 13 P1 semantic findings remain open and tracked, and they are not waived. Authorization is a decision, not evidence. The record is `conformance/p1140f/gate-authorization-v1.json`, and `make doctor` derives phase from it rather than from prose.

What exists today:

| | |
|---|---|
| Specification | ~34,000 lines — JSON Schema, CDDL, OpenAPI, SQL, protobuf, contracts |
| Executable code | ~4,400 lines |
| Running product | **None.** A `GET /healthz`, a fixture-driven Storybook/Next.js prototype, a Rust CBOR codec, and Python planning validators |

There is no daemon, adapter, collector, OAuth, database, or API yet, and opening the gate did not change that. `docs/project/STATUS.md` is the authority on what is and is not implemented, and it is deliberately blunt about it.

**Be skeptical of green checks.** A passing validator here proves structural consistency, not security, privacy, conformance, or runtime behavior. That rule is written into `AGENTS.md` and it applies to this README too.

## Quick start

```bash
git clone https://github.com/vedant-simulacrum/vibemaxxing && cd vibemaxxing
make doctor          # repository invariants — should print PASS
make validate        # full planning validator suite (needs Python deps)
make plan            # regenerate the deterministic work-unit issue plan
```

`make help` lists every target. Nothing here builds or runs a product, because there isn't one yet.

## Where to start reading

**If you are an AI agent:** read [`AGENTS.md`](AGENTS.md) and stop there until you have. It is the sole entrypoint and it tells you what you may and may not do in the current phase. `CLAUDE.md` is a symlink to it.

**If you are a human:**

1. [`docs/project/PROJECT.md`](docs/project/PROJECT.md) — what the product is, and the architecture that follows from it
2. [`docs/project/STATUS.md`](docs/project/STATUS.md) — current phase, what is implemented, what is not
3. [`docs/project/DOCUMENTATION.md`](docs/project/DOCUMENTATION.md) — the single map of which document owns which decision
4. [`docs/planning/DECISION_REGISTER.md`](docs/planning/DECISION_REGISTER.md) — every decision D-001..D-078 and its status
5. [`docs/planning/TASK_CATALOG.md`](docs/planning/TASK_CATALOG.md) — gates, programs, and what blocks what

For the current blocking work, `conformance/p1140f/semantic-findings-v1.json` is the machine-readable truth; prose summarizes it and may not redefine it.

## Repository map

```
docs/
  project/        authority: what this is, where it stands, who owns what
  planning/       decisions, gates, scope freeze, artifact policy
  architecture/   VibeProof protocol, adapters, server, ranking, native runtime
  product/        product spec, token accounting, pricing, social contract
  security/       threat model, integrity model, anti-cheat, attestation
  privacy/        the privacy boundary — the invariant everything else serves
  decisions/      accepted ADRs
  integrations/   agent compatibility, adapter certification
  operations/     launch, SLOs, incident response, release verification
  implementation/ active plan and frozen backlog
  engineering/    engineering system, performance and power budgets
  verification/   acceptance gates, evaluation and benchmark protocol
  style-guide/    brand, UI foundations, component registry and rules
  research/       primary evidence waves — README.md is the only entrypoint
  history/        superseded reports, retained as evidence, NOT authority

packages/schemas/ the real contract surface — OpenAPI, SQL, CDDL, JSON Schema
conformance/      registries and fixtures; empty certifications are not evidence
crates/           Rust seeds (protocol core; other crates are placeholders)
apps/             Go API skeleton, Next.js web prototype
packages/ui/      design system and storyboards — fixture-driven
scripts/          read-only repository and planning validators
```

`docs/implementation/REPOSITORY_LAYOUT.md` distinguishes paths that exist from paths that are planned. Check it before assuming a directory is real.

## Binding rules

These are not aspirations. They constrain every change.

- **No prompt, transcript, code, diff, file path, repository name, tool content, credential, embedding, summary, classification, personal insight, or content-derived hash may reach VibeMaxxing servers.** Only fixed-schema aggregates cross the device boundary.
- Public evidence status is assigned by the server verifier, never selected by the client.
- Historical imports never enter active competition.
- Authentic but intentionally pointless activity counts, when it is not duplicated.
- OAuth proves control of a provider account, not that you are one unique human.
- Deterministic controls are authoritative. Statistical and model-based detection is local-only, advisory, and post-launch — it cannot rewrite totals or ban anyone.
- Competitive support requires exercised certification evidence against an exact version, mode, platform, and artifact. A registry entry is not support.
- **Claims of verification, cryptographic proof, or cheat-proofing are forbidden unless a provider mechanism actually supports them** — and none does today. No score here is proof of real usage; someone who controls their own machine can inflate their own number. See `docs/security/THREAT_MODEL.md` and `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`.
- Specifications, mocks, fixtures, and runnable prototypes are not implementation evidence and are not launch evidence.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). Commits require a DCO `Signed-off-by`. Changes to protocol, privacy, security, accounting, identity, release, or governance need review from the code owner.

Security issues: see [`SECURITY.md`](SECURITY.md). Please do not include real prompts, keys, or user data in a report.

## License

Code is Apache-2.0 ([`LICENSE`](LICENSE)). Documentation is CC BY 4.0. See [`LICENSES.md`](LICENSES.md) and `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` for the full contribution and licensing model. Hosted components are not source-licensed.
