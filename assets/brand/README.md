# vibemaxxing brand assets

This directory is the canonical, approved identity package for `vibemaxxing`.

## Approved identity

- Lowercase wordmark: `vibemaxxing`.
- Compact mark: lowercase `vm`.
- Signature device: a thin ledger rule whose final 20% is electric indigo.
- No numbering, edition index, rank suffix, crossed `x`, flame, coin, gauge, lightning, or code-bracket motif is part of the identity.

## Directory map

```text
assets/brand/
├── source/       outlined SVG masters
├── exports/
│   ├── app-icons/  platform and application icons
│   ├── favicon/    SVG, PNG, WebP, and multi-size ICO
│   ├── social/     Open Graph, X/Twitter, and GitHub cards
│   └── wordmarks/  transparent PNG wordmark exports
└── manifest.json   file sizes and SHA-256 checksums
```

## Which file to use

| Need | Preferred asset |
|---|---|
| Product header on light surface | `source/wordmark-primary.svg` |
| Product header on dark surface | `source/wordmark-reverse.svg` |
| Very dense navigation | `source/wordmark-no-rule.svg` |
| Single-color print or engraving | `source/wordmark-monochrome.svg` |
| App/avatar mark | `source/mark-primary.svg` |
| Indigo campaign mark | `source/mark-indigo.svg` |
| Light neutral mark | `source/mark-light.svg` |
| PWA maskable icon | `source/mark-maskable.svg` |
| Modern browser icon | `exports/favicon/favicon.svg` |
| Legacy browser icon | `exports/favicon/favicon.ico` |
| Apple touch icon | `exports/app-icons/apple-touch-icon.png` |
| Android/PWA | `exports/app-icons/android-chrome-192.png`, `android-chrome-512.png` |
| Open Graph / LinkedIn | `exports/social/social-card-1200x630.png` |
| X/Twitter | `exports/social/social-card-1200x675.png` |
| GitHub repository social image | `exports/social/github-social-1280x640.png` |
| Press overview | `exports/brand-sheet.png` |

SVG is the default for web and design work. Use PNG where the consumer cannot render SVG, WebP for raster web delivery, and ICO only for legacy browser compatibility.

## Regeneration

```bash
python3 scripts/brand/generate_brand_assets.py
cd scripts/brand
npm install
npm run render
```

The generator converts the approved wordmark to outlined paths. Final SVGs contain no live text and do not require the development font at runtime. Do not manually edit generated exports; update the generator and regenerate the package.

The exact generation font is **Nimbus Sans Bold, Version 1.00, PostScript name `NimbusSans-Bold`**, pinned by SHA-256 in the generator. Maintainers obtain it from the official [Artifex URW Base 35 repository](https://github.com/ArtifexSoftware/urw-base35-fonts). It is not the product UI font and is not required by asset consumers. Read [`FONT_PROVENANCE.md`](FONT_PROVENANCE.md) before regenerating or redistributing font software.

## Governance

The identity shown here was explicitly approved by the project owner. Any change to the wordmark, `vm` geometry, ledger rule, palette, asset naming, or export matrix must be visually shown to the owner before it is committed.

See [`docs/design/BRAND.md`](../../docs/design/BRAND.md) for the full brand standard and [`docs/design/UI_FOUNDATIONS.md`](../../docs/design/UI_FOUNDATIONS.md) for the product UI framework.
