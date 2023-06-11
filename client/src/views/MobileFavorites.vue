<template>
  <div id="performer">
    <FavoritesHeading/>
    <div class="container-fluid">
      <b-row>
        <div class="cards-container" role="tablist">
          <b-card no-body class="mb-1 mobile-card">
            <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
              <b-button class="header-button" :disabled="composerDisabled" @click="composerToggle" block variant="secondary">
                <span class="heading-text">Favorite Composers</span><span class="mb-0 float-right">
                  <b-icon-chevron-down></b-icon-chevron-down>
                </span>
              </b-button>
            </b-card-header>
            <b-collapse :visible="composerDisabled" id="accordion-1" accordion="my-accordion" role="tabpanel">
              <b-card-body>
                <b-col class="composer-list-mobile disable-scrollbars" ref="scroll-box-comp" @scroll="hideKeyboard">
                  <ComposerList />
                </b-col>
              </b-card-body>
            </b-collapse>
          </b-card>
          <b-card no-body class="mb-1 mobile-card">
            <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
              <b-button class="header-button" :disabled="workDisabled" block @click="workToggle" variant="secondary">
                <span v-if="composer" class="heading-text">Favorite Works by {{ composer }}</span>
                <span v-else class="heading-text">Select a composer</span>
                <span class="mb-0 float-right">
                  <b-icon-chevron-down></b-icon-chevron-down>
                </span>
              </b-button>
            </b-card-header>
            <b-collapse :visible="workDisabled" id="accordion-2" accordion="my-accordion" role="tabpanel">
              <b-card-body>
                <b-col class="work-list-mobile disable-scrollbars" ref="scroll-box" @scroll="hideKeyboard">
                  <WorkList />
                </b-col>
              </b-card-body>
            </b-collapse>
          </b-card>
          <b-card no-body class="mb-1 mobile-card">
            <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
              <b-button class="header-button last-button" :disabled="albumDisabled" @click="albumToggle" block variant="secondary">
                <span class="heading-text">{{ title }}</span><span class="mb-0 float-right">
                  <b-icon-chevron-down></b-icon-chevron-down>
                </span>
              </b-button>
            </b-card-header>
            <b-collapse :visible="albumDisabled" id="accordion-3" accordion="my-accordion" role="tabpanel">
              <b-card-body>
                <b-col class="album-list-mobile disable-scrollbars" @scroll="hideKeyboard">
                  <AlbumList />
                </b-col>
              </b-card-body>
            </b-collapse>
          </b-card>
        </div>
      </b-row>
    </div>
  </div>
</template>



<script>
import FavoritesHeading from '@/components/favorites/FavoritesHeading.vue'
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

import {eventBus} from "../main.js";

export default {
  name: 'PerformerView',
  components: {
    FavoritesHeading,
    ComposerList,
    WorkList,
    AlbumList,
  },
  data() {
    return {
      showCloud: true,
      performers: [],
      composer: null,
      title: "Select a work",
      composerDisabled: true,
      workDisabled: false,
      albumDisabled: false,
      initialWorksLoad: true,
      initialAlbumsLoad: true,
      composerListKey: 0,
    };
  },
  methods: {
    hideCloud () {
      this.composerToggle();
      this.composer = null;
      this.showCloud = false;
    },
    unhideCloud () {
      this.showCloud = true;
    },
    hideKeyboard() {
      document.activeElement.blur();
    },
    composerToggle() {
      this.composerDisabled = true;
      this.workDisabled = false;
      this.albumDisabled = false;
    },
    workToggle() {
      this.composerDisabled = false;
      this.workDisabled = true;
      this.albumDisabled = false;
      eventBus.$emit("fireWorkScroll", this.$config.genre); // for mobile
    },
    albumToggle() {
      this.composerDisabled = false;
      this.workDisabled = false;
      this.albumDisabled = true;
    },
    detectKeyboard(){
      let vh = window.innerHeight * 0.01;
      // for mobile keyboard
      if (window.innerHeight < this.$view.initialWindowHeight) {
        this.$view.mobileKeyboard = true;
        vh = vh + 250 * 0.01;
      } else {
        this.$view.mobileKeyboard = false;
      }

      document.documentElement.style.setProperty("--vh", `${vh}px`);
    },
    selectArtist(artist) {
      eventBus.$emit("requestPerformer", artist);
    },
    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array.slice(0,100);
    },
    setWork(composer){
      this.composer = composer;
      this.workToggle();
    },
    setAlbums(){
      this.title = this.$config.workTitle;
      this.albumToggle();
    },
  },
  beforeCreate() {
    document.documentElement.style.setProperty("--workingheight", `193.2px`);
    this.$view.mobile = true;
  },
  created() {
    this.composerToggle();
    this.$view.mode = "favorites";
    this.$view.shuffle = false;
    this.composer = null;

    document.documentElement.style.setProperty("--playback-color", "var(--yellow)");

    eventBus.$on("requestWorksListForFavorites", this.setWork);
    eventBus.$on("requestFavoritesAlbums", this.setAlbums);

    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${vh}px`);

    window.addEventListener('resize', this.detectKeyboard);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.detectKeyboard);
    eventBus.$off("requestWorksListForFavorites", this.setWork);
    eventBus.$off("requestFavoritesAlbums", this.setAlbums);
  },
}
</script>

<style scoped src="./MobileOverrideStyles.css">
</style>

<style scoped>



.cards-container{
  width: 100%;
}

/* Overrides */
>>> .card .shadow-sm{
  color: var(--dark-gray);
  margin-top: 5px;
  margin-bottom: 0px !important;

}
>>> .composer-card{
  margin-left: -15px;
  margin-right: -10px;
}
>>> .work-card{
  margin-left: -15px;
  margin-right: -10px;
}
>>> .albums-card{
  margin-left: -15px;
  margin-right: -10px;
}
>>> .form-control{
  height: 31px !important;
}

/*>>> .v-select {
  --vs-selected-color: var(--yellow) !important;
}*/

/* Page styling */
.header-height{
  height: 76px !important;
}
.heading-text{
  padding-left: 20px;
  font-weight: 500;
}
.heading-card{
  background: var(--medium-gray) !important;
  padding-top:  0px;
  padding-right: 5px;
  margin-right: -15px;
  border-radius: 0px;
  padding-bottom: 5px;
}
.card-body{
  background: var(--medium-gray) !important;
  padding: 0px !important;
}
.btn-secondary{
  background-color: var(--dark-gray) !important;
  text-align: middle;
}
.btn.disabled, .btn:disabled {
  opacity: 1;
}
.card-header{
  border: 0px !important;
}
.btn{
  border:  0px;
}
.header-button{
  border-radius: 0px !important;
  border-top: solid 2px var(--medium-gray) !important;
    outline: none !important;
    box-shadow: none !important;
}
.p-1{
  padding: 0px !important;
  border-radius: 0px !important;
}
.mb-1{
  border: none;
  margin: 0px !important;
  width: 100%;
}
>>> .highlight{
  background-color: var(--red);
}
>>> .highlight td{
  background-color: var(--red);
}
>>> .music-note{
  color: var(--red);
}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}


/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--medium-dark-gray);
  --scroll-bar-bg-color: none;
}
.info-card-text {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
.info-card-text::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.info-card-text::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}
.info-card-text::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}
</style>
