import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const output = resolve(process.argv[2] ?? "storybook-captures");
const baseUrl = process.env.STORYBOOK_URL ?? "http://127.0.0.1:4173";
const stories = [
  "public-profile",
  "rival-comparison",
  "friends",
  "activity-and-notifications",
  "board-standings",
];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const story of stories) {
    const page = await browser.newPage({ viewport: { width: 1536, height: 1024 }, deviceScaleFactor: 1 });
    await page.goto(`${baseUrl}/iframe.html?id=approved-baseline-product-screens--${story}&viewMode=story`, { waitUntil: "networkidle" });
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
      throw new Error(`InterVariable failed to load for ${story}`);
    }
    await page.screenshot({ path: resolve(output, `${story}.png`) });
    await page.close();
  }
} finally {
  await browser.close();
}
