module.exports = {
  // prefix: "tw-",
  content: [
    "./app/**/*.{py,html,js,ts}",
    "./frontend/**/*.{html,js,ts}",
    "./static/**/*.{html,js,ts}",
  ],
  theme: {
    extend: {
      spacing: {
        1: "5px",
        2: "10px",
        3: "15px",
        4: "20px",
        5: "40px",
        6: "80px",
      },
      colors: {
        hotRed: "#D73F3F",
        hotPink: "#FFEDED",
        hotGrey: "#2C3038",
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
};
