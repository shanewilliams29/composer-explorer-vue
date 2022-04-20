<template>
  <div id="app">
    <router-view/>
    <SpotifyPlayer/>
    <div class="info-panel" v-show='showPanel'><InfoPanel/></div>
    <b-button class="info-panel-button float" @click="togglePanel()" variant="warning"><span v-if="!showPanel"><b-icon-chevron-up></b-icon-chevron-up></span><span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL</b-button>
    <PageFooter/>
  </div>
</template>

<script>
import SpotifyPlayer from '@/components/SpotifyPlayer.vue'
import InfoPanel from '@/components/InfoPanel.vue'
import PageFooter from '@/components/PageFooter.vue'

import axios from 'axios';
import {eventBus} from "./main.js";
import {currentConfig} from "./main.js";

export default {
  components: {
    SpotifyPlayer,
    InfoPanel,
    PageFooter
  },
  data() {
    return {
      showPanel: false
    };
  },
  methods: {
    getSpotifyToken() {
      const path = 'api/get_token';
      axios.get(path)
        .then((res) => {
          if (res.data.status == "success") {
            if (res.data.client_token !== null) {
              eventBus.$emit('fireLogIn', currentConfig.loggedIn);
              window.token = res.data.client_token;
            } else {
              window.token = res.data.app_token;
            }
          }
          console.log(window.token);
        })
        .catch((error) => {
          window.token = null;
          console.error(error);
        });
    },
    togglePanel(){
      this.showPanel = !this.showPanel;
      if (this.showPanel){
        document.documentElement.style.setProperty('--panelheight', `300px`);
        eventBus.$emit('expandInfoPanel', currentConfig.composer, currentConfig.work);
      } else{
        document.documentElement.style.setProperty('--panelheight', `0px`);
      }
    }
  },
  beforeCreate(){
    if( screen.width <= 760 ) {
        //this.$router.replace('mobile');
        window.location.replace('mobile');
    }
  document.documentElement.style.setProperty('--panelheight', `0px`);
  },
  created(){
    this.getSpotifyToken();
  },
}
</script>

<style>
  html, body {
    height: 100% !important;
    max-height: -webkit-fill-available !important;
    /*font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Open Sans", Roboto, Ubuntu, "Helvetica Neue", Helvetica !important;*/
  }
  #app{
    height: 100% !important;
    max-height: -webkit-fill-available !important;
    overflow-x: hidden;
    background: #f1f2f4 !important;
    }
  .info-panel-button{
  font-size: 10px !important;
  border-radius: 0px !important;
  padding-top: 1px !important;
  padding-bottom: 1px !important;
  position:fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom:92px;
  z-index: 1000;
  }
</style>
