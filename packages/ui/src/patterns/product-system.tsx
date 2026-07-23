import type { CSSProperties, ReactNode } from "react";
import { ArrowDown, ArrowUp, ChevronDown, Search } from "../ui/product-icons";
import { assetRegistry } from "../assets";
import { ProviderLogo } from "../ui/provider-logo";

export type ProductNav = "Leaderboard" | "Activity" | "Friends";
export type FixtureAvatarId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;
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

export function ProductShell({ active, children }: { active: ProductNav; children: ReactNode }) {
  return (
    <div className="vm-sb-page">
      <header className="vm-sb-header">
        <a className="vm-sb-wordmark" href="#" aria-label="vibemaxxing home">
          <img src={assetRegistry.brand.wordmark} alt="vibemaxxing" />
        </a>
        <nav aria-label="Primary">
          {(["Leaderboard", "Activity", "Friends"] as ProductNav[]).map((item) => (
            <a key={item} className={active === item ? "active" : ""} aria-current={active === item ? "page" : undefined} href="#">
              {item}
            </a>
          ))}
        </nav>
        <button className="vm-sb-search" type="button">
          <Search size={19} aria-hidden="true" />
          <span>Search</span>
        </button>
        <button className="vm-sb-account" type="button" aria-label="Open account" aria-haspopup="menu">
          <ProductAvatar id={0} size={50} />
          <ChevronDown size={17} aria-hidden="true" />
        </button>
      </header>
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
}: {
  children: ReactNode;
  tone?: "neutral" | "primary" | "danger";
  disabled?: boolean;
}) {
  return <button type="button" disabled={disabled} className={`vm-sb-button${tone === "neutral" ? "" : ` ${tone}`}`}>{children}</button>;
}

export function ProductMovement({ value }: { value: number }) {
  const direction = value === 0 ? "flat" : value > 0 ? "up" : "down";
  return (
    <span className={`vm-sb-${direction}`} aria-label={value === 0 ? "No rank change" : `${Math.abs(value)} places ${direction}`}>
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
  return (
    <div className="vm-sb-tabs" role="tablist" aria-label={label}>
      {labels.map((item) => (
        <button
          type="button"
          role="tab"
          aria-selected={item === active}
          className={item === active ? "active" : ""}
          onClick={() => onChange?.(item)}
          key={item}
        >
          {item}
        </button>
      ))}
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
