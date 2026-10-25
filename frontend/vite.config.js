import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    allowedHosts: true,
    proxy: {
      '/plan': 'http://127.0.0.1:8000',
      '/lock': 'http://127.0.0.1:8000',
      '/unlock': 'http://127.0.0.1:8000',
      '/log': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/geocode': 'http://127.0.0.1:8000',
    },
  },
});
