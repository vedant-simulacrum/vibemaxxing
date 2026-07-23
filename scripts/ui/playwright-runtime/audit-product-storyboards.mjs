import AxeBuilder from "@axe-core/playwright";
import { chromium } from "playwright";

const baseUrl = process.env.STORYBOOK_URL ?? "http://127.0.0.1:4173";
const stories = ["public-profile", "rival-comparison", "friends", "activity-and-notifications", "board-standings"];
const browser = await chromium.launch({ headless: true });
const failures = [];

try {
  for (const story of stories) {
    const page = await browser.newPage({ viewport: { width: 1536, height: 1024 } });
    await page.goto(`${baseUrl}/iframe.html?id=approved-baseline-product-screens--${story}&viewMode=story`, { waitUntil: "networkidle" });
    await page.waitForSelector(".vm-sb-page");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    for (const violation of results.violations) failures.push(`${story}: ${violation.id} — ${violation.help}`);

    await page.keyboard.press("Tab");
    const firstFocus = await page.evaluate(() => document.activeElement?.getAttribute("aria-label") || document.activeElement?.textContent?.trim());
    if (!firstFocus) failures.push(`${story}: keyboard focus did not enter the page`);

    await page.getByRole("button", { name: "Search" }).click();
    if (!await page.getByRole("dialog", { name: "Search VibeMaxxing" }).isVisible()) failures.push(`${story}: search dialog did not open`);
    await page.keyboard.press("Escape");
    if (await page.getByRole("dialog", { name: "Search VibeMaxxing" }).count()) failures.push(`${story}: search dialog did not close with Escape`);
    await page.close();
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(failures.map((failure) => `- ${failure}`).join("\n"));
  process.exit(1);
}
console.log(`Accessibility and keyboard interaction audit passed for ${stories.length} approved product screens.`);
