"use client";

import { useState, type ReactNode } from "react";
import { assetRegistry } from "../assets";
import { ProviderLogo } from "../ui/provider-logo";
import "./leaderboard-first.css";

type Period = "Today" | "7 days" | "Season";

type LeaderboardEntry = {
  rank: number;
  name: string;
  handle: string;
  initial: string;
  burnToday: string;
  sevenDayBurn: string;
  topModel: "GPT-5.4" | "Claude 3.7";
  movement: number;
  avatar: number;
  current?: boolean;
};

export const leaderboardFirstFixture: LeaderboardEntry[] = [
  { rank: 1, name: "Alex Chen", handle: "alexchen", initial: "A", avatar: 5, burnToday: "124.7M", sevenDayBurn: "612.3M", topModel: "GPT-5.4", movement: 5 },
  { rank: 2, name: "Maya Patel", handle: "mayapatel", initial: "M", avatar: 6, burnToday: "112.3M", sevenDayBurn: "565.9M", topModel: "Claude 3.7", movement: 2 },
  { rank: 3, name: "Jordan Lee", handle: "jordanlee", initial: "J", avatar: 3, burnToday: "105.8M", sevenDayBurn: "539.1M", topModel: "GPT-5.4", movement: 4 },
  { rank: 4, name: "Taylor Kim", handle: "taylorkim", initial: "T", avatar: 4, burnToday: "97.6M", sevenDayBurn: "512.6M", topModel: "Claude 3.7", movement: -1 },
  { rank: 5, name: "Riley Morgan", handle: "rileymorgan", initial: "R", avatar: 2, burnToday: "92.1M", sevenDayBurn: "489.3M", topModel: "GPT-5.4", movement: 1 },
  { rank: 6, name: "Devon Brooks", handle: "devonbrooks", initial: "D", avatar: 7, burnToday: "88.9M", sevenDayBurn: "467.8M", topModel: "Claude 3.7", movement: 2 },
  { rank: 7, name: "Vedant", handle: "vedant", initial: "V", avatar: 0, burnToday: "86.4M", sevenDayBurn: "498.7M", topModel: "GPT-5.4", movement: 3, current: true },
  { rank: 8, name: "Sam Rivera", handle: "samrivera", initial: "S", avatar: 1, burnToday: "81.1M", sevenDayBurn: "476.2M", topModel: "GPT-5.4", movement: -1 },
  { rank: 9, name: "Jamie Wu", handle: "jamiewu", initial: "J", avatar: 8, burnToday: "76.2M", sevenDayBurn: "441.6M", topModel: "Claude 3.7", movement: 2 },
  { rank: 10, name: "Parker Zhao", handle: "parkerzhao", initial: "P", avatar: 0, burnToday: "72.4M", sevenDayBurn: "419.3M", topModel: "Claude 3.7", movement: -2 },
];

function Avatar({ entry }: { entry: LeaderboardEntry }) {
  if (entry.current) return <span className="vm-lf-avatar has-photo"><img src={assetRegistry.fixtures.currentUser} alt="" /></span>;
  const column = entry.avatar % 3;
  const row = Math.floor(entry.avatar / 3);
  return <span className="vm-lf-avatar has-sprite" style={{ backgroundImage: `url("${assetRegistry.fixtures.leaderboardAvatarSprite}")`, backgroundPosition: `${column * 50}% ${row * 50}%` }} aria-hidden="true" />;
}

function TrophyIcon() {
  return <svg className="vm-lf-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z"/><path d="M7 6H4v2a4 4 0 0 0 4 4M17 6h3v2a4 4 0 0 1-4 4"/></svg>;
}

function PulseIcon() {
  return <svg className="vm-lf-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h4l2.5-6 4.5 12 3-7h4"/></svg>;
}

function RivalIcon() {
  return <svg className="vm-lf-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="7" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 4a3 3 0 0 1 0 6M18 13a5 5 0 0 1 3 5v2"/></svg>;
}

function SearchIcon() {
  return <svg className="vm-lf-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>;
}

function RefreshIcon() {
  return <svg className="vm-lf-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 0 0-14.9-3M4 5v5h5M4 13a8 8 0 0 0 14.9 3M20 19v-5h-5"/></svg>;
}

function StatusRegion({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`vm-lf-status-region ${className}`.trim()}>{children}</div>;
}

