// api/http.js — the configured axios client (one instance for the whole app).
//
// Separated from the endpoint definitions (index.js) so the "how we talk to the
// server" (base URL, headers, interceptors) lives in one small file.

import axios from 'axios'

export const http = axios.create({
  // Vite injects VITE_API_BASE from the .env file (must start with VITE_).
  baseURL: import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})
