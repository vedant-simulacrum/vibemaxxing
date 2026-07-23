import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = relative => fs.readFileSync(path.join(root, relative), "utf8");
const failures = [];
const assetManifest = JSON.parse(read("assets/manifest.json"));
for (const collection of assetManifest.collections ?? []) {
  if (!fs.existsSync(path.join(root, collection.path))) failures.push(`Missing asset collection: ${collection.path}`);
  if (!fs.existsSync(path.join(root, collection.manifest))) failures.push(`Missing asset manifest: ${collection.manifest}`);
}
const fixtureManifest = JSON.parse(read("assets/ui/fixtures/manifest.json"));
for (const asset of fixtureManifest.assets ?? []) {
  for (const file of asset.files ?? [asset.file]) {
    if (!fs.existsSync(path.join(root, "assets/ui/fixtures", file))) failures.push(`Missing governed UI fixture: ${file}`);
  }
}
const assetRegistry = read("packages/ui/src/assets.ts");
if (/https?:\/\//.test(assetRegistry)) failures.push("The asset registry must not hotlink remote files.");

const tokenCheck = spawnSync(process.execPath, ["scripts/generate-tokens.mjs", "--check"], { cwd: path.join(root, "packages/ui"), encoding: "utf8" });
if (tokenCheck.status !== 0) failures.push(tokenCheck.stderr || tokenCheck.stdout || "Token generation check failed.");

const governedFiles = ["packages/ui/src/components.css", "apps/web/app/globals.css"];
for (const file of governedFiles) {
  const content = read(file);
  if (/#[0-9a-f]{3,8}\b|rgba?\(/i.test(content)) failures.push(`${file} contains a raw color; add a canonical token.`);
}

const appPage = read("apps/web/app/page.tsx");
for (const name of ["Icon", "Wordmark", "Avatar", "RankMovement", "EvidenceBadge", "PresenceIndicator", "MetricValue", "LedgerRow", "Progress"]) {
  if (new RegExp(`function\\s+${name}\\b`).test(appPage)) failures.push(`apps/web/app/page.tsx recreates shared ${name}.`);
}
if (/style=\{\{/.test(appPage)) failures.push("apps/web/app/page.tsx contains page-local inline styles.");

const componentSource = read("packages/ui/src/components.tsx");
const publicComponents = [...componentSource.matchAll(/export function\s+(\w+)\b/g)].map(match => match[1]);
const storybookMain = read("packages/ui/.storybook/main.ts");
const storybookPreview = read("packages/ui/.storybook/preview.ts");
const stories = read("packages/ui/src/components.stories.tsx");
const packageJson = JSON.parse(read("packages/ui/package.json"));
const styleGuide = read("apps/web/app/style-guide/page.tsx");

for (const dependency of ["storybook", "@storybook/react-vite", "@storybook/addon-docs", "@storybook/addon-a11y"]) {
  if (!packageJson.devDependencies?.[dependency]) failures.push(`Storybook dependency ${dependency} is required.`);
}
for (const script of ["storybook", "storybook:build"]) {
  if (!packageJson.scripts?.[script]) failures.push(`packages/ui is missing the ${script} script.`);
}
for (const addon of ["@storybook/addon-docs", "@storybook/addon-a11y"]) {
  if (!storybookMain.includes(addon)) failures.push(`Storybook must enable ${addon}.`);
}
if (!storybookPreview.includes('test: "error"')) failures.push("Storybook accessibility violations must be configured as test errors.");
if (!stories.includes('from "@vibemaxxing/ui"')) failures.push("Storybook stories must consume the @vibemaxxing/ui public API.");
if (!styleGuide.includes("Curated brand reference")) failures.push("/style-guide must identify itself as the curated brand reference, not the executable catalogue.");
if (!styleGuide.includes('from "@vibemaxxing/ui"')) failures.push("/style-guide must consume the @vibemaxxing/ui public API.");

for (const name of publicComponents) {
  if (!stories.includes(`<${name}`)) failures.push(`Storybook does not render public component ${name}.`);
}

if (failures.length) {
  console.error(failures.map(item => `- ${item.trim()}`).join("\n"));
  process.exit(1);
}

console.log("UI system checks passed: generated tokens, governed assets, raw colors, component reuse, Storybook coverage, accessibility configuration, and /style-guide role parity.");
