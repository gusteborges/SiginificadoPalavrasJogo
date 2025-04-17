import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      './env/data.js': './env/data.mjs',
      '../env/data.js': '../env/data.mjs'
    }
  },
  optimizeDeps: {
    include: ['axios']
  }
});
