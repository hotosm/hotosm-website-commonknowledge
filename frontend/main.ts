import "./scss/main.scss";
import "@hotwired/turbo";
import "flowbite";

import { startApp } from "groundwork-django";

const controllers = import.meta.glob("./controllers/*-controller.ts");

startApp(controllers);
