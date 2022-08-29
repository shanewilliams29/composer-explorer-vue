<template>
  <div id="app">
    <NavBar/>
    <WelcomeOverlay />
    <router-view />
    <SpotifyPlayer />
    <Transition name="fadeHeight">
      <div class="info-panel" v-show="showPanel"><InfoPanel /></div>
    </Transition>
    <div v-if="!$view.mobile">
      <PageFooter />
    </div>
    <div id="footer" v-if="$view.mobile" v-show="!$view.mobileKeyboard">
      <div class="info-panel-mobile" v-show="showPanel"><MobileInfoPanel /></div>
      <MobileTracks />
      <MobileFooter/>
  </div>
  </div>
</template>

<script>
import WelcomeOverlay from '@/components/WelcomeOverlay.vue'
import SpotifyPlayer from '@/components/SpotifyPlayer.vue'
import InfoPanel from '@/components/InfoPanel.vue'
import PageFooter from '@/components/PageFooter.vue'
import NavBar from '@/components/NavBar.vue'
import MobileInfoPanel from '@/components/mobile/MobileInfoPanel.vue'
import MobileTracks from '@/components/mobile/MobileTracks.vue'
import MobileFooter from '@/components/mobile/MobileFooter.vue'

export default {
  components: {
    NavBar,
    WelcomeOverlay,
    SpotifyPlayer,
    MobileTracks,
    MobileFooter,
    MobileInfoPanel,
    InfoPanel,
    PageFooter
  },
  data() {
    return {
      showPanel: false
    };
  },
  methods: {
    togglePanel() {
      this.showPanel = !this.showPanel;
      if (this.showPanel) {
        this.$view.panelVisible = true;
        setTimeout(() => {
          document.documentElement.style.setProperty('--panelheight', `300px`);
        }, 300);
      } else {
        document.documentElement.style.setProperty('--panelheight', `0px`);
        setTimeout(() => {
          this.$view.panelVisible = false; // Delay to allow animation
        }, 300);
      }
    }
  },
  beforeCreate() {
    // if (screen.width <= 760) {
    //   window.location.replace('mobile');
    // }
    document.documentElement.style.setProperty('--panelheight', `0px`);
    this.$view.panelVisible = false;
  },
  mounted(){
    console.log(this.$view.mobile);
    if(this.$view.mobile){
      document.documentElement.style.setProperty('--playerpadding', `3px`);
    } else {
      document.documentElement.style.setProperty('--playerpadding', `21.5px`);
    }
  }
}
</script>

<style>
html,
body {
  height: 100% !important;
  max-height: -webkit-fill-available !important;
  background: #93989f !important;
}
#app {
  height: 100% !important;
  width: 100% !important;
  max-height: -webkit-fill-available !important;
  overflow-x: hidden;
  overflow-y: hidden;
  background-color: #f1f2f4 !important;
  max-width: 1440px;
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
}

.info-panel {
  position: fixed;
  bottom: 100px;
  width: 100%;
}
.info-panel-mobile {
  position: fixed;
  bottom: 123px;
  width: 100%;
}
.fadeHeight-enter-active,
.fadeHeight-leave-active {
  transition: all 0.3s;
  max-height: 300px;
}
.fadeHeight-enter,
.fadeHeight-leave-to {
  opacity: 0;
  max-height: 0px;
}
 .playback-container{
    padding-top: var(--playerpadding) !important;
  }
</style>
