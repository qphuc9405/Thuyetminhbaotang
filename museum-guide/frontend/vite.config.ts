/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: proxy /api -> backend FastAPI (mặc định http://localhost:8000). KHÔNG đặt khoá bí mật ở frontend.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': { target: process.env.VITE_API_TARGET || 'http://localhost:8000', changeOrigin: true } } },
  test: { environment: 'jsdom', globals: true, setupFiles: ['./src/setupTests.ts'], css: false },
})
