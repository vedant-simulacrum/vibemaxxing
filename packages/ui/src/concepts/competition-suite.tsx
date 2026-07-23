"use client";

import { useState, type ReactNode } from "react";
import {
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleUserRound,
  Clock3,
  Flame,
  Globe2,
  Info,
  ListFilter,
  LockKeyhole,
  Search,
  Shield,
  ShieldCheck,
  Trophy,
  Users,
} from "../ui/product-icons";
import {
  ProductAvatar,
  ProductButton,
  ProductModel,
  ProductMovement,
  ProductNotice,
  ProductPanel,
  ProductShell,
  ProductTabs,
  ProductTrendChart,
  ProductUserIdentity,
  type FixtureAvatarId,
} from "../patterns/product-system";
import "./product-storyboards.css";
import "./competition-suite.css";

export const leaderboardScopes = ["Global", "Friends", "Boards", "Organizations"] as const;
export const leaderboardPeriods = ["Today", "Daily", "Weekly", "Monthly", "Seasonal", "Yearly", "Lifetime"] as const;
export const ownProfileSections = ["Overview", "Analytics", "Connections", "Privacy"] as const;

export type LeaderboardScope = (typeof leaderboardScopes)[number];
export type LeaderboardPeriod = (typeof leaderboardPeriods)[number];
export type OwnProfileSection = (typeof ownProfileSections)[number];

type CompetitionEntry = {
  rank: number;
  name: string;
  handle: string;
  avatar: FixtureAvatarId;
  burn: string;
  estimatedCash: string;
  model: "GPT-5.4" | "Claude 3.7" | "Gemini 2.5";
  change: number;
  evidence: "Hardened" | "Standard";
  active?: boolean;
  current?: boolean;
};

const competitors: CompetitionEntry[] = [
  { rank: 1, name: "Alex Chen", handle: "alexchen", avatar: 5, burn: "124.7M", estimatedCash: "$83.14", model: "GPT-5.4", change: 5, evidence: "Hardened", active: true },
  { rank: 2, name: "Maya Patel", handle: "mayapatel", avatar: 6, burn: "112.3M", estimatedCash: "$74.83", model: "Claude 3.7", change: 2, evidence: "Standard" },
  { rank: 3, name: "Jordan Lee", handle: "jordanlee", avatar: 3, burn: "105.8M", estimatedCash: "$70.51", model: "GPT-5.4", change: 4, evidence: "Hardened", active: true },
  { rank: 4, name: "Taylor Kim", handle: "taylorkim", avatar: 4, burn: "97.6M", estimatedCash: "$65.05", model: "Claude 3.7", change: -1, evidence: "Standard" },
  { rank: 5, name: "Riley Morgan", handle: "rileymorgan", avatar: 2, burn: "92.1M", estimatedCash: "$61.39", model: "Gemini 2.5", change: 1, evidence: "Standard" },
  { rank: 6, name: "Devon Brooks", handle: "devonbrooks", avatar: 7, burn: "88.9M", estimatedCash: "$59.26", model: "Claude 3.7", change: 2, evidence: "Hardened" },
  { rank: 7, name: "Vedant", handle: "vedant", avatar: 0, burn: "86.4M", estimatedCash: "$57.59", model: "GPT-5.4", change: 3, evidence: "Hardened", active: true, current: true },
  { rank: 8, name: "Sam Rivera", handle: "samrivera", avatar: 1, burn: "81.1M", estimatedCash: "$54.06", model: "GPT-5.4", change: -1, evidence: "Standard", active: true },
  { rank: 9, name: "Jamie Wu", handle: "jamiewu", avatar: 8, burn: "76.2M", estimatedCash: "$50.79", model: "Claude 3.7", change: 2, evidence: "Hardened" },
  { rank: 10, name: "Parker Zhao", handle: "parkerzhao", avatar: 4, burn: "72.4M", estimatedCash: "$48.26", model: "Gemini 2.5", change: -2, evidence: "Standard" },
];

const scopeCopy: Record<LeaderboardScope, { title: string; detail: string; memberCount: string }> = {
  Global: { title: "Global leaderboard", detail: "Every accepted ranked identity, ordered by verified Token Burn.", memberCount: "48,291 ranked" },
  Friends: { title: "Friends leaderboard", detail: "Your accepted friends, with active-agent presence and rank movement.", memberCount: "14 friends" },
  Boards: { title: "Board leaderboard", detail: "A combined view across the private and community boards you joined.", memberCount: "4 boards" },
  Organizations: { title: "Organization leaderboard", detail: "Members competing inside organizations where you have access.", memberCount: "2 organizations" },
};

