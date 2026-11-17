import react from '@vitejs/plugin-react';
import type {Plugin} from 'vite';
import {defineConfig} from 'vitest/config';

const API = process.env.CONFERE_API ?? 'http://127.0.0.1:8000';

// CSP restritiva só no build (o servidor de desenvolvimento precisa de scripts inline para o HMR).
// Em produção o proxy deve repetir a política como cabeçalho (frame-ancestors só funciona em cabeçalho).
const csp: Plugin = {
  name: 'confere-csp',
  apply: 'build',
  transformIndexHtml: () => [
    {
      tag: 'meta',
      attrs: {
        'http-equiv': 'Content-Security-Policy',
        content:
          "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; " +
          "connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'",
      },
      injectTo: 'head-prepend',
    },
  ],
};

export default defineConfig({
  plugins: [react(), csp],
  server: {proxy: {'/v1': API}},
  preview: {proxy: {'/v1': API}},
  test: {environment: 'jsdom', include: ['tests/**/*.test.{ts,tsx}']},
});
