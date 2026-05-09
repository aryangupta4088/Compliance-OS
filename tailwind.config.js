/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cs: {
          50:  '#f0f3f4',
          100: '#e1e7ea',
          200: '#c4cfd4',
          300: '#a6b7bf',
          400: '#89a0a9',
          500: '#6b8894',
          600: '#566d76',
          700: '#405159',
          800: '#2b363b',
          900: '#151b1e',
          950: '#0f1315',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
