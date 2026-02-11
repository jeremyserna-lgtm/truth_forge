/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Brand colors from COLOR_SYSTEM.md
      colors: {
        // Foundation neutrals
        'brand-black': '#0D0D0D',
        'brand-charcoal': '#1A1A1A',
        'brand-graphite': '#2D2D2D',
        'brand-steel': '#4A4A4A',
        'brand-concrete': '#888888',
        'brand-ash': '#B5B5B5',
        'brand-warm-white': '#F5F0E6',

        // Truth Engine - Source White
        'source': '#F5F0E6',
        'source-glow': '#FFFEF5',
        'source-dim': '#E8E3D9',

        // Primitive Engine - Forge Gold
        'forge': '#D4A853',
        'ember': '#F5C065',
        'molten': '#B8923F',
        'ash-gold': '#A08050',

        // Credential Atlas - Steel Blue
        'steel-blue': '#4A6FA5',
        'clear': '#6B8FC5',
        'deep': '#3A5A8A',
        'muted-blue': '#5A7090',

        // Stage 5 Mind - Amber Warmth
        'amber': '#F59E0B',
        'glow': '#FBBF24',
        'deep-amber': '#D97706',
      },

      // Typography from TYPOGRAPHY_SYSTEM.md
      fontFamily: {
        'display': ['Instrument Serif', 'serif'],
        'mono': ['JetBrains Mono', 'monospace'],
        'body': ['Inter', 'sans-serif'],
      },

      // Type scale
      fontSize: {
        'hero': '4rem',      // 64px
        'h1': '2.5rem',      // 40px
        'h2': '2rem',        // 32px
        'h3': '1.563rem',    // 25px
        'h4': '1.25rem',     // 20px
        'body': '1rem',      // 16px
        'small': '0.875rem', // 14px
        'micro': '0.75rem',  // 12px
      },

      // Letter spacing
      letterSpacing: {
        'brand-tight': '-0.01em',
        'brand-normal': '0.02em',
        'brand-wide': '0.05em',
      },
    },
  },
  plugins: [],
}
