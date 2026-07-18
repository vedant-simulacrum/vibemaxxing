import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Resvg } from "@resvg/resvg-js";
import sharp from "sharp";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const source = path.join(root, "assets/brand/source");
const exportsRoot = path.join(root, "assets/brand/exports");
const webPublic = path.join(root, "apps/web/public/brand");

function ensure(directory) {
  fs.mkdirSync(directory, { recursive: true });
}

function render(svgPath, outputPath, width) {
  ensure(path.dirname(outputPath));
  const svg = fs.readFileSync(svgPath, "utf8");
  const png = new Resvg(svg, {
    fitTo: { mode: "width", value: width },
    background: "rgba(0,0,0,0)",
  }).render().asPng();
  fs.writeFileSync(outputPath, png);
}

const jobs = [
  ...[16, 32, 48, 64].map((size) => ["favicon.svg", `favicon/favicon-${size}.png`, size]),
  ...[16, 20, 24, 32, 40, 48, 64, 76, 96, 120, 128, 144, 150, 152, 167, 180, 192, 256, 310, 384, 512, 1024].map((size) => ["mark-primary.svg", `app-icons/app-icon-${size}.png`, size]),
  ...[192, 512].map((size) => ["mark-maskable.svg", `app-icons/maskable-icon-${size}.png`, size]),
  ...[512, 1024, 2048].flatMap((width) => [
    ["wordmark-primary.svg", `wordmarks/wordmark-primary-${width}.png`, width],
    ["wordmark-reverse.svg", `wordmarks/wordmark-reverse-${width}.png`, width],
    ["wordmark-no-rule.svg", `wordmarks/wordmark-no-rule-${width}.png`, width],
  ]),
  ["social-card-1200x630.svg", "social/social-card-1200x630.png", 1200],
  ["social-card-dark-1200x630.svg", "social/social-card-dark-1200x630.png", 1200],
  ["social-card-1200x675.svg", "social/social-card-1200x675.png", 1200],
  ["github-social-1280x640.svg", "social/github-social-1280x640.png", 1280],
  ["brand-sheet.svg", "brand-sheet.png", 1200],
];

for (const [input, output, width] of jobs) {
  render(path.join(source, input), path.join(exportsRoot, output), width);
}

const faviconDir = path.join(exportsRoot, "favicon");
await sharp(path.join(faviconDir, "favicon-64.png"))
  .resize(32, 32)
  .toFormat("webp")
  .toFile(path.join(faviconDir, "favicon-32.webp"));

await sharp(path.join(exportsRoot, "app-icons/app-icon-512.png"))
  .webp({ quality: 92 })
  .toFile(path.join(exportsRoot, "app-icons/app-icon-512.webp"));

await sharp(path.join(exportsRoot, "social/social-card-1200x630.png"))
  .webp({ quality: 92 })
  .toFile(path.join(exportsRoot, "social/social-card-1200x630.webp"));

fs.copyFileSync(path.join(source, "favicon.svg"), path.join(faviconDir, "favicon.svg"));
fs.copyFileSync(path.join(exportsRoot, "app-icons/app-icon-180.png"), path.join(exportsRoot, "app-icons/apple-touch-icon.png"));
fs.copyFileSync(path.join(exportsRoot, "app-icons/app-icon-192.png"), path.join(exportsRoot, "app-icons/android-chrome-192.png"));
fs.copyFileSync(path.join(exportsRoot, "app-icons/app-icon-512.png"), path.join(exportsRoot, "app-icons/android-chrome-512.png"));
fs.copyFileSync(path.join(exportsRoot, "app-icons/app-icon-150.png"), path.join(exportsRoot, "app-icons/mstile-150x150.png"));
fs.copyFileSync(path.join(exportsRoot, "app-icons/app-icon-310.png"), path.join(exportsRoot, "app-icons/mstile-310x310.png"));
fs.copyFileSync(path.join(source, "mark-one-color.svg"), path.join(faviconDir, "safari-pinned-tab.svg"));

fs.writeFileSync(path.join(exportsRoot, "app-icons/site.webmanifest"), `${JSON.stringify({
  name: "vibemaxxing",
  short_name: "vibemaxxing",
  icons: [
    { src: "android-chrome-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
    { src: "android-chrome-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
    { src: "maskable-icon-192.png", sizes: "192x192", type: "image/png", purpose: "maskable" },
    { src: "maskable-icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
  ],
  theme_color: "#F4F2ED",
  background_color: "#F4F2ED",
  display: "standalone",
}, null, 2)}\n`);

fs.writeFileSync(path.join(exportsRoot, "app-icons/browserconfig.xml"), `<?xml version="1.0" encoding="utf-8"?>
<browserconfig><msapplication><tile><square150x150logo src="mstile-150x150.png"/><square310x310logo src="mstile-310x310.png"/><TileColor>#171714</TileColor></tile></msapplication></browserconfig>\n`);

ensure(webPublic);
fs.copyFileSync(path.join(source, "wordmark-primary.svg"), path.join(webPublic, "wordmark.svg"));
fs.copyFileSync(path.join(source, "wordmark-reverse.svg"), path.join(webPublic, "wordmark-reverse.svg"));
fs.copyFileSync(path.join(source, "mark-primary.svg"), path.join(webPublic, "mark.svg"));
fs.copyFileSync(path.join(source, "mark-light.svg"), path.join(webPublic, "mark-light.svg"));
fs.copyFileSync(path.join(source, "favicon.svg"), path.join(webPublic, "favicon.svg"));
fs.copyFileSync(path.join(source, "social-card-1200x630.svg"), path.join(webPublic, "social-card.svg"));

console.log(`Rendered ${jobs.length} PNG exports plus WebP derivatives.`);
