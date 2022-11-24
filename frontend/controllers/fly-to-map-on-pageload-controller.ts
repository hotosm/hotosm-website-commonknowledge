import { Context } from "@hotwired/stimulus";
import { MapConfigController } from "groundwork-django";
import { Map } from "mapbox-gl";

export default class NavigateToMapController extends MapConfigController {
    constructor(context: Context) {
        super(context);
        this.goToPageCentroid = this.goToPageCentroid.bind(this);
    }

    connectMap(map: Map): void | Promise<void> {
        super.connect?.();
        this.goToPageCentroid();
    }

    goToPageCentroid() {
        setTimeout(() => {
            const el = this.element as HTMLElement;
            if (!el.dataset.lat || !el.dataset.lng) return;
            const coords = [
                parseFloat(el.dataset.lng),
                parseFloat(el.dataset.lat),
            ] as const;
            this.map?.flyTo({
                center: coords as any,
                zoom: this.map?.getZoom(),
            });
        }, 1000);
    }
}
