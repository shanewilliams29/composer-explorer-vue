import axios from 'axios';
import Vue from 'vue';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.css';

Vue.config.productionTip = false;

axios.defaults.baseURL = process.env.VUE_APP_BASE_URL;

new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
