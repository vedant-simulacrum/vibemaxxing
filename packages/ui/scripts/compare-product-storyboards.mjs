import fs from "node:fs";
import path from "node:path";
import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";

const root = path.resolve(import.meta.dirname, "../../..");
const captureRoot = path.resolve(process.argv[2] ?? "storybook-captures");
const diffRoot = path.resolve(process.argv[3] ?? "storybook-diffs");
const threshold = Number(process.env.VISUAL_DIFF_THRESHOLD ?? "0.0025");
const manifestPath = path.join(root, "assets/ui/references/manifest.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const failures = [];
const summary = [];

fs.mkdirSync(diffRoot, { recursive: true });

for (const reference of manifest.references) {
  const baselinePath = path.join(root, "assets/ui/references", reference.render);
  const capturePath = path.join(captureRoot, `${reference.id}.png`);
  if (!fs.existsSync(baselinePath) || !fs.existsSync(capturePath)) {
    failures.push(`${reference.id}: baseline or capture is missing`);
    continue;
  }

  const baseline = PNG.sync.read(fs.readFileSync(baselinePath));
  const capture = PNG.sync.read(fs.readFileSync(capturePath));
  if (baseline.width !== capture.width || baseline.height !== capture.height) {
    failures.push(`${reference.id}: expected ${baseline.width}×${baseline.height}, received ${capture.width}×${capture.height}`);
    continue;
  }

  const diff = new PNG({ width: baseline.width, height: baseline.height });
  const changed = pixelmatch(baseline.data, capture.data, diff.data, baseline.width, baseline.height, {
    threshold: 0.1,
    includeAA: false,
  });
  const ratio = changed / (baseline.width * baseline.height);
  const diffPath = path.join(diffRoot, `${reference.id}.png`);
  fs.writeFileSync(diffPath, PNG.sync.write(diff));
  summary.push({ id: reference.id, changedPixels: changed, ratio });
  if (ratio > threshold) failures.push(`${reference.id}: ${(ratio * 100).toFixed(3)}% visual drift exceeds ${(threshold * 100).toFixed(3)}%`);
}

fs.writeFileSync(path.join(diffRoot, "summary.json"), `${JSON.stringify({ threshold, stories: summary }, null, 2)}\n`);
for (const story of summary) console.log(`${story.id}: ${(story.ratio * 100).toFixed(3)}% (${story.changedPixels} pixels)`);
if (failures.length) {
  console.error(failures.map((failure) => `- ${failure}`).join("\n"));
  process.exit(1);
}
console.log(`Visual regression passed at ${(threshold * 100).toFixed(3)}% maximum drift.`);
