# Font provenance

This file distinguishes the font used to construct the approved outlined logo from the font used in the product UI.

## Logo construction source

| Field | Value |
|---|---|
| Family | Nimbus Sans |
| Style | Bold |
| OpenType version | 1.00 |
| PostScript name | `NimbusSans-Bold` |
| Unique identifier | `URW:NimbusSans-Bold:2016` |
| Canonical generator filename | `NimbusSans-Bold.otf` |
| Required SHA-256 | `7f33328e6b4d4cd21b45fa625791928c9407dc702db6780e56b09ca9a3ecaa67` |
| Official source | https://github.com/ArtifexSoftware/urw-base35-fonts |
| Upstream font license | GNU AGPL v3 with the font embedding exception in `fonts/LICENSE` |
| License text | https://github.com/ArtifexSoftware/urw-base35-fonts/blob/master/fonts/LICENSE |

The repository distributes the approved logo as outlined SVG paths and raster exports; consumers do not need Nimbus Sans. The font binary is not vendored in this repository.

The generator checks the font SHA-256 and refuses to regenerate different outlines by default. A checksum override is for an explicitly reviewed font migration only; it is not a convenience flag.

The font embedding exception and the licensing treatment of converted logo outlines must receive final legal review before public release. This document records provenance and does not replace legal advice.

## Product interface font

| Field | Value |
|---|---|
| Family | Inter |
| Preferred file | `InterVariable.woff2` |
| Upright weight range | 100–900 |
| Product weights used | Regular 400, Medium 500, SemiBold 600, Bold 700 |
| Official project | https://github.com/rsms/inter |
| Official download/site | https://rsms.me/inter/ |
| License | SIL Open Font License 1.1 |
| License text | https://github.com/rsms/inter/blob/master/LICENSE.txt |

Production should self-host the official Inter variable WOFF2 file with the OFL license notice. Do not fetch a font from an unpinned third-party CDN at runtime. Until the font is bundled, the token stack falls back to platform UI fonts.

## Monospace stack

Technical commands and identifiers use the platform stack:

```css
ui-monospace, "SFMono-Regular", "Cascadia Mono", Menlo, Consolas, "Liberation Mono", monospace
```

No monospace font is bundled by default. It is not used for body copy, navigation, headings, or the brand wordmark.
