import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = relative => fs.readFileSync(path.join(root, relative), "utf8");
const failures = [];

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

const catalogue = read("apps/web/app/style-guide/page.tsx");
for (const name of ["Wordmark", "Icon", "IconButton", "ChoiceGroup", "Avatar", "RankMovement", "EvidenceBadge", "PresenceIndicator", "MetricValue", "Progress", "LedgerRow"]) {
  if (!catalogue.includes(name)) failures.push(`Executable catalogue does not cover ${name}.`);
}

if (failures.length) {
  console.error(failures.map(item => `- ${item.trim()}`).join("\n"));
  process.exit(1);
}

console.log("UI system checks passed: generated tokens, raw colors, component reuse, inline styles, and catalogue coverage.");
