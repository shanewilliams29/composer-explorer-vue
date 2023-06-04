<template>
  <div id="performer">
    <MobilePerformersHeading/>
    <div class="container-fluid">
      <b-row v-if="showCloud">
      <div id="dummy-div">
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
                <span class="heading-text">Works by {{ composer }}</span><span class="mb-0 float-right">
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
      composer: this.$config.composer,
      title: this.$config.workTitle,
      composerDisabled: true,
      workDisabled: false,
      albumDisabled: false,
      initialWorksLoad: true,
      initialAlbumsLoad: true,
      composerListKey: 0,
      initialWindowHeight: 0,
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
      console.log(window.innerHeight);
      // for mobile keyboard
      if (window.innerHeight < this.initialWindowHeight) {
        this.$view.mobileKeyboard = true;
        vh = vh + 250 * 0.01;
      } else {
        this.$view.mobileKeyboard = false;
      }

      document.documentElement.style.setProperty("--vh", `${vh}px`);
    }
  },
  beforeCreate() {
    document.documentElement.style.setProperty("--workingheight", `228.6px`);
    this.$view.mobile = true;
  },
  created() {
    window.firstLoad = false; // allow playback on first load for performer view
    eventBus.$on('requestComposersForArtist', this.hideCloud);
    eventBus.$on('clearPerformers', this.unhideCloud);
    this.$view.mode = 'performer';
    if (this.$route.query.artist){
        this.showCloud = false;
    } else{
      this.showCloud = true;
    }
    this.$view.shuffle = false;
    this.initialWindowHeight = window.innerHeight;
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)");

    eventBus.$on("requestWorksListForArtist", (artist, composer) => {
      this.composer = composer;
      this.workToggle();
    });
    eventBus.$on("requestAlbums", () => {
      this.title = this.$config.workTitle;
      this.albumToggle();
    });
    eventBus.$on("requestAlbumsAndPlay", () => {
      this.title = this.$config.workTitle;
    });
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${vh}px`);

    window.addEventListener('resize', this.detectKeyboard);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.detectKeyboard);
  },
}
</script>

<style scoped src="./MobileOverrideStyles.css">
</style>

<style scoped>

#dummy-div {
  background-color: var(--dark-gray);
  width: 100%;
  height: calc(var(--vh, 1vh) * 100 - 121px + 44px - var(--workingheight));
}

.cards-container{
  width: 100%;
}

/* Overrides */
>>> .card .shadow-sm{
  color: var(--dark-gray);
  margin-top: 0px;
  margin-bottom: 5px !important;

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
.card-deck{
  padding-top: 0px !important;
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
</style>
