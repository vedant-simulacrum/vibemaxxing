# UI reference assets

This collection stores approved high-fidelity mock-ups and reproducible browser-rendered Storybook evidence. It is part of the root asset system so design targets cannot disappear into local scratch folders or CI artifacts.

## Product storyboards

Each entry in `manifest.json` pairs:

- the frozen 1536 × 1024 mock-up used as the visual target; and
- the corresponding 1536 × 1024 Storybook browser render used for review.

These files are review evidence, not runtime product assets. Screens consume shared components, registries, tokens, provider marks, and fixtures; they must never display these screenshots as implementation shortcuts.

Rejected explorations and intermediate generated images are intentionally excluded. Promote a new image here only after it becomes an approved reference, update the manifest, and rerun the UI-system checks.
