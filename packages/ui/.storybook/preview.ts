import type { Preview } from "@storybook/react-vite";
import "../src/tokens.css";
import "../src/components.css";
import "./preview.css";

const preview: Preview = {
  parameters: {
    a11y: {
      test: "error",
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: "centered",
    options: {
      storySort: {
        order: ["Foundations", "Primitives", "Components", "Product patterns"],
      },
    },
  },
};

export default preview;
