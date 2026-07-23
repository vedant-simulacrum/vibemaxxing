import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const absolute = relative => path.join(root, relative);
const read = relative => fs.readFileSync(absolute(relative), "utf8");
const failures = [];
const requireFile = relative => {
  if (!fs.existsSync(absolute(relative))) failures.push(`Missing required UI-system file: ${relative}`);
};

for (const required of [
  "assets/manifest.json",
  "assets/ui/fixtures/manifest.json",
  "assets/ui/references/manifest.json",
  "packages/ui/src/assets.ts",
  "packages/ui/src/foundations/asset-library.stories.tsx",
  "packages/ui/src/patterns/product-system.tsx",
  "packages/ui/src/ui/product-icons.ts",
  "packages/ui/src/concepts/product-storyboards.stories.tsx",
  "packages/ui/src/concepts/product-state-matrix.stories.tsx",
  "scripts/ui/playwright-runtime/audit-product-storyboards.mjs",
  "scripts/ui/playwright-runtime/package-lock.json",
  "packages/ui/scripts/compare-product-storyboards.mjs",
  "apps/web/app/profile/[handle]/page.tsx",
  "apps/web/app/rivals/[handle]/page.tsx",
  "apps/web/app/friends/page.tsx",
  "apps/web/app/activity/page.tsx",
  "apps/web/app/boards/[slug]/page.tsx",
]) requireFile(required);

const assetManifest = JSON.parse(read("assets/manifest.json"));
for (const collection of assetManifest.collections ?? []) {
  requireFile(collection.path);
  requireFile(collection.manifest);
}

const fixtureManifest = JSON.parse(read("assets/ui/fixtures/manifest.json"));
for (const asset of fixtureManifest.assets ?? []) {
  for (const file of asset.files ?? [asset.file]) requireFile(path.join("assets/ui/fixtures", file));
}

const referenceManifest = JSON.parse(read("assets/ui/references/manifest.json"));
for (const reference of referenceManifest.references ?? []) {
  requireFile(path.join("assets/ui/references", reference.mockup));
  requireFile(path.join("assets/ui/references", reference.render));
}
for (const evidence of referenceManifest.supportingEvidence ?? []) {
  requireFile(path.join("assets/ui/references", evidence.file));
}

const assetCatalogue = read("packages/ui/src/foundations/asset-library.stories.tsx");
for (const required of ["assetRegistry.brand", "providerLogoRegistry", "assetRegistry.fixtures", "iconNames", "ConsumptionContract"]) {
  if (!assetCatalogue.includes(required)) failures.push(`Storybook asset catalogue is missing ${required}.`);
}

