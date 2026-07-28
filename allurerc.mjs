import { defineConfig } from "allure";

export default defineConfig({
  name: "qdrant-cli Test Report",
  output: "./allure-report",
  plugins: {
    awesome: {
      options: {
        singleFile: true,
        reportLanguage: "en",
      },
    },
  },
});
