const plugin = require("tailwindcss/plugin");

function cssVarName(level) {
    return `--theme-${level}`;
}

/**
 * For each colour group specified in `theme`, generate a `.theme-{colourName}` class
 * which can be used in conjunction with `.bg-theme-300` and similar.
 *
 * Requires a `theme` colour group to be defined in the theme.
 * The keys of that group will be picked for the other groups.
 */
const themeColor = plugin(function ({
    addUtilities,
    matchUtilities,
    theme,
    e,
}) {
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
    addUtilities(utilities);
});

module.exports = themeColor;
