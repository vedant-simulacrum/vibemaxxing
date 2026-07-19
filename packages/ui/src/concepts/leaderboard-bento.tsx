import { useState } from "react";
import { Avatar, Icon, Wordmark, type AvatarTint } from "../components";
import "./leaderboard-bento.css";

type Period = "Today" | "7 days" | "Season";

type LeaderboardEntry = {
  rank: number;
  name: string;
  handle: string;
  initials: string;
  burnToday: string;
  sevenDayBurn: string;
  topModel: string;
  movement?: number;
  accent?: boolean;
};

export const leaderboardFixture: LeaderboardEntry[] = [
  { rank: 1, name: "Alex Chen", handle: "alexchen", initials: "A", burnToday: "128.7M", sevenDayBurn: "912.4M", topModel: "GPT-5.4" },
  { rank: 2, name: "Maya Patel", handle: "mayapatel", initials: "M", burnToday: "112.3M", sevenDayBurn: "798.1M", topModel: "GPT-5.4" },
  { rank: 3, name: "Jordan Lee", handle: "jordanlee", initials: "J", burnToday: "97.8M", sevenDayBurn: "645.2M", topModel: "Claude 3.7" },
  { rank: 4, name: "Taylor Kim", handle: "taylorkim", initials: "T", burnToday: "94.2M", sevenDayBurn: "612.7M", topModel: "GPT-5.4" },
  { rank: 5, name: "Riley Morgan", handle: "rileymorgan", initials: "R", burnToday: "91.6M", sevenDayBurn: "588.9M", topModel: "GPT-5.4" },
  { rank: 6, name: "Devon Brooks", handle: "devonbrooks", initials: "D", burnToday: "87.3M", sevenDayBurn: "532.4M", topModel: "Claude 3.7" },
  { rank: 7, name: "Vedant", handle: "vedant", initials: "V", burnToday: "86.4M", sevenDayBurn: "498.7M", topModel: "GPT-5.4", movement: 3, accent: true },
  { rank: 8, name: "Sam Rivera", handle: "samrivera", initials: "S", burnToday: "81.1M", sevenDayBurn: "476.2M", topModel: "GPT-5.4" },
  { rank: 9, name: "Jamie Wu", handle: "jamiewu", initials: "J", burnToday: "76.9M", sevenDayBurn: "445.1M", topModel: "Claude 3.7" },
  { rank: 10, name: "Parker Zhao", handle: "parkerzhao", initials: "P", burnToday: "72.4M", sevenDayBurn: "412.3M", topModel: "GPT-5.4" },
];

function Movement({ value }: { value: number }) {
  if (value === 0) return null;
  return (
    <span className={value > 0 ? "vm-bento-movement is-positive" : "vm-bento-movement is-negative"} aria-label={`${Math.abs(value)} places ${value > 0 ? "up" : "down"}`}>
      <span aria-hidden="true">{value > 0 ? "↑" : "↓"}</span>{Math.abs(value)}
    </span>
  );
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return <span className="vm-bento-eyebrow">{children}</span>;
}

function IdentityTile() {
  return (
    <section className="vm-bento-tile vm-bento-identity" aria-label="Current user">
      <span className="vm-bento-avatar-wrap vm-bento-avatar-lg"><Avatar initials="V" tint="violet" label="Vedant" /></span>
      <div>
        <strong>Vedant</strong>
        <span>@vedant</span>
      </div>
    </section>
  );
}

function MetricTile({ label, children, detail }: { label: string; children: React.ReactNode; detail?: React.ReactNode }) {
  return (
    <section className="vm-bento-tile vm-bento-metric">
      <Eyebrow>{label}</Eyebrow>
      <div className="vm-bento-metric-value">{children}</div>
      {detail ? <div className="vm-bento-metric-detail">{detail}</div> : null}
    </section>
  );
}

