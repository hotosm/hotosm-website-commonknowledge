export type GeocodedPageFeatureProperties = {
    url: string;
    label: string;
    title: string;
    relatedCountries: string[];
    geographical_location?: string | null;
    map_image_url?: string | null;
    has_unique_location?: boolean;
};

export type GeocodedPageFeature = WithRequiredProperty<
    GeoJSON.Feature<GeoJSON.Point, GeocodedPageFeatureProperties>,
    "id"
>;
export type GeocodedPageFeatureCollection = GeoJSON.FeatureCollection<
    GeoJSON.Point,
    GeocodedPageFeatureProperties
>;

export async function getMapData(url: string) {
    const data = await fetch(url, { cache: "force-cache" });
    return (await data.json()) as GeocodedPageFeatureCollection;
}
