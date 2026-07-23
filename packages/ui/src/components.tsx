import type { CSSProperties, ComponentType, SVGProps } from "react";
import { assetRegistry } from "./assets";
import { ArrowRight, Bell, ChevronRight, Copy, Globe2, Menu, Search, Shield, Users } from "./ui/product-icons";

export { ProviderLogo, providerLogoRegistry, type ProviderLogoName } from "./ui/provider-logo";
export {
  ProductActivityEventRow,
  ProductAvatar,
  ProductBoardStandingRow,
  ProductButton,
  ProductDialog,
  ProductFriendRow,
  ProductIconButton,
  ProductModel,
  ProductMovement,
  ProductNotice,
  ProductPanel,
  ProductRankChart,
  ProductShell,
  ProductSparkline,
  ProductStateBoundary,
  ProductTabs,
  ProductTrendChart,
  ProductUserIdentity,
  type FixtureAvatarId,
  type ProductPerson,
  type ProductNav,
  type ProductState,
} from "./patterns/product-system";

export type IconName = "bell" | "search" | "chevron" | "arrow" | "shield" | "copy" | "users" | "globe" | "menu";

const iconComponents: Record<IconName, ComponentType<SVGProps<SVGSVGElement>>> = {
  bell: Bell,
  search: Search,
  chevron: ChevronRight,
  arrow: ArrowRight,
  shield: Shield,
  copy: Copy,
  users: Users,
  globe: Globe2,
  menu: Menu,
};

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const Glyph = iconComponents[name];
  return <Glyph aria-hidden="true" className="icon" width={size} height={size} strokeWidth={1.8} />;
}

export function Wordmark({ href = "#", reverse = false }: { href?: string; reverse?: boolean }) {
  return <a className="wordmark" href={href} aria-label="vibemaxxing home"><img src={reverse ? assetRegistry.brand.wordmarks.reverse : assetRegistry.brand.wordmark} alt="vibemaxxing"/></a>;
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
