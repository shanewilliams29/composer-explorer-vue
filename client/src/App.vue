<template>
  <div id="app">
    <PatreonBanner />
    
    <NavBar />
    <MobileNavbar />
    <ConnectingOverlay />
    <WelcomeOverlay />
    <MobileWelcomeOverlay />
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
          <MobileInfoPanel @togglePanel="togglePanel" :showPanel="childShowPanel"/>
        </div>
      </Transition>
      <MobileTracks />
      <MobileFooter :showPanel="showPanel" @togglePanel="togglePanel"/>
      
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
import MobileWelcomeOverlay from "@/components/mobile/MobileWelcomeOverlay.vue";

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
    MobileWelcomeOverlay
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
      // Gets list of all artists for album view and radio mode
      const path = "api/artistlist";
      axios
        .get(path)
        .then((res) => {
          this.$lists.artistList = res.data.artists;
          var artistlist = {data: res.data.artists, timestamp: new Date().toISOString()};
          localStorage.setItem("artistlist", JSON.stringify(artistlist));
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
          this.$lists.albumViewWorks = this.$lists.workList;
          var workslist = {data: res.data.works, timestamp: new Date().toISOString()};
          localStorage.setItem("workslist", JSON.stringify(workslist));
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
    if (this.$route.name == "mobile" || this.$route.name == "mobileradio" || this.$route.name == "mobilesearch" || this.$route.name == "mobileperformers" || this.$route.name == "mobilealbums" || this.$route.name == "mobilefavorites") {
      this.$view.mobile = true;
      document.documentElement.style.setProperty("--playerpadding", `0px`);
      //document.documentElement.style.setProperty("--workingheight", `191.6px`);
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
    // For mobile keyboard detection
    this.$view.initialWindowHeight = window.innerHeight;
    // Get composer list (albums, radio)
    this.getComposerList();
    // Get works list (albums)
    this.getWorksList();
    // Get artists list (albums, radio)
    let artistlist = JSON.parse(localStorage.getItem("artistlist"));
    
    if (artistlist !== null) {
        let storedTimestamp = new Date(artistlist.timestamp);
        let oneMonthAgo = new Date();
        oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
        if (storedTimestamp < oneMonthAgo) {
          // console.log('The timestamp is more than one month old');
          this.getArtistList();
        } else {
          // console.log('The timestamp is less than one month old');
          this.$lists.artistList = artistlist.data;
        }
      } else {
        this.getArtistList();
      }
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
