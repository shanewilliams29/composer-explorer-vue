import Vue from 'vue'
import VueRouter from 'vue-router'
import PageNotFound from '../views/PageNotFound.vue'
import HomeView from '../views/HomeView.vue'
import MobileView from '../views/MobileView.vue'
import MobileSearch from '../views/MobileSearch.vue'
import PerformerView from '../views/PerformerView.vue'
import AlbumView from '../views/AlbumView.vue'
import RadioView from '../views/RadioView.vue'
import FavoritesView from '../views/FavoritesView.vue'
import MobileRadio from '../views/MobileRadio.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/mobile',
    name: 'mobile',
    component: MobileView
  },
  {
    path: '/performers',
    name: 'performers',
    component: PerformerView
  },
    {
    path: '/albums',
    name: 'albums',
    component: AlbumView
  },
  {
    path: '/radio',
    name: 'radio',
    component: RadioView
  },
    {
    path: '/favorites',
    name: 'favorites',
    component: FavoritesView
  },
    {
    path: '/mobilesearch',
    name: 'mobilesearch',
    component: MobileSearch
  },
    {
    path: '/mobileradio',
    name: 'mobileradio',
    component: MobileRadio
  },
  {
    path: '/:catchAll(.*)*',
    name: "PageNotFound",
    component: PageNotFound,
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
