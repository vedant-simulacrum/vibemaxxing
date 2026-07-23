import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";

const root = path.resolve(import.meta.dirname, "../../..");
const captureRoot = path.resolve(process.argv[2] ?? "storybook-captures");
const diffRoot = path.resolve(process.argv[3] ?? "storybook-diffs");
const threshold = Number(process.env.VISUAL_DIFF_THRESHOLD ?? "0.0025");
const manifest = JSON.parse(fs.readFileSync(path.join(root, "assets/ui/references/manifest.json"), "utf8"));
const failures = [];
const summary = [];

fs.mkdirSync(diffRoot, { recursive: true });
const sha256 = buffer => crypto.createHash("sha256").update(buffer).digest("hex");

for (const reference of manifest.references) {
  for (const [viewport, viewportMeta] of Object.entries(manifest.viewports)) {
    const baselinePath = path.join(root, "assets/ui/references", reference.renders[viewport]);
    const capturePath = path.join(captureRoot, `${reference.id}${viewportMeta.captureSuffix}.png`);
    const scenario = `${reference.id} / ${viewport}`;
    if (!fs.existsSync(baselinePath) || !fs.existsSync(capturePath)) {
      failures.push(`${scenario}: baseline or capture is missing`);
      continue;
    }

    const captureBytes = fs.readFileSync(capturePath);
    const captureSha256 = sha256(captureBytes);
    const expectedCaptureSha256 = reference.approvedCaptureSha256[viewport];
    if (captureSha256 === expectedCaptureSha256) {
      summary.push({ id: reference.id, viewport, approvedCapture: true, captureSha256, changedPixels: 0, ratio: 0 });
      continue;
    }

    const baseline = PNG.sync.read(fs.readFileSync(baselinePath));
    const capture = PNG.sync.read(captureBytes);
    if (baseline.width !== capture.width || baseline.height !== capture.height) {
      failures.push(`${scenario}: expected ${baseline.width}×${baseline.height}, received ${capture.width}×${capture.height}`);
      continue;
    }

    const diff = new PNG({ width: baseline.width, height: baseline.height });
    const changed = pixelmatch(baseline.data, capture.data, diff.data, baseline.width, baseline.height, {
      threshold: 0.1,
      includeAA: false,
    });
    const ratio = changed / (baseline.width * baseline.height);
    fs.writeFileSync(path.join(diffRoot, `${reference.id}${viewportMeta.captureSuffix}.png`), PNG.sync.write(diff));
    summary.push({ id: reference.id, viewport, approvedCapture: false, captureSha256, expectedCaptureSha256, changedPixels: changed, ratio });
    if (ratio > threshold) failures.push(`${scenario}: ${(ratio * 100).toFixed(3)}% visual drift exceeds ${(threshold * 100).toFixed(3)}%`);
  }
}

fs.writeFileSync(path.join(diffRoot, "summary.json"), `${JSON.stringify({ threshold, scenarios: summary }, null, 2)}\n`);
for (const scenario of summary) {
  const label = `${scenario.id} / ${scenario.viewport}`;
  console.log(scenario.approvedCapture
    ? `${label}: exact reviewed capture ${scenario.captureSha256}`
    : `${label}: ${(scenario.ratio * 100).toFixed(3)}% (${scenario.changedPixels} pixels), capture ${scenario.captureSha256}`);
}
if (failures.length) {
  console.error(failures.map(failure => `- ${failure}`).join("\n"));
  process.exit(1);
}
console.log(`Responsive visual regression passed for ${summary.length} governed scenarios.`);
