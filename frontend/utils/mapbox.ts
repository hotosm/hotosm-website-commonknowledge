import mapboxgl from "mapbox-gl";

export const MAPBOX_INTERACTION_METHODS: Array<keyof mapboxgl.Map> = [
    "scrollZoom",
    "boxZoom",
    "dragRotate",
    "dragPan",
    "keyboard",
    "doubleClickZoom",
    "touchZoomRotate",
];
