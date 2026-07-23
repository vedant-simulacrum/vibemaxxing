import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const output = resolve(process.argv[2] ?? "storybook-captures");
const baseUrl = process.env.STORYBOOK_URL ?? "http://127.0.0.1:4173";
const stories = [
  { id: "approved-baseline-product-screens--public-profile", file: "public-profile" },
  { id: "approved-baseline-product-screens--rival-comparison", file: "rival-comparison" },
  { id: "approved-baseline-product-screens--friends", file: "friends" },
  { id: "approved-baseline-product-screens--activity-and-notifications", file: "activity-and-notifications" },
  { id: "approved-baseline-product-screens--board-standings", file: "board-standings" },
  { id: "candidate-batch-leaderboard-and-own-profile--global-leaderboard", file: "candidate-global-leaderboard" },
  { id: "candidate-batch-leaderboard-and-own-profile--own-profile-overview", file: "candidate-own-profile-overview" },
  { id: "candidate-batch-leaderboard-and-own-profile--own-profile-analytics", file: "candidate-own-profile-analytics" },
  { id: "candidate-batch-leaderboard-and-own-profile--own-profile-connections", file: "candidate-own-profile-connections" },
  { id: "candidate-batch-leaderboard-and-own-profile--own-profile-privacy", file: "candidate-own-profile-privacy" },
];
const viewports = [
  { name: "desktop", width: 1536, height: 1024 },
  { name: "tablet", width: 1024, height: 1366 },
  { name: "mobile", width: 390, height: 844 },
];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of viewports) {
    for (const story of stories) {
      const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, deviceScaleFactor: 1 });
      await page.goto(`${baseUrl}/iframe.html?id=${story.id}&viewMode=story`, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForSelector(".vm-sb-page .vm-sb-header .vm-sb-search", { state: "visible" });
      await page.evaluate(async () => {
        await Promise.all([...document.images].map(image => image.complete
          ? image.decode().catch(() => undefined)
          : new Promise(resolve => {
              image.addEventListener("load", resolve, { once: true });
              image.addEventListener("error", resolve, { once: true });
            })));
        await new Promise(requestAnimationFrame);
        await new Promise(requestAnimationFrame);
      });
      if (!await page.evaluate(() => document.fonts.check("14px InterVariable"))) {
        throw new Error(`InterVariable failed to load for ${story.id} at ${viewport.name}`);
      }
      const suffix = viewport.name === "desktop" ? "" : `-${viewport.name}`;
      await page.screenshot({ path: resolve(output, `${story.file}${suffix}.png`), fullPage: viewport.name !== "desktop" });
      await page.close();
    }
  }
} finally {
  await browser.close();
}
