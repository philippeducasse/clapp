import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx,js,jsx,html}", "./components/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {},
  },
  darkMode: "class",
  plugins: [],
};

export default config;
