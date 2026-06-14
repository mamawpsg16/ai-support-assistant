// vite.config.js — configuration for Vite, the dev server + build tool.
//
// Vite does two things for us:
//   1. `npm run dev` -> a fast dev server (default http://localhost:5173) that
//      hot-reloads the page when you save a .vue file.
//   2. `npm run build` -> bundles everything into static files for production.
//
// The @vitejs/plugin-vue plugin teaches Vite how to understand .vue files
// (which mix template + script + style in one file).

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,    // the SPA runs here; the FastAPI API runs separately on 8000
    host: true,    // listen on 0.0.0.0 so it works inside a Docker container
    watch: {
      // Poll for file changes — needed for hot reload across Docker/Windows bind mounts
      // (native file events often don't propagate there). Harmless outside Docker.
      usePolling: true,
    },
  },
})
