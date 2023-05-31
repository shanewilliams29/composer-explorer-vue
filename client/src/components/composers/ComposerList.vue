<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span class="m-4 col no-composers-found" v-show="!loading && composers.length < 1 && !$view.mode">
        No composers found
      </span>
      <b-card-group deck v-show="!loading">
        <b-card 
          v-for="(region, regionName) in composers" 
          :key="regionName" 
          no-body 
          header-tag="header" 
          class="shadow-sm">
          <div class="#header" v-b-toggle="regionName.replace(/\s/g, '')">
            <h6 class="m-2 mb-0">
              {{ regionName }}
              <span class="mb-0 float-right when-opened">
                <b-icon-chevron-up></b-icon-chevron-up>
              </span>
              <span class="mb-0 float-right when-closed">
                <b-icon-chevron-down></b-icon-chevron-down>
              </span>
            </h6>
          </div>
          <b-collapse :visible="visibility" :id="regionName.replace(/\s/g, '')">
            <b-card-text>
              <table cellspacing="0">
                <tr
                  v-for="composer in region"
                  :key="composer.id"
                  :ref="composer.name_short"
                  @click="selectRow(composer); getWorks(composer.name_short);"
                  :class="[{'cursor': ($view.mode != 'radio')}, 
                          {'highlight': (composer.name_short == $config.composer)}]"
                >
                  <td width="2%" 
                    :style="{border: 'solid 0px !important', 
                            backgroundColor:composer.color, 
                            opacity: 0.66}">
                  </td>
                  <td width="2%"></td>
                  <td width="12%" style="white-space: nowrap;">
                    <img class="composer-img" :src="composer.flag" height="20" width="20" />
                    <img class="composer-img" :src="composer.img" height="20" width="20" />
                  </td>
                  <td width="50%" class="composer-name td-style" style="overflow: hidden;">
                    <span v-if="composer.catalogued">{{ composer.name_full }}</span>
                    <span v-else style="color: gray;">{{ composer.name_full }}</span>
                  </td>
                  <td width="25%" class="td-style" style="text-align: right;">
                    <span v-if="composer.catalogued">{{ composer.born }} - {{ deathDate(composer.died) }}</span>
                    <span v-else style="color: gray;">{{ composer.born }} - {{ deathDate(composer.died) }}</span>
                  </td>
                </tr>
              </table>
            </b-card-text>
          </b-collapse>
        </b-card>
      </b-card-group>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { eventBus } from "@/main.js";
import smoothscroll from "smoothscroll-polyfill";

