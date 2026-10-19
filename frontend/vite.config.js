import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const api = ['/auth', '/users', '/games', '/categories', '/platform-accounts', '/library-entries', '/roles', '/public', '/chat', '/debug']

export default defineConfig({
  plugins: [react()],
  build: { outDir: '../static', emptyOutDir: true },
  server: {
    port: 5173,
    proxy: Object.fromEntries(api.map(p => [p, { target: 'http://localhost:8000', changeOrigin: true }])),
  },
})
