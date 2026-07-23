import type { Meta, StoryObj } from "@storybook/react-vite";
import { ProductStateBoundary, type ProductState } from "@vibemaxxing/ui";
import { ActivityStoryboard, BoardStandingsStoryboard, FriendsStoryboard, PublicProfileStoryboard, RivalComparisonStoryboard } from "./product-storyboards";

const viewports = {
  vmDesktop: { name: "Desktop — 1536 × 1024", styles: { width: "1536px", height: "1024px" }, type: "desktop" },
  vmTablet: { name: "Tablet — 1024 × 1366", styles: { width: "1024px", height: "1366px" }, type: "tablet" },
  vmMobile: { name: "Mobile — 390 × 844", styles: { width: "390px", height: "844px" }, type: "mobile" },
};

const meta = {
  title: "Approved baseline/Product screens",
  parameters: {
    layout: "fullscreen",
    options: { layout: { showPanel: false } },
    viewport: { options: viewports },
    docs: { description: { component: "High-fidelity product storyboards sharing the governed product system, asset registry, responsive rules, and difficult-state boundary." } },
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

const mobile = { viewport: { defaultViewport: "vmMobile" } };
export const PublicProfileMobile: Story = { parameters: mobile, render: () => <PublicProfileStoryboard /> };
export const RivalComparisonMobile: Story = { parameters: mobile, render: () => <RivalComparisonStoryboard /> };
export const FriendsMobile: Story = { parameters: mobile, render: () => <FriendsStoryboard /> };
export const ActivityAndNotificationsMobile: Story = { parameters: mobile, render: () => <ActivityStoryboard /> };
export const BoardStandingsMobile: Story = { parameters: mobile, render: () => <BoardStandingsStoryboard /> };

const stateStory = (state: ProductState): Story => ({
  parameters: { layout: "fullscreen" },
  render: () => <ProductStateBoundary state={state}><PublicProfileStoryboard /></ProductStateBoundary>,
});
export const LoadingState = stateStory("loading");
export const EmptyState = stateStory("empty");
export const ErrorState = stateStory("error");
export const OfflineState = stateStory("offline");
export const StaleState = stateStory("stale");
export const PrivateState = stateStory("private");
export const BlockedState = stateStory("blocked");
export const RestrictedState = stateStory("restricted");
export const QuarantinedState = stateStory("quarantined");
