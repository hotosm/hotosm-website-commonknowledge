import { Controller } from "@hotwired/stimulus";
import { Map } from "mapbox-gl";
import type { LngLatLike } from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

export default class MapController extends Controller {
    static targets = ["canvas", "config"];
    static values = {
        apiKey: String,
        center: { type: Array, default: [0, 0] },
        style: { type: String, default: "mapbox://styles/mapbox/streets-v11" },
        zoom: { type: Number, default: 2 },
        /**
         * Decide whether to store the map element in the `window` object
         * or against the element that has been created.
         */
        global: { type: Boolean, default: false },
        /**
         * Symbol used to attach mapbox instance to dom element.
         */
        mapId: { type: String, default: "__mapbox_instance" },
    };

    private apiKeyValue?: string;
    private styleValue!: string;
    private centerValue!: LngLatLike;
    private zoomValue!: number;
    private globalValue!: boolean;
    private mapIdValue!: string;

    private canvasTarget!: HTMLElement;
    private configTargets!: HTMLElement[];

    initialize() {
        if (!this.canvasTarget) {
            console.error(
                'No canvas target registered with map controller. Add a child with the attribute `data-map-target="canvas"`',
            );
        }

        const el = this.globalValue ? window : (this.canvasTarget as any);

        // Install the mapbox instance on the canvas element. Adding it here means that frameworks like turbo can make the
        // canvas persist between loads while recreating controllers so that its configuration can be driven reactively,
        // eg - from the url.
        if (!el[this.mapIdValue]) {
            el[this.mapIdValue] = this.loadMap();
        }

        // Size the canvas element to match the containing element.
        const containerStyle = window.getComputedStyle(this.element);
        if (containerStyle.position === "static") {
            (this.element as HTMLElement).style.position = "relative";
        }

        this.canvasTarget.style.opacity = "0";
        this.canvasTarget.style.width = "100%";
        this.canvasTarget.style.height = "100%";
    }

    async connect() {
        const mapbox = await this.mapbox;
        if (!mapbox) {
            return;
        }

        // Give any config targets the opportunity to configure the map.
        for (const target of this.configTargets) {
            target.dispatchEvent(
                new CustomEvent("map:ready", {
                    bubbles: false,
                    detail: { map: mapbox },
                }),
            );
        }
    }

    /**
     * Return the mapbox instance attached to the map canvas element.
     */
    get mapbox() {
        const el = this.canvasTarget as any;
        return el[this.mapIdValue] as Promise<mapboxgl.Map> | undefined;
    }

    /**
     * Parse and return the centre value as a json object.
     */
    private get latLng() {
        return this.centerValue ?? [0, 0];
    }

    /**
     * Initialize the mapbox instance and attach to the dom.
     */
    private loadMap() {
        return new Promise<mapboxgl.Map | undefined>(async (resolve) => {
            if (!this.apiKeyValue) {
                console.error("Mapbox: No API token defined.");
                return resolve(undefined);
            }

            if (!this.canvasTarget) {
                console.error("Mapbox: No canvas target defined.");
                return resolve(undefined);
            }

            const map = new Map({
                accessToken: this.apiKeyValue,
                container: this.canvasTarget,
                style: this.styleValue,
                center: this.latLng,
                zoom: this.zoomValue,
            });

            // Wait for the map to finish loading before resolving.
            map.on("load", () => {
                map.resize();
                setTimeout(() => {
                    this.canvasTarget.style.opacity = "1";
                    resolve(map);
                }, 120);
            });
        });
    }
}
