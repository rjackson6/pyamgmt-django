import { defineConfig } from "vite";
import solidPlugin from "vite-plugin-solid";


export default defineConfig({
    appType: "custom",
    base: "/assets/",
    plugins: [solidPlugin()],
    build: {
        manifest: true
    },
    server: {
        host: '0.0.0.0',
        strictPort: true,
    }
});
