import type { CSSProperties, ReactNode } from "react";

export type IconName = "bell" | "search" | "chevron" | "arrow" | "shield" | "copy" | "users" | "globe" | "menu";

const iconPaths: Record<IconName, ReactNode> = {
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

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg aria-hidden="true" className="icon" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{iconPaths[name]}</svg>;
}

export function Wordmark({ href = "#", reverse = false }: { href?: string; reverse?: boolean }) {
  return <a className="wordmark" href={href} aria-label="vibemaxxing home"><img src={reverse ? "/brand/wordmark-reverse.svg" : "/brand/wordmark.svg"} alt="vibemaxxing"/></a>;
}

export function IconButton({ label, icon, className = "", onClick, expanded, disabled = false }: { label: string; icon: IconName; className?: string; onClick?: () => void; expanded?: boolean; disabled?: boolean }) {
  return <button className={`icon-button ${className}`.trim()} aria-label={label} onClick={onClick} aria-expanded={expanded} disabled={disabled}><Icon name={icon}/></button>;
}

export function ChoiceGroup<T extends string>({ label, items, value, onChange, className = "", getLabel = item => item }: { label: string; items: readonly T[]; value: T; onChange: (value: T) => void; className?: string; getLabel?: (item: T) => string }) {
  return <div className={className} role="group" aria-label={label}>{items.map(item => <button type="button" key={item} onClick={() => onChange(item)} className={value === item ? "active" : ""} aria-pressed={value === item}>{getLabel(item)}</button>)}</div>;
}

export type AvatarTint = "plum" | "sand" | "blue" | "rose" | "green" | "amber" | "violet" | "cyan";

export function Avatar({ initials, tint, label }: { initials: string; tint: AvatarTint; label?: string }) {
  return <span className={`avatar ${tint}`} aria-label={label} aria-hidden={label ? undefined : true}>{initials}</span>;
}

export function RankMovement({ value, label }: { value: number; label?: string }) {
  const accessible = label ?? (value === 0 ? "No rank change" : `${Math.abs(value)} places ${value > 0 ? "up" : "down"}`);
  if (value === 0) return <span className="movement flat" aria-label={accessible}>—</span>;
  return <span className={`movement ${value > 0 ? "up" : "down"}`} aria-label={accessible}><span aria-hidden="true">{value > 0 ? "↑" : "↓"}</span>{Math.abs(value)}</span>;
}

export type EvidenceLevel = "Hardened" | "Standard" | "Imported";

export function EvidenceBadge({ level }: { level: EvidenceLevel }) {
  return <span className={`evidence ${level.toLowerCase()}`}>{level === "Hardened" && <Icon name="shield" size={12}/>} {level}</span>;
}

export function PresenceIndicator({ agent }: { agent: string }) {
  return <span className="presence"><i aria-hidden="true"/> <span className="visually-hidden">Active in </span>{agent}</span>;
}

export function MetricValue({ metric, tokens, cash }: { metric: "tokens" | "cash"; tokens: number; cash: number }) {
  return <span className="burn-cell"><strong>{metric === "tokens" ? `${tokens.toFixed(1)}M` : `$${cash.toFixed(2)}`}</strong><small>{metric === "tokens" ? "tokens" : "estimated"}</small></span>;
}

export type LedgerPerson = {
  rank: number;
  name: string;
  handle: string;
  initials: string;
  burn: number;
  cash: number;
  change: number;
  evidence: EvidenceLevel;
  active?: string;
  tint: AvatarTint;
};

export function LedgerRow({ person, metric }: { person: LedgerPerson; metric: "tokens" | "cash" }) {
  return <div className="ledger-row">
    <div className="rank-cell"><span className="rank">{String(person.rank).padStart(2, "0")}</span><RankMovement value={person.change}/></div>
    <div className="person-cell"><Avatar initials={person.initials} tint={person.tint}/><span className="person-meta"><strong>{person.name}</strong><small>@{person.handle}</small></span>{person.active && <PresenceIndicator agent={person.active}/>}</div>
    <div className="evidence-cell"><EvidenceBadge level={person.evidence}/></div>
    <MetricValue metric={metric} tokens={person.burn} cash={person.cash}/>
    <button className="row-open" aria-label={`View ${person.name}'s profile`}><Icon name="chevron" size={16}/></button>
  </div>;
}

export function Progress({ value, label, compact = false }: { value: number; label: string; compact?: boolean }) {
  const bounded = Math.max(0, Math.min(100, value));
  return <span className={`vm-progress ${compact ? "compact" : ""}`} role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={bounded}><i style={{ "--vm-progress-value": `${bounded}%` } as CSSProperties}/></span>;
}
