import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Served under /app/ behind Caddy. Dev proxy forwards API calls to the orchestrator.
export default defineConfig({
  base: "/app/",
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/orchestrator-api": "http://localhost:8000",
    },
  },
});
