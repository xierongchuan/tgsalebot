/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef7ee',
          100: '#fdedd6',
          200: '#fad5a8',
          300: '#f6b970',
          400: '#f19233',
          500: '#ea720d',
          600: '#cd5707',
          700: '#a6410c',
          800: '#85350e',
          900: '#6c2d0e',
        },
      },
    },
  },
  plugins: [],
}
