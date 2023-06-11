<template>
  <div id="performer">
    <MobilePerformersHeading/>
    <div class="container-fluid">
      <b-row v-if="showCloud">
      <div id="dummy-div">
        <b-col class="cards-col">
          <div class="grid-container disable-scrollbars" @scroll="hideKeyboard">
            <div class="grid-item" v-for="artist in performers" :key="artist.id" @click="selectArtist(artist)">
              <b-card class="album-info-card shadow-sm">
                <b-card-body class="card-body centered-content">
                  <b-card-text class="info-card-text ">
                    <div>
                      <table class="margin-bottom">
                        <tr>
                          <td class="vertical-align-middle">
                            <b-avatar size="36px" :src="artist.img"></b-avatar>
                          </td>
                          <td class="info-td vertical-align-middle wrap-text">
                            <a class="artist-name" >{{ artist.name }}</a><br />
                            <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                          </td>
                        </tr>
                      </table>
                    </div>
                  </b-card-text>
                </b-card-body>
              </b-card>
            </div>
          </div>
        </b-col>
      </div>
      </b-row>
      <b-row v-if="!showCloud">
        <div class="cards-container" role="tablist">
          <b-card no-body class="mb-1 mobile-card">
            <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
              <b-button class="header-button" :disabled="composerDisabled" @click="composerToggle" block variant="secondary">
                <span class="heading-text">Composers</span><span class="mb-0 float-right">
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
                <span v-if="composer" class="heading-text">Works by {{ composer }}</span>
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
import MobilePerformersHeading from '@/components/mobile/MobilePerformersHeading.vue'
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

import {eventBus} from "../main.js";

export default {
  name: 'PerformerView',
  components: {
    MobilePerformersHeading,
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
      this.title = "Select a work";
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
    // eslint-disable-next-line
    setWork(artist, composer){
      this.composer = composer;
      this.workToggle();
    },
    setAlbums(){
      this.title = this.$config.workTitle;
      this.albumToggle();
    },
  },
  beforeCreate() {
    document.documentElement.style.setProperty("--workingheight", `228.6px`);
    this.$view.mobile = true;
  },
  created() {
    const conductors = require('@/assets/topconductors.json');
    const groups = require('@/assets/topgroups.json');
    const soloists = require('@/assets/topsoloists.json');
    const vocalists = require('@/assets/topvocalists.json');
    let performersArray = []

    performersArray.push(...conductors);
    performersArray.push(...groups);
    performersArray.push(...soloists);
    performersArray.push(...vocalists);
    this.performers = this.shuffleArray(performersArray);

    this.composerToggle();
    window.firstLoad = false; // allow playback on first load for performer view
    this.$view.shuffle = false;
    eventBus.$on('requestComposersForArtist', this.hideCloud);
    eventBus.$on('clearPerformers', this.unhideCloud);
    this.$view.mode = 'performer';
    if (this.$route.query.artist){
        this.showCloud = false;
    } else{
      this.showCloud = true;
    }
    this.$view.shuffle = false;
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)");

    eventBus.$on("requestWorksListForArtist", this.setWork);
    eventBus.$on("requestAlbums", this.setAlbums);
    eventBus.$on("requestAlbumsAndPlay", this.setAlbums);

    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${vh}px`);

    window.addEventListener('resize', this.detectKeyboard);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.detectKeyboard);
    eventBus.$off("requestWorksListForArtist", this.setWork);
    eventBus.$off("requestAlbums", this.setAlbums);
    eventBus.$off("requestAlbumsAndPlay", this.setAlbums);
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
  background-color: var(--purple);
}
>>> .highlight td{
  background-color: var(--purple);
}
>>> .music-note{
  color: var(--purple);
}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}




/* Performers startup grid */

#dummy-div {
  background-color: var(--dark-gray);
  width: 100%;
  height: calc(var(--vh, 1vh) * 100 - 121px + 44px - var(--workingheight));
}

.album-info-card .card-body{
  background: none !important;
  padding: 0px !important;
}
.centered-content {
    display: flex;
    align-items: center;
    height: 100%; /* You might need to adjust this */
  }
.vertical-align-middle {
    vertical-align: middle;
}
.narrow{
  font-family: Roboto Condensed !important;
 }
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  grid-gap: 0px;
  grid-auto-flow: dense;
  height: calc(var(--vh, 1vh) * 100 - 121px + 44px - var(--workingheight));
  overflow-x: hidden;
  overflow-y: auto;
  padding-bottom: 15px;
  padding-top: 5px;
}
.grid-item {
  display: flex;
  padding-right: 5px;
  padding-bottom: 5px;
}
.album-info-card {
  margin-top: 0px;
  padding: 10px;
  padding-bottom: 5px;
  background-color: var(--my-white) !important;
  border: none !important;
  width: 100%;
}
.info-card-text {
  vertical-align: middle !important;
  font-size: 13px;
  line-height: 130%;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
  text-overflow: ellipsis;
}
.wrap-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
a {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  text-decoration: none !important;
}
.margin-bottom {
  margin-bottom: 6px;
}
.cards-col{
  padding: 0px;
  padding-left: 5px;
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
