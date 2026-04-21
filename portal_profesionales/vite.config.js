import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      watch: {
        usePolling: true,
      },
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://api_padrones:8000',
          changeOrigin: false,
          headers: {
            'Host': 'localhost'
          }
        }
      }
    },
  }
})
