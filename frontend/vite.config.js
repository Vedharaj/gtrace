import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    open: false,
    host: true,
    proxy: {
      '/upload': 'http://127.0.0.1:5000',
      '/metrics': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000'
    }
  }
});
