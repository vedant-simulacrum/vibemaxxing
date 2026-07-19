"use client";

import { useMemo, useState } from "react";
import { Avatar, ChoiceGroup, Icon, IconButton, LedgerRow, Progress, RankMovement, Wordmark, type LedgerPerson } from "@vibemaxxing/ui";

const people: LedgerPerson[] = [
  { rank: 1, name: "Maya Chen", handle: "mayac", initials: "MC", burn: 148.2, cash: 392.14, change: 2, evidence: "Hardened", active: "Codex", tint: "plum" },
  { rank: 2, name: "Leon Park", handle: "leonp", initials: "LP", burn: 136.8, cash: 348.92, change: -1, evidence: "Standard", active: "Claude Code", tint: "sand" },
  { rank: 3, name: "Noah Williams", handle: "noahw", initials: "NW", burn: 121.4, cash: 305.48, change: 1, evidence: "Hardened", tint: "blue" },
  { rank: 4, name: "Iris K", handle: "irisk", initials: "IK", burn: 113.9, cash: 284.61, change: 0, evidence: "Standard", tint: "rose" },
  { rank: 5, name: "Dani Sol", handle: "danisol", initials: "DS", burn: 98.6, cash: 246.03, change: 3, evidence: "Hardened", active: "OpenCode", tint: "green" },
  { rank: 6, name: "Arjun Mehta", handle: "arjunm", initials: "AM", burn: 91.2, cash: 228.72, change: -2, evidence: "Standard", tint: "amber" },
  { rank: 7, name: "Sofia Reyes", handle: "sofiar", initials: "SR", burn: 87.5, cash: 218.46, change: 4, evidence: "Hardened", tint: "violet" },
  { rank: 8, name: "Kaito", handle: "kaito", initials: "KA", burn: 78.1, cash: 195.82, change: -1, evidence: "Standard", tint: "cyan" },
];

const periods = ["Today", "Week", "Month", "Season", "Year", "Lifetime"] as const;
const scopes = ["Global", "Friends", "Boards", "Countries"] as const;

export default function Home() {
  const [period, setPeriod] = useState<(typeof periods)[number]>("Week");
  const [scope, setScope] = useState<(typeof scopes)[number]>("Global");
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
            <IconButton className="search-button" label="Search" icon="search"/>
            <button className="icon-button notification" aria-label="Notifications"><Icon name="bell"/><i/></button>
            <button className="profile-button" aria-label="Open profile"><span>VK</span><span className="profile-copy"><strong>Vedant</strong><small>Rank 184</small></span><span className="caret">⌄</span></button>
            <IconButton className="mobile-menu" onClick={() => setMobileNav(!mobileNav)} label="Toggle menu" icon="menu" expanded={mobileNav}/>
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

          <ChoiceGroup className="scope-tabs" label="Leaderboard scope" items={scopes} value={scope} onChange={setScope}/>

          <div className="ledger">
            <div className="ledger-controls">
              <ChoiceGroup className="period-tabs" label="Leaderboard period" items={periods} value={period} onChange={setPeriod}/>
              <ChoiceGroup className="metric-switch" label="Ranking metric" items={["tokens", "cash"] as const} value={metric} onChange={setMetric} getLabel={item => item === "tokens" ? "Token Burn" : "Est. Cash"}/>
            </div>

            <div className="ledger-summary">
              <div><span>{scope} burn · {period.toLowerCase()}</span><strong>{metric === "tokens" ? `${total.toFixed(1)}M` : "$2,220.18"}</strong><small>{metric === "tokens" ? "tokens across 48,204 agents" : "API-equivalent estimate"}</small></div>
              <div className="summary-note"><span>24h velocity</span><strong>+12.8%</strong><small>against previous period</small></div>
            </div>

            <div className="ledger-head"><span>Rank</span><span>Builder</span><span>Evidence</span><span>{metric === "tokens" ? "Token burn" : "Est. cash burn"}</span><span/></div>
            <div className="ledger-body">{people.map(person => <LedgerRow key={person.handle} person={person} metric={metric}/>)}</div>
            <button className="load-more">View full leaderboard <Icon name="arrow" size={15}/></button>
          </div>

          <p className="method-note"><Icon name="shield" size={14}/> Rankings use privacy-safe usage claims. Prompts, code, and project names never enter the public ledger. <a href="#method">How counting works</a></p>
        </section>

        <aside className="rail">
          <section className="rail-section your-rank">
            <div className="rail-label"><span>Your position</span><button>View profile <Icon name="arrow" size={13}/></button></div>
            <div className="rank-display"><strong>184</strong><div><RankMovement value={23}/><small>this week</small></div></div>
            <Progress value={68} label="68 percent to next rank"/>
            <div className="rank-stats"><span><small>Token Burn</small><strong>12.84M</strong></span><span><small>To overtake</small><strong>+860K</strong></span></div>
          </section>

          <section className="rail-section rivals" id="friends">
            <div className="rail-label"><span>Close rivals</span><button>See all</button></div>
            <div className="rival-list">
              <div className="rival"><Avatar initials="AC" tint="blue"/><span><strong>Alex C.</strong><small>410K ahead</small></span><span className="rival-rank">#183</span></div>
              <div className="rival"><Avatar initials="JN" tint="sand"/><span><strong>Jules N.</strong><small>190K behind</small></span><span className="rival-rank">#185</span></div>
              <div className="rival"><Avatar initials="RK" tint="green"/><span><strong>Riya K.</strong><small>540K behind</small></span><span className="rival-rank">#186</span></div>
            </div>
          </section>

          <section className="rail-section activity-card" id="activity">
            <div className="rail-label"><span>Live now</span><span className="live-count">1,284 active</span></div>
            <div className="agent-bars">
              <div><span>Codex</span><Progress compact value={82} label="Codex 82 percent"/><strong>542</strong></div>
              <div><span>Claude Code</span><Progress compact value={57} label="Claude Code 57 percent"/><strong>378</strong></div>
              <div><span>Cursor</span><Progress compact value={33} label="Cursor 33 percent"/><strong>221</strong></div>
              <div><span>Other</span><Progress compact value={21} label="Other 21 percent"/><strong>143</strong></div>
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
