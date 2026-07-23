import AxeBuilder from "@axe-core/playwright";
import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const baseUrl = process.env.STORYBOOK_URL ?? "http://127.0.0.1:4173";
const reportPath = resolve("packages/ui/storybook-diffs/accessibility-audit.json");

const baseStories = [
  { id: "public-profile", label: "Public profile" },
  { id: "rival-comparison", label: "Rival comparison" },
  { id: "friends", label: "Friends" },
  { id: "activity-and-notifications", label: "Activity and notifications" },
  { id: "board-standings", label: "Board standings" },
];

const viewports = [
  { name: "desktop", width: 1536, height: 1024, interaction: "search" },
  { name: "tablet", width: 1024, height: 1366, interaction: "search" },
  { name: "mobile", width: 390, height: 844, interaction: "navigation" },
];

const stateScreens = ["profile", "rival", "friends", "activity", "board"];
const governedStates = ["loading", "empty", "error", "offline", "stale", "private", "blocked", "restricted", "quarantined"];
const accessibilityTags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
const failures = [];
const scenarios = [];

function storyUrl(storyId) {
  return `${baseUrl}/iframe.html?id=${storyId}&viewMode=story`;
}

function recordViolations(label, results) {
  for (const violation of results.violations) {
    const nodes = violation.nodes
      .map((node) => `${node.target.join(" ")}: ${node.failureSummary ?? node.html}`)
      .join(" | ");
    failures.push(`${label}: ${violation.id} — ${violation.help} — ${nodes}`);
  }
}

async function assertKeyboardEntry(page, label) {
  await page.keyboard.press("Tab");
  const focus = await page.evaluate(() => {
    const active = document.activeElement;
    if (!active || active === document.body) return null;
    const rect = active.getBoundingClientRect();
    return {
      label: active.getAttribute("aria-label") || active.textContent?.trim() || active.tagName,
      visible: rect.width > 0 && rect.height > 0,
    };
  });
  if (!focus?.label || !focus.visible) failures.push(`${label}: keyboard focus did not enter a visible control`);
}

async function assertSearchDialog(page, label) {
  const search = page.getByRole("button", { name: "Search" });
  await search.click();
  const dialog = page.getByRole("dialog", { name: "Search VibeMaxxing" });
  if (!await dialog.isVisible()) failures.push(`${label}: search dialog did not open`);
  const input = dialog.getByRole("searchbox");
  if (!await input.evaluate((element) => element === document.activeElement)) failures.push(`${label}: search dialog did not move focus to its search input`);
  await page.keyboard.press("Escape");
  if (await dialog.count()) failures.push(`${label}: search dialog did not close with Escape`);
}

async function assertMobileNavigation(page, label) {
  const openButton = page.getByRole("button", { name: "Open navigation" });
  await openButton.click();
  const closeButton = page.getByRole("button", { name: "Close navigation" });
  if (!await closeButton.isVisible()) failures.push(`${label}: mobile navigation did not open`);
  if (await closeButton.getAttribute("aria-expanded") !== "true") failures.push(`${label}: mobile navigation did not expose expanded state`);
  await page.keyboard.press("Escape");
  const restoredButton = page.getByRole("button", { name: "Open navigation" });
  if (!await restoredButton.isVisible()) failures.push(`${label}: mobile navigation did not close with Escape`);
  if (await restoredButton.getAttribute("aria-expanded") !== "false") failures.push(`${label}: mobile navigation did not clear expanded state`);
}

async function auditBaseStory(browser, story, viewport) {
  const label = `${story.label} / ${viewport.name}`;
  const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
  const page = await context.newPage();
  page.setDefaultTimeout(10_000);
  try {
    await page.goto(storyUrl(`approved-baseline-product-screens--${story.id}`), { waitUntil: "networkidle" });
    await page.waitForSelector(".vm-sb-page", { state: "visible" });
    const results = await new AxeBuilder({ page }).withTags(accessibilityTags).analyze();
    recordViolations(label, results);
    await assertKeyboardEntry(page, label);
    if (viewport.interaction === "search") await assertSearchDialog(page, label);
    if (viewport.interaction === "navigation") await assertMobileNavigation(page, label);
    scenarios.push({
      kind: "base-responsive",
      story: story.id,
      viewport: viewport.name,
      violations: results.violations.length,
      passes: results.passes.length,
      incomplete: results.incomplete.length,
    });
  } catch (error) {
    failures.push(`${label}: ${error instanceof Error ? error.message : String(error)}`);
  } finally {
    await context.close();
  }
}

async function auditExceptionalState(browser, screen, state) {
  const storyId = `approved-baseline-product-state-matrix--${screen}-${state}`;
  const label = `${screen} / ${state} / desktop`;
  const context = await browser.newContext({ viewport: { width: 1536, height: 1024 } });
  const page = await context.newPage();
  page.setDefaultTimeout(10_000);
  try {
    await page.goto(storyUrl(storyId), { waitUntil: "networkidle" });
    await page.waitForSelector(".vm-product-state", { state: "visible" });
    const message = page.locator(".vm-product-state-message");
    if (!await message.isVisible()) failures.push(`${label}: governed state message is not visible`);
    const expectedRole = state === "error" || state === "offline" ? "alert" : "status";
    if (await message.getAttribute("role") !== expectedRole) failures.push(`${label}: expected role ${expectedRole}`);
    const results = await new AxeBuilder({ page }).withTags(accessibilityTags).analyze();
    recordViolations(label, results);
    scenarios.push({
      kind: "exceptional-state",
      story: `${screen}-${state}`,
      viewport: "desktop",
      violations: results.violations.length,
      passes: results.passes.length,
      incomplete: results.incomplete.length,
    });
  } catch (error) {
    failures.push(`${label}: ${error instanceof Error ? error.message : String(error)}`);
  } finally {
    await context.close();
  }
}

const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of viewports) {
    for (const story of baseStories) await auditBaseStory(browser, story, viewport);
  }
  for (const screen of stateScreens) {
    for (const state of governedStates) await auditExceptionalState(browser, screen, state);
  }
} finally {
  await browser.close();
}

const report = {
  schema_version: 1,
  artifact_maturity: "runnable-prototype",
  fixture_policy: "synthetic-only",
  scope: {
    base_screens: baseStories.length,
    responsive_viewports: viewports.map(({ name, width, height }) => ({ name, width, height })),
    responsive_base_scenarios: baseStories.length * viewports.length,
    exceptional_state_scenarios: stateScreens.length * governedStates.length,
    total_scenarios: scenarios.length,
    accessibility_tags: accessibilityTags,
  },
  scenarios,
  failures,
};
await mkdir(dirname(reportPath), { recursive: true });
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

if (failures.length) {
  console.error(failures.map((failure) => `- ${failure}`).join("\n"));
  console.error(`Accessibility report written to ${reportPath}`);
  process.exit(1);
}

console.log(
  `Prototype accessibility and interaction audit passed: ${baseStories.length * viewports.length} responsive base scenarios and ${stateScreens.length * governedStates.length} exceptional-state scenarios.`,
);
console.log(`Accessibility report written to ${reportPath}`);
