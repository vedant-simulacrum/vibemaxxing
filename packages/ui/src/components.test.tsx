import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import { ChoiceGroup, EvidenceBadge, LedgerRow, Progress, RankMovement, Wordmark, type LedgerPerson } from "./components";

const person: LedgerPerson = { rank: 1, name: "Maya Chen", handle: "mayac", initials: "MC", burn: 148.2, cash: 392.14, change: 2, evidence: "Hardened", active: "Codex", tint: "plum" };

test("Wordmark uses the approved outlined asset", () => {
  const html = renderToStaticMarkup(<Wordmark/>);
  assert.match(html, /\/brand\/wordmark\.svg/);
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

test("LedgerRow composes identity, evidence, presence, metric, and action label", () => {
  const html = renderToStaticMarkup(<LedgerRow person={person} metric="tokens"/>);
  for (const expected of ["Maya Chen", "@mayac", "Hardened", "Codex", "148.2M", "View Maya Chen&#x27;s profile"]) assert.match(html, new RegExp(expected));
});
