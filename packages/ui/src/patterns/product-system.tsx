"use client";

import { useEffect, useId, useState, type CSSProperties, type KeyboardEvent, type ReactNode } from "react";
import { ArrowDown, ArrowUp, Bell, ChevronDown, Menu, Search, X } from "../ui/product-icons";
import { assetRegistry } from "../assets";
import { ProviderLogo } from "../ui/provider-logo";

export type ProductNav = "Leaderboard" | "Activity" | "Friends" | "Boards";
export type FixtureAvatarId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;
export type ProductPerson = {
  name: string;
  handle: string;
  avatar: FixtureAvatarId;
  rank: number;
  burn: string;
  week?: string;
  change?: number;
  model?: "GPT-5.4" | "Claude 3.7";
};
export type ProductState =
  | "ready"
  | "loading"
  | "empty"
  | "error"
  | "offline"
  | "stale"
  | "private"
  | "blocked"
  | "restricted"
  | "quarantined";

const stateCopy: Record<Exclude<ProductState, "ready">, { title: string; detail: string; action?: string }> = {
  loading: { title: "Loading competition data", detail: "The ledger is being reconciled with the latest accepted claims." },
  empty: { title: "Nothing to show yet", detail: "This view will populate after eligible competitive activity is recorded.", action: "Explore the leaderboard" },
  error: { title: "This view could not be loaded", detail: "No score or evidence state has been changed.", action: "Try again" },
  offline: { title: "You are offline", detail: "Showing the last locally available view. New activity will appear after reconnection.", action: "Retry connection" },
  stale: { title: "Data may be out of date", detail: "The last successful refresh was 18 minutes ago.", action: "Refresh" },
  private: { title: "This profile is private", detail: "Competitive totals are visible only to audiences selected by this person." },
  blocked: { title: "This relationship is blocked", detail: "Profiles, activity, and social actions are unavailable between these accounts." },
  restricted: { title: "Account access is restricted", detail: "Some social and ranking actions are temporarily unavailable.", action: "View restriction" },
  quarantined: { title: "Score under review", detail: "Affected claims are excluded from standings until review is complete.", action: "View review status" },
};

export function ProductAvatar({
  id,
  size = 44,
  online = false,
  label = "",
}: {
  id: FixtureAvatarId;
  size?: number;
  online?: boolean;
  label?: string;
}) {
  const source = id === 0 ? assetRegistry.fixtures.currentUser : assetRegistry.fixtures.storyboardAvatar(id);
  return (
    <span
      className="vm-sb-avatar"
      style={{ "--vm-avatar-size": `${size}px` } as CSSProperties}
      aria-label={label || undefined}
      aria-hidden={label ? undefined : true}
    >
      <img src={source} alt="" />
      {online && <i aria-hidden="true" />}
    </span>
  );
}

const productNavigation: Array<{ label: ProductNav; href: string }> = [
  { label: "Leaderboard", href: "/" },
  { label: "Activity", href: "/activity" },
  { label: "Friends", href: "/friends" },
  { label: "Boards", href: "/boards/founders-house" },
];

