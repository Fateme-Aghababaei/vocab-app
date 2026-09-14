import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig(({ mode }) => {
  const siteUrl = loadEnv(mode, process.cwd(), "VITE_").VITE_SITE_URL;
  const origin = siteUrl ? new URL(siteUrl).origin : undefined;
  if (origin && !origin.startsWith("https://")) {
    throw new Error("VITE_SITE_URL must be your public HTTPS origin.");
  }
  return {
    plugins: [vue(), {
      name: "landing-seo",
      transformIndexHtml() {
        return origin ? [
          { tag: "link", attrs: { rel: "canonical", href: `${origin}/` }, injectTo: "head" },
          { tag: "meta", attrs: { property: "og:url", content: `${origin}/` }, injectTo: "head" },
          { tag: "meta", attrs: { property: "og:image", content: `${origin}/icons/icon-512.png` }, injectTo: "head" },
        ] : [];
      },
      generateBundle() {
        this.emitFile({ type: "asset", fileName: "robots.txt", source: `User-agent: *\nAllow: /\n${origin ? `Sitemap: ${origin}/sitemap.xml\n` : ""}` });
        if (origin) {
          this.emitFile({ type: "asset", fileName: "sitemap.xml", source: `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>${origin}/</loc></url></urlset>` });
        }
      },
    }],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
