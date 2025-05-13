import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => {
  const config = {
    plugins: [react(), tailwindcss()],
    base: '/',
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      emptyOutDir: true,
      sourcemap: false
    }
  };

  // Only add the proxy in development mode
  if (command === 'serve') {
    return {
      ...config,
      server: {
        proxy: {
          '/api': {
            target: 'http://localhost:8000',
            changeOrigin: true,
            secure: false,
          }
        }
      }
    };
  }
  
  return config;
});