function PlayerStatusStrip() {
  return (
    <section className="vm-lf-status" aria-label="Your leaderboard status">
      <StatusRegion className="vm-lf-identity">
        <span className="vm-lf-player-avatar"><img src={assetRegistry.fixtures.currentUser} alt="Vedant" /><i aria-label="Online" /></span>
        <div><h1>Vedant</h1><p>@vedant</p></div>
      </StatusRegion>
      <StatusRegion className="vm-lf-metric">
        <span className="vm-lf-icon-field"><TrophyIcon /></span>
        <span className="vm-lf-metric-main vm-lf-num">#07</span>
      </StatusRegion>
      <StatusRegion className="vm-lf-metric">
        <span className="vm-lf-icon-field is-positive"><PulseIcon /></span>
        <span className="vm-lf-metric-copy"><span className="vm-lf-metric-main vm-lf-num">86.4M</span><span className="vm-lf-metric-note">today</span></span>
        <span className="vm-lf-movement is-up vm-lf-num" aria-label="3 places up">↑ 3</span>
      </StatusRegion>
      <StatusRegion className="vm-lf-metric">
        <span className="vm-lf-provider"><ProviderLogo provider="openai" size={22} decorative />GPT-5.4</span>
      </StatusRegion>
      <StatusRegion className="vm-lf-rival">
        <span className="vm-lf-icon-field is-rival"><RivalIcon /></span>
        <div><div className="vm-lf-rival-label">Closest rival</div><h2>Sam Rivera</h2><div className="vm-lf-rival-meta vm-lf-num"><span>#08</span><span>81.1M</span></div></div>
        <span className="vm-lf-chevron" aria-hidden="true">›</span>
      </StatusRegion>
    </section>
  );
}

function PeriodControl({ value, onChange }: { value: Period; onChange: (value: Period) => void }) {
  const periods: Period[] = ["Today", "7 days", "Season"];
  return <div className="vm-lf-period" role="group" aria-label="Leaderboard period">{periods.map((period) => <button type="button" key={period} className={value === period ? "is-active" : ""} aria-pressed={value === period} onClick={() => onChange(period)}>{period}</button>)}</div>;
}

function ModelIdentifier({ model }: { model: LeaderboardEntry["topModel"] }) {
  const claude = model.startsWith("Claude");
  return <span className="vm-lf-model"><ProviderLogo provider={claude ? "claude" : "openai"} size={16} decorative />{model}</span>;
}

function LeaderboardDataTable() {
  return (
    <table className="vm-lf-table">
      <thead><tr><th>Rank</th><th>User</th><th className="is-numeric">Burn today</th><th className="is-numeric">7d burn</th><th>Top model</th><th className="is-numeric">Change</th></tr></thead>
      <tbody>{leaderboardFirstFixture.map((entry) => (
        <tr key={entry.handle} className={entry.current ? "is-current" : undefined}>
          <td className="vm-lf-rank vm-lf-num">{String(entry.rank).padStart(2, "0")}</td>
          <td><div className="vm-lf-user"><Avatar entry={entry} /><span className="vm-lf-user-copy"><strong>{entry.name}</strong><small>@{entry.handle}</small></span></div></td>
          <td className="is-numeric vm-lf-value vm-lf-num">{entry.burnToday}</td>
          <td className="is-numeric vm-lf-value vm-lf-num">{entry.sevenDayBurn}</td>
          <td><ModelIdentifier model={entry.topModel} /></td>
          <td className="is-numeric"><span className={`vm-lf-change ${entry.movement > 0 ? "is-up" : "is-down"} vm-lf-num`} aria-label={`${Math.abs(entry.movement)} places ${entry.movement > 0 ? "up" : "down"}`}>{entry.movement > 0 ? "↑" : "↓"} {Math.abs(entry.movement)}</span></td>
        </tr>
      ))}</tbody>
    </table>
  );
}

