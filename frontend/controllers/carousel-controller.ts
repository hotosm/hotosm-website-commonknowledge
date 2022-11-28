import { Controller } from "@hotwired/stimulus";
import { SwiperOptions } from "swiper";
// @ts-ignore
import Swiper from "swiper/bundle";
import type SwiperClass from "swiper";
import { debounce } from "lodash";

export default class extends Controller<HTMLElement> {
    swiper!: SwiperClass;

    static values = {
        options: Object,
        activeIndex: { default: 0, type: Number },
    };
    activeIndexValue?: number;
    optionsValue?: SwiperOptions;

    connect(): void {
        this.swiper = new Swiper(this.element, {
            ...this.defaultOptions,
            ...this.optionsValue,
        });
        if (!!this.activeIndexValue) {
            this.swiper.slideTo(this.activeIndexValue);
        }
        this.swiper.on("activeIndexChange", () => {
            this.activeIndexValue = this.swiper.activeIndex;
        });
    }

    disconnect(): void {
        this.swiper.destroy();
    }

    slideTo = debounce(({ params: { index, speed = undefined } }: any) => {
        if (index !== this.swiper.realIndex) {
            this.swiper.slideTo(index, speed);
        }
    }, 250);

    get defaultOptions(): SwiperOptions {
        return {
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                    spaceBetween: 30,
                },
                768: {
                    slidesPerView: 2,
                    spaceBetween: 20,
                },
                1024: {
                    slidesPerView: 3,
                    spaceBetween: 30,
                },
            },
        };
    }
}
