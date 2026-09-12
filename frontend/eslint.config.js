import js from "@eslint/js";
import stylistic from "@stylistic/eslint-plugin";
import vue from "eslint-plugin-vue";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**", "node_modules/**", "**/*.tsbuildinfo"] },
  js.configs.recommended,
  {
    files: ["**/*.{ts,vue}"],
    extends: [...tseslint.configs.recommended],
    rules: {
      "@typescript-eslint/consistent-type-imports": ["error", { prefer: "type-imports" }],
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
  ...vue.configs["flat/recommended"],
  {
    files: ["**/*.{js,ts,vue}"],
    plugins: { "@stylistic": stylistic },
    rules: {
      "eqeqeq": ["error", "always"],
      "prefer-const": "error",
      "@stylistic/indent": ["error", 2, { SwitchCase: 1 }],
      "@stylistic/quotes": ["error", "double", { avoidEscape: true }],
      "@stylistic/semi": ["error", "always"],
      "@stylistic/comma-dangle": ["error", "always-multiline"],
      "@stylistic/arrow-parens": ["error", "always"],
      "@stylistic/object-curly-spacing": ["error", "always"],
      "@stylistic/keyword-spacing": "error",
      "@stylistic/space-before-blocks": "error",
      "@stylistic/comma-spacing": "error",
      "@stylistic/no-trailing-spaces": "error",
      "@stylistic/eol-last": ["error", "always"],
      "@stylistic/no-multiple-empty-lines": ["error", { max: 1, maxEOF: 0 }],
    },
  },
  {
    files: ["src/**/*.{ts,vue}"],
    languageOptions: { globals: globals.browser },
  },
  {
    files: ["*.{js,ts}"],
    languageOptions: { globals: globals.node },
  },
  {
    files: ["public/**/*.js"],
    languageOptions: { globals: globals.serviceworker },
  },
  {
    files: ["**/*.vue"],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
    rules: {
      "vue/block-order": ["error", { order: ["template", "script", "style"] }],
      "vue/html-indent": ["error", 2],
      "vue/max-attributes-per-line": ["error", { singleline: 3, multiline: 1 }],
      "vue/attributes-order": "error",
      "vue/html-quotes": ["error", "double"],
      "vue/html-self-closing": ["error", {
        html: { void: "always", normal: "never", component: "always" },
        svg: "always",
        math: "always",
      }],
      "vue/v-bind-style": ["error", "shorthand"],
      "vue/v-on-style": ["error", "shorthand"],
      "vue/v-slot-style": ["error", "shorthand"],
    },
  },
);
