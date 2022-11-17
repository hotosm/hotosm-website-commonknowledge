import { MapConfigController } from "groundwork-django";
import { debounce } from "lodash";
import { GeocodedPageFeatureCollection, getMapData } from "../utils/api";
import { tailwindTheme } from "../utils/css";
import { MAPBOX_INTERACTION_METHODS } from "../utils/mapbox";

export default class MapBlockController extends MapConfigController {
    // Modes
    public static EXPANDED = "expanded" as const;
    public static COLLAPSED = "collapsed" as const;
    public static MODES = [
        MapBlockController.EXPANDED,
        MapBlockController.COLLAPSED,
    ] as const;

    // Targets
    static targets = [];

    // CSS
    static classes = MapBlockController.MODES;
    public collapsedClasses!: string[];
    public expandedClasses!: string[];

    // Values
    public static values = {
        mode: { type: String, default: MapBlockController.COLLAPSED },
        geoApiEndpoint: String,
    };
    public modeValue!: typeof MapBlockController.MODES[number];
    public geoApiEndpointValue?: string;
    public mapDataValue?: GeocodedPageFeatureCollection;

    // Hooks
    connectMap() {
        super.connect?.();
        this.updateUI();
        this.setupResizeListeners();
        this.loadData();
    }

    disconnectMap(): void {
        this.teardownResizeListeners();
    }

    modeValueChanged() {
        this.updateUI();
    }

    /**
     * Display mode state
     */

    expand() {
        this.modeValue = MapBlockController.EXPANDED;
    }

    collapse() {
        this.modeValue = MapBlockController.COLLAPSED;
    }

    setMode({ params: { mode } }: any) {
        if (!MapBlockController.MODES.includes(mode)) return;
        this.modeValue = mode;
    }

    toggle() {
        this.modeValue =
            this.modeValue === MapBlockController.EXPANDED
                ? MapBlockController.COLLAPSED
                : MapBlockController.EXPANDED;
    }

    /**
     * Data
     */

    async loadData() {
        if (!this.geoApiEndpointValue)
            return console.error("No API endpoint defined");
        // this.mapDataValue = await getMapData(this.geoApiEndpointValue)
        this.map?.addSource("all-pages", {
            type: "geojson",
            data: this.geoApiEndpointValue,
        });

        this.map?.addLayer({
            id: "all-pages",
            type: "circle",
            source: "all-pages",
            paint: {
                "circle-color": "transparent",
                "circle-radius": 16,
                "circle-stroke-width": 2,
                "circle-stroke-color": tailwindTheme.extend.colors.blue[500],
            },
            filter: ["==", "$type", "Point"],
        });
    }

    /**
     * DOM
     */

    updateUI() {
        // Add classes
        this.element.classList.remove(
            ...this.collapsedClasses,
            ...this.expandedClasses,
        );
        const newClasses = this[`${this.modeValue}Classes`] as string[];
        this.element.classList.add(...newClasses);

        if (this.modeValue === MapBlockController.COLLAPSED) {
            this.map?.setZoom(0);

            for (const interaction of MAPBOX_INTERACTION_METHODS) {
                (this.map?.[interaction] as any)?.disable();
            }
        } else if (this.modeValue === MapBlockController.EXPANDED) {
            this.map?.setZoom(0);

            for (const interaction of MAPBOX_INTERACTION_METHODS) {
                (this.map?.[interaction] as any)?.enable();
            }
        }
    }

    // Resizing on window change
    // to make the expand/collapse transition smooth

    resizeMap = debounce(() => {
        requestAnimationFrame(() => {
            this.map?.resize();
        });
    });

    public resizeObserver?: ResizeObserver;

    setupResizeListeners() {
        this.resizeObserver = new ResizeObserver(this.resizeMap);
        this.resizeObserver?.observe(this.element);
    }

    teardownResizeListeners() {
        this.resizeObserver?.unobserve(this.element);
    }
}