export function ProductIconButton({
  label,
  children,
  onClick,
  expanded,
  controls,
  className = "",
}: {
  label: string;
  children: ReactNode;
  onClick?: () => void;
  expanded?: boolean;
  controls?: string;
  className?: string;
}) {
  return (
    <button
      type="button"
      className={`vm-sb-icon-button ${className}`.trim()}
      aria-label={label}
      aria-expanded={expanded}
      aria-controls={controls}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export function ProductShell({ active, children }: { active: ProductNav; children: ReactNode }) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const searchId = useId();
  const accountId = useId();
  const mobileId = useId();
  useEffect(() => {
    const closeOverlays = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setSearchOpen(false);
      setAccountOpen(false);
      setMobileOpen(false);
    };
    window.addEventListener("keydown", closeOverlays);
    return () => window.removeEventListener("keydown", closeOverlays);
  }, []);
  return (
    <div className="vm-sb-page">
      <header className="vm-sb-header">
        <a className="vm-sb-wordmark" href="/" aria-label="vibemaxxing home">
          <img src={assetRegistry.brand.wordmark} alt="vibemaxxing" />
        </a>
        <nav id={mobileId} className={mobileOpen ? "mobile-open" : ""} aria-label="Primary">
          {productNavigation.map((item) => (
            <a key={item.label} className={active === item.label ? "active" : ""} aria-current={active === item.label ? "page" : undefined} href={item.href}>
              {item.label}
            </a>
          ))}
        </nav>
        <button className="vm-sb-search" type="button" aria-expanded={searchOpen} aria-controls={searchId} onClick={() => setSearchOpen(true)}>
          <Search size={19} aria-hidden="true" />
          <span>Search</span>
        </button>
        <ProductIconButton
          className="vm-sb-notifications"
          label="Open notifications"
        >
          <Bell size={19} aria-hidden="true" />
        </ProductIconButton>
        <button className="vm-sb-account" type="button" aria-label="Open account" aria-haspopup="menu" aria-expanded={accountOpen} aria-controls={accountId} onClick={() => setAccountOpen((value) => !value)}>
          <ProductAvatar id={0} size={50} />
          <ChevronDown size={17} aria-hidden="true" />
        </button>
        <ProductIconButton
          className="vm-sb-mobile-menu"
          label={mobileOpen ? "Close navigation" : "Open navigation"}
          expanded={mobileOpen}
          controls={mobileId}
          onClick={() => setMobileOpen((value) => !value)}
        >
          {mobileOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
        </ProductIconButton>
        {accountOpen && (
          <div className="vm-sb-account-menu" id={accountId} role="menu" aria-label="Account">
            <a role="menuitem" href="/profile/vedant">View profile</a>
            <a role="menuitem" href="/settings">Settings</a>
            <button role="menuitem" type="button">Sign out</button>
          </div>
        )}
      </header>
      {searchOpen && (
        <ProductDialog title="Search VibeMaxxing" onClose={() => setSearchOpen(false)} id={searchId}>
          <label className="vm-sb-search-field">
            <span>Search people, boards, and leaderboards</span>
            <input autoFocus type="search" placeholder="Search" />
          </label>
          <ProductNotice title="Search is fixture-backed">
            Results remain synthetic until the hosted search contract is implemented.
          </ProductNotice>
        </ProductDialog>
      )}
      {children}
    </div>
  );
}

export function ProductPanel({ className = "", children, label }: { className?: string; children: ReactNode; label?: string }) {
  return <section className={`vm-sb-panel ${className}`.trim()} aria-label={label}>{children}</section>;
}

export function ProductButton({
  children,
  tone = "neutral",
  disabled = false,
  onClick,
}: {
  children: ReactNode;
  tone?: "neutral" | "primary" | "danger";
  disabled?: boolean;
  onClick?: () => void;
}) {
  return <button type="button" disabled={disabled} onClick={onClick} className={`vm-sb-button${tone === "neutral" ? "" : ` ${tone}`}`}>{children}</button>;
}

export function ProductMovement({ value }: { value: number }) {
  const direction = value === 0 ? "flat" : value > 0 ? "up" : "down";
  return (
    <span className={`vm-sb-${direction}`} role="img" aria-label={value === 0 ? "No rank change" : `${Math.abs(value)} places ${direction}`}>
      {value > 0 ? <ArrowUp size={18} aria-hidden="true" /> : value < 0 ? <ArrowDown size={18} aria-hidden="true" /> : "—"}
      {value === 0 ? "" : Math.abs(value)}
    </span>
  );
}

export function ProductModel({ name = "GPT-5.4" }: { name?: string }) {
  const provider = name.startsWith("Claude") ? "claude" : name.startsWith("Gemini") ? "gemini" : "openai";
  return <span className="vm-sb-model"><ProviderLogo provider={provider} size={18} decorative />{name}</span>;
}

export function ProductTabs({
  labels,
  active,
  onChange,
  label = "View",
}: {
  labels: readonly string[];
  active: string;
  onChange?: (value: string) => void;
  label?: string;
}) {
  const moveFocus = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const buttons = Array.from(event.currentTarget.parentElement?.querySelectorAll<HTMLButtonElement>('[role="tab"]') ?? []);
    const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
    buttons[next]?.focus();
    onChange?.(labels[next]);
  };
  return (
    <div className="vm-sb-tabs" role="tablist" aria-label={label}>
      {labels.map((item, index) => (
        <button
          type="button"
          role="tab"
          aria-selected={item === active}
          tabIndex={item === active ? 0 : -1}
          className={item === active ? "active" : ""}
          onClick={() => onChange?.(item)}
          onKeyDown={(event) => moveFocus(event, index)}
          key={item}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

export function ProductUserIdentity({
  name,
  handle,
  avatar,
  size = 44,
  online = false,
}: {
  name: string;
  handle: string;
  avatar: FixtureAvatarId;
  size?: number;
  online?: boolean;
}) {
  return (
    <span className="vm-sb-user-identity">
      <ProductAvatar id={avatar} size={size} online={online} label={`${name}${online ? ", online" : ""}`} />
      <span><b>{name}</b><small>@{handle}</small></span>
    </span>
  );
}

export function ProductFriendRow({ person, active = false }: { person: ProductPerson; active?: boolean }) {
  return (
    <div className="friend-row">
      <div className="friend-name"><ProductUserIdentity name={person.name} handle={person.handle} avatar={person.avatar} size={44} online={active} /></div>
      <span className={active ? "presence" : ""}>{active ? "Burning now" : "Last seen 1h ago"}</span>
      <b>#{String(person.rank).padStart(2, "0")}</b>
      <b>{person.burn}</b>
      <ProductMovement value={person.change ?? 0} />
      <ProductModel name={person.model} />
      <span>3</span>
      <span className="row-actions"><ProductButton>Compare</ProductButton><ProductButton>Rival</ProductButton><span aria-hidden="true">•••</span></span>
    </div>
  );
}

export function ProductBoardStandingRow({ person, current = false }: { person: ProductPerson; current?: boolean }) {
  return (
    <div className={`board-row ${current ? "current" : ""}`}>
      <b>{String(person.rank).padStart(2, "0")}</b>
      <span className="friend-name"><ProductUserIdentity name={person.name} handle={person.handle} avatar={person.avatar} size={41} /></span>
      <b>{person.burn}</b>
      <b>{person.week}</b>
      <ProductModel name={person.model} />
      <ProductMovement value={person.change ?? 0} />
    </div>
  );
}

export function ProductActivityEventRow({
  icon,
  avatar,
  title,
  detail,
  trailing,
  compact = false,
  unread = false,
  tone = "",
}: {
  icon: ReactNode;
  avatar?: FixtureAvatarId;
  title: string;
  detail: string;
  trailing: ReactNode;
  compact?: boolean;
  unread?: boolean;
  tone?: string;
}) {
  return (
    <div className={`event-row${compact ? " compact" : ""}`}>
      <span className={`big-event ${tone}`.trim()}>{icon}</span>
      {avatar !== undefined && <ProductAvatar id={avatar} size={compact ? 40 : 44} />}
      <div><b>{title}</b><small>{detail}</small></div>
      {trailing}
      {unread && <i className="unread" role="img" aria-label="Unread" />}
    </div>
  );
}

export function ProductTrendChart({
  compare = false,
  label = "Token Burn trend",
}: {
  compare?: boolean;
  label?: string;
}) {
  const gradientId = useId().replaceAll(":", "");
  const points = compare
    ? "0,178 53,171 105,158 158,145 210,137 263,127 315,119 368,104 420,91 473,80 525,66 578,56 630,45 683,38 735,27 788,23 840,17"
    : "0,173 44,171 88,168 132,164 176,161 220,159 264,156 308,153 352,149 396,146 440,139 484,114 528,91 572,89 616,85 660,76 704,70 748,65 792,57 836,49";
  return (
    <div className="vm-sb-trend" role="img" aria-label={label}>
      <svg viewBox="0 0 840 210" preserveAspectRatio="none" aria-hidden="true">
        <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0" className="trend-fill-start" /><stop offset="1" className="trend-fill-end" /></linearGradient></defs>
        {[24, 72, 120, 168].map((y) => <line key={y} x1="0" y1={y} x2="840" y2={y} className="grid" />)}
        <polygon points={`${points} 840,198 0,198`} fill={`url(#${gradientId})`} />
        <polyline points={points} className="line" />
        {compare && <polyline points="0,190 53,183 105,173 158,160 210,151 263,145 315,137 368,122 420,110 473,96 525,84 578,72 630,59 683,49 735,40 788,32 840,27" className="line rival" />}
      </svg>
      <div className="vm-sb-dates"><span>Apr 22</span><span>Apr 29</span><span>May 6</span><span>May 13</span><span>May 20</span></div>
    </div>
  );
}

export function ProductSparkline({ down = false, label }: { down?: boolean; label: string }) {
  const values = down ? [5, 12, 14, 20, 27, 30] : [31, 24, 23, 15, 12, 2];
  const xValues = [0, 28, 54, 82, 110, 148];
  return (
    <svg className={`mini-spark ${down ? "down" : ""}`} viewBox="0 0 150 36" role="img" aria-label={label}>
      <polyline points={xValues.map((x, index) => `${x},${values[index]}`).join(" ")} />
      {xValues.map((x, index) => <circle key={x} cx={x} cy={values[index]} r="2.3" />)}
    </svg>
  );
}

export function ProductRankChart({ label = "Rank improved from 20 to 7 during the week" }: { label?: string }) {
  const xValues = [0, 55, 110, 165, 220, 275, 350];
  const yValues = [110, 94, 87, 80, 31, 25, 8];
  return (
    <div className="rank-chart" role="img" aria-label={label}>
      <span>01</span><span>05</span><span>10</span><span>20</span>
      <svg viewBox="0 0 350 130" preserveAspectRatio="none" aria-hidden="true">
        <polyline points={xValues.map((x, index) => `${x},${yValues[index]}`).join(" ")} />
        {xValues.map((x, index) => <circle key={x} cx={x} cy={yValues[index]} r="4" />)}
      </svg>
      <footer><small>May 15</small><small>May 16</small><small>May 17</small><small>May 18</small><small>May 19</small><small>May 21</small></footer>
    </div>
  );
}

export function ProductNotice({ title, children, tone = "info" }: { title: string; children: ReactNode; tone?: "info" | "warning" | "danger" }) {
  return <aside className={`vm-sb-notice ${tone}`} role={tone === "danger" ? "alert" : "status"}><b>{title}</b><span>{children}</span></aside>;
}

export function ProductDialog({ id, title, children, onClose }: { id?: string; title: string; children: ReactNode; onClose: () => void }) {
  const titleId = useId();
  const keepFocusInside = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key !== "Tab") return;
    const focusable = Array.from(event.currentTarget.querySelectorAll<HTMLElement>('button, input, a[href], [tabindex]:not([tabindex="-1"])')).filter((element) => !element.hasAttribute("disabled"));
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };
  return (
    <div className="vm-sb-dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section id={id} className="vm-sb-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} onKeyDown={keepFocusInside}>
        <header><h2 id={titleId}>{title}</h2><ProductIconButton label="Close dialog" onClick={onClose}><X size={20} aria-hidden="true" /></ProductIconButton></header>
        {children}
      </section>
    </div>
  );
}

export function ProductStateBoundary({ state, children }: { state: ProductState; children: ReactNode }) {
  if (state === "ready") return <>{children}</>;
  const copy = stateCopy[state];
  return (
    <div className={`vm-product-state state-${state}`}>
      <div aria-hidden={state !== "loading"} className="vm-product-state-context">{children}</div>
      <section className="vm-product-state-message" role={state === "error" || state === "offline" ? "alert" : "status"} aria-live="polite">
        {state === "loading" && <span className="vm-product-state-spinner" aria-hidden="true" />}
        <p>{state.replace("-", " ")}</p>
        <h2>{copy.title}</h2>
        <span>{copy.detail}</span>
        {copy.action && <ProductButton tone={state === "error" ? "primary" : "neutral"}>{copy.action}</ProductButton>}
      </section>
    </div>
  );
}
