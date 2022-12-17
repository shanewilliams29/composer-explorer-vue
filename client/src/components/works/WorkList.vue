<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="noWorks()" class="col no-works-found">
        <div class="m-4">{{ message }}</div>
      </span>
      <b-card-group deck v-if="!loading && works">
        <b-card v-for="(genre, index) in works" :key="index" :ref="index" no-body header-tag="header" class="shadow-sm">
          <div class="header" @click="toggleOpen(index);">
            <h6 class="m-2 mb-0">
              <span>{{ index }}&nbsp;&nbsp;</span>
              <span v-if="!visibility && index == $config.genre" class="mb-0 float-right when-opened"><b-icon-chevron-up></b-icon-chevron-up></span>
              <span v-if="!visibility && index != $config.genre" class="mb-0 float-right when-closed"><b-icon-chevron-down></b-icon-chevron-down></span>
            </h6>
          </div>
          <b-collapse @shown="onShown(index)" :visible="visibility || index == $config.genre" :id="index.replace(/\s/g, '')">
            <b-card-text v-if="visibility || index == $config.genre">
              <table cellspacing="0" class="works-table">
                <tr
                  v-for="(work, index) in genre"
                  :ref="work.id"
                  :key="work.id"
                  :id="index"
                  @click="selectRow(work.id); getAlbums(work.id, work.title); setGenre(work.genre);"
                  :class="{'highlight': (work.id == selectedWork), 'no-albums': (work.album_count == 0)}"
                >
                  <td width="17%">
                    <span style="white-space: nowrap; color: darkred;">
                      <span v-if="work.cat">{{ work.cat }}&nbsp;&nbsp;</span><span v-else><span v-if="work.date">{{ work.date }}</span><span v-else>-</span></span>
                    </span>
                  </td>
                  <td width="78%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;"><span>{{ work.title }}</span><span v-if="work.nickname" style="color: gray;"> · {{ work.nickname }}</span></td>
                  <td width="5%" style="text-align: right;">
                    <span class="heart-number" style="white-space: nowrap;">
                      <span style="color: rgb(52, 58, 64, 0.7); font-size: 12px;" v-if="work.liked"><b-icon-heart-fill></b-icon-heart-fill>&nbsp;</span> <b-badge>{{ work.album_count }}</b-badge>
                    </span>
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
import { useSound } from "@vueuse/sound";
import dingding from "@/assets/dingding.mp3";