function EvidenceStatus({ value }: { value: CompetitionEntry["evidence"] }) {
  return <span className={`vm-suite-evidence ${value.toLowerCase()}`}><ShieldCheck size={15} aria-hidden="true" />{value}</span>;
}

function LeaderboardRow({ entry }: { entry: CompetitionEntry }) {
  return (
    <div className={`vm-suite-ledger-row${entry.current ? " current" : ""}`}>
      <span className="vm-suite-rank">{String(entry.rank).padStart(2, "0")}</span>
      <ProductUserIdentity name={entry.name} handle={entry.handle} avatar={entry.avatar} online={entry.active} />
      <strong>{entry.burn}<small>tokens</small></strong>
      <strong>{entry.estimatedCash}<small>estimated</small></strong>
      <ProductModel name={entry.model} />
      <EvidenceStatus value={entry.evidence} />
      <ProductMovement value={entry.change} />
      <a href={`/profile/${entry.handle}`} aria-label={`View ${entry.name}'s profile`}><ChevronRight size={18} aria-hidden="true" /></a>
    </div>
  );
}

function ScopeControl({ value, onChange }: { value: LeaderboardScope; onChange: (scope: LeaderboardScope) => void }) {
  return (
    <div className="vm-suite-scope-control" aria-label="Leaderboard scope">
      {leaderboardScopes.map((scope) => (
        <button type="button" className={scope === value ? "active" : ""} aria-pressed={scope === value} onClick={() => onChange(scope)} key={scope}>
          {scope}
        </button>
      ))}
      <button type="button" disabled title="Country leaderboards are post-launch">Countries <small>later</small></button>
    </div>
  );
}

function StandingCard() {
  return (
    <ProductPanel className="vm-suite-standing">
      <header><span>Your standing</span><a href="/me">View profile</a></header>
      <div><strong>#07</strong><ProductMovement value={3} /></div>
      <p>Top 0.02% globally</p>
      <dl><div><dt>Token Burn</dt><dd>86.4M</dd></div><div><dt>Next rank</dt><dd>2.5M away</dd></div></dl>
    </ProductPanel>
  );
}

function RivalCard() {
  return (
    <ProductPanel className="vm-suite-rival">
      <header><span>Closest rival</span><a href="/rivals/samrivera">Compare</a></header>
      <ProductUserIdentity name="Sam Rivera" handle="samrivera" avatar={1} online />
      <div className="vm-suite-rival-gap"><span>5.3M ahead</span><small>6.5% lead</small></div>
      <div className="vm-suite-gap-track" aria-label="Vedant leads Sam Rivera by 5.3 million tokens"><i /></div>
    </ProductPanel>
  );
}

function RulesCard({ period }: { period: LeaderboardPeriod }) {
  return (
    <ProductPanel className="vm-suite-rules">
      <header><span>Competition contract</span><Info size={17} aria-hidden="true" /></header>
      <dl>
        <div><dt><Flame size={17} aria-hidden="true" />Ranking metric</dt><dd>Token Burn</dd></div>
        <div><dt><CalendarDays size={17} aria-hidden="true" />Window</dt><dd>{period}</dd></div>
        <div><dt><Shield size={17} aria-hidden="true" />Accepted evidence</dt><dd>Standard + Hardened</dd></div>
        <div><dt><ListFilter size={17} aria-hidden="true" />Imported history</dt><dd>Excluded</dd></div>
      </dl>
    </ProductPanel>
  );
}

