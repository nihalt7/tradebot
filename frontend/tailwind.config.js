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
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        chat: {
          darkBg: '#0c1317',
          darkPanel: '#111b21',
          darkSidebar: '#111b21',
          darkHeader: '#202c33',
          darkInput: '#2a3942',
          darkBubbleUser: '#005c4b',
          darkBubbleAi: '#202c33',
          lightBg: '#efeae2',
          lightPanel: '#ffffff',
          lightSidebar: '#f0f2f5',
          lightHeader: '#f0f2f5',
          lightInput: '#ffffff',
          lightBubbleUser: '#d9fdd3',
          lightBubbleAi: '#ffffff',
        }
      }
    },
  },
  plugins: [],
}
