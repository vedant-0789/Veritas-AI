
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    build: {
        emptyOutDir: false, // Don't delete popup build
        outDir: 'dist',
        lib: {
            entry: resolve(__dirname, 'content/content-script.ts'),
            name: 'content',
            fileName: 'content',
            formats: ['iife'] // Force IIFE for Chrome visibility
        },
        rollupOptions: {
            output: {
                extend: true,
                inlineDynamicImports: true,
                entryFileNames: 'content.iife.js',
            }
        }
    },
    define: {
        'process.env.NODE_ENV': '"production"'
    }
})