export default {
  setup() {
    const play = useSound(dingding, { volume: 0.3 });

    return {
      play,
    };
  },
  data() {
    return {
      works: [],
      searchItem: null,
      filterItem: null,
      radioPayload: {},
      playlist: [],
      loading: false,
      selectedWork: null,
      visibility: true,
      message: "Select from the options above to create your own customized radio",
    };
  },
  methods: {
    noWorks(){
      if(!this.loading && this.works.length < 1 ){
        if(!this.$view.mode && !this.$config.composer){
          this.message = `Select a composer to view works`;
        }
        if(!this.$view.mode && this.$config.composer){
          this.message = `No works found for ${this.$config.composer} (yet!)`;
        }
        if(this.$view.mode == 'performer' && this.$config.artist){
          this.message = `Select a composer to view performances by ${this.$config.artist}`;
        }
        if(this.$view.mode == 'performer' && !this.$config.artist){
          this.message = ``;
        }
        if(this.$view.mode == 'favorites'){
          this.message = `Access your favorite works and performances here`;
        }
        return true;
      } 
      return false;
    },
    getWorks(composer) {
      // standard mode
      this.searchItem = null;
      this.filterItem = null;
      this.loading = true;
      this.$config.composer = composer;
      const path = "api/works/" + composer;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.visibility = true;
          this.loading = false;
          this.setGenre(this.$config.genre);
          eventBus.$emit("fireWorksLoaded"); // for mobile
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getFavoriteWorks(composer) {
      // favorites mode
      this.searchItem = null;
      this.filterItem = null;
      this.loading = true;
      this.$config.composer = composer;
      const path = "api/favoriteworks/" + composer;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.visibility = true;
          this.loading = false;
          this.setGenre(this.$config.genre);
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    refreshWorks() {
      // used to quietly refresh works when likes change
      this.loading = false;
      // getWorks base
      if (!this.$view.mode && !this.searchItem && !this.filterItem) {
        const path = "api/works/" + this.$config.composer;
        axios
          .get(path)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
      // getWorks search
      if (!this.$view.mode && this.searchItem) {
        const path = "api/works/" + this.$config.composer + "?search=" + this.searchItem;
        axios
          .get(path)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
      // getWorks filter
      if (!this.$view.mode && this.filterItem) {
        const path = "api/works/" + this.$config.composer + "?filter=" + this.filterItem;
        axios
          .get(path)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
      // Performer view works
      if (this.$view.mode == "performer") {
        const path = "api/artistworks?artist=" + this.$config.artist + "&composer=" + this.$config.composer;
        axios
          .get(path)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
      // Radio view works
      if (this.$view.mode == "radio") {
        const payload = this.radioPayload;
        const path = "api/worksbygenre";
        axios
          .post(path, payload)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
      // Favorites view works
      if (this.$view.mode == "favorites") {
        const path = "api/favoriteworks/" + this.$config.composer;
        axios
          .get(path)
          .then((res) => {
            this.works = res.data.works;
          })
          .catch((error) => {
            console.error(error);
          });
      }
    },
    scrollToWork(genre){
     // scrolling animation for when collapsible expanded
    var timeout = 0;
    smoothscroll.polyfill(); // for Safari smooth scrolling

    // scroll to work
            setTimeout(() => {
              try {
                var card = this.$refs[genre][0];
                var row = this.$refs[this.selectedWork][0];
                var height = this.$refs[genre][0].offsetParent.offsetHeight / 2;
                var top = card.offsetTop + row.offsetTop - height + 100;
                
                var scrollBox = {};
                if (this.$route.name == "mobile") {
                  scrollBox = this.$parent.$parent.$refs["scroll-box"];
                } else {
                  scrollBox = this.$parent.$refs["scroll-box"];
                }
                scrollBox.scrollTo({
                  top: top,
                  left: 0,
                  behavior: "smooth",
                });
              } catch {
                //pass
              }
            }, timeout);       
        

    //   else { //scroll to genre

    },
    scrollToPanel(genre){
     // scrolling animation for when collapsible expanded
    var timeout = 0;
    smoothscroll.polyfill(); // for Safari smooth scrolling

     setTimeout(() => {
        try {
          var card = this.$refs[genre][0]
          var top = card.offsetTop - 5
          
          var scrollBox = {};
          if (this.$route.name == "mobile") {
            scrollBox = this.$parent.$parent.$refs["scroll-box"];
          } else {
            scrollBox = this.$parent.$refs["scroll-box"];
          }
          scrollBox.scrollTo({
            top: top,
            left: 0,
            behavior: "smooth",
          });
        } catch {
          //pass
        }
      }, timeout);
    },
    onShown(genre){
      if(this.searchItem != ''){
        if(this.$view.mode == 'radio'){
          this.scrollToWork(genre);
        } else{
          this.scrollToPanel(genre);
        }
      }
  },
    getRadioWorks(genres, filter, search, artist, radioType) {
      if (genres.length < 1) {
        // no works
        eventBus.$emit("clearAlbumsList");
        this.loading = false;
        this.$view.radioPlaying = false;
        this.$view.enableRadio = false;
        this.$view.enableExport = false;
        this.works = [];
      } else {
        this.loading = true;
        const payload = {
          genres: genres,
          filter: filter,
          search: search,
          artist: artist,
          radio_type: radioType,
        };
        this.radioPayload = payload;
        const path = "api/radioworks";
        axios
          .post(path, payload)
          .then((res) => {
            this.loading = false;
            this.works = res.data.works;
            this.playlist = res.data.playlist;
            if (this.playlist.length > 300) {
              this.visibility = false;
              this.$view.enableRadio = true;
              this.$view.enableExport = false;
            } else if (this.playlist.length < 1) {
              this.$view.enableExport = false;
              this.$view.enableRadio = false;
              this.message = 'No works found for selection. Try different genres, and selecting "All works"';
            } else {
              this.visibility = true;
              this.$view.enableExport = true;
              this.$view.enableRadio = true;
            }
          })
          .catch((error) => {
            console.error(error);
            this.loading = false;
            this.$view.enableRadio = false;
            this.$view.enableExport = false;
            this.works = [];
          });
      }
    },
    preparePlaylist(performer, radioType, genres, filter, search, limit, prefetch, name) {
      // used in radio mode to export to Spotify
      if (!genres) {
        // no works
        alert("No works are selected!");
      } else {
        this.$bvModal.show("playlist-modal");
        const payload = {
          performer: performer,
          radio_type: radioType,
          genres: genres,
          filter: filter,
          search: search,
          limit: limit,
          prefetch: prefetch,
          name: name,
          random: this.$view.randomAlbum,
        };
        const path = "api/exportplaylist";
        axios
          .post(path, payload)
          .then((res) => {
            if (prefetch) {
              this.$view.playlistTrackCount = res.data.track_count;
            } else if ("error" in res.data) {
              this.$view.playlistError = res.data.error.message;
              this.$view.playlistSuccess = false;
            } else {
              this.$view.playlistSuccess = true;
              this.$view.playlistError = false;
            }
          })
          .catch((error) => {
              this.$view.playlistError = error;
              this.$view.playlistSuccess = false;
          });
      }
    },
    getArtistWorks(artist, composer) {
      // used in Performer mode
      this.loading = true;
      this.$config.artist = artist;
      this.$config.composer = composer;
      localStorage.setItem("config", JSON.stringify(this.$config));
      const path = "api/artistworks?artist=" + artist + "&composer=" + composer;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.visibility = true;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getAlbums(workId, title) {
      this.$config.work = workId;
      this.$config.workTitle = title;
      localStorage.setItem("config", JSON.stringify(this.$config));
      eventBus.$emit("changeWork");
      if (!this.$view.mode) {
        // standard compsoer mode
        eventBus.$emit("requestAlbums", workId);
      } else if (this.$view.mode == "performer") {
        // performer mode
        eventBus.$emit("requestAlbums", workId, this.$config.artist);
      } else if (this.$view.mode == "favorites") {
        // favorites mode
        eventBus.$emit("requestFavoritesAlbums", workId);
      } else {
        // radio mode, play automatically
        if (this.$config.artist) {
          eventBus.$emit("requestAlbumsAndPlay", workId, this.$config.artist);
        } else {
          eventBus.$emit("requestAlbumsAndPlay", workId);
        }
        this.$view.radioPlaying = true;
      }
    },
    getAlbumsAndPlay(workId, title) {
      this.$config.work = workId;
      this.$config.workTitle = title;
      localStorage.setItem("config", JSON.stringify(this.$config));
      eventBus.$emit("changeWork");

      if (this.$view.mode != "performer") {
        if (this.$config.artist && this.$view.mode == "radio") {
          eventBus.$emit("requestAlbumsAndPlay", workId, this.$config.artist);
        } else if (this.$view.mode == "favorites") {
          // favorites mode
          this.$view.favoritesAlbums = true;
          eventBus.$emit("requestAlbumsAndPlay", workId);
        } else {
          eventBus.$emit("requestAlbumsAndPlay", workId);
        }
      } else {
        eventBus.$emit("requestAlbumsAndPlay", workId, this.$config.artist);
      }
    },
    toggleOpen(genre) {
      if (genre == this.$config.genre){
        this.$config.genre = null;
      } else {
        this.$config.genre = genre;
      }
      localStorage.setItem("config", JSON.stringify(this.$config));
      
    },
    selectRow(workid) {
      this.selectedWork = workid;
    },
    setGenre(genre) {
      this.$config.genre = genre;
      localStorage.setItem("config", JSON.stringify(this.$config));
      this.scrollToWork(genre);
    },
    getFilteredWorks(item) {
      this.filterItem = item;
      this.searchItem = null;
      this.loading = true;
      if (item == "all") {
        this.visibility = false;
      } else {
        this.visibility = true;
      }
      const path = "api/works/" + this.$config.composer + "?filter=" + item;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    scrollToTop(){
          var scrollBox = {};
          if (this.$route.name == "mobile") {
            scrollBox = this.$parent.$parent.$refs["scroll-box"];
          } else {
            scrollBox = this.$parent.$refs["scroll-box"];
          }
          scrollBox.scrollTo({
            top: 0,
            left: 0,
          });
    },
    getSearchWorks(item) {
      this.scrollToTop();
      this.filterItem = null;
      this.searchItem = item;
      const path = "api/works/" + this.$config.composer + "?search=" + item;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.visibility = true;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    requestWorksList(composer) {
      this.getWorks(composer);
      this.$config.composer = composer;
      localStorage.setItem("config", JSON.stringify(this.$config));
    },
    clearWorksList(artist) {
      this.$config.artist = artist;
      this.works = [];
      this.message = "Select from the options above to create your own customized radio";
    },
    nextWork() {
      this.play.play();
      eventBus.$emit("changeWork");
      if (this.$view.shuffle) {
        this.$config.previousWork = this.$config.work;
        this.$config.previousGenre = this.$config.genre;
        this.$config.previousWorkTitle = this.$config.workTitle;
        this.playRandomWork();
      } else {
        for (var i = 0; i < this.playlist.length; i++) {
          if (this.playlist[i]["id"] == this.selectedWork && i !== this.playlist.length - 1) {
            this.selectRow(this.playlist[i + 1]["id"]);
            this.setGenre(this.playlist[i + 1]["genre"]);
            this.getAlbumsAndPlay(this.playlist[i + 1]["id"], this.playlist[i + 1]["title"]);
            break;
          }
        }
      }
    },
    previousWork() {
      this.play.play();
      eventBus.$emit("changeWork");
      if (this.$view.shuffle) {
        this.selectRow(this.$config.previousWork); //allows you to jump one back
        this.setGenre(this.$config.previousGenre);
        this.getAlbumsAndPlay(this.$config.previousWork, this.$config.previousWorkTitle);
      } else {
        for (var i = 0; i < this.playlist.length; i++) {
          if (this.playlist[i]["id"] == this.selectedWork && i !== 0) {
            this.selectRow(this.playlist[i - 1]["id"]);
            this.setGenre(this.playlist[i - 1]["genre"]);
            this.getAlbumsAndPlay(this.playlist[i - 1]["id"], this.playlist[i - 1]["title"]);
            break;
          }
        }
      }
    },
    playRandomWork() {
      eventBus.$emit("changeWork");
      function randomIntFromInterval(min, max) {
        // min and max included
        return Math.floor(Math.random() * (max - min + 1) + min);
      }
      const rndInt = randomIntFromInterval(0, this.playlist.length - 1);
      this.selectRow(this.playlist[rndInt]["id"]);
      this.setGenre(this.playlist[rndInt]["genre"]);
      this.getAlbumsAndPlay(this.playlist[rndInt]["id"], this.playlist[rndInt]["title"]);
    },
  },
  created() {
    if (!this.$view.mode) {
      // dont get works in radio mode or artist mode
      this.getWorks(this.$config.composer);
      this.selectRow(this.$config.work);
    }
    eventBus.$on("requestWorksList", this.requestWorksList);
    eventBus.$on("requestWorksListForArtist", this.getArtistWorks);
    eventBus.$on("fireWorkFilter", this.getFilteredWorks);
    eventBus.$on("fireWorkSearch", this.getSearchWorks);
    eventBus.$on("clearWorksList", this.clearWorksList);
    eventBus.$on("requestWorksForRadio", this.getRadioWorks);
    eventBus.$on("fireNextWork", this.nextWork);
    eventBus.$on("firePreviousWork", this.previousWork);
    eventBus.$on("firePlaylistExport", this.preparePlaylist);
    eventBus.$on("fireRefreshWorks", this.refreshWorks);
    eventBus.$on("requestWorksListForFavorites", this.getFavoriteWorks);
    eventBus.$on("fireWorkScroll", this.setGenre);
  },
  beforeDestroy() {
    eventBus.$off("requestWorksList", this.requestWorksList);
    eventBus.$off("requestWorksListForArtist", this.getArtistWorks);
    eventBus.$off("fireWorkFilter", this.getFilteredWorks);
    eventBus.$off("fireWorkSearch", this.getSearchWorks);
    eventBus.$off("clearWorksList", this.clearWorksList);
    eventBus.$off("requestWorksForRadio", this.getRadioWorks);
    eventBus.$off("fireNextWork", this.nextWork);
    eventBus.$off("firePreviousWork", this.previousWork);
    eventBus.$off("firePlaylistExport", this.preparePlaylist);
    eventBus.$off("fireRefreshWorks", this.refreshWorks);
    eventBus.$off("requestWorksListForFavorites", this.getFavoriteWorks);
    eventBus.$off("fireWorkScroll", this.setGenre);
  },
};

</script>

<style scoped>\
.collapsed .when-closed {
    display: show;
}
.collapsed .when-opened {
    display: none;
}
.not-collapsed .when-closed {
    display: none;
}
.not-collapsed .when-opened {
    display: show;
}
.collapsing {
    -webkit-transition: none !important;
    transition: none !important;
    display: none;
}
.spinner {
    text-align: center;
}
.m-5 {
    color: #9da6af;
}
.m-4 {
    color: #9da6af;
}
.card-deck {
    display: flex;
    flex-direction: column;
    width: 100%;
}
.card {
    width: 100%;
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
    background-color: var(--highlight-color);
    color: var(--my-white) !important;
}
.highlight span {
    color: var(--my-white) !important;
}
tr:hover {
    cursor: pointer;
}

.highlight td:first-child,
.highlight td:last-child {
    position: relative;
}

.highlight td:first-child:before,
.highlight td:last-child:after {
    content: "";
    position: absolute;
    top: 0px !important;
    bottom: 0px !important;
    width: 6px;
    display: block;
    background: inherit;
    border: inherit;
}
.highlight td:first-child:before {
    right: 100%;
}
.highlight td:last-child:after {
    left: 100%;
}

.no-albums span {
    opacity: 0.45;
}
.no-albums:hover {
    cursor: default !important;
}
.header{
  cursor: pointer;
}
.header:hover {
    cursor: pointer;
}
.header.card-header {
    background-color: var(--my-white);
    border: none;
    padding-left: 10px;
    padding-bottom: 0px;
    cursor: pointer;
}
.header.card-header:hover {
    cursor: pointer;
}
.mb-0 {
    font-size: 14px;
    font-weight: bold;
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
.badge {
    color: var(--my-white);
    background-color: rgb(52, 58, 64, 0.7);
    border-radius: 7px;
}
.no-works-found {
    font-size: 14px;
    color: grey;
    text-align: center;
}
</style>