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
const contentSeparator = plugin(function ({
    matchUtilities,
    theme,
    createUtilityPlugin,
}) {
    matchUtilities(
        {
            "content-separator": (width) => ({
                "& > :not(:last-child)": {
                    marginRight: width,
                },
                "& > :not(:last-child):after": {
                    marginLeft: width,
                    content: "var(--tw-content-separator)",
                },
            }),
        },
        {
            values: theme("spacing"),
            supportsNegativeValues: true,
        },
    );

    matchUtilities(
        {
            "separator-content": (symbol) => ({
                "&": {
                    "--tw-content-separator": symbol,
                },
            }),
        },
        {
            values: theme("content"),
        },
    );
});

module.exports = contentSeparator;

// `content-separator-4 content-['•']`
