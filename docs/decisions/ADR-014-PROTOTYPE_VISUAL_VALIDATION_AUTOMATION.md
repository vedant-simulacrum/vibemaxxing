# ADR-014: Prototype visual-validation automation

Status: accepted
Date: 2026-07-23
Decision: D-069, D-635

**The subject of this ADR no longer exists.** D-635 deleted `packages/ui` and the component half of `docs/style-guide/`, so there is no Storybook prototype to validate and no locked reference to drift against. The decision below is not reversed and is not rewritten: it classifies what this kind of automation may and may not be taken for, and that classification is what a replacement would be read against. The automation it permits is dormant until a replacement component system exists. Nothing here authorizes rebuilding the workflow ahead of one, and this ADR is superseded rather than reversed when a replacement declares its own normative owner.

## Context

The repository contains a Storybook-based UI prototype, governed assets, and a GitHub Actions workflow that installs UI dependencies, runs prototype tests, builds Storybook, captures fixed-viewport screenshots and uploads them as review artifacts. Decision D-034 otherwise keeps product build, dependency, security, evaluation, release and deployment automation disabled during planning.

Without an explicit classification, the workflow could be mistaken for product CI or implementation evidence.

## Decision

Automated Storybook visual validation is allowed during planning solely as prototype/design-system validation.

It is not product CI, production build evidence, launch evidence, security evidence, accessibility completion, backend integration evidence, deployment automation or authorization to expand implementation.

## Allowed scope

The workflow may:

- run only for changes to `packages/ui`, governed assets, UI-specific scripts, style-guide documents and the workflow itself;
- install dependencies from the UI lockfile;
- run deterministic UI/design-system checks;
- build static Storybook output;
- render synthetic fixtures only;
- capture locked screenshots for review;
- upload short-lived review artifacts;
- use read-only repository permissions;
- run without production credentials, network services or customer data.

## Prohibited scope

The workflow may not:

- build or test the daemon, collector, sync process, protocol, adapters, server, database or installers;
- deploy preview or production environments;
- sign releases or update metadata;
- access secrets beyond platform-provided read-only tokens;
- call production APIs;
- ingest real user data;
- run security, anti-cheat or model evaluations;
- claim implementation or launch readiness;
- become a required product release gate before P-1104 opens implementation.

## Workflow requirements

- Trigger only on pull requests affecting the allowed paths and optionally manual dispatch.
- Do not trigger general product builds on pushes to `main` or arbitrary branches during planning.
- Pin third-party actions and runtime/tool versions through the lockfile or immutable references where practicable.
- Use synthetic fixtures and an isolated local Storybook server.
- Retain artifacts for no longer than 30 days.
- Label artifacts as prototype visual-review evidence.
- Fail when governed assets, UI contracts or locked references drift.

## Evidence classification

Outputs are `runnable prototype` and `design review` artifacts under D-047. They may support visual decisions such as D-048, but cannot satisfy implementation, security, cross-platform, accessibility or launch gates unless later implementation-phase workflows independently prove those claims.

## Consequences

- The existing Storybook workflow is permitted after it is narrowed to this contract.
- D-034 remains intact for all product automation.
- Future product CI requires P-1104 implementation authorization and restoration under P-1007.
