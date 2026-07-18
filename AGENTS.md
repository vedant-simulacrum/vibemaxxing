# Public Repository Agent Instructions

These instructions apply to humans and coding agents working in the public VibeMaxxing repository.

## Mission

Build a privacy-preserving, cross-platform, open-source AI-agent activity protocol and social leaderboard without compromising the local/server trust boundary.

## Non-negotiable privacy boundary

VibeMaxxing servers must never receive prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project names, credentials, embeddings, summaries, classifications, or personal insights.

Only fixed-schema safe claims may cross the network boundary. Any change to that schema requires protocol, privacy, and security review.

## Repository independence

The repository must build and test independently. Do not introduce dependencies on hidden context, private infrastructure, unpublished credentials, or proprietary task logs.

## Engineering rules

- Read the nearest `AGENTS.md` before modifying a subtree.
- Keep changes atomic and reviewable.
- Add or update tests with behavior changes.
- Use deterministic accounting for exact totals, deduplication, replay prevention, and sequence checks.
- Local semantic models may classify structural authenticity locally but must not transmit content or decide numerical accounting.
- Historical imports never enter active competitive rankings.
- Public UI uses `Standard`, `Hardened`, and `Imported`; avoid consumer-facing claims of absolute verification.
- Do not add generic dashboard UI. Follow `docs/design/design.md`.
- Avoid platform assumptions; support macOS, Windows, Linux, WSL, containers, local workspaces, and CI through capability-specific adapters.

## Pull-request requirements

A pull request must include:

- problem and scope;
- security/privacy impact;
- tests and evidence;
- screenshots for UI changes;
- protocol compatibility impact;
- migration or rollback notes when applicable.

Untrusted public pull-request code must run only on GitHub-hosted disposable runners without Azure secrets or private-network access.

## Current development constraint

Development is local-first. Do not configure or propose a remote development control plane, autonomous remote setup, remote model router, persistent remote worker fleet, or remote project-context source of truth.

## Mandatory engineering evidence

Before marking work complete, identify its risk class and run the relevant CI and eval suites. Changes to privacy boundaries, schemas, signatures, accounting, replay handling, authentication, authorization or migrations are R3 and require independent review, negative tests, updated threat-model/ADR material and rollback notes.