export function LeaderboardHubStoryboard({
  initialScope = "Global",
  initialPeriod = "Today",
}: {
  initialScope?: LeaderboardScope;
  initialPeriod?: LeaderboardPeriod;
}) {
  const [scope, setScope] = useState<LeaderboardScope>(initialScope);
  const [period, setPeriod] = useState<LeaderboardPeriod>(initialPeriod);
  const copy = scopeCopy[scope];
  return (
    <ProductShell active="Leaderboard">
      <main className="vm-sb-content vm-suite-page">
        <section className="vm-suite-heading">
          <div><p>Competitive ledger</p><h1>{copy.title}</h1><span>{copy.detail}</span></div>
          <div className="vm-suite-heading-meta"><Clock3 size={16} aria-hidden="true" />Updated 12 seconds ago　·　{copy.memberCount}</div>
        </section>
        <ScopeControl value={scope} onChange={setScope} />
        <div className="vm-suite-layout">
          <ProductPanel className="vm-suite-ledger" label={`${scope} ${period} leaderboard`}>
            <header>
              <ProductTabs labels={leaderboardPeriods} active={period} onChange={(value) => setPeriod(value as LeaderboardPeriod)} label="Leaderboard period" />
              <label className="vm-suite-filter"><Search size={17} aria-hidden="true" /><span className="visually-hidden">Filter leaderboard</span><input type="search" placeholder="Filter competitors" /></label>
            </header>
            <div className="vm-suite-summary">
              <span><small>Window</small><strong>{period}</strong></span>
              <span><small>Total accepted burn</small><strong>4.83T</strong></span>
              <span><small>Active now</small><strong>1,284</strong></span>
              <span><small>Your movement</small><strong><ProductMovement value={3} /></strong></span>
            </div>
            <div className="vm-suite-ledger-head">
              <span>Rank</span><span>Competitor</span><span>Token Burn</span><span>Cash Burn</span><span>Top model</span><span>Evidence</span><span>Change</span><span />
            </div>
            <div className="vm-suite-ledger-body">{competitors.map((entry) => <LeaderboardRow entry={entry} key={entry.handle} />)}</div>
            <footer><span>Estimated Cash Burn is a server-interpreted estimate, never actual spend.</span><ProductButton>Load more</ProductButton></footer>
          </ProductPanel>
          <aside className="vm-suite-rail"><StandingCard /><RivalCard /><RulesCard period={period} /></aside>
        </div>
      </main>
    </ProductShell>
  );
}

function Metric({ label, value, detail, icon }: { label: string; value: string; detail: string; icon: ReactNode }) {
  return <ProductPanel className="vm-suite-metric"><span>{icon}</span><div><small>{label}</small><strong>{value}</strong><p>{detail}</p></div></ProductPanel>;
}

function OverviewSection() {
  return (
    <>
      <div className="vm-suite-metrics">
        <Metric label="Rank today" value="#07" detail="↑ 3 since yesterday" icon={<Trophy aria-hidden="true" />} />
        <Metric label="Token Burn" value="86.4M" detail="498.7M over 7 days" icon={<Flame aria-hidden="true" />} />
        <Metric label="Cash Burn" value="$57.59" detail="Estimated, not actual spend" icon={<CircleUserRound aria-hidden="true" />} />
        <Metric label="Active streak" value="14 days" detail="28 active days this month" icon={<CalendarDays aria-hidden="true" />} />
      </div>
      <div className="vm-suite-profile-grid">
        <ProductPanel className="vm-suite-profile-trend"><header><div><h2>Competitive trend</h2><p>Accepted Token Burn only</p></div><ProductTabs labels={["7 days", "30 days", "Season"]} active="7 days" /></header><ProductTrendChart label="Vedant accepted Token Burn over seven days" /></ProductPanel>
        <ProductPanel className="vm-suite-model-mix"><h2>Model mix</h2>{[["GPT-5.4", "58%", "openai"], ["Claude 3.7", "29%", "claude"], ["Gemini 2.5", "13%", "gemini"]].map(([name, value]) => <div key={name}><ProductModel name={name} /><span className="vm-suite-bar"><i style={{ width: value }} /></span><b>{value}</b></div>)}</ProductPanel>
      </div>
    </>
  );
}

function AnalyticsSection() {
  return (
    <div className="vm-suite-analytics">
      <ProductPanel className="vm-suite-breakdown"><header><div><h2>Agent breakdown</h2><p>Local aggregates accepted into competition</p></div><ProductTabs labels={["Today", "7 days", "30 days"]} active="Today" /></header>{[["Codex", "42.8M", "49.5%"], ["Claude Code", "24.6M", "28.5%"], ["OpenCode", "12.1M", "14.0%"], ["Other certified", "6.9M", "8.0%"]].map(([name, burn, share]) => <div className="vm-suite-breakdown-row" key={name}><b>{name}</b><span className="vm-suite-bar"><i style={{ width: share }} /></span><strong>{burn}</strong><small>{share}</small></div>)}</ProductPanel>
      <ProductPanel className="vm-suite-imported"><header><div><p>Private analytics only</p><h2>Imported history</h2></div><LockKeyhole size={22} aria-hidden="true" /></header><strong>1.92B tokens</strong><span>Imported from earlier local records</span><ProductNotice title="Never enters competition" tone="warning">Imported history is private, visibly labelled Imported, and excluded from every active ranking window.</ProductNotice></ProductPanel>
    </div>
  );
}

