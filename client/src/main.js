import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import axios from 'axios';

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import router from './router'

Vue.config.productionTip = false

axios.defaults.baseURL = process.env.VUE_APP_BASE_URL;
// axios.defaults.withCredentials = true;

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

export const eventBus = new Vue();
export const spotifyPlayer = new Vue();
export const baseURL = process.env.VUE_APP_BASE_URL;
export const defaultConfig = {
                                  composer: "Beethoven",
                                  composerId: "1",
                                  work: "BEETHOVEN00005",
                                  workTitle: "Symphony No. 5 in C minor",
                                  playTracks: "spotify:track:6cUCckpdlqHJ5Ascf2uH2A spotify:track:1L0a0dpHaMWgAoEEvFfycT spotify:track:7ojkji0OYCOpl3UMy92gEf spotify:track:4IHaNEgvWUD63pMTWrclb2",
                                  album: "BEETHOVEN000056eOuqhCfrTPp1H0YbQ9PmL"
                                };

let config = {}

if (localStorage.getItem("currentConfig") !== null) {
    config = JSON.parse(localStorage.getItem('currentConfig'));
} else {
    config = defaultConfig;
}

export const currentConfig = config;

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
