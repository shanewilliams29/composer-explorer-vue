<template>
  <div id="app">
    <PatreonBanner />
    
    <NavBar />
    <MobileNavbar />
    <ConnectingOverlay />
    <WelcomeOverlay />
    <ModalContainer />

    <SpotifyPlayer />

    <router-view />

    <Transition name="fadeHeight">
      <div class="info-panel" v-if="showPanel && !$view.mobile">
        <InfoPanel/>
      </div>
    </Transition>
    <PageFooter v-if="!$view.mobile" :showPanel="showPanel" @togglePanel="togglePanel"/>

    <div id="footer" v-if="$view.mobile" v-show="!$view.mobileKeyboard">
      <Transition name="fadeHeight2">
        <div class="info-panel-mobile" v-show="showPanel">
          <MobileInfoPanel :showPanel="childShowPanel"/>
        </div>
      </Transition>
      <MobileTracks />
      <MobileFooter @togglePanel="togglePanel"/>
      
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import PatreonBanner from "@/components/modals/PatreonBanner.vue";
import ConnectingOverlay from "@/components/modals/ConnectingOverlay.vue";
import WelcomeOverlay from "@/components/modals/WelcomeOverlay.vue";
import SpotifyPlayer from "@/components/global/SpotifyPlayer.vue";
import InfoPanel from "@/components/global/InfoPanel.vue";
import PageFooter from "@/components/global/PageFooter.vue";
import NavBar from "@/components/global/NavBar.vue";
import MobileNavbar from "@/components/mobile/MobileNavbar.vue";
import ModalContainer from "@/components/modals/ModalContainer.vue";
import MobileInfoPanel from "@/components/mobile/MobileInfoPanel.vue";
import MobileTracks from "@/components/mobile/MobileTracks.vue";
import MobileFooter from "@/components/mobile/MobileFooter.vue";

export default {
  components: {
    PatreonBanner,
    NavBar,
    MobileNavbar,
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
      childShowPanel: false
    };
  },
  methods: {
    togglePanel() {
      this.showPanel = !this.showPanel;
      this.childShowPanel = true;
      if (this.showPanel) {
        setTimeout(() => {
          document.documentElement.style.setProperty("--panelheight", `300px`);
        }, 500); // Delay for animation
      } else {
        document.documentElement.style.setProperty("--panelheight", `0px`);
        setTimeout(() => {
          this.childShowPanel = false;
        }, 500); // Delay for animation
      }
    },
    getArtistList() {
      // Gets list of all artists for performer and omni search, radio mode
      const path = "api/artistlist";
      axios
        .get(path)
        .then((res) => {
          this.$lists.artistList = res.data.artists;
          localStorage.setItem("ArtistList", JSON.stringify(res.data.artists));
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getWorksList() {
      // Gets list of all works for album view mode
      const path = "api/workslist";
      axios
        .get(path)
        .then((res) => {
          this.$lists.workList = res.data.works;
          this.$lists.albumViewWorks = this.$lists.workList
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getComposerList() {
      // Gets list for radio composers multiselect dropdown
      this.$lists.composerList = []
      const path = "api/composersradio";
      axios
        .get(path)
        .then((res) => {
          this.$lists.composerList = res.data.composers;
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  beforeCreate() {
    if (this.$route.name == "mobile" || this.$route.name == "mobileradio" || this.$route.name == "mobilesearch") {
      this.$view.mobile = true;
      document.documentElement.style.setProperty("--playerpadding", `0px`);
      document.documentElement.style.setProperty("--workingheight", `191.6px`);
      document.documentElement.style.setProperty("--appbackgroundcolor", `var(--dark-gray)`);
    } else {
      this.$view.mobile = false;
      document.documentElement.style.setProperty("--playerpadding", `21.5px`);
      document.documentElement.style.setProperty("--workingheight", `244px`);
      document.documentElement.style.setProperty("--appbackgroundcolor", `var(--light-gray)`);
    }
    document.documentElement.style.setProperty("--panelheight", `0px`);
  },
  mounted(){
    if (localStorage.getItem("ArtistList") !== null) {
        this.$lists.artistList = JSON.parse(localStorage.getItem("ArtistList"));
      } else {
        this.getArtistList();
      }
localStorage.setItem("config", JSON.stringify(this.$config));
    
    this.getComposerList();
    this.getWorksList();
  }
};

</script>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed');
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
  width: 100%;
  position: fixed;
  background: none;
  z-index: 9999;
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
}
.fadeHeight-enter-active,
.fadeHeight-leave-active {
  transition: all 0.5s;
  max-height: 300px;
}
.fadeHeight-enter,
.fadeHeight-leave-to {
  opacity: 0;
  max-height: 0px;
}
.fadeHeight2-enter-active,
.fadeHeight2-leave-active {
  transition: all 0.5s;
  max-height: calc(100vh - 66px);
}
.fadeHeight2-enter,
.fadeHeight2-leave-to {
  opacity: 0;
  max-height: 0px;
  bottom: 130px;
}
</style>
