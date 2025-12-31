
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    build: {
        emptyOutDir: false,
        outDir: 'dist',
        lib: {
            entry: resolve(__dirname, 'background/background.ts'),
            name: 'background',
            fileName: 'background',
            formats: ['iife']
        },
    },
    define: {
        'process.env.NODE_ENV': '"production"'
    }
})
