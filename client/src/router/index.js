import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MobileView from '../views/MobileView.vue'
import PerformerView from '../views/PerformerView.vue'
import RadioView from '../views/RadioView.vue'

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
    path: '/radio',
    name: 'radio',
    component: RadioView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },

]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