const assetRegistry = read("packages/ui/src/assets.ts");
if (/https?:\/\//.test(assetRegistry)) failures.push("The asset registry must not hotlink remote files.");

const tokenCheck = spawnSync(process.execPath, ["scripts/generate-tokens.mjs", "--check"], {
  cwd: absolute("packages/ui"),
  encoding: "utf8",
});
if (tokenCheck.status !== 0) failures.push(tokenCheck.stderr || tokenCheck.stdout || "Token generation check failed.");

const walk = directory => fs.readdirSync(absolute(directory), { withFileTypes: true }).flatMap(entry => {
  const relative = path.join(directory, entry.name);
  return entry.isDirectory() ? walk(relative) : [relative];
});
const uiSource = [...walk("packages/ui/src"), ...walk("apps/web/app")]
  .filter(file => /\.(?:css|tsx?)$/.test(file));
const archivedConcepts = new Set([
  "packages/ui/src/concepts/competition-slice.tsx",
  "packages/ui/src/concepts/leaderboard-bento.tsx",
  "packages/ui/src/concepts/leaderboard-first.tsx",
]);

const frozenVisualCss = new Set([
  "packages/ui/src/tokens.css",
  "packages/ui/src/concepts/competition-slice.css",
  "packages/ui/src/concepts/leaderboard-bento.css",
  "packages/ui/src/concepts/leaderboard-first.css",
]);
for (const file of uiSource.filter(file => file.endsWith(".css") && !frozenVisualCss.has(file))) {
  if (/#[0-9a-f]{3,8}\b|rgba?\(/i.test(read(file))) failures.push(`${file} contains a raw color; add a canonical token.`);
}

for (const file of uiSource.filter(file => file.endsWith(".tsx"))) {
  const content = read(file);
  if (content.includes('from "lucide-react"') && file !== "packages/ui/src/ui/product-icons.ts" && !archivedConcepts.has(file)) {
    failures.push(`${file} imports Lucide directly; use the governed product icon gateway.`);
  }
  if (/["'`]\/brand-assets\//.test(content) && !["packages/ui/src/assets.ts", "packages/ui/src/ui/provider-logo.tsx"].includes(file) && !archivedConcepts.has(file)) {
    failures.push(`${file} bypasses the asset registry with a direct brand-assets path.`);
  }
}

const storyboardSource = read("packages/ui/src/concepts/product-storyboards.tsx");
for (const name of ["Avatar", "ProductShell", "Panel", "Button", "Movement", "Model", "Tabs", "Trend", "FriendRow", "MiniSpark", "MiniRankChart"]) {
  if (new RegExp(`function\\s+${name}\\b`).test(storyboardSource)) {
    failures.push(`Product storyboards recreate shared ${name}.`);
  }
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
const productStories = read("packages/ui/src/concepts/product-storyboards.stories.tsx");
const stateMatrixStories = read("packages/ui/src/concepts/product-state-matrix.stories.tsx");
const packageJson = JSON.parse(read("packages/ui/package.json"));
const browserRuntime = JSON.parse(read("scripts/ui/playwright-runtime/package.json"));
const styleGuide = read("apps/web/app/style-guide/page.tsx");
const workflow = read(".github/workflows/storyboard-visuals.yml");

for (const dependency of ["storybook", "@storybook/react-vite", "@storybook/addon-docs", "@storybook/addon-a11y", "pixelmatch", "pngjs"]) {
  if (!packageJson.devDependencies?.[dependency]) failures.push(`UI dependency ${dependency} is required.`);
}
for (const dependency of ["playwright", "@axe-core/playwright"]) {
  if (!browserRuntime.dependencies?.[dependency]) failures.push(`Locked prototype browser runtime is missing ${dependency}.`);
}
for (const script of ["storybook", "storybook:build", "storybook:compare"]) {
  if (!packageJson.scripts?.[script]) failures.push(`packages/ui is missing the ${script} script.`);
}
for (const addon of ["@storybook/addon-docs", "@storybook/addon-a11y"]) {
  if (!storybookMain.includes(addon)) failures.push(`Storybook must enable ${addon}.`);
}
if (!storybookPreview.includes('test: "error"')) failures.push("Storybook accessibility violations must be configured as test errors.");
if (!stories.includes('from "@vibemaxxing/ui"') || !productStories.includes('from "@vibemaxxing/ui"')) {
  failures.push("Storybook stories must consume the @vibemaxxing/ui public API.");
}
if (!styleGuide.includes("Curated brand reference") || !styleGuide.includes('from "@vibemaxxing/ui"')) {
  failures.push("/style-guide must remain a curated reference consuming the public UI API.");
}

for (const name of publicComponents) {
  if (!stories.includes(`<${name}`)) failures.push(`Storybook does not render public component ${name}.`);
}
for (const state of ["Loading", "Empty", "Error", "Offline", "Stale", "Private", "Blocked", "Restricted", "Quarantined"]) {
  if (!productStories.includes(`export const ${state}State`)) failures.push(`Storybook is missing the ${state.toLowerCase()} product state.`);
}
for (const viewport of ["vmDesktop", "vmTablet", "vmMobile"]) {
  if (!productStories.includes(viewport)) failures.push(`Storybook is missing the ${viewport} viewport.`);
}
for (const screen of ["Profile", "Rival", "Friends", "Activity", "Board"]) {
  for (const state of ["Loading", "Empty", "Error", "Offline", "Stale", "Private", "Blocked", "Restricted", "Quarantined"]) {
    if (!stateMatrixStories.includes(`export const ${screen}${state}`)) failures.push(`State matrix is missing ${screen}${state}.`);
  }
}
for (const required of ["Prototype storyboard visuals", "compare-product-storyboards.mjs", "audit-product-storyboards.mjs", "storybook-diffs"]) {
  if (!workflow.includes(required)) failures.push(`Visual workflow is missing ${required}.`);
}

const routeContracts = new Map([
  ["apps/web/app/page.tsx", "LeaderboardFirstPrototype"],
  ["apps/web/app/profile/[handle]/page.tsx", "PublicProfileStoryboard"],
  ["apps/web/app/rivals/[handle]/page.tsx", "RivalComparisonStoryboard"],
  ["apps/web/app/friends/page.tsx", "FriendsStoryboard"],
  ["apps/web/app/activity/page.tsx", "ActivityStoryboard"],
  ["apps/web/app/boards/[slug]/page.tsx", "BoardStandingsStoryboard"],
]);
for (const [route, component] of routeContracts) {
  if (!read(route).includes(component)) failures.push(`${route} must compose the approved ${component}.`);
}

if (failures.length) {
  console.error(failures.map(item => `- ${item.trim()}`).join("\n"));
  process.exit(1);
}
console.log("UI system checks passed: shared product components, governed assets, one icon gateway, required states, responsive viewports, Storybook coverage, accessibility configuration, and visual regression wiring.");
