# Cash Burn Pricing Provenance

Cash Burn is an estimated API-equivalent value. It is never represented as the user's actual invoice or spend.

## Data model

Pricing is an immutable versioned dataset. Each record includes provider, canonical model ID, effective dates, currency, unit, usage category, tier/region constraints, rounding rules, source reference, retrieval time, source digest, and review status.

Usage events retain token categories and model identity independently from pricing. Estimates are computed using a named pricing dataset version.

## Update process

1. Fetch or manually capture a provider-published price source.
2. Normalize it into the pricing schema.
3. Verify model aliases and effective dates.
4. Review changes, including cache and batch categories.
5. Produce a signed dataset manifest and changelog.
6. Run golden pricing fixtures and regression tests.
7. Publish a new immutable dataset version.

## Historical behavior

Previously published estimates retain their original dataset version. The product may expose a separately labeled “repriced using current rates” view, but must not silently rewrite historical competitive values.

## Exclusions

Do not infer actual spend from subscription plans, credits, negotiated enterprise discounts, taxes, regional invoicing, or bundled usage. These may be supported only as separate private analytics inputs supplied by the user.
