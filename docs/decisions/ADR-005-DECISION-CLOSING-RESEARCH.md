# ADR-005: Decision-Closing Research and Beta Gates

## Status

Accepted.

## Decision

Further research must produce executable probes, fixtures, benchmarks, or adversarial demonstrations. Architecture-only research is insufficient.

The following gates are mandatory before competitive beta:

- Three independently exercised live adapters.
- A generated adapter capability registry.
- Cross-language canonical claim vectors.
- Parser and encoding differential tests.
- PostgreSQL scale benchmark with documented tie semantics.
- Platform IPC enforcement tests.
- Replay, duplicate-race, rollback, and state-cloning attack tests.
- Consumer-side release-chain verification.
- Telemetry canary leakage tests.

## Adapter policy

Each adapter declares:

- supported product and version range;
- operating systems;
- observation mechanism;
- token categories available;
- source authority;
- privacy fields observed locally;
- fields emitted to synchronization;
- evidence class;
- degradation behavior;
- last conformance date.

Support claims are generated from this registry.

## Rejected approach

A manually maintained list that says “supports all agents” is rejected. A product is supported only when its adapter probe and privacy tests pass.
