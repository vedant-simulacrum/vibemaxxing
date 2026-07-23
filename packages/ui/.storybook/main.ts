import type { StorybookConfig } from "@storybook/react-vite";
import tailwindcss from "@tailwindcss/vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: ["@storybook/addon-docs", "@storybook/addon-a11y"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  staticDirs: [
    { from: "../../../apps/web/public", to: "/" },
    { from: "../../../assets", to: "/brand-assets" },
  ],
  viteFinal: async (config) => ({
    ...config,
    plugins: [...(config.plugins ?? []), tailwindcss()],
  }),
};

export default config;
