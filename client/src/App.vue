<template>
  <div id="app">
    <NavBar/>
    <router-view/>
    <SpotifyPlayer/>
    <Transition name="fadeHeight"><div class="info-panel" v-show='showPanel'><InfoPanel/></div></Transition>
    <b-button class="info-panel-button float" @click="togglePanel()" variant="warning"><span v-if="!showPanel"><b-icon-chevron-up></b-icon-chevron-up></span><span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL</b-button>
    <PageFooter/>
  </div>
</template>

<script>
import SpotifyPlayer from '@/components/SpotifyPlayer.vue'
import InfoPanel from '@/components/InfoPanel.vue'
import PageFooter from '@/components/PageFooter.vue'
import NavBar from '@/components/NavBar.vue'

export default {
  components: {
    NavBar,
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
    togglePanel(){
      this.showPanel = !this.showPanel;
      if (this.showPanel){
        document.documentElement.style.setProperty('--panelheight', `300px`);
        // eventBus.$emit('expandInfoPanel', currentConfig.composer, currentConfig.work);
      } else{
        document.documentElement.style.setProperty('--panelheight', `0px`);
      }
    }
  },
  beforeCreate(){
    if( screen.width <= 760 ) {
        window.location.replace('mobile');
    }
  document.documentElement.style.setProperty('--panelheight', `0px`);
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

.page-height{
    height: calc(100vh - 66px - 78px + 78px - 100px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
}

.info-panel{
  position:  fixed;
  bottom: 100px;
  width: 100%;
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
.fadeHeight-enter-active,
.fadeHeight-leave-active {
  transition: all 0.3s;
  max-height: 300px;
}
.fadeHeight-enter,
.fadeHeight-leave-to
{
  opacity: 0;
  max-height: 0px;
}
</style>
