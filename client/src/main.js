import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import axios from 'axios';
import VueTypeaheadBootstrap from 'vue-typeahead-bootstrap';
import vSelect from 'vue-select'
import InfiniteLoading from 'vue-infinite-loading';



import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-select/dist/vue-select.css';

import router from './router'

Vue.config.productionTip = false;

axios.defaults.baseURL = process.env.VUE_APP_BASE_URL;
// axios.defaults.withCredentials = true;

Vue.use(InfiniteLoading);
Vue.use(BootstrapVue);
Vue.use(IconsPlugin);

Vue.component('vue-typeahead-bootstrap', VueTypeaheadBootstrap);
Vue.component('v-select', vSelect);

export const eventBus = new Vue();
export const spotifyPlayer = new Vue();
export const baseURL = process.env.VUE_APP_BASE_URL;


// Preserve view state between page reloads
let config = {}
const defaultConfig = {
                                  composer: "Beethoven",
                                  composerId: "1",
                                  work: "BEETHOVEN00005",
                                  workTitle: "Symphony No. 5 in C minor",
                                  playTracks: "spotify:track:6cUCckpdlqHJ5Ascf2uH2A spotify:track:1L0a0dpHaMWgAoEEvFfycT spotify:track:7ojkji0OYCOpl3UMy92gEf spotify:track:4IHaNEgvWUD63pMTWrclb2",
                                  allTracks: "spotify:track:6cUCckpdlqHJ5Ascf2uH2A spotify:track:1L0a0dpHaMWgAoEEvFfycT spotify:track:7ojkji0OYCOpl3UMy92gEf spotify:track:4IHaNEgvWUD63pMTWrclb2",
                                  previousTracks: "spotify:track:6cUCckpdlqHJ5Ascf2uH2A spotify:track:1L0a0dpHaMWgAoEEvFfycT spotify:track:7ojkji0OYCOpl3UMy92gEf spotify:track:4IHaNEgvWUD63pMTWrclb2",
                                  trackNo: 0,
                                  album: "BEETHOVEN000056eOuqhCfrTPp1H0YbQ9PmL"
                                };

if (localStorage.getItem("currentConfig") !== null) {
    config = JSON.parse(localStorage.getItem('currentConfig'));
} else {
    config = defaultConfig;
}
export const currentConfig = config;

// Spotify config
let spConfig = {}
const defaultSpotify = {        appToken: null,
                                clientToken: null,
                                deviceID: null
                                };

if (localStorage.getItem("spotifyConfig") !== null) {
    spConfig = JSON.parse(localStorage.getItem('spotifyConfig'));
} else {
    spConfig = defaultSpotify;
}
export const spotifyConfig = spConfig;

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
