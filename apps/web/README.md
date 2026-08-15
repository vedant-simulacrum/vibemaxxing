# vibemaxxing web

The hosted product web app. Its route files are retained as the record of which
product screens exist.

## Status: exploratory prototype, quarantined, does not build

Quarantined under P-1140F-1. This app renders synthetic fixtures and is not
evidence that the product works.

D-636 deleted the component system this app imported. Eight route files still
import the deleted package and therefore do not build; they are kept
deliberately, because they are the only remaining record of which product
screens exist. D-637 then deleted the brand and the governed asset library as
well, including the public brand directory this app's metadata pointed at.
Brand identity, visual language, components, tokens, screen composition and the
asset library have no normative owner. No replacement has been designed and no
path is reserved for one; `docs/project/DOCUMENTATION.md` records that absence.

What this app is measured against is therefore what it is supposed to show,
not how it is supposed to look: `docs/product/PRODUCT_SPEC.md` is its normative
owner, and every incompatibility below is a way these routes fail to be that
product.

Known incompatibilities:

- synthetic fixtures
- no live backend integration
- routes import a package that no longer exists
- renders no brand, because D-637 deleted it

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

This does not currently produce a running app: the routes import the component
package deleted under D-636 and the build fails on the missing module. Data was,
and would remain, local fixture data; no backend integration is implied.

There are no component rules, token definitions, brand values or governed assets
in this repository, and nothing has been decided about what replaces them. Do
not restore any of it from history to satisfy a reference; repair the reference.
