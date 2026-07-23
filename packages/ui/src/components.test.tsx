import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import {
  ChoiceGroup,
  EvidenceBadge,
  LedgerRow,
  ProductAvatar,
  ProductButton,
  ProductShell,
  ProductStateBoundary,
  ProductTabs,
  Progress,
  ProviderLogo,
  RankMovement,
  Wordmark,
  providerLogoRegistry,
  type LedgerPerson,
} from "./components";
import { LeaderboardBentoPrototype, leaderboardFixture } from "./concepts/leaderboard-bento";

const person: LedgerPerson = { rank: 1, name: "Maya Chen", handle: "mayac", initials: "MC", burn: 148.2, cash: 392.14, change: 2, evidence: "Hardened", active: "Codex", tint: "plum" };

test("Wordmark uses the approved outlined asset", () => {
  const html = renderToStaticMarkup(<Wordmark/>);
  assert.match(html, /\/brand-assets\/brand\/source\/wordmark-no-rule\.svg/);
  assert.match(html, /alt="vibemaxxing"/);
});

test("ChoiceGroup exposes selected state", () => {
  const html = renderToStaticMarkup(<ChoiceGroup label="Scope" items={["Global", "Friends"] as const} value="Global" onChange={() => {}}/>);
  assert.match(html, /aria-label="Scope"/);
  assert.match(html, /aria-pressed="true">Global/);
  assert.match(html, /aria-pressed="false">Friends/);
});

test("RankMovement communicates direction without color", () => {
  assert.match(renderToStaticMarkup(<RankMovement value={3}/>), /aria-label="3 places up"/);
  assert.match(renderToStaticMarkup(<RankMovement value={-2}/>), /aria-label="2 places down"/);
  assert.match(renderToStaticMarkup(<RankMovement value={0}/>), /aria-label="No rank change"/);
});

test("EvidenceBadge renders every approved evidence level", () => {
  for (const level of ["Hardened", "Standard", "Imported"] as const) assert.match(renderToStaticMarkup(<EvidenceBadge level={level}/>), new RegExp(level));
});

test("Progress clamps values and exposes progress semantics", () => {
  const html = renderToStaticMarkup(<Progress value={120} label="Completion"/>);
  assert.match(html, /role="progressbar"/);
  assert.match(html, /aria-valuenow="100"/);
  assert.match(html, /--vm-progress-value:100%/);
});

test("provider logo registry exposes governed local SVG assets", () => {
  assert.equal(Object.keys(providerLogoRegistry).length, 15);
  const providersRoot = resolve(process.cwd(), "../../assets/providers");
  const manifest = JSON.parse(readFileSync(resolve(providersRoot, "manifest.json"), "utf8")) as { icons: Array<{ id: string; file: string }> };
  assert.deepEqual(manifest.icons.map(({ id }) => id).sort(), Object.keys(providerLogoRegistry).sort());
  for (const { file } of manifest.icons) assert.equal(existsSync(resolve(providersRoot, file)), true, `missing provider asset: ${file}`);
  const html = renderToStaticMarkup(<ProviderLogo provider="claude" size={16} />);
  assert.match(html, /\/brand-assets\/providers\/icons\/claude\.svg/);
  assert.match(html, /alt="Claude"/);
  assert.match(renderToStaticMarkup(<ProviderLogo provider="openai" decorative />), /aria-hidden="true"/);
});

test("LedgerRow composes identity, evidence, presence, metric, and action label", () => {
  const html = renderToStaticMarkup(<LedgerRow person={person} metric="tokens"/>);
  for (const expected of ["Maya Chen", "@mayac", "Hardened", "Codex", "148.2M", "View Maya Chen&#x27;s profile"]) assert.match(html, new RegExp(expected));
});

test("product shell owns shared navigation, brand, search, and account controls", () => {
  const html = renderToStaticMarkup(<ProductShell active="Friends"><main>Content</main></ProductShell>);
  for (const expected of ["vibemaxxing home", "Primary", 'aria-current="page"', "Search", "Open account", "Content"]) {
    assert.match(html, new RegExp(expected));
  }
});

test("product primitives expose governed semantics", () => {
  assert.match(renderToStaticMarkup(<ProductAvatar id={0} online label="Vedant, online" />), /vedant-avatar\.png/);
  assert.match(renderToStaticMarkup(<ProductButton tone="danger">Remove rival</ProductButton>), /vm-sb-button danger/);
  const tabs = renderToStaticMarkup(<ProductTabs labels={["Today", "Season"]} active="Today" />);
  assert.match(tabs, /role="tablist"/);
  assert.match(tabs, /aria-selected="true"/);
});

test("difficult product states preserve explicit user-facing meaning", () => {
  const offline = renderToStaticMarkup(<ProductStateBoundary state="offline"><main>Ledger</main></ProductStateBoundary>);
  assert.match(offline, /You are offline/);
  assert.match(offline, /role="alert"/);
  const quarantined = renderToStaticMarkup(<ProductStateBoundary state="quarantined"><main>Ledger</main></ProductStateBoundary>);
  assert.match(quarantined, /Score under review/);
  assert.doesNotMatch(quarantined, /cheat-proof/i);
});

test("deprecated bento fixture remains renderable as design history", () => {
  const current = leaderboardFixture.find((entry) => entry.handle === "vedant");
  const rival = leaderboardFixture.find((entry) => entry.handle === "samrivera");
  assert.equal(current?.rank, 7);
  assert.equal(current?.burnToday, "86.4M");
  assert.equal(rival?.rank, 8);
  assert.equal(rival?.burnToday, "81.1M");
  assert.equal((Number.parseFloat(current!.burnToday) - Number.parseFloat(rival!.burnToday)).toFixed(1), "5.3");

  const html = renderToStaticMarkup(<LeaderboardBentoPrototype/>);
  for (const expected of ["Leaderboard", "Sam is 5.3M behind", "Updates every 30s", "Showing top 10 of 2,842 users"]) {
    assert.match(html, new RegExp(expected));
  }
});
