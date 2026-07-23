import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Avatar,
  ChoiceGroup,
  EvidenceBadge,
  Icon,
  IconButton,
  LedgerRow,
  MetricValue,
  PresenceIndicator,
  Progress,
  ProductAvatar,
  ProductButton,
  ProductModel,
  ProductMovement,
  ProductPanel,
  ProductShell,
  ProductStateBoundary,
  ProductTabs,
  ProviderLogo,
  RankMovement,
  Wordmark,
  providerLogoRegistry,
  type AvatarTint,
  type IconName,
  type LedgerPerson,
} from "@vibemaxxing/ui";
import "./concepts/product-storyboards.css";

const meta = {
  title: "Foundations/Current component inventory",
  parameters: {
    docs: {
      description: {
        component: "The implemented @vibemaxxing/ui inventory. Product routes and the curated /style-guide route consume these same exports.",
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const iconNames: IconName[] = ["bell", "search", "chevron", "arrow", "shield", "copy", "users", "globe", "menu"];
const avatarTints: AvatarTint[] = ["plum", "sand", "blue", "rose", "green", "amber", "violet", "cyan"];
const person: LedgerPerson = {
  rank: 1,
  name: "Maya Chen",
  handle: "mayac",
  initials: "MC",
  burn: 148.2,
  cash: 392.14,
  change: 2,
  evidence: "Hardened",
  active: "Codex",
  tint: "plum",
};

export const BrandAndIconSet: Story = {
  render: () => (
    <div className="showcase-stage row">
      <Wordmark />
      {iconNames.map((name) => <Icon key={name} name={name} />)}
    </div>
  ),
};

export const ProviderAndModelLogos: Story = {
  parameters: { layout: "padded" },
  render: () => (
    <div className="showcase-stage" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(144px, 1fr))", gap: 12, maxWidth: 960 }}>
      {(Object.keys(providerLogoRegistry) as Array<keyof typeof providerLogoRegistry>).map((provider) => (
        <div key={provider} style={{ minHeight: 64, display: "flex", alignItems: "center", gap: 12, padding: 16, border: "1px solid var(--vm-color-row-line)", borderRadius: 9, background: "var(--vm-color-surface)" }}>
          <ProviderLogo provider={provider} size={24} />
          <span style={{ fontSize: 13, fontWeight: 500 }}>{providerLogoRegistry[provider].label}</span>
        </div>
      ))}
    </div>
  ),
};

export const IconButtonStates: Story = {
  render: () => (
    <div className="showcase-stage row">
      <IconButton label="Search" icon="search" />
      <IconButton label="Notifications" icon="bell" expanded={false} />
      <IconButton label="Unavailable action" icon="copy" disabled />
    </div>
  ),
};

export const ChoiceGroupStates: Story = {
  render: () => (
    <div className="showcase-stage">
      <ChoiceGroup className="scope-tabs" label="Leaderboard scope" items={["Global", "Friends", "Boards"] as const} value="Global" onChange={() => undefined} />
    </div>
  ),
};

export const AvatarAndPresenceStates: Story = {
  render: () => (
    <div className="showcase-stage row">
      {avatarTints.map((tint, index) => <Avatar key={tint} tint={tint} initials={["MC", "LP", "NW", "IK", "DS", "AM", "SR", "KA"][index]} label={`${tint} avatar`} />)}
      <PresenceIndicator agent="Codex" />
    </div>
  ),
};

export const EvidenceAndRankStates: Story = {
  render: () => (
    <div className="showcase-stage row">
      <EvidenceBadge level="Hardened" />
      <EvidenceBadge level="Standard" />
      <EvidenceBadge level="Imported" />
      <RankMovement value={4} />
      <RankMovement value={0} />
      <RankMovement value={-2} />
    </div>
  ),
};

export const MetricAndProgressStates: Story = {
  render: () => (
    <div className="showcase-stage metric-examples">
      <MetricValue metric="tokens" tokens={148.2} cash={392.14} />
      <MetricValue metric="cash" tokens={148.2} cash={392.14} />
      <Progress value={0} label="Not started" />
      <Progress value={68} label="68 percent complete" />
      <Progress value={100} label="Complete" compact />
    </div>
  ),
};

export const LedgerRowStates: Story = {
  parameters: { layout: "padded" },
  render: () => (
    <div className="showcase-stage ledger-preview storybook-ledger">
      <LedgerRow person={person} metric="tokens" />
      <LedgerRow person={{ ...person, rank: 2, name: "Leon Park", handle: "leonp", initials: "LP", change: -1, evidence: "Standard", active: undefined, tint: "sand" }} metric="cash" />
      <LedgerRow person={{ ...person, rank: 12, name: "A builder with a deliberately long display name", handle: "long-content-state", initials: "AB", change: 0, evidence: "Imported", active: undefined, tint: "blue" }} metric="tokens" />
    </div>
  ),
};

export const ProductSystemPrimitives: Story = {
  parameters: { layout: "padded" },
  render: () => (
    <ProductPanel label="Product component contract">
      <div className="showcase-stage row">
        <ProductAvatar id={0} size={48} online label="Vedant, online" />
        <ProductButton>Secondary action</ProductButton>
        <ProductButton tone="primary">Primary action</ProductButton>
        <ProductButton tone="danger">Destructive action</ProductButton>
        <ProductMovement value={3} />
        <ProductMovement value={-2} />
        <ProductModel name="GPT-5.4" />
        <ProductTabs labels={["Today", "7 days", "Season"]} active="7 days" />
      </div>
    </ProductPanel>
  ),
};

export const ProductShellContract: Story = {
  parameters: { layout: "fullscreen" },
  render: () => (
    <ProductShell active="Leaderboard">
      <main className="vm-sb-content">
        <ProductPanel label="Shell content"><div className="showcase-stage">Routes compose content here.</div></ProductPanel>
      </main>
    </ProductShell>
  ),
};

export const ProductStateContract: Story = {
  parameters: { layout: "fullscreen" },
  render: () => (
    <ProductStateBoundary state="offline">
      <ProductShell active="Activity"><main className="vm-sb-content" /></ProductShell>
    </ProductStateBoundary>
  ),
};
