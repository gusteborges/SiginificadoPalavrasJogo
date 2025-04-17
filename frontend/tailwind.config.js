/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#FFF9E5',
          100: '#FFF2CC',
          200: '#FFE699',
          300: '#FFD966',
          400: '#FFCC33',
          500: '#FFB300',
          600: '#CC9000',
          700: '#996C00',
          800: '#664800',
          900: '#332400',
        },
        navy: {
          900: '#0A192F',
        },
        forest: {
          900: '#1A2F1E',
        },
        app: {
          background: {
            light: '#FFFFFF',
            dark: '#1F1F1F',
          },
          card: {
            light: '#F5F5F5',
            dark: '#000000',
          },
          text: {
            light: '#000000',
            dark: '#FFFFFF',
          }
        }
      },
    },
  },
  plugins: [],
}