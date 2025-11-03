export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#00A6FF",   // electric blue
        accent: "#FF3B3B",    // red CTA
        neon: "#00FF8C",      // neon green highlight
        dark: "#121212",      // base background
      },
    },
  },
  plugins: [],
};
