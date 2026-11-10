import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  root: path.resolve(import.meta.dirname, 'driver'),
  plugins: [react(), tailwindcss()],
  server: {
    port: 3110,
    strictPort: true,
    host: true,
  },
  build: {
    outDir: path.resolve(import.meta.dirname, 'dist/driver'),
    emptyOutDir: true,
  },
});
