import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    // E2E tests are slower and may involve waiting for backend responses
    testTimeout: 30000,
    // Don't use setup files that mock the API
    // setupFiles: [],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
