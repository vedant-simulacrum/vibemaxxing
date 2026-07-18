# ADR-001: Local-first development

- Status: accepted
- Date: 2026-07-18

## Context

A previous attempt to make a remote development machine own orchestration, model routing, secrets, project context, and implementation failed and introduced unnecessary complexity.

## Decision

Develop VibeMaxxing locally in the repository. Do not make remote infrastructure a prerequisite for coding, model routing, agent orchestration, secrets management, or context preservation.

Use ordinary local Git workflows, local tooling, and hosted CI for public pull requests. Introduce production cloud resources only when required by the product and through explicit infrastructure decisions.

## Consequences

- The repository remains directly understandable and runnable.
- Development does not depend on a remote control plane.
- Model and agent tooling can be changed without rebuilding infrastructure.
- Project context should be versioned in safe repository documents and backed up through normal source-control and local backup practices.
- Obsolete remote-bootstrap archives must not be treated as current instructions.
