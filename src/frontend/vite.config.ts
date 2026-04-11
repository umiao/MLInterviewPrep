import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `test` is consumed by vitest, which is configured separately via vitest.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
});
