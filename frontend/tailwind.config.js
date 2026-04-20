/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: { 50: '#EEF2FF', 100: '#E0E7FF', 500: '#6366F1', 600: '#4F46E5', 700: '#4338CA' },
        surface: { 50: '#F8FAFC', 100: '#F1F5F9', 200: '#E2E8F0' },
      },
    },
  },
  plugins: [],
}
