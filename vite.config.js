import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// VITE_BASE_PATH lets the GitHub Pages workflow build with the repo name as
// the base path (e.g. "/aquasense-ai/"), since project pages are served from
// a sub-path rather than the domain root. Defaults to "/" for local dev and
// for Docker/other static hosts served from the root.
export default defineConfig({
  base: process.env.VITE_BASE_PATH || "/",
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
});
