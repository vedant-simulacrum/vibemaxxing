# Brand Guidelines

Status: active design system, validation phase  
Design thesis: **The Competitive Ledger**

## Canonical name

`vibemaxxing`

Prefer lowercase wordmark presentation. The legal/product name may appear as VibeMaxxing in prose.

## Brand character

- Premium
- Competitive
- Technically credible
- Social
- Slightly provocative
- Privacy-conscious
- Calm rather than noisy
- Serious but playful

## Visual thesis

> Codex restraint × Steam social competition

Approximately 70% refined technical product and 30% competitive social network.

The leaderboard is the hero object. The interface should feel like a public record that happens to be alive: orderly rows, exact values, visible movement, restrained presence, and social tension created through rank—not through decoration.

## Identity system

The primary identity is the lowercase wordmark `vibemaxxing`. Its custom crossed `x` depicts two competitors exchanging position. One crossing path is near-black; the overtaking path is indigo. The standalone mark uses the same geometry, but the wordmark remains primary.

Asset sources:

- `apps/web/public/brand/wordmark.svg`
- `apps/web/public/brand/wordmark-reverse.svg`
- `apps/web/public/brand/mark.svg`
- `apps/web/public/brand/mark-light.svg`
- `apps/web/public/brand/favicon.svg`
- `apps/web/public/brand/social-card.svg`

Use the primary wordmark on warm-neutral or white surfaces and the reverse wordmark on near-black. Clear space is at least one lowercase `v` height. Never stretch, rotate, add a container around the full wordmark, apply gradients, or recolor arbitrary letters.

The current wordmark is a validation asset and retains live SVG text. Convert it to outlined paths after the letter spacing and custom `x` pass usability and trademark review.

## Color

| Token | Value | Use |
|---|---:|---|
| Canvas | `#F4F2ED` | Warm-neutral page background |
| Surface | `#FFFFFF` | Primary ledger and navigation surfaces |
| Surface subtle | `#FAF9F6` | Table headers and quiet hover states |
| Ink | `#171714` | Primary text and dark controls |
| Muted | `#716F68` | Secondary text |
| Hairline | `#DEDAD1` | Default boundaries |
| Electric indigo | `#5847E8` | Active states, rank progress, custom `x` |
| Indigo soft | `#EFEDFF` | Selected-control background |
| Positive | `#18794E` | Upward movement and live health |
| Negative | `#B84B44` | Downward movement and destructive states |

Indigo is a signal, not atmosphere. It should normally occupy less than 10% of a screen. Do not use large indigo gradients, glowing backgrounds, or purple-on-black cyberpunk compositions.

## Typography

Use a neutral grotesk stack led by Inter where available and platform system fonts otherwise. Headings are calm, medium-weight, and tightly tracked. UI copy is compact but never cramped. Numerical columns use tabular figures; technical commands use the platform monospace stack.

- Display: 32–48px, weight 560–620, negative tracking.
- Page title: 28–40px, weight 560–620.
- Body: 13–16px, regular.
- UI label: 10–12px, weight 550–700.
- Eyebrow: 9–11px, uppercase, 0.08–0.12em tracking.
- Numbers: tabular numerals wherever ranks, tokens, money, or movement appear.

Avoid oversized marketing typography inside the product, ultra-light display weights, condensed esports faces, and monospace as a general brand font.

## Layout and surfaces

- Base desktop content width: 1396px with 32px gutters.
- The ledger takes the dominant column; contextual social information uses a narrower rail.
- Prefer hairline-bounded sections over nested cards.
- Use 16px radius for the primary ledger, 12px for contained callouts, and 6–9px for controls.
- Shadows are almost imperceptible and only separate major white surfaces from the warm canvas.
- Spacing follows a practical 4px base, with 8, 12, 16, 24, 32, 48, and 64px as primary steps.

Do not assemble pages from equally weighted analytics cards. Summary values may live inside the ledger so the ranked rows remain the product's center of gravity.

## Components

### Ledger rows

Rows always prioritize rank, identity, evidence, and the selected burn metric. Movement uses arrows plus values so color is never the sole signal. Values align right and use tabular figures. On small screens, evidence may move into a detail view but identity and burn remain visible.

### Evidence

Use the public labels `Standard`, `Hardened`, and `Imported` exactly. `Hardened` may receive the indigo shield treatment. `Standard` remains visually neutral. `Imported` must never resemble live competitive evidence.

### Presence

Presence uses a small green point and an agent name, such as `Active in Codex`. Never expose project, repository, file, prompt, or task names. Motion must be subtle and disabled under reduced-motion preferences.

### Controls

Solid near-black pills choose the broad scope. Pale-indigo selections choose period or metric inside a surface. Avoid excessive pill usage; plain text and hairlines should do most structural work.

## Wordmark and imagery

Begin with the refined wordmark rather than forcing a symbol. The crossed `x` and overtaking path are the canonical motif.

Avoid:

- Coins
- Flames
- Gauges
- Lightning
- Literal tokens
- Code brackets
- Crypto styling
- Esports chrome
- Generic 3D objects

The product should not depend on stock photography or decorative AI-generated imagery. For launch campaigns, use documentary images of real builders and real environments with neutral color grading. Diagrammatic graphics should borrow ledger rules, crossing paths, exact coordinates, and rank movement.

## Iconography

Use simple 1.5–1.8px outline icons with round joins. Icons clarify known actions; they do not replace labels for unfamiliar concepts. A filled icon is reserved for selected or high-emphasis state. Do not mix illustration-like icons with system icons.

## Motion

Motion communicates rank change, new ledger entries, and overtakes. Default transitions are 120–180ms with ease-out timing. Avoid bouncing numbers, slot-machine counters, constant pulsing, confetti for routine actions, and ambient animation. Respect `prefers-reduced-motion` with functionally equivalent static states.

## Accessibility

- Meet WCAG 2.2 AA contrast for text and controls.
- Preserve visible keyboard focus with a 2px indigo outline and offset.
- Minimum interactive target is 36px in dense desktop contexts and 44px on touch layouts.
- Never encode movement, evidence, or status through color alone.
- Responsive layouts recompose; they do not shrink the desktop table until it becomes illegible.
- Test keyboard order, screen-reader names, 200% zoom, forced colors, and reduced motion.

## Copy voice

Balanced, concise, premium, mildly internet-native.

Examples:

- `Burn more. Rank higher.`
- `Public competition. Private transcripts.`
- `You were overtaken.`
- `Active in Codex.`

Rules:

- Prefer short declarative sentences.
- Say exactly what is measured: `Token Burn`, `Estimated Cash Burn`, and `active agent`.
- Treat competition with dry confidence, not manufactured hype.
- Explain privacy boundaries literally. Never say `zero knowledge`, `unhackable`, or `cheat-proof` without a matching reviewed technical claim.
- Overtake and rivalry copy may be mildly provocative, but moderation, appeals, privacy, and deletion copy must remain calm and direct.

Avoid corporate language and exaggerated security claims.

## Reference screen

`apps/web/app/page.tsx` is the first reference implementation. It establishes the desktop ledger, responsive row recomposition, contextual social rail, active states, evidence presentation, and privacy explanation. It is a product/brand prototype backed by fixture data, not evidence of completed product integration.
