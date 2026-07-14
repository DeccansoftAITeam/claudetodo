import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward API calls to the FastAPI dev server during development.
      '/api': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})