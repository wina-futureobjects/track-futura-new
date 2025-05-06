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
    },
  },
  plugins: [],
} 