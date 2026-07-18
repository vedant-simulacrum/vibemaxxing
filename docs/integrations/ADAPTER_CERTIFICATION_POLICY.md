# Adapter Certification Policy

An adapter is not publicly supported until every mandatory artifact exists.

## Required manifest

- adapter ID and display name
- agent vendor and product
- exact tested versions and modes
- supported operating systems and architectures
- observation surface
- token source and source precedence
- evidence class
- privacy field allowlist
- explicit forbidden-field list
- deduplication identity strategy
- upgrade detection strategy
- failure/degradation behavior
- last conformance timestamp
- maintainer and review owner

## Required executable evidence

- installation/version probe
- synthetic qualifying session
- authoritative/structured token reconciliation
- cache/reasoning/retry fixtures where supported
- no-content negative tests
- duplicate observation test
- crash and restart test
- unsupported-version behavior
- upgrade fixture from at least one prior version
- performance overhead result

## Certification states

- `experimental`: implementation exists but evidence is incomplete; never active competitive default.
- `standard`: live deterministic evidence passes privacy, accounting, upgrade, and duplicate tests.
- `hardened`: standard plus documented OS-native isolation and stronger source binding.
- `imported`: retrospective analytics only.
- `suspended`: previously supported version no longer passes or cannot be reproduced.

## Fail-safe degradation

An adapter must stop competitive submission or downgrade explicitly when its parser, telemetry contract, version, or evidence surface changes. It must never continue with zeroed categories, guessed totals, or inflated evidence labels.