export default {
  data() {
    return {
      composers: [],
      loading: false,
      visibility: true, // determines whether panels open or closed initially
      artist: "",
    };
  },
  computed: {
    composerChanged() {
      return this.$config.composer;
    },
  },
  watch: {
    composerChanged(newComposer) {
      this.scrollToComposer(newComposer);
    },
  },
  methods: {
    deathDate(yearOfDeath) {
      // living composer death date stored as 2050 in database
      const currentYear = new Date().getFullYear();
      return currentYear < yearOfDeath ? "present" : yearOfDeath;
    },
    scrollToComposer(composer) {
      // scrolls to selected composer
      var timeout = 0;
      if (this.visibility) {
        timeout = 0;
      } else {
        timeout = 1000;
      }

      smoothscroll.polyfill(); // for Safari smooth scrolling
      
      setTimeout(() => {

        const card = this.$refs[composer][0].offsetParent.offsetParent;
        const row = this.$refs[composer][0];
        const height = this.$refs[composer][0].offsetParent.offsetParent.offsetParent.offsetHeight / 2;
        const top = card.offsetTop + row.offsetTop - height + 100;

        let scrollBox = {};
        if (this.$view.mobile) {
          scrollBox = this.$parent.$parent.$refs["scroll-box-comp"];
        } else {
          scrollBox = this.$parent.$refs["scroll-box-comp"];
        }

        scrollBox.scrollTo({
          top: top,
          left: 0,
          behavior: "smooth",
        });

      }, timeout);
    },
    getComposers() {
      // populates composer list initially
      this.loading = true;

      const path = "api/composers?filter=" + this.$config.tier;
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.visibility = true;
          this.loading = false;
          
          this.scrollToComposer(this.$config.composer);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getFilteredComposers(item) {
      // populates composer list with filters
      this.loading = true;
      if (item == "all" || item == "alphabet" || item == "romantic" || item == "20th" || item == "common") {
        this.visibility = true; // change to false when there are a lot of composers
      } else {
        this.visibility = true;
      }

      const path = "api/composers?filter=" + item;
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading = false;
          this.scrollToComposer(this.$config.composer);
          
          if (this.$view.mode == "radio") {
            eventBus.$emit("sendGenreListToRadio", res.data.genres);
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getSearchComposers(item) {
      // populates composer list with search item
      this.visibility = true;
      const path = "api/composers?search=" + item;
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getArtistComposers(artist_id) {
      // populates composer list for a performer (used in performer and radio modes)
      this.loading = true;
      this.artist = artist_id;
      this.visibility = true;

      eventBus.$emit("clearWorksList");
      eventBus.$emit("clearAlbumsList");

      const path = "api/artistcomposers/" + artist_id;
      console.log(path);
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading = false;

          if (this.$view.mode == "radio") {
            eventBus.$emit("sendGenreListToRadio", res.data.genres);
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getWorks(composer) {
      // requests works list for a composer
      if (!this.$view.mode) {
        eventBus.$emit("requestWorksList", composer);
      } else if (this.$view.mode == "performer") {
        eventBus.$emit("requestWorksListForArtist", this.artist, composer);
      } else if (this.$view.mode == "favorites") {
        eventBus.$emit("requestWorksListForFavorites", composer);
      }
    },
    selectRow(composer) {
      if (this.$view.mode != "radio") {
        this.$config.composer = composer.name_short;
        this.$config.tier = composer.tier;
        localStorage.setItem("config", JSON.stringify(this.$config));
      }
    },
    clearComposers() {
      this.composers = [];
    },
    getFavoritesComposers() {
      this.loading = true;

      const path = "api/favoritescomposers";
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.visibility = true;
          this.loading = false;

          if (this.$view.mode == "radio") {
            eventBus.$emit("sendGenreListToRadio", res.data.genres);
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getMultiComposers(composers) {
      // gets specified composers (used in radio mode composer multiselect)
      if (composers.length < 1) {
        this.composers = [];
      } else {
        const path = "api/multicomposers";
        axios
          .post(path, composers)
          .then((res) => {
            this.composers = res.data.composers;
            eventBus.$emit("sendGenreListToRadio", res.data.genres);
            this.visibility = true;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
      }
    },
  },
  created() {
    if (!this.$view.mode && !this.$route.query.search) { // dont get composers in performer or radio modes or if omnisearch present
      this.getComposers();
      const config = JSON.parse(localStorage.getItem("config"));
      this.$config.composer = config.composer;
    }

    if (this.$view.mode && !this.$view.mobile) {
      // clear selected composer in other modes, except for mobile
      this.$config.composer = "";
    }

    if (this.$view.mode == "favorites") {
      this.getFavoritesComposers();
    }

    if (this.$route.query.artist) {
      this.getArtistComposers(this.$route.query.artist);
    }

    eventBus.$on("requestComposersFromFilter", this.getFilteredComposers);
    eventBus.$on("requestComposersFromSearch", this.getSearchComposers);
    eventBus.$on("requestComposersForArtist", this.getArtistComposers);
    eventBus.$on("requestFavoritesComposers", this.getFavoritesComposers);
    eventBus.$on("requestComposersFromRadioMultiselect", this.getMultiComposers);
    eventBus.$on("clearComposersList", this.clearComposers);
  },
  beforeDestroy() {
    eventBus.$off("requestComposersFromFilter", this.getFilteredComposers);
    eventBus.$off("requestComposersFromSearch", this.getSearchComposers);
    eventBus.$off("requestComposersForArtist", this.getArtistComposers);
    eventBus.$off("requestFavoritesComposers", this.getFavoritesComposers);
    eventBus.$off("requestComposersFromRadioMultiselect", this.getMultiComposers);
    eventBus.$off("clearComposersList", this.clearComposers);
  },
};

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.collapsed .when-closed{
  display: show;
}
.collapsed .when-opened{
  display: none;
}
.not-collapsed .when-closed{
  display: none;
}
.not-collapsed .when-opened{
  display: show;
}
.card-deck {
  display: flex;
  flex-direction: column;
  width: 100%;
}
.card {
  width: 100%;
}
.td-style{
  white-space: nowrap; 
  text-overflow: ellipsis; 
  max-width: 1px;
}
.narrow{
  font-family: Roboto Condensed !important;
}
td {
  padding: 1px;
  vertical-align: middle;
  border-top: 1px dotted var(--medium-light-gray);
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  font-size: 13px;
  padding: 6px;
  padding-top: 0px;
  padding-bottom: 2px;
}
.highlight td {
  border-top: 0px solid var(--medium-light-gray);
  color: var(--my-white) !important;
}
.cursor {
  cursor: pointer;
}
.highlight td:last-child {
  position: relative;
}

.highlight td:last-child:after {
  content: "";
  position: absolute;
  top: 0px;
  bottom: 0px;
  width: 6px;
  display: block;
  background: inherit;
  border: inherit;
  left: 100%;
}
.composer-img {
  border-radius: 50%;
  object-fit: cover;
}
header.card-header {
  background-color: var(--my-white);
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
header.card-header:hover {
  cursor: pointer;
}
.mb-0 {
  font-size: 14px;
  font-weight: bold;
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.card {
  background-color: var(--my-white);
  border: none;
  margin-top: 5px;
}
.card-deck {
  padding-left: 5px;
  padding-right: 5px;
}
.no-composers-found {
  font-size: 15px;
  color: #9da6af;
  text-align: center;
  font-family: Roboto Condensed !important;
}

.collapsing {
    -webkit-transition: none !important;
    transition: none !important;
    display: none;
}
</style>
