import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// =============================================================================
// Digital Finance Tracker - Vite Configuration
// PURPOSE: Build configuration with security headers for development
// =============================================================================

// Auth0 domain for CSP - matches production
const AUTH0_DOMAIN = "dev-2d371r8njde648mh.us.auth0.com";
const BACKEND_URL = "https://securebankai.mysticdatanode.net";

// Content Security Policy for development (matches vercel.json production CSP)
const developmentCSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Required for React/Vite HMR
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://use.fontawesome.com https://maxcdn.bootstrapcdn.com",
  "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://use.fontawesome.com https://maxcdn.bootstrapcdn.com data:",
  "img-src 'self' data: https: blob:",
  `connect-src 'self' ws: wss: ${BACKEND_URL} https://${AUTH0_DOMAIN} https://*.auth0.com`, // ws: for HMR
  `frame-src https://${AUTH0_DOMAIN} https://*.auth0.com`, // Auth0 login iframe
  "worker-src 'self' blob:",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [["babel-plugin-react-compiler"]],
      },
    }),
  ],
  server: {
    host: true,
    port: 3000,
    headers: {
      // Security headers for development (mirrors production)
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "X-XSS-Protection": "1; mode=block",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
      "Content-Security-Policy": developmentCSP,
    },
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
