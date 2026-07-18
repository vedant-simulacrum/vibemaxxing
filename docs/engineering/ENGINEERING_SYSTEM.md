# Engineering System

This document defines the production engineering baseline for VibeMaxxing. It is a system of evidence, not a claim that the current repository is already production-ready.

## Required quality layers

1. **Fast PR checks** — formatting, linting, type checking, unit tests, schema validation and repository policy.
2. **Security checks** — secret scanning, dependency review, CodeQL, license policy, SBOM generation and container scanning when images exist.
3. **Protocol conformance** — canonical encoding, signature verification, replay protection, sequence handling, duplicate idempotency and cross-platform fixtures.
4. **Privacy evals** — fixed-schema enforcement, forbidden-field rejection, packet-capture assertions and process-boundary tests.
5. **Product evals** — aggregation determinism, ranking correctness, privacy controls and import exclusion.
6. **Frontend quality** — accessibility, state coverage, responsive layouts, browser matrix and visual regression.
7. **Release evidence** — changelog, signed provenance, SBOM, reproducible-build evidence, migration plan and rollback plan.
8. **Operational readiness** — SLOs, runbooks, dashboards, alerts, backup restoration and incident exercises.

## Branch protection contract

The `main` branch must require pull requests, at least one approving review, CODEOWNER review for sensitive paths, resolved review threads, linear history, signed commits where practical, and the following checks:

- `policy`
- `docs`
- `build-test`
- `protocol-conformance`
- `privacy-evals`
- `frontend-quality`
- `dependency-review`
- `codeql`

Checks may initially report `not-applicable` for components that do not yet exist, but they must never report success for a missing test that is required by the current milestone.

## Change risk classes

- **R0:** documentation or comments only.
- **R1:** isolated UI or tooling change with no protocol, privacy or persistence effect.
- **R2:** backend behavior, schema-compatible API changes, collector adapter changes.
- **R3:** privacy boundary, claim schema, cryptography, accounting, replay protection, authentication, authorization, infrastructure or data migration.

R3 changes require two reviewers, security-owner approval, updated threat model or ADR, dedicated negative tests and an explicit rollback plan.

## Definition of done

A change is done only when code, tests, documentation, telemetry, migration/rollback notes and relevant eval evidence are updated together. Passing unit tests alone is not sufficient.
