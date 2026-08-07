# vibemaxxing web

The first implementation slice of the **Competitive Ledger** design system and hosted product UI.

## Status: exploratory prototype, quarantined

Quarantined under P-1140F-1. This app renders synthetic fixtures and is not
evidence that the product works.

Its normative owner is `docs/style-guide/UI_FOUNDATIONS.md`.

Known incompatibilities:

- synthetic fixtures
- no live backend integration

Prohibited uses:

- production-readiness
- launch-evidence

`conformance/p1140f/artifact-authority-v1.json` is the authority for this
status; `scripts/repository/validate_artifact_quarantine.py` enforces it.

## Run locally

```bash
npm install
npm run dev
```

The current screen is a responsive, accessible product prototype with interactive scope, period, and metric controls. Data is intentionally local fixture data; no backend integration is implied.

Canonical visual rules and token definitions live in `docs/style-guide/BRAND.md` at the repository root. Final brand assets are pending visual review and explicit approval before they are added to the repository.
