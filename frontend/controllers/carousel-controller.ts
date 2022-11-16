import { Controller } from "@hotwired/stimulus";
import { SwiperOptions } from "swiper";
// @ts-ignore
import Swiper from "swiper/bundle";

export default class extends Controller {
    swiper: Swiper;

    values = {
        options: Object,
    };
    optionsValue?: SwiperOptions;

    static values = {
        options: Object,
    };

    connect(): void {
        this.swiper = new Swiper(this.element, {
            ...this.defaultOptions,
            ...this.optionsValue,
        });
    }

    disconnect(): void {
        this.swiper.destroy();
        this.swiper = undefined;
    }

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
