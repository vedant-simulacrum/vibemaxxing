"use client";

import { useMemo, useState } from "react";

type Person = {
  rank: number;
  name: string;
  handle: string;
  initials: string;
  burn: number;
  cash: number;
  change: number;
  evidence: "Hardened" | "Standard";
  active?: string;
  tint: string;
};

const people: Person[] = [
  { rank: 1, name: "Maya Chen", handle: "mayac", initials: "MC", burn: 148.2, cash: 392.14, change: 2, evidence: "Hardened", active: "Codex", tint: "plum" },
  { rank: 2, name: "Leon Park", handle: "leonp", initials: "LP", burn: 136.8, cash: 348.92, change: -1, evidence: "Standard", active: "Claude Code", tint: "sand" },
  { rank: 3, name: "Noah Williams", handle: "noahw", initials: "NW", burn: 121.4, cash: 305.48, change: 1, evidence: "Hardened", tint: "blue" },
  { rank: 4, name: "Iris K", handle: "irisk", initials: "IK", burn: 113.9, cash: 284.61, change: 0, evidence: "Standard", tint: "rose" },
  { rank: 5, name: "Dani Sol", handle: "danisol", initials: "DS", burn: 98.6, cash: 246.03, change: 3, evidence: "Hardened", active: "OpenCode", tint: "green" },
  { rank: 6, name: "Arjun Mehta", handle: "arjunm", initials: "AM", burn: 91.2, cash: 228.72, change: -2, evidence: "Standard", tint: "amber" },
  { rank: 7, name: "Sofia Reyes", handle: "sofiar", initials: "SR", burn: 87.5, cash: 218.46, change: 4, evidence: "Hardened", tint: "violet" },
  { rank: 8, name: "Kaito", handle: "kaito", initials: "KA", burn: 78.1, cash: 195.82, change: -1, evidence: "Standard", tint: "cyan" },
];

const periods = ["Today", "Week", "Month", "Season", "Year", "Lifetime"];
const scopes = ["Global", "Friends", "Boards", "Countries"];

