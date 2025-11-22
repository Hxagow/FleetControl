/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./static/css/input.css"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'sans-serif'],
        grotesk: ['"Space Grotesk"', 'sans-serif'], // alias si tu veux
      },
    },
  },
  plugins: [],
  safelist: [
    'input-field',
    'input-label',
    'input-error',
    'input-container'
  ]
}