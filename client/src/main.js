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

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