function Icon({ name, size = 18 }: { name: "bell" | "search" | "chevron" | "arrow" | "shield" | "copy" | "users" | "globe" | "menu"; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    shield: <path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z"/>,
    copy: <><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></>,
    globe: <><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
  };
  return <svg aria-hidden="true" className="icon" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function Wordmark() {
  return <a className="wordmark" href="#" aria-label="vibemaxxing home">vibemaxxing</a>;
}

function Movement({ value }: { value: number }) {
  if (value === 0) return <span className="movement flat">—</span>;
  return <span className={`movement ${value > 0 ? "up" : "down"}`}><span aria-hidden="true">{value > 0 ? "↑" : "↓"}</span>{Math.abs(value)}</span>;
}

function LeaderRow({ person, metric }: { person: Person; metric: "tokens" | "cash" }) {
  return (
    <div className="ledger-row">
      <div className="rank-cell"><span className="rank">{String(person.rank).padStart(2, "0")}</span><Movement value={person.change}/></div>
      <div className="person-cell">
        <span className={`avatar ${person.tint}`}>{person.initials}</span>
        <span className="person-meta"><strong>{person.name}</strong><small>@{person.handle}</small></span>
        {person.active && <span className="presence"><i/> {person.active}</span>}
      </div>
      <div className="evidence-cell"><span className={`evidence ${person.evidence.toLowerCase()}`}>{person.evidence === "Hardened" && <Icon name="shield" size={12}/>} {person.evidence}</span></div>
      <div className="burn-cell"><strong>{metric === "tokens" ? `${person.burn.toFixed(1)}M` : `$${person.cash.toFixed(2)}`}</strong><small>{metric === "tokens" ? "tokens" : "estimated"}</small></div>
      <button className="row-open" aria-label={`View ${person.name}'s profile`}><Icon name="chevron" size={16}/></button>
    </div>
  );
}

export default function Home() {
  const [period, setPeriod] = useState("Week");
  const [scope, setScope] = useState("Global");
  const [metric, setMetric] = useState<"tokens" | "cash">("tokens");
  const [copied, setCopied] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const total = useMemo(() => people.reduce((sum, person) => sum + person.burn, 0), []);

  function copyInstall() {
    navigator.clipboard?.writeText("npx vibemaxxing");
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <main>
      <header className="topbar">
        <div className="topbar-inner">
          <Wordmark/>
          <nav className={mobileNav ? "open" : ""} aria-label="Primary navigation">
            <a className="active" href="#leaderboard">Leaderboard</a>
            <a href="#activity">Activity</a>
            <a href="#friends">Friends</a>
            <a href="#boards">Boards</a>
          </nav>
          <div className="header-actions">
            <button className="icon-button search-button" aria-label="Search"><Icon name="search"/></button>
            <button className="icon-button notification" aria-label="Notifications"><Icon name="bell"/><i/></button>
            <button className="profile-button" aria-label="Open profile"><span>VK</span><span className="profile-copy"><strong>Vedant</strong><small>Rank 184</small></span><span className="caret">⌄</span></button>
            <button className="icon-button mobile-menu" onClick={() => setMobileNav(!mobileNav)} aria-label="Toggle menu" aria-expanded={mobileNav}><Icon name="menu"/></button>
          </div>
        </div>
      </header>

      <div className="shell">
        <section className="content" id="leaderboard">
          <div className="eyebrow-row"><span className="eyebrow"><Icon name="globe" size={14}/> Public ledger</span><span className="updated"><i/> Live · Updated 8s ago</span></div>
          <div className="title-row">
            <div><h1>{scope} leaderboard</h1><p>See who is burning the most across their AI agents.</p></div>
            <button className="install-button" onClick={copyInstall}><span className="terminal-mark">›_</span><code>npx vibemaxxing</code><span className="copy-state">{copied ? "Copied" : <Icon name="copy" size={15}/>}</span></button>
          </div>

          <div className="scope-tabs" aria-label="Leaderboard scope">
            {scopes.map(item => <button key={item} onClick={() => setScope(item)} className={scope === item ? "active" : ""}>{item}</button>)}
          </div>

          <div className="ledger">
            <div className="ledger-controls">
              <div className="period-tabs" aria-label="Leaderboard period">
                {periods.map(item => <button key={item} onClick={() => setPeriod(item)} className={period === item ? "active" : ""}>{item}</button>)}
              </div>
              <div className="metric-switch" aria-label="Ranking metric">
                <button className={metric === "tokens" ? "active" : ""} onClick={() => setMetric("tokens")}>Token Burn</button>
                <button className={metric === "cash" ? "active" : ""} onClick={() => setMetric("cash")}>Est. Cash</button>
              </div>
            </div>

            <div className="ledger-summary">
              <div><span>{scope} burn · {period.toLowerCase()}</span><strong>{metric === "tokens" ? `${total.toFixed(1)}M` : "$2,220.18"}</strong><small>{metric === "tokens" ? "tokens across 48,204 agents" : "API-equivalent estimate"}</small></div>
              <div className="summary-note"><span>24h velocity</span><strong>+12.8%</strong><small>against previous period</small></div>
            </div>

            <div className="ledger-head"><span>Rank</span><span>Builder</span><span>Evidence</span><span>{metric === "tokens" ? "Token burn" : "Est. cash burn"}</span><span/></div>
            <div className="ledger-body">{people.map(person => <LeaderRow key={person.handle} person={person} metric={metric}/>)}</div>
            <button className="load-more">View full leaderboard <Icon name="arrow" size={15}/></button>
          </div>

          <p className="method-note"><Icon name="shield" size={14}/> Rankings use privacy-safe usage claims. Prompts, code, and project names never enter the public ledger. <a href="#method">How counting works</a></p>
        </section>

        <aside className="rail">
          <section className="rail-section your-rank">
            <div className="rail-label"><span>Your position</span><button>View profile <Icon name="arrow" size={13}/></button></div>
            <div className="rank-display"><strong>184</strong><div><span className="up">↑ 23</span><small>this week</small></div></div>
            <div className="rank-meter"><i style={{ width: "68%" }}/></div>
            <div className="rank-stats"><span><small>Token Burn</small><strong>12.84M</strong></span><span><small>To overtake</small><strong>+860K</strong></span></div>
          </section>

          <section className="rail-section rivals" id="friends">
            <div className="rail-label"><span>Close rivals</span><button>See all</button></div>
            <div className="rival-list">
              <div className="rival"><span className="avatar blue">AC</span><span><strong>Alex C.</strong><small>410K ahead</small></span><span className="rival-rank">#183</span></div>
              <div className="rival"><span className="avatar sand">JN</span><span><strong>Jules N.</strong><small>190K behind</small></span><span className="rival-rank">#185</span></div>
              <div className="rival"><span className="avatar green">RK</span><span><strong>Riya K.</strong><small>540K behind</small></span><span className="rival-rank">#186</span></div>
            </div>
          </section>

          <section className="rail-section activity-card" id="activity">
            <div className="rail-label"><span>Live now</span><span className="live-count">1,284 active</span></div>
            <div className="agent-bars">
              <div><span>Codex</span><i><b style={{ width: "82%" }}/></i><strong>542</strong></div>
              <div><span>Claude Code</span><i><b style={{ width: "57%" }}/></i><strong>378</strong></div>
              <div><span>Cursor</span><i><b style={{ width: "33%" }}/></i><strong>221</strong></div>
              <div><span>Other</span><i><b style={{ width: "21%" }}/></i><strong>143</strong></div>
            </div>
            <p><span className="pulse-dot"/> Presence shows the active agent only—never the project.</p>
          </section>

          <section className="callout" id="boards">
            <div className="callout-icon"><Icon name="users" size={18}/></div>
            <div><strong>Make it personal.</strong><p>Create a private board for your team, hacker house, or group chat.</p><a href="#create">Create a board <Icon name="arrow" size={14}/></a></div>
          </section>
        </aside>
      </div>

      <footer><Wordmark/><span>Public competition. Private transcripts.</span><div><a href="#privacy">Privacy</a><a href="#github">GitHub</a><a href="#docs">Docs</a></div></footer>
    </main>
  );
}
