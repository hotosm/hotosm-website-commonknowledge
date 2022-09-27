/** @type {import('tailwindcss').Config} */
module.exports = {
    // prefix: "tw-",
    content: [
        "./app/**/*.{py,html,js,ts}",
        "./frontend/**/*.{html,js,ts}",
        "./static/**/*.{html,js,ts}",
        "./node_modules/flowbite/**/*.js",
    ],
    theme: {
        extend: {
            spacing: {
                1: "5px",
                2: "10px",
                3: "15px",
                4: "20px",
                icon: "1.25rem",
                5: "40px",
                6: "80px",
            },
            colors: {
                hotRed: "#D73F3F",
                hotPink: "#FFEDED",
                hotGrey: "#2C3038",
                hotLightGrey: "#929DB3",
            },
            // "Barlow Condensed",sans-serif
        },
    },
    plugins: [require("@tailwindcss/typography"), require("flowbite/plugin")],
};
