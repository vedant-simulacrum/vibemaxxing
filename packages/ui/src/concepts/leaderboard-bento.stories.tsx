import type { Meta, StoryObj } from "@storybook/react-vite";
import { LeaderboardBentoPrototype } from "./leaderboard-bento";

const meta = {
  title: "Approved baseline/Leaderboard bento",
  component: LeaderboardBentoPrototype,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: "Approved light-mode UI baseline. Fixture-only Storybook prototype for validating visual fidelity, component boundaries, hierarchy, and responsive recomposition before production implementation.",
      },
    },
  },
  tags: ["autodocs"],
} satisfies Meta<typeof LeaderboardBentoPrototype>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Desktop: Story = {};

export const Tablet: Story = {
  decorators: [(Story) => <div style={{ width: 1024 }}><Story /></div>],
};

export const Mobile: Story = {
  decorators: [(Story) => <div style={{ width: 390 }}><Story /></div>],
};
