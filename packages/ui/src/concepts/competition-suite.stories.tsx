import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  LeaderboardHubStoryboard,
  OwnProfileStoryboard,
  ProductStateBoundary,
  type LeaderboardScope,
  type OwnProfileSection,
  type ProductState,
} from "@vibemaxxing/ui";

const viewports = {
  vmDesktop: { name: "Desktop — 1536 × 1024", styles: { width: "1536px", height: "1024px" }, type: "desktop" },
  vmTablet: { name: "Tablet — 1024 × 1366", styles: { width: "1024px", height: "1366px" }, type: "tablet" },
  vmMobile: { name: "Mobile — 390 × 844", styles: { width: "390px", height: "844px" }, type: "mobile" },
};

const meta = {
  title: "Candidate batch/Leaderboard and own profile",
  parameters: {
    layout: "fullscreen",
    viewport: { options: viewports },
    docs: {
      description: {
        component: "Candidate product batch for visual approval. Uses only governed assets and shared product patterns. Fixture-backed; not production or backend evidence.",
      },
    },
  },
  globals: { viewport: { value: "vmDesktop", isRotated: false } },
  tags: ["autodocs"],
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const leaderboard = (scope: LeaderboardScope): Story => ({ render: () => <LeaderboardHubStoryboard initialScope={scope} /> });
const profile = (section: OwnProfileSection): Story => ({ render: () => <OwnProfileStoryboard initialSection={section} /> });

export const GlobalLeaderboard = leaderboard("Global");
export const FriendsLeaderboard = leaderboard("Friends");
export const BoardsLeaderboard = leaderboard("Boards");
export const OrganizationsLeaderboard = leaderboard("Organizations");
export const OwnProfileOverview = profile("Overview");
export const OwnProfileAnalytics = profile("Analytics");
export const OwnProfileConnections = profile("Connections");
export const OwnProfilePrivacy = profile("Privacy");

export const GlobalLeaderboardTablet: Story = {
  parameters: { viewport: { defaultViewport: "vmTablet" } },
  render: () => <LeaderboardHubStoryboard />,
};
export const GlobalLeaderboardMobile: Story = {
  parameters: { viewport: { defaultViewport: "vmMobile" } },
  render: () => <LeaderboardHubStoryboard />,
};
export const OwnProfileTablet: Story = {
  parameters: { viewport: { defaultViewport: "vmTablet" } },
  render: () => <OwnProfileStoryboard />,
};
export const OwnProfileMobile: Story = {
  parameters: { viewport: { defaultViewport: "vmMobile" } },
  render: () => <OwnProfileStoryboard />,
};

const states: ProductState[] = ["loading", "empty", "error", "offline", "stale", "private", "blocked", "restricted", "quarantined"];
export const LeaderboardStateMatrix: Story = {
  render: () => <div>{states.map((state) => <ProductStateBoundary state={state} key={state}><LeaderboardHubStoryboard /></ProductStateBoundary>)}</div>,
};
export const OwnProfileStateMatrix: Story = {
  render: () => <div>{states.map((state) => <ProductStateBoundary state={state} key={state}><OwnProfileStoryboard /></ProductStateBoundary>)}</div>,
};
