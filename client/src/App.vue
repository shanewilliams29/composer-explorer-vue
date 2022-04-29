<template>
  <div id="app">
    <NavBar/>
    <router-view/>
    <SpotifyPlayer/>
    <Transition name="fadeHeight"><div class="info-panel" v-show='showPanel'><InfoPanel/></div></Transition>
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
    background: #93989f !important;
    /*font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Open Sans", Roboto, Ubuntu, "Helvetica Neue", Helvetica !important;*/
  }
  #app{
    height: 100% !important;
    width: 100% !important;
    max-height: -webkit-fill-available !important;
    overflow-x: hidden;
    overflow-y: hidden;
    background-color: #f1f2f4 !important;
    max-width:1280px;
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
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
.last-col{

    -ms-flex: 0 0 330px;
    flex: 0 0 330px;
}
</style>
