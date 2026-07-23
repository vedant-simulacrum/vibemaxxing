import type { Meta, StoryObj } from "@storybook/react-vite";
import { ActivityStoryboard, BoardStandingsStoryboard, FriendsStoryboard, PublicProfileStoryboard, RivalComparisonStoryboard } from "./product-storyboards";

const meta = {
  title: "Approved baseline/Product screens",
  parameters: {
    layout: "fullscreen",
    options: { layout: { showPanel: false } },
    viewport: { options: { vmDesktop: { name: "VibeMaxxing desktop — 1536 × 1024", styles: { width: "1536px", height: "1024px" }, type: "desktop" } } },
    docs: { description: { component: "High-fidelity product storyboards sharing one governed ProductShell, asset registry, typography system, and 1536 × 1024 review viewport." } },
  },
  globals: { viewport: { value: "vmDesktop", isRotated: false } },
  tags: ["autodocs"],
} satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;
export const PublicProfile: Story = { render: () => <PublicProfileStoryboard /> };
export const RivalComparison: Story = { render: () => <RivalComparisonStoryboard /> };
export const Friends: Story = { render: () => <FriendsStoryboard /> };
export const ActivityAndNotifications: Story = { render: () => <ActivityStoryboard /> };
export const BoardStandings: Story = { render: () => <BoardStandingsStoryboard /> };
