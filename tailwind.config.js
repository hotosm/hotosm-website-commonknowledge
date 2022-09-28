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
                red: {
                    DEFAULT: "#D73F3F",
                    50: "#FFEDED",
                    100: "#FAE8E8",
                    200: "#F3C6C6",
                    300: "#ECA4A4",
                    400: "#E58383",
                    500: "#DE6161",
                    600: "#D73F3F",
                    700: "#B82626",
                    800: "#891D1D",
                    900: "#5B1313",
                },
                blue: {
                    DEFAULT: "#3352E0",
                    50: "#F6F7FE",
                    100: "#ECEFFF",
                    200: "#C1CAF6",
                    300: "#9DACF0",
                    400: "#7A8EEB",
                    500: "#5670E5",
                    600: "#3352E0",
                    700: "#1D3ABE",
                    800: "#152B8D",
                    900: "#0E1C5D",
                },
                hotBeige: "#F8F2EC",
                hotGrey: "#23304D",
                hotLightGrey: "#929DB3",
                hotBlack: "#282613",
                hotNavy: "#23304D",
                hotTeal: "#4AA2A6",
                hotBrick: "#762C2D",
                hotYellow: "#FCAB3C",
            },
            // "Barlow Condensed",sans-serif
            keyframes: {
                fadeIn: {
                    "0%": { opacity: 0 },
                    "100%": { opacity: 1 },
                },
            },
            animation: {
                fadeIn: "fadeIn 0.075s ease-in-out",
            },
        },
    },
    plugins: [require("@tailwindcss/typography"), require("flowbite/plugin")],
};
