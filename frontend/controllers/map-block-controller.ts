import { MapConfigController } from "groundwork-django";
import { debounce, random } from "lodash";
import { Marker } from "mapbox-gl";
import {
    GeocodedPageFeature,
    GeocodedPageFeatureCollection,
    GeocodedPageFeatureProperties,
    getMapData,
} from "../utils/api";
import { tailwindTheme } from "../utils/css";
import { createElement } from "../utils/dom";
import { MAPBOX_INTERACTION_METHODS } from "../utils/mapbox";
import { randomPosition } from "@turf/random";

interface MarkerConfig {
    currentDisplayModeOnly?: boolean;
    allowedDisplayModes?: Array<typeof MapBlockController.MODES[number]>;
}

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
        this.resetMarkers();
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
        if (!this.map) return;
        if (!this.geoApiEndpointValue)
            return console.error("No API endpoint defined");

        this.mapDataValue = await getMapData(this.geoApiEndpointValue);
        this.mapDataValue = {
            ...this.mapDataValue,
            features: this.mapDataValue.features
                // Clean up the geo
                .filter(
                    (point) =>
                        point.geometry && point.geometry.type === "Point",
                )
                .map((f) => {
                    // For country-only pages, give a little jitter to make things navigable
                    if (f.properties.has_unique_location) return f;
                    const OFFSET = 0.1;
                    return {
                        ...f,
                        geometry: {
                            ...f.geometry,
                            coordinates: randomPosition([
                                f.geometry.coordinates[0] - OFFSET,
                                f.geometry.coordinates[1] - OFFSET,
                                f.geometry.coordinates[0] + OFFSET,
                                f.geometry.coordinates[1] + OFFSET,
                            ]),
                        },
                    };
                }),
        };

        this.map.addSource("pages", {
            type: "geojson",
            data: this.mapDataValue,
            cluster: true,
            clusterMaxZoom: 14, // Max zoom to cluster points on
            clusterRadius: 50, // Radius of each cluster when clustering points (defaults to 50)
        });

        // TODO: Style
        this.map.addLayer({
            id: "clustered-pages-shadow",
            type: "circle",
            source: "pages",
            filter: ["has", "point_count"],
            paint: {
                "circle-radius": [
                    "step",
                    ["get", "point_count"],
                    25,
                    10,
                    35,
                    20,
                    45,
                ],
                "circle-color": "rgba(0,0,0,0.1)",
                "circle-blur": 0.4,
            },
        });

        this.map.addLayer({
            id: "clustered-pages",
            type: "circle",
            source: "pages",
            filter: ["has", "point_count"],
            paint: {
                // Use step expressions (https://docs.mapbox.com/mapbox-gl-js/style-spec/#expressions-step)
                // with three steps to implement three types of circles:
                //   * Blue, 20px circles when point count is less than 100
                //   * Yellow, 30px circles when point count is between 100 and 750
                //   * Pink, 40px circles when point count is greater than or equal to 750
                "circle-color": tailwindTheme.extend.colors.blue[100],
                "circle-opacity": 0.8,
                "circle-radius": [
                    "step",
                    ["get", "point_count"],
                    20,
                    10,
                    30,
                    20,
                    40,
                ],
            },
        });

        // TODO: Style
        this.map.addLayer({
            id: "clustered-pages-count",
            type: "symbol",
            source: "pages",
            filter: ["has", "point_count"],
            layout: {
                "text-field": "{point_count_abbreviated}",
                "text-font": ["DIN Offc Pro Medium", "Arial Unicode MS Bold"],
                "text-size": 20,
            },
            paint: {
                "text-color": tailwindTheme.extend.colors.blue[500],
            },
        });

        this.map?.addLayer({
            id: "unclustered-pages",
            type: "circle",
            source: "pages",
            paint: {
                "circle-color": "transparent",
                "circle-radius": 16,
                "circle-stroke-width": 2,
                "circle-stroke-color": tailwindTheme.extend.colors.blue[500],
            },
            filter: ["all", ["!has", "point_count"], ["==", "$type", "Point"]],
        });

        this.map.on("idle", (event) => this.addMapMarkers(event));
    }

    private addedMarkers = false;
    async addMapMarkers(
        event: mapboxgl.MapboxEvent<undefined> & mapboxgl.EventData,
    ) {
        if (this.addedMarkers || !this.mapDataValue) return;
        this.addedMarkers = true;

        // Valid map items
        const data = this.mapDataValue.features.filter(
            (point) => point.properties?.map_image_url?.length,
        );

        // Make a sample
        let indexes: number[] = [];
        let randomPoints = Array(20)
            .fill(0)
            .map((_) => {
                let index;
                let point;
                do {
                    index = random(0, data.length - 1);
                    point = data[index];
                } while (indexes.includes(index));
                return point;
            });

        // Render markers
        for (const item of randomPoints) {
            this.createMarker(
                `photo-marker:${item.properties.url}`,
                item.geometry.coordinates as mapboxgl.LngLatLike,
                `
            <div class='w-[65px] h-[65px] rounded-full overflow-hidden relative shadow-md'>
              <div class='w-full h-full inset-0 absolute bg-cover bg-no-repeat transition-all scale-100 hover:scale-110' style='background-image: url("${
                  (item.properties as GeocodedPageFeatureProperties)
                      ?.map_image_url
              }")'></div>
            </div>
          `,
                {
                    anchor: "center",
                },
                {
                    allowedDisplayModes: [MapBlockController.COLLAPSED],
                },
            );
        }
    }

    private markers: {
        [id: string]: {
            marker: Marker;
        } & MarkerConfig;
    } = {};

    createMarker(
        id: string,
        lngLat: mapboxgl.LngLatLike,
        html: string,
        mapboxConfig?: Exclude<mapboxgl.MarkerOptions, "element">,
        controllerConfig?: MarkerConfig,
    ) {
        if (!this.map) return;
        let marker = this.markers[id];
        if (marker) {
            // Update the marker
            let element = marker.marker.getElement();
            element.innerHTML = html;
            marker.marker.setLngLat(lngLat).addTo(this.map);
        } else {
            // Create the marker
            this.markers[id] = {
                ...controllerConfig,
                marker: new Marker({
                    ...mapboxConfig,
                    element: createElement(html),
                })
                    // @ts-ignore
                    .setLngLat(lngLat)
                    // @ts-ignore
                    .addTo(this.map),
            };
        }
    }

    /**
     * DOM
     */

    resetMarkers() {
        if (!this.map) return;
        for (const marker of Object.values(this.markers)) {
            if (
                !marker.allowedDisplayModes?.includes(this.modeValue) ||
                marker.currentDisplayModeOnly
            ) {
                marker.marker.remove();
            } else {
                marker.marker.addTo(this.map);
            }
        }
    }

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
