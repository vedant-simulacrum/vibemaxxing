import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = JSON.parse(fs.readFileSync(path.join(root, "src/tokens.source.json"), "utf8"));
const entries = Object.entries(source.tokens);
const variable = key => `--vm-${key.replaceAll(".", "-")}`;

const css = `/* Generated from tokens.source.json. Do not edit. */\n:root {\n  color-scheme: light;\n${entries.map(([key, value]) => `  ${variable(key)}: ${value};`).join("\n")}\n\n  --canvas: var(--vm-color-canvas);\n  --surface: var(--vm-color-surface);\n  --surface-subtle: var(--vm-color-surface-subtle);\n  --ink: var(--vm-color-ink);\n  --muted: var(--vm-color-muted);\n  --muted-2: var(--vm-color-muted-2);\n  --line: var(--vm-color-line);\n  --line-strong: var(--vm-color-line-strong);\n  --indigo: var(--vm-color-indigo);\n  --indigo-dark: var(--vm-color-indigo-dark);\n  --indigo-soft: var(--vm-color-indigo-soft);\n  --positive: var(--vm-color-positive);\n  --negative: var(--vm-color-negative);\n  --radius-md: var(--vm-radius-md);\n  --radius-lg: var(--vm-radius-lg);\n  --shadow: var(--vm-shadow-surface);\n  --font-sans: var(--vm-font-sans);\n  --font-mono: var(--vm-font-mono);\n}\n`;

const ts = `/* Generated from tokens.source.json. Do not edit. */\nexport const tokens = ${JSON.stringify(source.tokens, null, 2)} as const;\n\nexport type TokenName = keyof typeof tokens;\n`;
const outputs = [["src/tokens.css", css], ["src/tokens.ts", ts]];

if (process.argv.includes("--check")) {
  const stale = outputs.filter(([file, content]) => !fs.existsSync(path.join(root, file)) || fs.readFileSync(path.join(root, file), "utf8") !== content);
  if (stale.length) {
    console.error(`Generated token files are stale: ${stale.map(([file]) => file).join(", ")}`);
    process.exit(1);
  }
  console.log(`Verified ${entries.length} canonical UI tokens.`);
} else {
  for (const [file, content] of outputs) fs.writeFileSync(path.join(root, file), content);
  console.log(`Generated CSS and TypeScript from ${entries.length} canonical UI tokens.`);
}
