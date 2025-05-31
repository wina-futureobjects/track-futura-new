/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#E1251B",    // Red color as requested
        secondary: "#FFFFFF",  // White color as requested
        tertiary: "#0A1F8F",   // Blue color as requested
        
        // Add derived colors based on the main colors
        "primary-foreground": "#FFFFFF",
        "secondary-foreground": "#000000",
        "tertiary-foreground": "#FFFFFF",

        // Add other utility colors
        background: "#F8F9FA",
        foreground: "#2C3E50",
        destructive: "#E74C3C",
        "destructive-foreground": "#FFFFFF",
        muted: "#F1F5F9",
        "muted-foreground": "#64748B",
        accent: "#F1F5F9",
        "accent-foreground": "#0F172A",
        success: "#2ECC71",
        info: "#3498DB",
        warning: "#F39C12",
      },
      // Add compact spacing scale
      spacing: {
        '0.25': '0.0625rem', // 1px
        '0.75': '0.1875rem', // 3px
        '1.25': '0.3125rem', // 5px
        '1.75': '0.4375rem', // 7px
        '2.25': '0.5625rem', // 9px
        '2.75': '0.6875rem', // 11px
        '3.25': '0.8125rem', // 13px
        '3.75': '0.9375rem', // 15px
        '4.25': '1.0625rem', // 17px
        '4.75': '1.1875rem', // 19px
      },
      // Add compact font sizes
      fontSize: {
        'xs': ['0.7rem', { lineHeight: '1rem' }],
        'sm': ['0.8rem', { lineHeight: '1.25rem' }],
        'base': ['0.9rem', { lineHeight: '1.5rem' }],
        'lg': ['1rem', { lineHeight: '1.75rem' }],
        'xl': ['1.1rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.3rem', { lineHeight: '2rem' }],
        '3xl': ['1.6rem', { lineHeight: '2.25rem' }],
      },
    },
  },
  plugins: [],
} 