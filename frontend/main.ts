import "./scss/main.scss";
import "@hotwired/turbo";
import "flowbite";
import "swiper/css/bundle";
import { startApp } from "groundwork-django";
const controllers = import.meta.glob("./controllers/*-controller.ts");
const application = startApp(controllers);

if (import.meta.env.DEV) {
    application.debug = true;
}
