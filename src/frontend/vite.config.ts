import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `test` is consumed by vitest, which is configured separately via vitest.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    // T-P3-483 (pensieve MLI-INT): pin OFF Vite's default 5173 so a stray
    // `vite` project cannot squat the /ml-interview iframe slot. strictPort
    // makes a collision fail loudly instead of silently bumping to 5181.
    port: 5180,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
});