function RivalTile() {
  return (
    <section className="vm-bento-tile vm-bento-closest" aria-label="Closest rival">
      <span className="vm-bento-avatar-wrap is-rival"><Avatar initials="S" tint="violet" label="Sam Rivera" /></span>
      <div>
        <Eyebrow>Closest rival</Eyebrow>
        <strong>Sam Rivera</strong>
        <span>#08&nbsp;&nbsp;·&nbsp;&nbsp;81.1M</span>
      </div>
    </section>
  );
}

function PeriodControl({ value, onChange }: { value: Period; onChange: (period: Period) => void }) {
  const periods: Period[] = ["Today", "7 days", "Season"];
  return (
    <div className="vm-bento-period" role="group" aria-label="Leaderboard period">
      {periods.map((period) => (
        <button key={period} type="button" className={period === value ? "is-active" : ""} aria-pressed={period === value} onClick={() => onChange(period)}>
          {period}
        </button>
      ))}
    </div>
  );
}

function LeaderboardTable() {
  const tints: AvatarTint[] = ["plum", "sand", "blue", "rose", "green", "amber", "violet", "violet", "cyan", "sand"];
  return (
    <div className="vm-bento-table-wrap">
      <table className="vm-bento-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>User</th>
            <th className="is-numeric">Burn today <span aria-hidden="true">↓</span></th>
            <th className="is-numeric vm-bento-seven-day">7d burn</th>
            <th className="vm-bento-model">Top model</th>
            <th><span className="vm-sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody>
          {leaderboardFixture.map((entry) => (
            <tr key={entry.handle} className={entry.accent ? "is-current" : undefined}>
              <td className="vm-bento-rank">
                <span>{String(entry.rank).padStart(2, "0")}</span>
                {entry.movement ? <Movement value={entry.movement} /> : null}
              </td>
              <td>
                <div className="vm-bento-user">
                  <span className={`vm-bento-avatar-wrap${entry.handle === "samrivera" ? " is-rival" : ""}`}><Avatar initials={entry.initials} tint={tints[entry.rank - 1]} label={`${entry.name} avatar`} /></span>
                  <span><strong>{entry.name}</strong><small>@{entry.handle}</small></span>
                </div>
              </td>
              <td className="is-numeric vm-bento-number">{entry.burnToday}</td>
              <td className="is-numeric vm-bento-number vm-bento-seven-day">{entry.sevenDayBurn}</td>
              <td className="vm-bento-model vm-bento-number">{entry.topModel}</td>
              <td>
                <button type="button" className="vm-bento-row-action" aria-label={`More actions for ${entry.name}`}><span aria-hidden="true">•••</span></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <footer className="vm-bento-table-footer">Showing top 10 of 2,842 users</footer>
    </div>
  );
}

function RivalSnapshot() {
  return (
    <section className="vm-bento-panel vm-bento-rival-card" aria-labelledby="rival-heading">
      <div className="vm-bento-rival-heading">
        <span className="vm-bento-avatar-wrap is-rival"><Avatar initials="S" tint="violet" label="Sam Rivera" /></span>
        <div><h2 id="rival-heading">Sam Rivera</h2><span>@samrivera</span></div>
        <button type="button" aria-label="Close rival details"><span aria-hidden="true">×</span></button>
      </div>
      <div className="vm-bento-lead"><strong>5.3M lead</strong><span>Sam is 5.3M behind</span></div>
      <dl className="vm-bento-rival-stats">
        <div><dt>Rank</dt><dd>#08</dd></div>
        <div><dt>Burn today</dt><dd>81.1M <small>tokens</small></dd></div>
        <div><dt>7d burn</dt><dd>476.2M <small>tokens</small></dd></div>
        <div><dt>Top model</dt><dd>GPT-5.4</dd></div>
      </dl>
    </section>
  );
}

function ComparisonChart() {
  return (
    <section className="vm-bento-panel vm-bento-chart-card" aria-labelledby="comparison-heading">
      <h2 id="comparison-heading"><Eyebrow>7-day comparison</Eyebrow></h2>
      <div className="vm-bento-chart" role="img" aria-label="Vedant leads Sam Rivera throughout the seven-day comparison and ends at 86.4 million versus 81.1 million tokens">
        <span className="vm-bento-y y100">100M</span><span className="vm-bento-y y75">75M</span><span className="vm-bento-y y50">50M</span><span className="vm-bento-y y25">25M</span><span className="vm-bento-y y0">0</span>
        <svg viewBox="0 0 320 150" preserveAspectRatio="none" aria-hidden="true">
          <g className="vm-bento-grid"><line x1="0" y1="8" x2="320" y2="8"/><line x1="0" y1="43" x2="320" y2="43"/><line x1="0" y1="78" x2="320" y2="78"/><line x1="0" y1="113" x2="320" y2="113"/><line x1="0" y1="148" x2="320" y2="148"/></g>
          <polyline className="vm-bento-line is-user" points="0,116 18,106 36,101 54,102 72,85 90,79 108,82 126,67 144,61 162,68 180,62 198,51 216,49 234,48 252,36 270,38 288,27 306,26 320,20"/>
          <polyline className="vm-bento-line is-rival" points="0,136 18,128 36,119 54,113 72,103 90,104 108,94 126,84 144,87 162,77 180,73 198,66 216,60 234,58 252,52 270,47 288,43 306,38 320,34"/>
        </svg>
        <div className="vm-bento-x"><span>7d ago</span><span>5d ago</span><span>3d ago</span><span>1d ago</span><span>Today</span></div>
      </div>
      <div className="vm-bento-legend"><span><i className="is-user" />Vedant</span><span><i className="is-rival" />Sam Rivera</span></div>
      <div className="vm-bento-movement-block"><Eyebrow>Recent movement</Eyebrow><strong>+12.4% <span aria-hidden="true">↗</span></strong><span>vs 7 days ago</span></div>
      <button type="button" className="vm-bento-profile-link">View profile <span aria-hidden="true">›</span></button>
    </section>
  );
}

export function LeaderboardBentoPrototype() {
  const [period, setPeriod] = useState<Period>("Today");
  return (
    <div className="vm-bento-page">
      <header className="vm-bento-header">
        <div className="vm-bento-header-inner">
          <Wordmark />
          <nav aria-label="Primary">
            <a href="#" className="is-active" aria-current="page">Leaderboard</a>
            <a href="#">Activity</a>
            <a href="#">Friends</a>
          </nav>
          <button type="button" className="vm-bento-search"><Icon name="search" size={16} /><span>Search users…</span><kbd>⌘K</kbd></button>
          <button type="button" className="vm-bento-account"><span className="vm-bento-account-avatar"><Avatar initials="V" tint="violet" label="Vedant account" /></span><span aria-hidden="true">⌄</span></button>
        </div>
      </header>

      <main className="vm-bento-shell">
        <div className="vm-bento-summary">
          <IdentityTile />
          <MetricTile label="Your rank" detail={<Movement value={3} />}>#07</MetricTile>
          <MetricTile label="Burn today" detail="tokens">86.4M</MetricTile>
          <MetricTile label="Top model">GPT-5.4</MetricTile>
          <RivalTile />
        </div>

        <div className="vm-bento-workspace">
          <section className="vm-bento-panel vm-bento-ledger" aria-label={`${period} leaderboard`}>
            <header className="vm-bento-ledger-header">
              <PeriodControl value={period} onChange={setPeriod} />
              <span className="vm-bento-update"><i />Updates every 30s</span>
            </header>
            <LeaderboardTable />
          </section>
          <aside className="vm-bento-rail" aria-label="Closest rival details">
            <RivalSnapshot />
            <ComparisonChart />
          </aside>
        </div>
      </main>
    </div>
  );
}
