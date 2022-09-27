import { Modal } from "tailwindcss-stimulus-components";

export default class _Modal extends Modal {
    open(e: any) {
        super.open(e);
        this.containerTarget.querySelector("[tabindex='0']")?.focus();
    }
}
