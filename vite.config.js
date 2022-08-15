import { defineConfig } from "vite";

const BUNDLE_ENTRYPOINTS = {
  main: "./frontend/main.ts",
};

export default defineConfig(() => {
  return {
    base: "/static/",
    optimizeDeps: {
      entries: Object.values(BUNDLE_ENTRYPOINTS),
    },
    build: {
      manifest: true,
      emptyOutDir: true,
      polyfillModulePreload: false,
      rollupOptions: {
        output: {
          dir: "vite/",
        },
        input: BUNDLE_ENTRYPOINTS,
      },
    },
    server: {
      hmr: {
        clientPort: 3000,
      },
      port: 3000,
      strictPort: true,
      host: "localhost",
    },
  };
});
