# vibemaxxing Brand Guidelines

Status: approved identity system  
Approved direction: **Ledger Wordmark**  
Visual thesis: **The Competitive Ledger**

## 1. Brand foundation

### Canonical name

- Product name in prose: `VibeMaxxing`.
- Canonical wordmark: `vibemaxxing`, always lowercase.
- Domain: `vibemaxxing.dev`.

### Positioning

VibeMaxxing is the privacy-preserving public competition layer for AI-agent activity. Its identity combines technical restraint with social competition:

> Codex restraint × Steam social competition

The intended balance is approximately 70% refined technical product and 30% competitive social network.

### Character

- Premium, not luxurious.
- Competitive, not aggressive.
- Technically credible, not corporate.
- Social, not noisy.
- Slightly provocative, never hostile.
- Privacy-conscious, never fear-based.
- Serious enough to trust and playful enough to share.

## 2. Approved identity

The approved system contains three elements:

1. A heavy lowercase `vibemaxxing` wordmark.
2. A compact lowercase `vm` mark.
3. A ledger rule whose final 20% changes from the base color to electric indigo.

The ledger rule represents a competitive record and a change in position. It is deliberately separate from the letterforms; the wordmark itself remains quiet and legible.

No number, edition index, rank suffix, slash-number, crossed `x`, or numeric badge is part of the identity. Actual ranks belong to product data, not the logo.

## 3. Logo family

| Variant | Purpose |
|---|---|
| `wordmark-primary.svg` | Default on white or warm-neutral backgrounds |
| `wordmark-reverse.svg` | Default on near-black or dark photography |
| `wordmark-indigo.svg` | Controlled campaign emphasis |
| `wordmark-monochrome.svg` | One-color production, engraving, or fax-like constraints |
| `wordmark-no-rule.svg` | Dense navigation below the standard minimum width |
| `mark-primary.svg` | Default app icon, avatar, and compact product mark |
| `mark-indigo.svg` | Campaign and selected-state use |
| `mark-light.svg` | Light neutral tiles |
| `mark-one-color.svg` | Single-color production |
| `mark-maskable.svg` | Android/PWA masks and full-bleed crops |
| `favicon.svg` | Browser and very small digital use |

All masters live in `assets/brand/source/`. They use outlined paths and have no runtime font dependency.

### Priority

Use the wordmark whenever horizontal space allows. Use the `vm` mark only when the brand name appears nearby, the context is already established, or the format is inherently compact, such as an app icon or avatar.

### Clear space

- Wordmark: preserve clear space equal to the cap height of the `v` on every side.
- Mark: preserve at least 12.5% of the mark width on every side unless the containing app-icon mask provides the safe area.
- Never allow a border, headline, avatar, or browser edge to touch the ledger rule.

### Minimum size

- Wordmark with rule: 140px wide digitally; 35mm in print.
- Wordmark without rule: 110px wide digitally; 28mm in print.
- `vm` mark: 24px digitally; use the dedicated favicon below 32px.
- Ledger-rule thickness must never rasterize below one physical pixel.

### Backgrounds

- Primary wordmark: white, Canvas, or photography with a quiet light field.
- Reverse wordmark: Ink or photography with a consistent dark field.
- Indigo wordmark: white or Canvas only.
- Do not place a logo across a high-detail boundary or over a gradient that reduces rule visibility.

### Misuse

Never:

- change the final indigo segment to another accent;
- extend the indigo segment beyond 20% of the rule;
- add a number, rank, season, or edition to the lockup;
- manipulate individual letters or emphasize `maxxing` separately;
- rotate, stretch, skew, bevel, extrude, glow, or add a drop shadow;
- put the full wordmark inside an arbitrary pill or badge;
- recreate the wordmark with live text;
- combine the mark with flames, coins, gauges, lightning, tokens, code brackets, or esports chrome.

## 4. Color system

### Core palette

| Token | Hex | Role |
|---|---:|---|
| Canvas | `#F4F2ED` | Warm-neutral product and campaign background |
| Surface | `#FFFFFF` | Primary ledger and navigation surfaces |
| Surface subtle | `#FAF9F6` | Table headers, hover states, and quiet groups |
| Ink | `#171714` | Primary text, dark marks, and strong controls |
| Muted | `#716F68` | Secondary text |
| Hairline | `#DEDAD1` | Default boundaries |
| Electric indigo | `#5847E8` | Ledger endpoint, active state, rank progress |
| Indigo dark | `#4636C9` | Accessible indigo text on light surfaces |
| Indigo soft | `#EFEDFF` | Selected-control background |
| Positive | `#18794E` | Rank gain and healthy live state |
| Negative | `#B84B44` | Rank loss and destructive state |
| Warning | `#96651B` | Review, provisional, or attention state |

### Accent discipline

Indigo is a signal, not atmosphere. It should usually occupy less than 10% of a product screen. Large purple gradients, neon glows, and purple-on-black cyberpunk compositions are outside the system.

Positive, negative, and warning colors communicate state only. They never replace labels, icons, arrows, or explanatory text.

## 5. Typography

### Logo construction

