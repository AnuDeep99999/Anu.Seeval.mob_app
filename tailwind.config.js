/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",   // 👈 add this
  ],
  theme: { extend: {} },
  plugins: [],
};
