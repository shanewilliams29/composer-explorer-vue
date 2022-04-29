import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import axios from 'axios'
import VueTypeaheadBootstrap from 'vue-typeahead-bootstrap' // not used?
import vSelect from 'vue-select'
import InfiniteLoading from 'vue-infinite-loading'
import VueLazyload from 'vue-lazyload'
import vueDebounce from 'vue-debounce'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-select/dist/vue-select.css'

import router from './router'

Vue.config.productionTip = false;

axios.defaults.baseURL = process.env.VUE_APP_BASE_URL;

Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(vueDebounce, {
  defaultTime: '300ms'
})
Vue.use(InfiniteLoading, {
  props: {
    spinner: 'spiral',
    distance: 200,
  },
});

const loadimage = require('./assets/album_placeholder.png')
Vue.use(VueLazyload, {
  preLoad: 1.3,
  error: loadimage,
  loading: loadimage,
  attempt: 1
})

Vue.component('vue-typeahead-bootstrap', VueTypeaheadBootstrap);
Vue.component('v-select', vSelect);

export const eventBus = new Vue();
export const spotifyPlayer = new Vue();
export const baseURL = process.env.VUE_APP_BASE_URL;

//Vue.prototype.$userSettings = Vue.observable({albumSize: 'large'});

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
                          album: "BEETHOVEN000056eOuqhCfrTPp1H0YbQ9PmL",
                          albumSize: 'large'
                        };

if (localStorage.getItem("config") !== null) {
    config = JSON.parse(localStorage.getItem('config'));
} else {
    config = defaultConfig;
}

export const startTracks = config.playTracks; // used in initial startp play button press

Vue.prototype.$config = Vue.observable(config);
Vue.prototype.$auth = Vue.observable({ appToken: null,
                                       clientToken: null,
                                       deviceID: null
                                      });

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
