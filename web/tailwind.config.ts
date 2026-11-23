import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#121212",
        surface: {
          DEFAULT: "#181818",
          elevated: "#242424",
          highlight: "#2a2a2a",
          hover: "#282828",
        },
        primary: {
          DEFAULT: "#1DB954",
          hover: "#1ed760",
          light: "#22c55e",
        },
        muted: {
          DEFAULT: "#b3b3b3",
          light: "#d1d5db",
          dark: "#727272",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
export default config;
