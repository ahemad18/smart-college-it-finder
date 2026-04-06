import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/AI-Powered-Comparison-of-IT-Programs-Across-Ontario-Colleges/',
  plugins: [react(), tailwindcss()],
})
