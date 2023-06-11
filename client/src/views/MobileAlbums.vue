<template>
  <div id="performer">
    <MobileAlbumsHeading/>
    <div class="albums-container">
    <div class="container-fluid">
      <Transition name="fade">
      <b-row v-if="showCloud">
        <b-col class="display-list disable-scrollbars" @scroll="hideKeyboard"><MobileAlbumsBody/></b-col>
      </b-row>
      </Transition>
    </div>
  </div>
  </div>
</template>



<script>
import MobileAlbumsHeading from '@/components/mobile/MobileAlbumsHeading.vue'
import MobileAlbumsBody from '@/components/mobile/MobileAlbumsBody.vue';

import {eventBus} from "../main.js";

export default {
  name: 'MobileAlbums',
  components: {
    MobileAlbumsHeading,
    MobileAlbumsBody
  },
  data() {
    return {
      showCloud: true
    };
  },
  methods: {
    hideCloud () {
      this.showCloud = false;
    },
    unhideCloud () {
      this.showCloud = true;
    },
    hideKeyboard() {
      document.activeElement.blur();
    },
    detectKeyboard() {
      let vh = window.innerHeight * 0.01;
      // for mobile keyboard
      if (window.innerHeight < this.$view.initialWindowHeight) {
        this.$view.mobileKeyboard = true;
        vh = vh + 145 * 0.01;
      } else {
        this.$view.mobileKeyboard = false;
      }
      document.documentElement.style.setProperty("--vh", `${vh}px`);
    }
  },
  beforeCreate() {
    document.documentElement.style.setProperty("--flex", "1");
    document.documentElement.style.setProperty("--workingheight", `191.6px`);
  },
  created() {
    this.initialWindowHeight = window.innerHeight;
    window.addEventListener('resize', this.detectKeyboard);

    window.firstLoad = false; // allow playback on first load
    this.$view.shuffle = false;
    eventBus.$on('requestComposersForArtist', this.hideCloud);
    eventBus.$on('clearPerformers', this.unhideCloud);
    this.$view.mode = 'performer';
    if (this.$route.query.artist){
        this.showCloud = false;
    } else{
      this.showCloud = true;
    }
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); //#fd7e14
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.detectKeyboard);
  }
}
</script>
<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.75s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
>>> .highlight{
  background-color: #e47112 !important;
}
>>> .highlight td{
  background-color: #e47112 !important;
}
>>> .music-note{
  color: var(--orange);
}
.albums-container{
  height: calc(var(--vh, 1vh) * 100 - 78px - var(--workingheight));
}
.display-list{
  height: calc(var(--vh, 1vh) * 100 - 78px - var(--workingheight));
  padding: 0px !important;
}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}
</style>
