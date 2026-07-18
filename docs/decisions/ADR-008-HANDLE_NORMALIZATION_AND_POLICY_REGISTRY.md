# ADR-008: Handle Normalization and Policy Registry

Status: accepted
Date: 2026-07-19

## Handle normalization

VibeMaxxing handles use Unicode 16.0 data and the following deterministic pipeline:

1. Reject control, format, private-use, unassigned, separator, emoji, combining-only, and default-ignorable code points.
2. Apply NFKC normalization.
3. Apply full Unicode case folding for uniqueness.
4. Permit only letters, decimal numbers, underscore, and hyphen in the normalized display handle.
5. Require 3-30 Unicode scalar values after normalization.
6. Reject mixed-script handles except Common and Inherited characters combined with one primary script.
7. Generate a Unicode confusable skeleton and reject collisions with existing, reserved, protected-brand, or recently released handles.
8. Preserve the approved normalized display form; uniqueness uses the case-folded form and confusable skeleton.

A Unicode-data upgrade is a versioned identity migration. Existing handles are not silently renamed. New collisions enter administrator review, with existing ownership preserved unless abuse or impersonation is established.

## Policy registry

`packages/schemas/policy-defaults-v1.json` is the canonical planning registry for configurable product, integrity, privacy, and operational defaults. Every entry defines value, valid range, owner, and whether changes may affect existing records.

Policy changes require:

- a new policy version;
- decision-register entry for material changes;
- prospective application by default;
- explicit rebuild/correction semantics and user notice for retroactive changes;
- no hidden change to metric, evidence, privacy, authorization, or appeal semantics.

Code may provide emergency safer bounds, but it may not silently widen an accepted range.

## Consequences

The social contract's references to normalization, cohort minimums, hysteresis, retention, and configurable thresholds resolve through this ADR and the policy registry. Cross-language implementations must use the same Unicode and policy versions.
