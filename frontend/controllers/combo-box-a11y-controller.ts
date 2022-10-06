import { Controller } from "@hotwired/stimulus";
import * as focusTrap from "focus-trap";

/**
 * Obey the ComboBox spec: https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
 *
* Use like:
    <div data-controller="combo-box-a11y">
        <input data-combo-box-a11y-target="item input" />
        <div tab-index="1">3 results</div>
        <ul>
            <li tab-index="0" data-combo-box-a11y-target="item"></li>
            <li tab-index="0" data-combo-box-a11y-target="item"></li>
            <li tab-index="0" data-combo-box-a11y-target="item"></li>
        </ul>
    </div>
*
* Combine with tab-index="-1" for decorative elements
* Combine with tab-index="0" for navigable elements
*/
export default class ComboBoxA11yController extends Controller<HTMLElement> {
    static targets = ["focusTrap", "item", "input"];
    readonly inputTarget?: HTMLInputElement;
    readonly itemTarget?: HTMLElement;
    readonly itemTargets!: HTMLElement[];
    readonly focusTrapTarget?: HTMLElement;
    private focusTrap?: focusTrap.FocusTrap;
    private boundPressKeyHandler!: any;

    initialize() {
        this.boundPressKeyHandler = this.pressKey.bind(this);
    }

    connect() {
        if (!this.focusTrapTarget) return;
        this.focusTrap = focusTrap.createFocusTrap(this.focusTrapTarget);
    }

    disconnect() {
        this.blur();
    }

    focus() {
        if (!this.focusTrapTarget) return;
        this.focusTrapTarget.addEventListener(
            "keydown",
            this.boundPressKeyHandler,
        );
        this.focusTrap?.activate();
    }

    blur() {
        if (!this.focusTrapTarget) return;
        this.focusTrapTarget.removeEventListener(
            "keydown",
            this.boundPressKeyHandler,
        );
        this.focusTrap?.deactivate();
    }

    blurOnEscape(e: any) {
        if (e.key === "Escape") {
            this.blur();
        }
    }

    pressKey(e: any) {
        if (!this.itemTargets?.length) return;
        const currentFocus = document.activeElement;
        let cursor = currentFocus
            ? this.itemTargets.indexOf(currentFocus as any)
            : -1;
        if (e.key === "ArrowDown") {
            e.preventDefault();
            cursor = Math.min(cursor + 1, this.itemTargets.length - 1);
            this.itemTargets?.[cursor]?.focus();
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            cursor = Math.max(0, cursor - 1);
            this.itemTargets?.[cursor]?.focus();
        } else if (
            !["Enter", "Tab"].includes(e.key) &&
            this.inputTarget !== currentFocus
        ) {
            this.inputTarget?.focus();

            if (e.key === "ArrowLeft") {
                e.preventDefault();
                this.inputTarget?.focus();
                this.inputTarget?.setSelectionRange(0, 0);
            } else if (
                e.key === "ArrowRight" ||
                e.key === "Delete" ||
                e.key === "Backspace"
            ) {
                e.preventDefault();
                this.inputTarget?.focus();
                this.inputTarget?.setSelectionRange(
                    this.inputTarget.value.length,
                    this.inputTarget.value.length,
                );
            }
        } else {
            // Do nothing, normal key behaviour
        }
    }
}
