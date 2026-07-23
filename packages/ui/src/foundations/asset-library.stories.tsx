import type { Meta, StoryObj } from "@storybook/react-vite";
import { Icon, type IconName } from "@vibemaxxing/ui";
import { assetRegistry } from "../assets";
import { ProviderLogo, providerLogoRegistry, type ProviderLogoName } from "../ui/provider-logo";
import "./asset-library.css";

const meta = {
  title: "Foundations/Asset library",
  parameters: {
    layout: "padded",
    docs: {
      description: {
        component: "The executable inventory for VibeMaxxing's governed bare-bones assets. AI and human contributors should use these registries and components instead of inventing marks, provider symbols, avatars, or interface icons.",
      },
    },
  },
  tags: ["autodocs"],
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const brandAssets = [
  { label: "Primary mark", src: assetRegistry.brand.marks.primary },
  { label: "Indigo mark", src: assetRegistry.brand.marks.indigo },
  { label: "One-color mark", src: assetRegistry.brand.marks.oneColor },
  { label: "Light mark", src: assetRegistry.brand.marks.light, dark: true },
  { label: "Maskable mark", src: assetRegistry.brand.marks.maskable },
  { label: "Primary wordmark", src: assetRegistry.brand.wordmarks.primary, wide: true },
  { label: "Indigo wordmark", src: assetRegistry.brand.wordmarks.indigo, wide: true },
  { label: "Monochrome wordmark", src: assetRegistry.brand.wordmarks.monochrome, wide: true },
  { label: "No-rule wordmark", src: assetRegistry.brand.wordmarks.noRule, wide: true },
  { label: "Reverse wordmark", src: assetRegistry.brand.wordmarks.reverse, wide: true, dark: true },
  { label: "Favicon", src: assetRegistry.brand.favicon },
  { label: "App icon", src: assetRegistry.brand.appIcon },
] as const;

const iconNames: IconName[] = ["bell", "search", "chevron", "arrow", "shield", "copy", "users", "globe", "menu"];

function Intro({ title, copy }: { title: string; copy: string }) {
  return <header className="vm-asset-intro"><p>Governed asset system</p><h1>{title}</h1><span>{copy}</span></header>;
}

export const BrandIdentity: Story = {
  render: () => (
    <main className="vm-asset-catalogue">
      <Intro title="Brand identity" copy="Canonical marks and wordmarks. Reference the semantic registry key; never copy a file into a feature." />
      <section className="vm-asset-grid vm-brand-grid">
        {brandAssets.map(asset => (
          <figure className={asset.dark ? "vm-asset-tile vm-asset-dark" : "vm-asset-tile"} key={asset.label}>
            <div className={asset.wide ? "vm-asset-preview vm-wide" : "vm-asset-preview"}>
              <img alt={asset.label} src={asset.src} />
            </div>
            <figcaption><strong>{asset.label}</strong><code>{asset.src}</code></figcaption>
          </figure>
        ))}
      </section>
      <aside className="vm-asset-note">Social cards and platform export sizes remain in the root brand manifest. Storybook shows the reusable source identities and representative required raster exports.</aside>
    </main>
  ),
};

export const ProviderAndModelMarks: Story = {
  render: () => (
    <main className="vm-asset-catalogue">
      <Intro title="Provider and model marks" copy="Every supported provider, model family, router, and agent mark comes through ProviderLogo." />
      <section className="vm-provider-grid">
        {(Object.entries(providerLogoRegistry) as [ProviderLogoName, (typeof providerLogoRegistry)[ProviderLogoName]][]).map(([id, asset]) => (
          <figure className="vm-provider-tile" key={id}>
            <ProviderLogo provider={id} size={32} />
            <figcaption><strong>{asset.label}</strong><code>{id}</code></figcaption>
          </figure>
        ))}
      </section>
      <aside className="vm-asset-note"><code>{"<ProviderLogo provider=\"openai\" />"}</code> is the supported consumer. Do not hotlink, redraw, recolor, or substitute text glyphs for these marks.</aside>
    </main>
  ),
};

export const FixturePeople: Story = {
  render: () => (
    <main className="vm-asset-catalogue">
      <Intro title="Fixture people" copy="Synthetic, deterministic identities for Storybook and visual tests. Never treat these as production users." />
      <section className="vm-people-grid">
        <figure className="vm-person-tile">
          <img alt="Current-user fixture" src={assetRegistry.fixtures.currentUser} />
          <figcaption><strong>Current user</strong><code>fixtures.currentUser</code></figcaption>
        </figure>
        {Array.from({ length: 8 }, (_, index) => index + 1).map(id => (
          <figure className="vm-person-tile" key={id}>
            <img alt={`Synthetic storyboard person ${id}`} src={assetRegistry.fixtures.storyboardAvatar(id)} />
            <figcaption><strong>Person {id}</strong><code>storyboardAvatar({id})</code></figcaption>
          </figure>
        ))}
      </section>
    </main>
  ),
};

export const InterfaceIcons: Story = {
  render: () => (
    <main className="vm-asset-catalogue">
      <Intro title="Interface icons" copy="The approved semantic icon names exposed by the shared Icon component. Product code should request meaning, not embed SVG." />
      <section className="vm-icon-grid">
        {iconNames.map(name => (
          <figure className="vm-icon-tile" key={name}>
            <Icon name={name} size={24} />
            <figcaption><strong>{name}</strong><code>{`<Icon name="${name}" />`}</code></figcaption>
          </figure>
        ))}
      </section>
      <aside className="vm-asset-note">Lucide is the pinned interface-icon system. Add new semantic names through the shared component and this inventory; do not vendor screen-local SVG files.</aside>
    </main>
  ),
};

export const ConsumptionContract: Story = {
  render: () => (
    <main className="vm-asset-catalogue">
      <Intro title="Asset consumption contract" copy="The minimum rules an AI or contributor must follow before composing a new VibeMaxxing surface." />
      <table className="vm-asset-contract">
        <thead><tr><th>Need</th><th>Canonical source</th><th>Use</th><th>Never</th></tr></thead>
        <tbody>
          <tr><td>Product identity</td><td><code>assetRegistry.brand</code></td><td>Semantic registry key</td><td>Feature-local copies</td></tr>
          <tr><td>Provider/model identity</td><td><code>ProviderLogo</code></td><td>Provider ID and label</td><td>Glyphs, initials, hotlinks</td></tr>
          <tr><td>Demo people</td><td><code>assetRegistry.fixtures</code></td><td>Storybook/tests only</td><td>Production defaults</td></tr>
          <tr><td>Interface actions</td><td><code>Icon</code></td><td>Semantic icon name</td><td>Embedded screen SVG</td></tr>
          <tr><td>Data charts</td><td>Tokens + code</td><td>Render from data</td><td>Static chart artwork</td></tr>
          <tr><td>Approved UI target</td><td><code>assets/ui/references</code></td><td>Review comparison only</td><td>Screenshot implementation</td></tr>
        </tbody>
      </table>
    </main>
  ),
};
