import { MapConfigController } from "groundwork-django";
import { Map } from "mapbox-gl";

export default class FloatingMapController extends MapConfigController {
    // Modes
    public static EXPANDED = "expanded" as const;
    public static MINIMAP = "minimap" as const;
    public static MODES = [
        FloatingMapController.EXPANDED,
        FloatingMapController.MINIMAP,
    ] as const;

    // Targets
    static targets = ["container"];
    public containerTarget?: HTMLElement;

    // CSS
    static classes = FloatingMapController.MODES;
    public minimapClasses!: string[];
    public expandedClasses!: string[];

    // Values
    public static values = {
        mode: { type: String, default: FloatingMapController.MINIMAP },
    };
    public modeValue!: typeof FloatingMapController.MODES[number];

    // Hooks
    connect() {
        super.connect?.();
        this.updateUI();
    }

    connectMap(map: Map): void | Promise<void> {
        this.updateUI();
    }

    modeValueChanged() {
        this.updateUI();
    }

    // Methods
    expand() {
        this.modeValue = FloatingMapController.EXPANDED;
    }

    collapse() {
        this.modeValue = FloatingMapController.MINIMAP;
    }

    setMode({ params: { mode } }: any) {
        if (!FloatingMapController.MODES.includes(mode)) return;
        this.modeValue = mode;
    }

    toggle() {
        this.modeValue =
            this.modeValue === FloatingMapController.EXPANDED
                ? FloatingMapController.MINIMAP
                : FloatingMapController.EXPANDED;
    }

    updateUI() {
        // Add classes
        const container = this.containerTarget;
        if (!container)
            return console.warn("Couldn't find container", container);
        container.classList.remove(
            ...this.minimapClasses,
            ...this.expandedClasses,
        );
        const newClasses = this[`${this.modeValue}Classes`] as string[];
        container.classList.add(...newClasses);

        // Camera logic etc.
        if (this.modeValue === "minimap") {
            // Camera
            // @ts-ignore
            this.map?.setProjection("globe");
            this.map?.setZoom(0);

            // Interactivity
            this.map?.boxZoom.disable();
            this.map?.doubleClickZoom.disable();
            this.map?.scrollZoom.disable();
        } else if (this.modeValue === "expanded") {
            // @ts-ignore
            this.map?.setProjection("mercator");

            // Interactivity
            this.map?.boxZoom?.enable();
            this.map?.doubleClickZoom.disable();
            this.map?.scrollZoom.enable();
        }
    }
}
