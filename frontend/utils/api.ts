export type GeocodedPageFeatureProperties = {
    url: string;
    id: string;
    title: string;
    relatedCountries: string[];
    geographical_location: string | null;
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
    const data = await fetch(url);
    return (await data.json()) as GeocodedPageFeatureCollection;
}
