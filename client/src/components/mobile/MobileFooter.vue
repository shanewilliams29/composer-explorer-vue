<template>
  <div>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
          <b-button class="info-panel-button" @click="togglePanel()">
          <span class="icon-inactive" v-if="!buttonActive"><b-icon-info-circle></b-icon-info-circle></span>
          <span class="icon-active" v-if="buttonActive"><b-icon-info-circle></b-icon-info-circle></span>
        </b-button>
        <MobilePlayerControls />
      </b-col>
    </b-row>
  </div>
<div>
  <img class="header-image" :src="liveImage">
</div>
<div class="fade-panel">
   
</div>
</div>
</template>

<script>
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import MobilePlayerControls from '@/components/mobile/MobilePlayerControls.vue'
import {eventBus} from "@/main.js";

export default {
  components: {
    AlbumInfo,
    MobilePlayerControls,
  },
  data() {
    return {
      buttonActive: false,
      genreTitle: this.$config.genre,
      defaultImage: "https://storage.googleapis.com/composer-explorer.appspot.com/headers/Chamber.jpg",
      imgLink: "https://storage.googleapis.com/composer-explorer.appspot.com/headers/" + encodeURIComponent(this.$config.genre) + ".jpg",
      liveImage: ''
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
      this.imgLink = "https://storage.googleapis.com/composer-explorer.appspot.com/headers/" + encodeURIComponent(this.genreTitle) + ".jpg"
      console.log(this.imgLink);
    },
    titleChanged(newTitle){
      if(this.genreTitle == 'Opera' || this.genreTitle == 'Stage Work' || this.genreTitle == 'Ballet'){
        this.imgLink = "https://storage.googleapis.com/composer-explorer.appspot.com/headers/" + encodeURIComponent(newTitle) + ".jpg"
      }
    }
  },
  methods:{
    togglePanel(){
      this.$parent.togglePanel();
      this.buttonActive = !this.buttonActive;
    },
      updatePic(){
      this.checkImage(this.imgLink, 
        () => { this.liveImage = this.imgLink; }, 
        () => { this.liveImage = this.defaultImage; } 
        );
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
  }
};
</script>

<style scoped>
/*.fade-panel {
  position: fixed;
  bottom: 0px;
  height: 120px;
  width: 100%;
  background: rgb(0,0,0);
  background: linear-gradient(0deg, rgba(0,0,0,1) 0%, rgba(52,58,64,1) 100%);
  z-index: -10;
}*/
.header-image {
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 1.0) 0%, transparent 100%);
  position: absolute;
  object-fit: cover;
  height: 130px;
  width: 100%;
/*  left: 50%;
  transform: translate(-50%, 0);*/
  left: 0px;
  bottom: 0px;
  z-index: -5;
  opacity: 0.3;
/*  -webkit-filter: grayscale(100%);
  filter: grayscale(100%);*/
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
  color: white;
  z-index: 10;
  opacity: 1;
}
.col {
  padding: 0px;
}
.info-panel-button {
  position: absolute;
  right: 13px;
  font-size: 18px !important;
  border-radius: 50% !important;
  padding-left: 2.8px !important;
  padding-right: 2.8px !important;
  padding-top: 1.2px;
  padding-bottom: 0px;
  bottom: calc(117px - 22.5px - 13px);
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
  color: white !important;
}
.icon-active{
  color: var(--yellow) !important;
}
</style>
