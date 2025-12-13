/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Terminal color scheme
        terminal: {
          bg: {
            primary: '#0a0e14',
            secondary: '#131721',
            tertiary: '#1c212b',
          },
          fg: {
            primary: '#e6e6e6',
            secondary: '#8a8a8a',
            tertiary: '#4a4a4a',
          },
          accent: {
            green: '#00ff88',
            blue: '#00d4ff',
            yellow: '#ffcc00',
            red: '#ff4444',
            purple: '#bb00ff',
          },
          border: '#2a2e3a',
          'border-focus': '#00ff88',
          cursor: '#00ff88',
          selection: 'rgba(0, 255, 136, 0.3)',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'cursor-blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      boxShadow: {
        'glow-green': '0 0 10px rgba(0, 255, 136, 0.5)',
        'glow-blue': '0 0 10px rgba(0, 212, 255, 0.5)',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
