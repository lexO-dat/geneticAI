import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Ignore TypeScript errors during build
    typescript: {
      noEmit: true,
      ignoreBuildErrors: true,
    }
  }
});