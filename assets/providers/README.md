# Provider and model logos

This directory is the canonical source for third-party AI provider and model-family marks used by VibeMaxxing UI. Product code and stories must not draw substitutes, use text glyphs such as `AI` or `◉`, hotlink remote logos, or create route-local copies.

## Source and version

The normalized SVG set is vendored from [`@lobehub/icons-static-svg` 1.94.0](https://www.npmjs.com/package/@lobehub/icons-static-svg), an MIT-licensed AI/LLM icon collection. The package tarball integrity recorded at import was `sha512-Inx1TYkjLH6Ye…fAiFj9E9Mmw9Q==`; the complete npm integrity remains available in the package lock/registry metadata. Lobe Icons provides static SVG assets and tracks corrections upstream.

The underlying names and logos remain trademarks of their respective owners. OpenAI usage must follow the official [OpenAI design guidelines](https://openai.com/brand/). Mistral publishes its own [brand assets and guidelines](https://mistral.ai/brand/). A library license does not grant trademark rights or imply endorsement.

## Rendering contract

- Use the SVG files directly; they scale to every required UI dimension.
- Approved icon boxes are `16px` in dense tables, `20px` in ordinary controls, `22–24px` in summary surfaces, and `32px` in provider selectors.
- Preserve each SVG view box, proportions, and supplied colors.
- Do not place routine model identifiers inside pills or colored badges.
- Do not recolor multicolor marks. Monochrome marks use their supplied neutral form.
- Use `ProviderLogo` from `@vibemaxxing/ui`; do not hand-author `<img>` paths in product components.
- A model family uses its model mark when one exists: Claude → Claude, Gemini → Gemini, Grok → Grok. GPT models use the OpenAI mark. Llama models use Meta until a separately governed Llama mark is added.
- Provider routing surfaces use provider marks: Anthropic, OpenAI, Azure AI, Bedrock, OpenRouter, and so on.

## Included set

The initial universal set contains OpenAI, Anthropic, Claude, Codex, Gemini, Google, Mistral, DeepSeek, Grok, xAI, Meta, Qwen, OpenRouter, Azure AI, and Amazon Bedrock. Additions require updating `manifest.json`, the `ProviderLogo` registry, provenance, and the provider-logo Storybook story together.