function TrendCard() {
  return (
    <section className="vm-lf-panel vm-lf-rail-card vm-lf-trend-card" aria-labelledby="trend-heading">
      <h2 id="trend-heading">7-day trend</h2>
      <div className="vm-lf-lead"><strong className="vm-lf-num">5.3M</strong> lead</div>
      <div className="vm-lf-chart" role="img" aria-label="Seven-day burn trend rising from 55 million to 100 million tokens">
        <svg viewBox="0 0 400 210" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="vm-lf-trend-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5a38ff" stopOpacity=".16"/><stop offset="1" stopColor="#5a38ff" stopOpacity=".015"/></linearGradient></defs><line className="vm-lf-grid-line" x1="0" y1="30" x2="350" y2="30"/><line className="vm-lf-grid-line" x1="0" y1="84" x2="350" y2="84"/><line className="vm-lf-grid-line" x1="0" y1="138" x2="350" y2="138"/><polygon className="vm-lf-trend-fill" points="0,150 48,132 95,124 143,96 190,86 238,68 285,52 333,28 333,166 0,166"/><polyline className="vm-lf-trend" points="0,150 48,132 95,124 143,96 190,86 238,68 285,52 333,28"/><g className="vm-lf-points"><circle cx="0" cy="150" r="3.5"/><circle cx="48" cy="132" r="3.5"/><circle cx="95" cy="124" r="3.5"/><circle cx="143" cy="96" r="3.5"/><circle cx="190" cy="86" r="3.5"/><circle cx="238" cy="68" r="3.5"/><circle cx="285" cy="52" r="3.5"/><circle cx="333" cy="28" r="4"/></g></svg>
        <span className="vm-lf-axis is-right is-100 vm-lf-num">100M</span><span className="vm-lf-axis is-right is-80 vm-lf-num">80M</span><span className="vm-lf-axis is-right is-60 vm-lf-num">60M</span>
        <div className="vm-lf-axis vm-lf-dates"><span>May 15</span><span>May 17</span><span>May 19</span><span>May 21</span></div>
      </div>
    </section>
  );
}

function CompareRow({ name, value, photo, rival }: { name: string; value: string; photo?: boolean; rival?: boolean }) {
  return <div className="vm-lf-compare-row">{photo ? <span className="vm-lf-avatar has-photo"><img src={assetRegistry.fixtures.currentUser} alt="" /></span> : <span className="vm-lf-avatar has-sprite" style={{ backgroundImage: `url("${assetRegistry.fixtures.leaderboardAvatarSprite}")`, backgroundPosition: "50% 0%" }} aria-hidden="true" />}<div><strong>{name}</strong><span className={`vm-lf-bar${rival ? " is-rival" : ""}`}><i /></span></div><span className="vm-lf-compare-value vm-lf-num">{value}</span></div>;
}

function RivalComparisonCard() {
  return <section className="vm-lf-panel vm-lf-rail-card vm-lf-rival-card" aria-labelledby="closest-heading"><h2 id="closest-heading">Closest rival</h2><div className="vm-lf-compare"><CompareRow name="Vedant" value="86.4M" photo /><CompareRow name="Sam Rivera" value="81.1M" rival /></div><p className="vm-lf-ahead"><strong className="vm-lf-num">5.3M</strong> ahead</p><button type="button" className="vm-lf-profile">View profile</button></section>;
}

export function LeaderboardFirstPrototype() {
  const [period, setPeriod] = useState<Period>("Today");
  return (
    <div className="vm-lf-page">
      <header className="vm-lf-header"><div className="vm-lf-header-inner"><a className="wordmark" href="/" aria-label="vibemaxxing home"><img src={assetRegistry.brand.wordmark} alt="vibemaxxing" /></a><nav aria-label="Primary"><a href="/" className="is-active" aria-current="page">Leaderboard</a><a href="/activity">Activity</a><a href="/friends">Friends</a><a href="/boards/founders-house">Boards</a></nav><button type="button" className="vm-lf-search"><SearchIcon /><span>Search</span></button><a className="vm-lf-account" aria-label="Open Vedant account" href="/profile/vedant"><img src={assetRegistry.fixtures.currentUser} alt="" /><span aria-hidden="true">⌄</span></a></div></header>
      <main className="vm-lf-main"><PlayerStatusStrip /><div className="vm-lf-workspace"><section className="vm-lf-panel vm-lf-leaderboard" aria-label={`${period} leaderboard`}><div className="vm-lf-toolbar"><PeriodControl value={period} onChange={setPeriod} /><span className="vm-lf-freshness"><RefreshIcon />Updates every 30s</span></div><LeaderboardDataTable /></section><aside className="vm-lf-rail" aria-label="Leaderboard context"><TrendCard /><RivalComparisonCard /></aside></div></main>
    </div>
  );
}