function ConnectionsSection() {
  const sources = [
    ["Codex", "Active now", "Last accepted 12s ago", "healthy"],
    ["Claude Code", "Connected", "Last accepted 4m ago", "healthy"],
    ["OpenCode", "Needs attention", "Adapter update available", "warning"],
  ];
  return (
    <div className="vm-suite-connections">
      <ProductPanel className="vm-suite-source-list"><header><div><h2>Connected agents</h2><p>Only fixed-schema aggregate accounting leaves this device.</p></div><ProductButton>Connect agent</ProductButton></header>{sources.map(([name, state, detail, tone]) => <div className="vm-suite-source" key={name}><span className={`vm-suite-health ${tone}`} /><ProductModel name={name} /><div><b>{state}</b><small>{detail}</small></div><ProductButton>Manage</ProductButton></div>)}</ProductPanel>
      <aside className="vm-suite-connection-rail"><ProductPanel><h2>Collector health</h2><strong>Healthy</strong><p>Queue empty · last sync 12s ago</p><dl><div><dt>Device</dt><dd>Vedant’s MacBook</dd></div><div><dt>Local queue</dt><dd>0 claims</dd></div><div><dt>Clock status</dt><dd>In tolerance</dd></div></dl></ProductPanel><ProductNotice title="Privacy boundary">Prompts, code, filenames, repository names, tool content, and project names never cross the device boundary.</ProductNotice></aside>
    </div>
  );
}

function PrivacySection() {
  return (
    <div className="vm-suite-privacy">
      <ProductPanel className="vm-suite-privacy-controls">
        <header><div><h2>Public profile controls</h2><p>Preview exactly what other competitors can see.</p></div><ProductButton>Open public preview</ProductButton></header>
        {[
          ["Public ranking identity", "Name, handle, avatar, current rank, and accepted Token Burn", true],
          ["Model mix", "Show the model-family percentage breakdown", true],
          ["Active-agent presence", "Show only that a qualifying agent is active", true],
          ["Board memberships", "Show public boards; private boards remain private", false],
          ["Estimated Cash Burn", "Show the explicit estimate on your public profile", false],
        ].map(([title, detail, checked]) => <label className="vm-suite-toggle" key={String(title)}><span><b>{title}</b><small>{detail}</small></span><input type="checkbox" defaultChecked={Boolean(checked)} /><i aria-hidden="true" /></label>)}
      </ProductPanel>
      <aside className="vm-suite-privacy-rail">
        <ProductPanel><ShieldCheck size={25} aria-hidden="true" /><h2>One ranked identity</h2><p>Uniqueness is enforced with privacy safeguards, conflict recovery, and appeal rights.</p><span>Verification method is intentionally vendor-neutral until the governing contract is accepted.</span></ProductPanel>
        <ProductPanel><h2>Never public</h2><ul><li>Prompts or responses</li><li>Code, diffs, or tool content</li><li>Filenames, paths, or repositories</li><li>Imported-history details</li></ul></ProductPanel>
      </aside>
    </div>
  );
}

export function OwnProfileStoryboard({ initialSection = "Overview" }: { initialSection?: OwnProfileSection }) {
  const [section, setSection] = useState<OwnProfileSection>(initialSection);
  return (
    <ProductShell active="Leaderboard">
      <main className="vm-sb-content vm-suite-profile">
        <ProductPanel className="vm-suite-profile-hero">
          <ProductAvatar id={0} size={92} online label="Vedant, active now" />
          <div><p>Your ranking identity</p><h1>Vedant <ShieldCheck size={21} aria-label="Verified competitor" /></h1><span>@vedant　·　Bengaluru, India　·　Joined May 2025</span></div>
          <div className="vm-suite-profile-actions"><ProductButton>Edit profile</ProductButton><ProductButton tone="primary">Share profile</ProductButton></div>
        </ProductPanel>
        <div className="vm-suite-profile-nav"><ProductTabs labels={ownProfileSections} active={section} onChange={(value) => setSection(value as OwnProfileSection)} label="Own profile section" /><span><CheckCircle2 size={16} aria-hidden="true" />Fixture-backed prototype</span></div>
        {section === "Overview" && <OverviewSection />}
        {section === "Analytics" && <AnalyticsSection />}
        {section === "Connections" && <ConnectionsSection />}
        {section === "Privacy" && <PrivacySection />}
      </main>
    </ProductShell>
  );
}
