import type { CSSProperties } from "react";

export const providerLogoRegistry = {
  anthropic: { label: "Anthropic", file: "anthropic.svg" },
  "azure-ai": { label: "Azure AI", file: "azure-ai.svg" },
  bedrock: { label: "Amazon Bedrock", file: "bedrock.svg" },
  claude: { label: "Claude", file: "claude.svg" },
  codex: { label: "Codex", file: "codex.svg" },
  deepseek: { label: "DeepSeek", file: "deepseek.svg" },
  gemini: { label: "Gemini", file: "gemini.svg" },
  google: { label: "Google", file: "google.svg" },
  grok: { label: "Grok", file: "grok.svg" },
  meta: { label: "Meta", file: "meta.svg" },
  mistral: { label: "Mistral", file: "mistral.svg" },
  openai: { label: "OpenAI", file: "openai.svg" },
  openrouter: { label: "OpenRouter", file: "openrouter.svg" },
  qwen: { label: "Qwen", file: "qwen.svg" },
  xai: { label: "xAI", file: "xai.svg" },
} as const;

export type ProviderLogoName = keyof typeof providerLogoRegistry;

export function ProviderLogo({ provider, size = 20, decorative = false, className = "" }: { provider: ProviderLogoName; size?: number; decorative?: boolean; className?: string }) {
  const asset = providerLogoRegistry[provider];
  return (
    <img
      alt={decorative ? "" : asset.label}
      aria-hidden={decorative || undefined}
      className={`vm-provider-logo ${className}`.trim()}
      height={size}
      src={`/brand-assets/providers/icons/${asset.file}`}
      style={{ "--vm-provider-logo-size": `${size}px` } as CSSProperties}
      width={size}
    />
  );
}
