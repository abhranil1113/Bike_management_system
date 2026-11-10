import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  root: path.resolve(import.meta.dirname, 'admin'),
  plugins: [react(), tailwindcss()],
  server: {
    port: 5431,
    strictPort: true,
    host: true,
  },
  build: {
    outDir: path.resolve(import.meta.dirname, 'dist/admin'),
    emptyOutDir: true,
  },
});
