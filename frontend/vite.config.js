import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },

  build: {
    // Do not generate source maps for production.
    // This makes the original JSX/source structure
    // much less exposed through browser DevTools.
    sourcemap: false,

    // Minify the production JavaScript.
    minify: "esbuild",
  },
});