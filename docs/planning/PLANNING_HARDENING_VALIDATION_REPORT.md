# Historical Planning Hardening Validation Report

Status: historical evidence; superseded as current authority
Original date: 2026-07-19
Reclassified: 2026-07-23

## Authority warning

This document records a successful validation run against an older planning state. It does **not** describe the current repository phase and must not be used as an implementation entrance signal.

The July 23 cross-contract audit superseded its former conclusions:

- D-045 is superseded by D-049;
- D-046 is provisional rather than an accepted launch gate;
- P-1140B is active and P-1140C through P-1140E remain blocked in dependency order;
- P-1104 is not the only remaining gate;
- country leaderboards are post-launch under D-052;
- implementation remains unauthorized.

## Historical clean-checkout evidence

The older `Planning checks` workflow passed in a fresh GitHub-hosted checkout:

- run ID: `29666765188`;
- run number: `21`;
- validation head: `093aab79c64582507e9c2a1f95b8e819b91231df`;
- base main commit: `5c51c6da43d03ce12c2b067cf64d63e2c5d420ce`;
- result: success;
- trigger PR: #10, closed unmerged.

That run demonstrated that the then-current documents and placeholders were syntactically parseable and internally linked. It did not prove their future correctness.

## Historical checks

The run covered:

- repository paths and references;
- JSON Schema fixtures and registries;
- CDDL parsing;
- Protobuf compilation;
- OpenAPI syntax and operation coverage;
- structural PostgreSQL loading;
- policy and observability consistency;
- the former numbered issue-plan generator;
- the former phase assertions.

Several of those assumptions were later invalidated. In particular, the fixed `IMP-001` through `IMP-052` plan, country launch coverage and the D-045 planning-complete state are obsolete.

## Current replacement

Current structural validation is owned by:

- `scripts/repository/doctor.py`;
- `scripts/repository/validate_planning_artifacts.py`;
- `scripts/repository/validate_planning_coverage.py`;
- `scripts/repository/validate_t20_contract.py`;
- `scripts/repository/generate_issue_plan.py`;
- `.github/workflows/planning-checks.yml`.

Those checks validate the current repair phase, D-001 through D-069 traceability, D-052 country removal, provisional D-046 status, stable work-unit IDs and blocked-placeholder maturity.

## Evidence boundary

Historical success is not current success. A new clean-checkout run is required after the repaired validators land. Even a passing current run proves only structural planning consistency—not runtime correctness, cryptographic interoperability, source compatibility, packaging, deployment, security hardening or launch readiness.
