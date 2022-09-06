import { Controller } from "@hotwired/stimulus";
import "tocbot/dist/tocbot.js";

/**
 * Creates a clickable element that takes you back a page in the history
 * inspired by https://stackoverflow.com/a/46163215
 */
class CustomController extends Controller {
    // Targets
    static targets = ["toc", "content"];
    readonly tocTarget!: HTMLElement;
    readonly contentTarget!: HTMLFormElement;

    // Values
    static values = {
        headingSelector: {
            type: String,
            default: "h2, h3, h4",
        },
        hasInnerContainers: {
            type: Boolean,
            default: false,
        },
        options: Object,
    };
    readonly headingSelectorValue!: string;
    readonly hasInnerContainers!: boolean;
    // @ts-ignore
    readonly optionsValue!: tocbot.IStaticOptions;

    async connect() {
        console.log(this.optionsValue);
        // @ts-ignore
        tocbot.init({
            // Where to render the table of contents.
            // @ts-ignore
            tocElement: this.tocTarget,
            // Where to grab the headings to build the table of contents.
            contentElement: this.contentTarget,
            // Which headings to grab inside of the contentSelector element.
            headingSelector: this.headingSelectorValue,
            // For headings inside relative or absolute positioned containers within content.
            // hasInnerContainers: this.hasInnerContainers,
            ...this.optionsValue,
        });
    }

    disconnect(): void {
        // @ts-ignore
        window.tocbot.destroy();
    }
}

export default CustomController;
