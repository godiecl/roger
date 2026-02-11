/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        roger: {
          "primary": "#2563eb",        // Blue
          "secondary": "#64748b",      // Slate
          "accent": "#f59e0b",         // Amber/Orange
          "neutral": "#1e293b",        // Dark slate
          "base-100": "#ffffff",       // White
          "base-200": "#f8fafc",       // Very light gray
          "base-300": "#e2e8f0",       // Light gray
          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#ef4444",
        },
      },
    ],
  },
}
