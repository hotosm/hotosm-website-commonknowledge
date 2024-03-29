/**
 * When you update this file, ideally also copy the changes across to
 * ./frontend/utils/css.ts
 *
 * TODO: Automate this.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{py,html,svg,js,ts,jsx,tsx}",
        "./frontend/**/*.{html,svg,js,ts,jsx,tsx}",
        "./static/**/*.{html,svg,js,ts,jsx,tsx}",
        "./node_modules/flowbite/**/*.js",
    ],
    safelist: [
        {
            pattern: /theme-[a-zA-Z-]+/,
        },
    ],
    theme: {
        screens: {
            "<xs": { max: "479px" },
            xs: "480px",
            // Tailwind defaults as at 22 Nov 2022
            "<sm": { max: "639px" },
            sm: "640px",
            "<md": { max: "767px" },
            md: "768px",
            "<lg": { max: "1023px" },
            lg: "1024px",
            "<xl": { max: "1279px" },
            xl: "1280px",
            "<2xl": { max: "1535px" },
            "2xl": "1536px",
        },
        extend: {
            spacing: {
                icon: "1.25rem",
            },
            colors: {
                black: "#15140b",
                white: "#ffffff",
                background: "#f7f7f7",
                "background-tint": "#efefef",
                // For use with tailwind-theme-colours-plugin
                theme: {
                    50: "var(--theme-50)",
                    100: "var(--theme-100)",
                    200: "var(--theme-200)",
                    300: "var(--theme-300)",
                    400: "var(--theme-400)",
                    500: "var(--theme-500)",
                    600: "var(--theme-600)",
                    700: "var(--theme-700)",
                    800: "var(--theme-800)",
                    900: "var(--theme-900)",
                },
                blue: {
                    50: "#ebeefc",
                    100: "#c3ccf6",
                    200: "#9aaaf0",
                    300: "#7288ea",
                    400: "#4a65e3",
                    500: "#2243dd",
                    600: "#1c37b5",
                    700: "#152b8d",
                    800: "#0f1f65",
                    900: "#09123c",
                },
                gray: {
                    50: "#f7f7f7",
                    100: "#efefef",
                    200: "#dfdfdf",
                    300: "#cacaca",
                    400: "#a8a8a8",
                    500: "#878787",
                    600: "#6d6d6d",
                    700: "#5f5f5f",
                    800: "#4a4a4a",
                    900: "#3d3d3d",
                },
                red: {
                    50: "#fdf2f2",
                    100: "#fde8e8",
                    200: "#fbd5d5",
                    300: "#f8b4b4",
                    400: "#db5252",
                    500: "#d73f3f",
                    600: "#c23939",
                    700: "#ac3232",
                    800: "#972c2c",
                    900: "#701f21",
                },
                yellow: {
                    50: "#fff5e8",
                    100: "#fee1ba",
                    200: "#fdce8d",
                    300: "#fdba5f",
                    400: "#fca632",
                    500: "#fb9304",
                    600: "#cd7803",
                    700: "#a05d02",
                    800: "#724302",
                    900: "#442801",
                },
                green: {
                    50: "#f3faf7",
                    100: "#def7ec",
                    200: "#bcf0da",
                    300: "#84e1bc",
                    400: "#31c48d",
                    500: "#0e9f6e",
                    600: "#057a55",
                    700: "#046c4e",
                    800: "#03543f",
                    900: "#014737",
                },
                teal: {
                    50: "#eff7f8",
                    100: "#cfe8ea",
                    200: "#afd9db",
                    300: "#8fcacd",
                    400: "#6fbbbf",
                    500: "#4aa2a6",
                    600: "#408d90",
                    700: "#326e70",
                    800: "#244e50",
                    900: "#071010",
                },
                primary: {
                    50: "#ebeefc",
                    100: "#c3ccf6",
                    200: "#9aaaf0",
                    300: "#7288ea",
                    400: "#4a65e3",
                    500: "#2243dd",
                    600: "#1c37b5",
                    700: "#152b8d",
                    800: "#0f1f65",
                    900: "#09123c",
                },
                indigo: {
                    50: "#eff2f8",
                    100: "#cfd7e9",
                    200: "#afbddb",
                    300: "#8fa2cc",
                    400: "#506daf",
                    500: "#41598f",
                    600: "#334670",
                    700: "#23304d",
                    800: "#161e30",
                    900: "#070a10",
                },
                purple: {
                    50: "#f6f5ff",
                    100: "#edebfe",
                    200: "#dcd7fe",
                    300: "#cabffd",
                    400: "#ac94fa",
                    500: "#9061f9",
                    600: "#7e3af2",
                    700: "#6c2bd9",
                    800: "#5521b5",
                    900: "#4a1d96",
                },
                pink: {
                    50: "#fdf2f8",
                    100: "#fce8f3",
                    200: "#fad1e8",
                    300: "#f8b4d9",
                    400: "#f17eb8",
                    500: "#e74694",
                    600: "#d61f69",
                    700: "#bf125d",
                    800: "#99154b",
                    900: "#751a3d",
                },
                social: {
                    facebook: "#35518d",
                    twitter: "#1da1f2",
                    google: "#4284f4",
                    dribbble: "#ea4c89",
                    github: "#1b1f23",
                },
                orange: {
                    50: "#fff8f1",
                    100: "#feecdc",
                    200: "#fcd9bd",
                    300: "#fdba8c",
                    400: "#ff8a4c",
                    500: "#ff5a1f",
                    600: "#d03801",
                    700: "#b43403",
                    800: "#8a2c0d",
                    900: "#771d1d",
                },
            },
            fontSize: {
                xs: "0.75rem",
                sm: "0.875rem",
                base: "1rem",
                lg: "1.125rem",
                xl: "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem",
                "5xl": "3rem",
                "6xl": "3.75rem",
                "7xl": "4.5rem",
                "8xl": "6rem",
                "9xl": "8rem",
            },
            fontFamily: {
                archivo: "Archivo, sans-serif",
                inter: "Inter, sans-serif",
            },
            boxShadow: {
                "shadow-sm": "0px 1px 2px 0px rgba(0,0,0,0.08)",
                shadow: "0px 1px 2px -1px rgba(0,0,0,0.1), 0px 1px 3px 0px rgba(0,0,0,0.1)",
                "shadow-md":
                    "0px 2px 4px -2px rgba(0,0,0,0.05), 0px 4px 6px -1px rgba(0,0,0,0.1)",
                "shadow-lg":
                    "0px 4px 6px 0px rgba(0,0,0,0.05), 0px 10px 15px -3px rgba(0,0,0,0.1)",
                "shadow-xl":
                    "0px 10px 10px 0px rgba(0,0,0,0.04), 0px 20px 25px -5px rgba(0,0,0,0.1)",
                "shadow-2xl": "0px 25px 50px -12px rgba(0,0,0,0.25)",
                "shadow-blue-600/50":
                    "0px 4px 6px 0px rgba(28,100,242,0.5), 0px 10px 15px -3px rgba(28,100,242,0.5)",
                "shadow-green-500/50":
                    "0px 4px 6px 0px rgba(14,159,110,0.5), 0px 10px 15px -3px rgba(14,159,110,0.5)",
                "shadow-teal-500/50":
                    "0px 4px 6px 0px rgba(6,148,162,0.5), 0px 10px 15px -3px rgba(6,148,162,0.5)",
                "shadow-indigo-600/50":
                    "0px 4px 6px 0px rgba(88,80,236,0.5), 0px 10px 15px -3px rgba(88,80,236,0.5)",
                "shadow-purple-600/50":
                    "0px 4px 6px 0px rgba(126,58,242,0.5), 0px 10px 15px -3px rgba(126,58,242,0.5)",
                "shadow-pink-500/50":
                    "0px 4px 6px 0px rgba(231,70,148,0.5), 0px 10px 15px -3px rgba(231,70,148,0.5)",
                "shadow-red-500/50":
                    "0px 4px 6px 0px rgba(240,82,82,0.5), 0px 10px 15px -3px rgba(240,82,82,0.5)",
                "shadow-orange-500/50":
                    "0px 4px 6px 0px rgba(255,90,31,0.5), 0px 10px 15px -3px rgba(255,90,31,0.5)",
            },
            borderRadius: {
                xs: 6,
                sm: 8,
                md: 12,
                lg: 16,
                xl: 24,
            },
            keyframes: {
                fadeIn: {
                    "0%": { opacity: 0 },
                    "100%": { opacity: 1 },
                },
                popup: {
                    "0%": {
                        opacity: 0,
                        transform:
                            "perspective(200px) translate3d(0, 0, -10px)",
                    },
                    "20%": {
                        opacity: 0.5,
                    },
                    "100%": {
                        opacity: 1,
                        transform: "perspective(200px) translate3d(0, 0, 0)",
                    },
                },
            },
            animation: {
                fadeIn: "fadeIn 0.075s ease-in-out",
                popup: "popup 0.15s ease forwards",
            },
            content: {
                bullet: "'•'",
                slash: "'/'",
            },
        },
    },
    plugins: [
        require("@tailwindcss/typography"),
        require("flowbite/plugin"),
        require("./tailwind-theme-colours-plugin"),
        require("./tailwind-content-separator-plugin"),
    ],
};
