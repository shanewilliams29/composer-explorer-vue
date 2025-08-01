<template>
  <div>
    <div class="container-fluid">
      <b-row class="footer-row">
        <b-col v-show="false" class="info-col">
          <AlbumInfo />
        </b-col>
        <b-col>
          <b-button class="info-panel-button" @click="togglePanel();">
            <span class="icon-inactive" v-if="!showPanel"><b-icon-info-circle></b-icon-info-circle></span>
            <span class="icon-active" v-if="showPanel"><b-icon-info-circle></b-icon-info-circle></span>
          </b-button>
          <PlayerControls />
        </b-col>
      </b-row>
    </div>
    <div>
      <Transition name="fade">
        <img v-if="reveal" class="header-image" key="1" :src="image1" />
      </Transition>
      <Transition name="fade">
        <img v-if="!reveal" class="header-image" key="2" :src="image2" />
      </Transition>
    </div>
    <div class="fade-panel"></div>
  </div>
</template>


<script>
import AlbumInfo from '@/components/playback/AlbumInfo.vue'
import PlayerControls from '@/components/playback/PlayerControls.vue'
import {eventBus} from "@/main.js";

export default {
  components: {
    AlbumInfo,
    PlayerControls,
  },
  props: {
    showPanel: Boolean
  },
  data() {
    return {
      genreTitle: this.$config.genre,
      defaultImage: "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/Orchestral.jpg",
      imgLink: "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/" + encodeURIComponent(this.$config.genre) + ".jpg",
      image1: "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/Orchestral.jpg",
      image2: "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/Orchestral.jpg",
      reveal: false
    };
  },
  computed:{
    genreChanged(){
      return this.$config.genre;
    },
    titleChanged(){
      return this.$config.workTitle;
    }
  },
  watch: {
    genreChanged(newGenre) {
      this.genreTitle = newGenre;
      this.imgLink = "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/" + encodeURIComponent(this.genreTitle) + ".jpg"
    },
    titleChanged(newTitle){
      if(this.genreTitle == 'Opera' || this.genreTitle == 'Stage Work' || this.genreTitle == 'Ballet'){
        this.imgLink = "https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/" + encodeURIComponent(newTitle) + ".jpg"
      }
    }
  },
  methods:{
    iOS() {
      return [
        'iPad Simulator',
        'iPhone Simulator',
        'iPod Simulator',
        'iPad',
        'iPhone',
        'iPod'
      ].includes(navigator.platform)
      // iPad on iOS 13 detection
      || (navigator.userAgent.includes("Mac") && "ontouchend" in document)
    },
    makeToast() {
      this.$bvToast.toast(`Get the App on Google Play Store`, {
        href: 'https://play.google.com/store/apps/details?id=com.app.composerexplorer',
        title: 'App available for Android',
        toaster: 'b-toaster-bottom-full',
        solid: true,
        autoHideDelay: 3600000,
      })
    },
    togglePanel(){
      this.$emit('togglePanel'); 
    },
    updatePic(){
      this.reveal = !this.reveal;

      if (this.reveal) {
        this.checkImage(this.imgLink, 
          () => { this.image1 = this.imgLink; }, 
          () => { this.image1 = this.defaultImage; } 
          );
      } else {
        this.checkImage(this.imgLink, 
          () => { this.image2 = this.imgLink; }, 
          () => { this.image2 = this.defaultImage; } 
        );
      }
    },
    checkImage(imageSrc, good, bad) {
      var img = new Image();
      img.onload = good; 
      img.onerror = bad;
      img.src = imageSrc;
    }
  },
  created(){
    eventBus.$on('fireSetAlbum', this.updatePic);
    eventBus.$on('fireSetAlbumHopper', this.updatePic);
  },
  mounted(){
    var apple = this.iOS();
    var userAgent = window.navigator.userAgent.toLowerCase();

    if (!userAgent.includes('wv')) { // Webview (App)
      if (this.$view.mobile && !apple) {
        // this.makeToast();
      }
    }
  },
};
</script>

<style scoped>
.header-image {
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 1.0) 0%, transparent 100%);
  position: absolute;
  object-fit: cover;
  height: 130px;
  width: 100%;
  left: 0px;
  bottom: 70px;
  z-index: -5;
  opacity: 0.3;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 2s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
.container-fluid {
  position: relative;
  background:  none;
  padding-bottom: 0px;
  border-radius: 0px;
  border-radius: 0px;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  color: var(--my-white);
  z-index: 10;
  opacity: 1;
}
.col {
  padding: 0px;
}
.info-panel-button {
  position: absolute;
  right: 20px;
  font-size: 18px !important;
  border-radius: 50% !important;
  padding-left: 2.8px !important;
  padding-right: 2.8px !important;
  padding-top: 1.2px;
  padding-bottom: 0px;
  bottom: calc(90px);
  z-index: 1;
  background: none;
  border: none !important;
  box-shadow: none !important;
}
.btn:hover, .btn:focus, .btn:active{
   outline: none !important;
   box-shadow: none;
}
.icon-inactive{
  color: var(--my-white) !important;
}
.icon-active{
  color: var(--yellow) !important;
}
</style>