The logo is an outlined lockup constructed from **Nimbus Sans Bold, OpenType Version 1.00** (`NimbusSans-Bold`, unique ID `URW:NimbusSans-Bold:2016`). The approved generator input is pinned to SHA-256 `7f33328e6b4d4cd21b45fa625791928c9407dc702db6780e56b09ca9a3ecaa67`.

Maintainers obtain the font from the official [Artifex URW Base 35 repository](https://github.com/ArtifexSoftware/urw-base35-fonts). Its upstream license is GNU AGPL v3 with the font embedding exception; see the official [`fonts/LICENSE`](https://github.com/ArtifexSoftware/urw-base35-fonts/blob/master/fonts/LICENSE). The binary is not shipped with this repository, and product consumers do not need it because all approved logos are outlined. Do not recreate the wordmark with live text or regenerate it from a different font. Read `assets/brand/FONT_PROVENANCE.md` before regeneration or redistribution; final public-release licensing treatment remains subject to legal review.

### Product interface

Product typography uses **Inter**. Production uses the official `InterVariable.woff2` upright variable font, range 100–900, self-hosted with its SIL Open Font License 1.1 notice. Obtain it from the official [Inter project](https://github.com/rsms/inter) or [Inter download site](https://rsms.me/inter/); the license is published in the official [`LICENSE.txt`](https://github.com/rsms/inter/blob/master/LICENSE.txt). Do not depend on a third-party font CDN at runtime.

The canonical CSS stack is:

```css
"InterVariable", "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Until the WOFF2 file is bundled by an application, this stack intentionally falls back to the platform UI font. The logo font and product font are separate systems.

| Role | Size | Weight | Notes |
|---|---:|---:|---|
| Display | 40–48px | 600–700 | Tight tracking; marketing and major product moments |
| Page title | 28–40px | 600–700 | Calm, never theatrical |
| Section title | 18–24px | 600–700 | Sentence case |
| Body | 14–16px | 400–500 | Comfortable reading |
| UI label | 10–12px | 500–700 | Compact but legible |
| Eyebrow | 9–11px | 700 | Uppercase, 0.08–0.12em tracking |
| Data | contextual | 600–700 | Always tabular numerals |

The allowed Inter weights are 400 Regular, 500 Medium, 600 SemiBold, and 700 Bold. Use the platform monospace stack `ui-monospace, "SFMono-Regular", "Cascadia Mono", Menlo, Consolas, "Liberation Mono", monospace` for commands and immutable identifiers only. No monospace font is bundled. Do not make monospace the general brand voice.

## 6. Composition

The leaderboard is the dominant object. Screens should feel like a public record that happens to be alive: exact rows, stable alignment, visible movement, restrained presence, and social tension created through rank.

- Use warm Canvas around white ledger surfaces.
- Prefer hairlines over nested cards.
- Keep the main ledger visually heavier than side rails.
- Use the ledger-rule motif sparingly for brand attribution, selected navigation, or campaign endings—not as a divider under every heading.
- Preserve large quiet zones around major wordmarks.

## 7. Imagery and campaign system

The product should not depend on stock photography or decorative AI imagery. Preferred campaign materials are:

- product-led ledger crops;
- documentary images of real builders in real environments;
- exact rank movement, timestamps, and tabular values;
- clean typographic statements such as `Burn more. Rank higher.`;
- the ledger rule as a restrained ending device.

Neutral color grading is preferred. Avoid vaporwave, cyberpunk, holograms, glossy 3D tokens, floating dashboards, and generic AI brains.

## 8. Voice

The voice is concise, premium, and mildly internet-native.

Approved examples:

- `Burn more. Rank higher.`
- `Public competition. Private transcripts.`
- `You were overtaken.`
- `Active in Codex.`
- `12.8M Credited Token Burn.`

Rules:

- Prefer short declarative sentences.
- Say precisely what is measured. On a public surface the figure is `Credited Token Burn`; `Token Burn` is the raw figure and appears only on the participant's own surface, because D-144 forbids publishing both. Also `Estimated Cash Burn` and `active agent`.
- Always label cash values as estimated.
- Treat competition with dry confidence rather than manufactured hype.
- Privacy explanations must be literal and specific.
- Never claim `zero knowledge`, `unhackable`, `cheat-proof`, or equivalent absolutes without a matching reviewed technical guarantee.

## 9. Accessibility

- All product text and essential logo placements must meet WCAG 2.2 AA contrast.
- Never rely on indigo, green, or red alone to communicate meaning.
- Preserve the full wordmark as accessible text in adjacent markup or an accessible image label.
- Use the monochrome variants in forced-color and single-ink environments.
- Do not animate the wordmark or ledger rule continuously.

## 10. Asset production and governance

Canonical files, export dimensions, checksums, and regeneration instructions live in `assets/brand/`.

The current identity was explicitly approved by the project owner. Any proposed change must follow this order:

1. Create visual concepts outside GitHub.
2. Show the actual rendered result to the project owner.
3. Iterate until explicit approval.
4. Update the generator, masters, exports, manifest, and this document together.
5. Commit only the approved identity.

UI page mock-ups follow the same review-before-implementation rule. Stable foundations may be codified, but unapproved page designs must not be silently turned into production components.
