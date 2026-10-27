/** @type {import('tailwindcss').Config} */
// Tokens mirror the :root custom properties in public/assets/css/site.css (the original's stylesheet).
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  corePlugins: { preflight: false }, // the original ships its own reset in site.css
  theme: {
    extend: {
      colors: {
        paper: { DEFAULT: '#F5F0E6', 2: '#EFE8D8', 3: '#E8DFCB' },
        card: '#FFFDF8',
        ink: { DEFAULT: '#1E2318', 2: '#464B3A' },
        muted: '#6A6E5B',
        faint: '#8A8C78',
        line: { DEFAULT: '#DDD3BF', 2: '#CFC4AB', soft: '#EDE6D6' },
        olive: { DEFAULT: '#3D5A2A', 2: '#4E7A35', tint: '#E3EBD8' },
        lime: '#C5D69A',
        amber: { DEFAULT: '#B07A1E', ink: '#8A5A12' },
        night: { DEFAULT: '#1B2414', 2: '#131A0E', line: '#3B4A30' },
        'on-night': { DEFAULT: '#F1ECDF', 2: '#C9CBB6' },
      },
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
        serif: ['"Perfectly Nineties"', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
