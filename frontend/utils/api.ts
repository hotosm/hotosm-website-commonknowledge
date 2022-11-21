export type GeocodedPageFeatureProperties = {
    url: string;
    id: string;
    title: string;
    relatedCountries: string[];
    geographical_location?: string | null;
    map_image_url?: string | null;
    has_unique_location?: boolean;
};

export type GeocodedPageFeature = GeoJSON.Feature<
    GeoJSON.Point,
    GeocodedPageFeatureProperties
>;
export type GeocodedPageFeatureCollection = GeoJSON.FeatureCollection<
    GeoJSON.Point,
    GeocodedPageFeatureProperties
>;

export async function getMapData(url: string) {
    const data = await fetch(url, { cache: "force-cache" });
    return (await data.json()) as GeocodedPageFeatureCollection;
}
