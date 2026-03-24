import { type PluginConfig as SortImportsPluginOptions } from "@trivago/prettier-plugin-sort-imports";
import { type Config as PrettierConfig } from "prettier";
import { type PluginOptions as TailwindCSSPluginOptions } from "prettier-plugin-tailwindcss";

const config: PrettierConfig & SortImportsPluginOptions & TailwindCSSPluginOptions = {
  arrowParens: "always",
  bracketSameLine: false,
  bracketSpacing: true,
  endOfLine: "lf",
  jsxSingleQuote: false,
  semi: true,
  singleQuote: false,
  tabWidth: 2,
  trailingComma: "es5",
  useTabs: false,
  printWidth: 100,
  importOrder: [
    "^react$",
    "^next",
    "<THIRD_PARTY_MODULES>",
    "^@/components/(.*)$",
    "^@/utils/(.*)$",
    "^[./]",
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
  plugins: [
    "@trivago/prettier-plugin-sort-imports",
    "prettier-plugin-tailwindcss", // Must be loaded at end
  ],
  tailwindStylesheet: "app/globals.css",
  tailwindFunctions: ["cn", "cva"],
};

export default config;
