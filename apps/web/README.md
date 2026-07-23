# vibemaxxing web

The first implementation slice of the **Competitive Ledger** design system and hosted product UI.

## Run locally

```bash
npm install
npm run dev
```

The current screen is a responsive, accessible product prototype with interactive scope, period, and metric controls. Data is intentionally local fixture data; no backend integration is implied.

Routes compose public `@vibemaxxing/ui` exports. They do not own reusable UI, fixtures, ranking logic, identity verification, or backend policy. The canonical route and screen map is `docs/style-guide/PRODUCT_SURFACE_CONTRACTS.md`.

Canonical visual rules and token definitions live in `docs/design/BRAND.md` at the repository root. Final brand assets are pending visual review and explicit approval before they are added to the repository.
