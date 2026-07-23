import type { Meta, StoryObj } from "@storybook/react-vite";
import { ProductStateBoundary, type ProductState } from "@vibemaxxing/ui";
import {
  ActivityStoryboard,
  BoardStandingsStoryboard,
  FriendsStoryboard,
  PublicProfileStoryboard,
  RivalComparisonStoryboard,
} from "./product-storyboards";

const meta = {
  title: "Approved baseline/Product state matrix",
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: "Every approved product screen rendered through every governed exceptional-state boundary.",
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const states = ["loading", "empty", "error", "offline", "stale", "private", "blocked", "restricted", "quarantined"] as const;
type Screen = "profile" | "rival" | "friends" | "activity" | "board";

function ScreenState({ screen, state }: { screen: Screen; state: ProductState }) {
  const content = {
    profile: <PublicProfileStoryboard />,
    rival: <RivalComparisonStoryboard />,
    friends: <FriendsStoryboard />,
    activity: <ActivityStoryboard />,
    board: <BoardStandingsStoryboard />,
  }[screen];
  return <ProductStateBoundary state={state}>{content}</ProductStateBoundary>;
}

const story = (screen: Screen, state: (typeof states)[number]): Story => ({
  render: () => <ScreenState screen={screen} state={state} />,
});

export const ProfileLoading = story("profile", "loading");
export const ProfileEmpty = story("profile", "empty");
export const ProfileError = story("profile", "error");
export const ProfileOffline = story("profile", "offline");
export const ProfileStale = story("profile", "stale");
export const ProfilePrivate = story("profile", "private");
export const ProfileBlocked = story("profile", "blocked");
export const ProfileRestricted = story("profile", "restricted");
export const ProfileQuarantined = story("profile", "quarantined");

export const RivalLoading = story("rival", "loading");
export const RivalEmpty = story("rival", "empty");
export const RivalError = story("rival", "error");
export const RivalOffline = story("rival", "offline");
export const RivalStale = story("rival", "stale");
export const RivalPrivate = story("rival", "private");
export const RivalBlocked = story("rival", "blocked");
export const RivalRestricted = story("rival", "restricted");
export const RivalQuarantined = story("rival", "quarantined");

export const FriendsLoading = story("friends", "loading");
export const FriendsEmpty = story("friends", "empty");
export const FriendsError = story("friends", "error");
export const FriendsOffline = story("friends", "offline");
export const FriendsStale = story("friends", "stale");
export const FriendsPrivate = story("friends", "private");
export const FriendsBlocked = story("friends", "blocked");
export const FriendsRestricted = story("friends", "restricted");
export const FriendsQuarantined = story("friends", "quarantined");

export const ActivityLoading = story("activity", "loading");
export const ActivityEmpty = story("activity", "empty");
export const ActivityError = story("activity", "error");
export const ActivityOffline = story("activity", "offline");
export const ActivityStale = story("activity", "stale");
export const ActivityPrivate = story("activity", "private");
export const ActivityBlocked = story("activity", "blocked");
export const ActivityRestricted = story("activity", "restricted");
export const ActivityQuarantined = story("activity", "quarantined");

export const BoardLoading = story("board", "loading");
export const BoardEmpty = story("board", "empty");
export const BoardError = story("board", "error");
export const BoardOffline = story("board", "offline");
export const BoardStale = story("board", "stale");
export const BoardPrivate = story("board", "private");
export const BoardBlocked = story("board", "blocked");
export const BoardRestricted = story("board", "restricted");
export const BoardQuarantined = story("board", "quarantined");
