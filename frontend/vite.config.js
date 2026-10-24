import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// У docker-compose бекенд доступний як http://backend:8000
const target = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target,
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/uploads': { target, changeOrigin: true },
    },
  },
})
