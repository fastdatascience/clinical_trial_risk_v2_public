import {defineConfig} from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        target: "es2022",
    },
    esbuild: {
        target: "es2022",
    },
    optimizeDeps: {
        exclude: ["pdfjs-dist"],
        esbuildOptions: {
            target: "es2022", // to fix top level await issue, resource: https://github.com/mozilla/pdf.js/issues/17245#issuecomment-1820013153
        },
    },
    server: {
        watch: {
            usePolling: true,
        },
        host: true,
        strictPort: true,
        port: 5173,
    },
});
