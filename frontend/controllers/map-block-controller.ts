import { MapConfigController } from "groundwork-django";
import { debounce, random } from "lodash";
import mapboxgl, { LngLatLike, Map, Marker, Popup } from "mapbox-gl";
import {
    GeocodedPageFeature,
    GeocodedPageFeatureCollection,
    GeocodedPageFeatureProperties,
    getMapData,
} from "../utils/api";
import { screen, tailwindTheme } from "../utils/css";
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
    async connectMap(map: Map) {
        super.connect?.();
        this.updateUI();
        this.setupResizeListeners();
        await this.loadData();
        map.on("idle", (event) => this.addMapMarkers(event));
        this.createLayers();
    }

    disconnectMap(): void {
        this.teardownResizeListeners();
    }

    modeValueChanged() {
        this.updateUI();
        this.updateMarkerVisibilitys();
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
    }

    /**
     * Map
     */

    createLayers() {
        if (!this.map) return;
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
                "circle-color": [
                    "case",
                    ["boolean", ["feature-state", "hover"], false],
                    tailwindTheme.extend.colors.blue[500],
                    "transparent",
                ],
                "circle-radius": 16,
                "circle-stroke-width": 2,
                "circle-stroke-color": tailwindTheme.extend.colors.blue[500],
            },
            filter: ["all", ["!has", "point_count"], ["==", "$type", "Point"]],
        });

        // On desktop, hover and click
        this.map.on("mouseenter", "unclustered-pages", (e) =>
            this.showFeaturePopup(e),
        );
        this.map.on("mouseup", "unclustered-pages", (e) =>
            this.clickFeaturePopup(e),
        );
        this.map.on("mouseleave", "unclustered-pages", (e) =>
            this.hideFeaturePopup(e),
        );
        // On mobile, touching a feature should bring up the popup, so they can click on the popup and manually click off
        this.map.on("touchstart", "unclustered-pages", (e) =>
            this.showFeaturePopup(e),
        );
        this.map.on("click", (e) => this.hideFeaturePopup(e));
    }

    clickFeaturePopup(
        e: mapboxgl.MapMouseEvent & {
            features?: mapboxgl.MapboxGeoJSONFeature[] | undefined;
        } & mapboxgl.EventData,
    ) {
        if (
            !this.map ||
            !e.features ||
            !e.features?.[0]?.geometry?.type ||
            e.features?.[0]?.geometry?.type !== "Point" ||
            !e.features?.[0]?.properties
        )
            return;
        // @ts-ignore
        let feature = e.features[0] as GeocodedPageFeature;
        window.location.href = feature.properties.url;
    }

    showFeaturePopup(
        e: (mapboxgl.MapMouseEvent | mapboxgl.MapTouchEvent) & {
            features?: mapboxgl.MapboxGeoJSONFeature[] | undefined;
        } & mapboxgl.EventData,
    ) {
        if (
            !this.map ||
            !e.features ||
            !e.features?.[0]?.geometry?.type ||
            e.features?.[0]?.geometry?.type !== "Point" ||
            !e.features?.[0]?.properties
        )
            return;

        // Clear previous popup first
        this.resetFeaturePopup();

        // Change the cursor style as a UI indicator.
        this.map.getCanvas().style.cursor = "pointer";

        // @ts-ignore
        this.highlightedFeature = e.features[0] as GeocodedPageFeature;

        // Set this to true in case of touch events
        // where we still want to style them as though they were hovered
        this.map.setFeatureState(
            {
                source: "pages",
                id: this.highlightedFeature.id,
            },
            {
                hover: true,
            },
        );

        // Copy coordinates array.
        const coordinates =
            this.highlightedFeature.geometry.coordinates.slice();

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the featurePopup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        // Populate the featurePopup and set its coordinates
        // based on the feature found.
        this.featurePopup
            .setLngLat(coordinates as LngLatLike)
            .setHTML(
                `
            <a class='flex flex-row group/popup items-center justify-between' href='${
                this.highlightedFeature.properties.url
            }'>
              <div class='p-4'>
                <div class='text-gray-700 text-sm font-medium capitalize'>${
                    this.highlightedFeature.properties.label
                }</div>
                <div class='text-gray-900 leading-tight text-base font-semibold'>${
                    this.highlightedFeature.properties.title
                }</div>
              </div>
              ${
                  this.highlightedFeature.properties.map_image_url?.length
                      ? `
                <div class='relative w-[130px] h-[130px] overflow-hidden'>
                  <div class="absolute inset-0 bg-cover bg-center scale-100 transition-all group-hover/popup:scale-110" style="background-image: url('${this.highlightedFeature.properties.map_image_url}')"></div>
                </div>
              `
                      : ""
              }
            </a>
          `,
            )
            .addTo(this.map);
    }

    hideFeaturePopup(
        e: mapboxgl.MapMouseEvent & {
            features?: mapboxgl.MapboxGeoJSONFeature[] | undefined;
        } & mapboxgl.EventData,
    ) {
        if (!this.map) return;
        this.map.getCanvas().style.cursor = "";
        this.resetFeaturePopup();
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
                    .setLngLat(lngLat),
            };

            this.updateMarkerVisibility(this.markers[id]);
        }
    }

    private highlightedFeature?: GeocodedPageFeature;
    private _featurePopup!: Popup;
    get featurePopup() {
        if (!this._featurePopup) {
            // Create a popup, but don't add it to the map yet.
            this._featurePopup = new Popup({
                closeButton: false,
                closeOnClick: false,
                maxWidth: "350px",
                offset: 30,
                anchor: "top",
            });
        }
        return this._featurePopup;
    }

    resetFeaturePopup() {
        if (!this.map || !this.highlightedFeature) return;
        this.featurePopup.remove();
        this.map.removeFeatureState({
            source: "pages",
            id: this.highlightedFeature.id,
        });
        this.highlightedFeature = undefined;
    }

    /**
     * DOM
     */

    updateMarkerVisibilitys() {
        if (!this.map) return;
        for (const marker of Object.values(this.markers)) {
            this.updateMarkerVisibility(marker);
        }
    }

    updateMarkerVisibility(marker: typeof this.markers[number]) {
        if (!this.map) return;
        if (
            !marker.allowedDisplayModes?.includes(this.modeValue) ||
            marker.currentDisplayModeOnly
        ) {
            marker.marker.remove();
        } else {
            marker.marker.addTo(this.map);
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

        // Reset UI elements
        this.resetFeaturePopup();

        // Mode-specific config
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
