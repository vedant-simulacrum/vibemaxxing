# vibemaxxing web

The hosted product web app. Its route files are retained as the record of which
product screens exist.

## Status: exploratory prototype, quarantined, does not build

Quarantined under P-1140F-1. This app renders synthetic fixtures and is not
evidence that the product works.

D-635 deleted the component system this app imported. Eight route files still
import the deleted package and therefore do not build; they are kept
deliberately, because they are the only remaining record of which product
screens exist. Components, tokens and screen composition have no normative owner
until a replacement declares one in `docs/project/DOCUMENTATION.md`.

Known incompatibilities:

- synthetic fixtures
- no live backend integration
- routes import a package that no longer exists

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
package deleted under D-635 and the build fails on the missing module. Data was,
and would remain, local fixture data; no backend integration is implied.

Brand identity, palette, voice and logo remain owned by
`docs/style-guide/BRAND.md`, and the governed visual library by
`docs/style-guide/ASSET_SYSTEM.md` and `assets/`; D-635 did not touch either.
There are no component rules or token definitions in this repository, and
nothing has been decided about what replaces them.
