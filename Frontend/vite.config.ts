import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    hmr: {
      protocol: 'http',
      host: 'localhost',
      port: 5173
    }
  },
  build: {
    target: 'ES2020',
    outDir: 'dist',
  }
})
