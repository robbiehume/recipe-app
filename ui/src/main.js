import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import ToastService from "primevue/toastservice";

import App from "./App.vue";
import router from "./router";

import PrimeVue from "primevue/config";
// import 'primevue/resources/themes/saga-blue/theme.css'; // Choose a theme
import "primevue/resources/themes/aura-light-blue/theme.css";
import "primevue/resources/primevue.min.css"; // Core CSS
import "primeicons/primeicons.css"; // Icons

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  ripple: true,
  inputStyle: "outlined",
});
app.use(ToastService);

app.mount("#app");
