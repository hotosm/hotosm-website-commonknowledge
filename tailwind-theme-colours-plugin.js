const plugin = require("tailwindcss/plugin");

function cssVarName(level) {
    return `--theme-${level}`;
}

/**
 * specify `themeLevels` for the colour increments to go for
 */
const themeColor = plugin(function ({
    addUtilities,
    matchUtilities,
    theme,
    e,
}) {
    // For each colour group, generate a `.theme-{colourName}` class
    // .theme-{colourName} {
    //   // For each colour in group, create a CSS variable
    //   --theme-{colourIndex}: {colour}
    // }
    const themeColorLevels = Object.keys(theme("colors.theme"));
    const colourGroups = Object.entries(theme("colors")).filter(
        ([group, value]) => typeof value !== "string",
    );
    const utilities = colourGroups.map(([group, colours]) => {
        const themeClassName = `.${e(`theme-${group}`)}`;
        const themeCSSVariables = Object.entries(colours).reduce(
            (dict, [level, value]) => {
                if (themeColorLevels.includes(level.toString())) {
                    dict[`--theme-${level}`] = value;
                }
                return dict;
            },
            {},
        );
        return {
            [themeClassName]: themeCSSVariables,
        };
    });
    console.log(utilities);
    addUtilities(utilities);
});

module.exports = themeColor;
