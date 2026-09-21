import js from "@eslint/js";
import globals from "globals";
import pluginReact from "eslint-plugin-react";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    plugins: {
      js,
      react: pluginReact,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      "no-console": "warn",
      "prefer-arrow-callback": "error",
      "func-style": ["error", "expression", { allowArrowFunctions: true }],
      "prefer-arrow-functions/prefer-arrow-functions": [
        "warn",
        {
          allowNamedFunctions: false,
          classPropertiesAllowed: false,
          disallowPrototype: false,
          returnStyle: "unchanged",
          singleReturnOnly: false,
        },
      ],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
  {
    files: ["src/redux/store.ts"],
    rules: {
      "no-console": "off",
    },
  },
  js.configs.recommended,
]);
