/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Manual dark mode toggle
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5C6BC0',
          light: '#7E8CD8',
          dark: '#3F51B5',
        },
        glass: {
          light: 'rgba(255, 255, 255, 0.7)',
          dark: 'rgba(0, 0, 0, 0.7)',
          border: {
            light: 'rgba(255, 255, 255, 0.18)',
            dark: 'rgba(255, 255, 255, 0.08)',
          }
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
        },
        bg: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
        }
      },
      backdropBlur: {
        glass: '20px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      }
    },
  },
  plugins: [],
}
