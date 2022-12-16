<template>
  <div id="app">
    <PatreonBanner />
    <NavBar />
    <ConnectingOverlay />
    <WelcomeOverlay />
    <router-view />
    <SpotifyPlayer />
    <ModalContainer />
    <Transition name="fadeHeight">
      <div class="info-panel" v-show="showPanel"><InfoPanel /></div>
    </Transition>
    <div v-if="!$view.mobile">
      <PageFooter />
    </div>
    <div id="footer" v-if="$view.mobile" v-show="!$view.mobileKeyboard">
      <div class="info-panel-mobile" v-show="showPanel"><MobileInfoPanel /></div>
      <MobileTracks />
      <MobileFooter />
    </div>
  </div>
</template>

<script>
import PatreonBanner from "@/components/subcomponents/PatreonBanner.vue";
import ConnectingOverlay from "@/components/ConnectingOverlay.vue";
import WelcomeOverlay from "@/components/WelcomeOverlay.vue";
import SpotifyPlayer from "@/components/SpotifyPlayer.vue";
import InfoPanel from "@/components/InfoPanel.vue";
import PageFooter from "@/components/PageFooter.vue";
import NavBar from "@/components/NavBar.vue";
import ModalContainer from "@/components/ModalContainer.vue";
import MobileInfoPanel from "@/components/mobile/MobileInfoPanel.vue";
import MobileTracks from "@/components/mobile/MobileTracks.vue";
import MobileFooter from "@/components/mobile/MobileFooter.vue";

export default {
  components: {
    PatreonBanner,
    NavBar,
    WelcomeOverlay,
    ConnectingOverlay,
    SpotifyPlayer,
    ModalContainer,
    MobileTracks,
    MobileFooter,
    MobileInfoPanel,
    InfoPanel,
    PageFooter,
  },
  data() {
    return {
      showPanel: false,
    };
  },
  methods: {
    togglePanel() {
      this.showPanel = !this.showPanel;
      if (this.showPanel) {
        this.$view.panelVisible = true;
        setTimeout(() => {
          document.documentElement.style.setProperty("--panelheight", `300px`);
        }, 300);
      } else {
        document.documentElement.style.setProperty("--panelheight", `0px`);
        setTimeout(() => {
          this.$view.panelVisible = false; // Delay to allow animation
        }, 300);
      }
    },
  },
  beforeCreate() {
    if (this.$route.name == "mobile" || this.$route.name == "mobileradio") {
      this.$view.mobile = true;
      document.documentElement.style.setProperty("--playerpadding", `0px`);
      document.documentElement.style.setProperty("--workingheight", `310px`);
      document.documentElement.style.setProperty("--workingheightnoheader", `194px`);
      document.documentElement.style.setProperty("--appbackgroundcolor", `var(--dark-gray)`);
    } else {
      this.$view.mobile = false;
      document.documentElement.style.setProperty("--playerpadding", `21.5px`);
      document.documentElement.style.setProperty("--workingheight", `244px`);
      document.documentElement.style.setProperty("--workingheightnoheader", `183px`);
      document.documentElement.style.setProperty("--appbackgroundcolor", `var(--light-gray)`);
    }
    document.documentElement.style.setProperty("--panelheight", `0px`);
    this.$view.panelVisible = false;
  },
};

</script>

<style>
  @import '@/assets/styles.css';
</style>

<style scoped>
#app {
  height: 100% !important;
  width: 100% !important;
  max-height: -webkit-fill-available !important;
  overflow-x: hidden;
  overflow-y: hidden;
  background-color: var(--appbackgroundcolor) !important;
  max-width: 1440px;
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
}
#footer {
  height: 200px !important;
  background: none;
}
.info-panel {
  position: fixed;
  bottom: 100px;
  width: 100%;
}
.info-panel-mobile {
  position: fixed;
  bottom: 130px;
  width: 100%;
  z-index: 1000;
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
</style>
