import { defineConfig } from "vite";
import solidPlugin from "vite-plugin-solid";


export default defineConfig({
    appType: "custom",
    base: "/assets/",
    plugins: [solidPlugin()]
});
