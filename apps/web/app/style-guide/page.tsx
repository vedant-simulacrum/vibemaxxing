"use client";

import { useState } from "react";
import { Avatar, ChoiceGroup, EvidenceBadge, Icon, IconButton, LedgerRow, MetricValue, PresenceIndicator, Progress, RankMovement, Wordmark, type LedgerPerson } from "@vibemaxxing/ui";

const sample: LedgerPerson = { rank: 1, name: "Maya Chen", handle: "mayac", initials: "MC", burn: 148.2, cash: 392.14, change: 2, evidence: "Hardened", active: "Codex", tint: "plum" };
const scopes = ["Global", "Friends", "Boards"] as const;

export default function StyleGuidePage() {
  const [scope, setScope] = useState<(typeof scopes)[number]>("Global");

  return <main className="style-guide-page">
    <header className="style-guide-header"><Wordmark href="/"/><div><span>UI system</span><strong>Executable component catalogue</strong></div></header>

    <section className="style-guide-intro"><p className="eyebrow">Implemented inventory</p><h1>Reusable interface components</h1><p>Rendered from <code>@vibemaxxing/ui</code>. This route documents real components and difficult states; proposed components remain in the inventory until implemented.</p></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>Brand and icons</h2><p>Approved outlined wordmark and one consistent outline icon family.</p></div><div className="showcase-stage row"><Wordmark/>{(["globe", "search", "bell", "shield", "users", "arrow"] as const).map(name => <Icon key={name} name={name}/>)}</div></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>IconButton</h2><p>Accessible names are required. Disabled state remains visibly unavailable.</p></div><div className="showcase-stage row"><IconButton label="Search" icon="search"/><IconButton label="Notifications" icon="bell"/><IconButton label="Unavailable action" icon="copy" disabled/></div></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>ChoiceGroup</h2><p>Finite single-choice controls expose pressed state and semantic labels.</p></div><div className="showcase-stage"><ChoiceGroup className="scope-tabs" label="Leaderboard scope" items={scopes} value={scope} onChange={setScope}/></div></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>Identity and presence</h2><p>Avatar fallbacks, private-safe presence, and approved color tints.</p></div><div className="showcase-stage row">{(["plum", "sand", "blue", "rose", "green", "amber", "violet", "cyan"] as const).map((tint, index) => <Avatar key={tint} tint={tint} initials={["MC", "LP", "NW", "IK", "DS", "AM", "SR", "KA"][index]}/>)}<PresenceIndicator agent="Codex"/></div></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>Evidence and movement</h2><p>Meaning is always present in text or an accessible name, never color alone.</p></div><div className="showcase-stage row"><EvidenceBadge level="Hardened"/><EvidenceBadge level="Standard"/><EvidenceBadge level="Imported"/><RankMovement value={4}/><RankMovement value={0}/><RankMovement value={-2}/></div></section>

    <section className="component-showcase"><div className="showcase-copy"><h2>Metrics and progress</h2><p>Token Burn and Estimated Cash Burn remain explicitly distinguished.</p></div><div className="showcase-stage metric-examples"><MetricValue metric="tokens" tokens={148.2} cash={392.14}/><MetricValue metric="cash" tokens={148.2} cash={392.14}/><Progress value={68} label="68 percent complete"/></div></section>

    <section className="component-showcase full"><div className="showcase-copy"><h2>LedgerRow</h2><p>The canonical responsive public-ledger record composed from shared identity, movement, evidence, presence, and metric components.</p></div><div className="showcase-stage ledger-preview"><LedgerRow person={sample} metric="tokens"/><LedgerRow person={{...sample, rank: 2, name: "Leon Park", handle: "leonp", initials: "LP", change: -1, evidence: "Standard", active: undefined, tint: "sand"}} metric="cash"/></div></section>
  </main>;
}
