import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: '.',
  build: {
    outDir: 'dist/client',
    emptyOutDir: true
  },
  server: {
    port: 5173,
    // Proxy API requests to the Node server during development
    proxy: {
      '/api': {
        target: 'http://localhost:3311',
        changeOrigin: true
      }
    }
  }
});
