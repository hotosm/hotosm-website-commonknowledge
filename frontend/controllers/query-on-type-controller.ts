import { Controller } from "@hotwired/stimulus";
import qs from "query-string";
import { debounce } from "lodash";

/**
* Use like:
<div data-controller="query-on-type" data-query-on-type-debounce-value="300" data-query-on-type-original-src-value="/frame/search">
<input type="text" data-action="input->query-on-type#update" data-query-on-type-property-param="query" />
<turbo-frame src="" data-query-on-type-target="frame" />
</div>
*/
export default class QueryOnTypeController extends Controller {
    static targets = ["frame"];
    private readonly frameTarget?: HTMLIFrameElement;
    static values = {
        debounce: { type: Number, default: 300 },
        originalSrc: String,
    };
    debounceValue!: number;
    originalSrcValue?: string;
    private updateSrcDebounced!: (property: string, value: string) => void;

    connect() {
        this.updateSrcDebounced = debounce(
            (property: string, value: string) => {
                if (!this.frameTarget || !this.originalSrcValue) return;
                const newURL = qs.stringifyUrl({
                    url: this.originalSrcValue,
                    query: {
                        [property]: value.trim(),
                    },
                });
                if (this.frameTarget.src === newURL) return;
                this.frameTarget.src = newURL;
            },
            this.debounceValue,
        );
    }

    update(e: any) {
        this.updateSrcDebounced(e.params.property, e.target.value);
    }
}
