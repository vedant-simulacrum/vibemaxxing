# VibeMaxxing asset library

`assets/` is the single canonical source for every repository-owned visual asset. Product features, Storybook stories, documentation, and marketing surfaces reference this library; they do not keep private copies.

## Collections

| Directory | Owner | Contents | Runtime access |
|---|---|---|---|
| `brand/` | Brand system | Wordmarks, marks, favicons, app icons, social exports, font provenance | `assetRegistry.brand` |
| `providers/` | UI system | Governed AI-provider and model-family marks, provenance, trademark rules | `ProviderLogo` |
| `ui/fixtures/` | UI system | Synthetic people and demo imagery used by Storybook and visual tests | `assetRegistry.fixtures` |

Add future shared collections here (`illustrations/`, `media/`, `flags/`), not inside route or component folders.

## Consumption rules

1. Use `assetRegistry` or a purpose-built component such as `ProviderLogo`. Do not hand-build asset URLs in screens.
2. Brand and provider marks are SVG-first. Raster exports exist only for platforms that require them.
3. Never hotlink assets. Runtime and test rendering must be reproducible offline.
4. Do not copy an asset to create a size variant. Size and color are presentation concerns unless the source artwork genuinely differs.
5. Every collection needs a manifest, provenance/licensing notes, an owner, and replacement rules.
6. Fixture people are synthetic demo data. They are never customer identities, testimonials, or production defaults.
7. Static artwork belongs here. Data charts remain code-native; interface icons come from the one pinned Lucide dependency.

## Change workflow

- Replace assets deliberately and review every consumer.
- Preserve stable IDs and paths when the meaning is unchanged.
- Add a new semantic ID when the meaning changes.
- Run `node scripts/ui/check-ui-system.mjs`.
- Verify affected Storybook stories at the locked review viewport.

See [`docs/style-guide/ASSET_SYSTEM.md`](../docs/style-guide/ASSET_SYSTEM.md) for architecture and governance.
