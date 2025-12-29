// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1890FF',
        'primary-dark': '#096DD9',
        secondary: '#f97316',
        success: '#52C41A',
        warning: '#FAAD14',
        error: '#FF4D4F',
      },
      maxWidth: {
        'mobile': '375px',
      },
      height: {
        'screen-mobile': '812px',
      },
    },
  },
  plugins: [],
}