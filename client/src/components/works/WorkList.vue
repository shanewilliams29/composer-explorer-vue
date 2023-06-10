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
        <b-card v-for="(genre, genreName) in works" 
          :key="genreName" 
          :ref="genreName" 
          no-body 
          header-tag="header" 
          class="shadow-sm">
          <div class="header" @click="toggleOpen(genreName);">
            <h6 class="m-2 mb-0">
              <span>{{ genreName }}&nbsp;&nbsp;</span>
              <span v-if="!visibility && genreName == $config.genre" class="mb-0 float-right when-opened"> <b-icon-chevron-up></b-icon-chevron-up></span>
              <span v-if="!visibility && genreName != $config.genre" class="mb-0 float-right when-closed"> <b-icon-chevron-down></b-icon-chevron-down></span>
            </h6>
          </div>
          <b-collapse 
            @shown="onShown(genreName)" 
            :visible="visibility || genreName == $config.genre" 
            :id="genreName.replace(/\s/g, '')">
            <b-card-text v-if="visibility || genreName == $config.genre">
              <table cellspacing="0" class="works-table">
                <tr
                  v-for="(work, genreName) in genre"
                  :ref="work.id"
                  :key="work.id"
                  :id="genreName"
                  @click="selectRow(work.id); setRecommended(work.recommend); getAlbums(work.id, work.title); setGenre(work.genre);"
                  :class="{'highlight': (work.id == selectedWork), 'no-albums': (work.album_count == 0)}"
                >
                  <td width="16%">
                    <span style="white-space: nowrap; color: darkred;">
                      <span v-if="work.cat">{{ work.cat }}&nbsp;&nbsp;</span>
                      <span v-else>
                        <span v-if="work.date">{{ work.date }}</span>
                        <span v-else>-</span>
                      </span>
                    </span>
                  </td>
                  <td width="79%" class="td-style">
                    <span style="color: black;">{{ work.title }}</span>
                    <span class="narrow" v-if="work.nickname" style="color: gray;"> · {{ work.nickname }}</span>
                  </td>
                  <td width="5%" style="text-align: right;">
                    <span class="heart-number" style="white-space: nowrap;">
                      <span class="narrow" v-if="work.duration && !$view.mobile" style="color: rgb(52, 58, 64, 0.7); font-size: 12px;">
                        {{ duration(work.duration) }}&nbsp;
                      </span>
<!--                       <span v-if="work.liked" style="color: rgb(52, 58, 64, 0.7); font-size: 12px;">
                        <b-icon-heart-fill></b-icon-heart-fill>&nbsp;
                      </span>  -->
                      <b-badge v-if="work.liked" class="liked-badge">{{ work.album_count }}</b-badge>
                      <b-badge v-if="!work.liked" class="plain-badge">{{ work.album_count }}</b-badge>
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
import { randomIntFromInterval } from "@/HelperFunctions.js";
import smoothscroll from "smoothscroll-polyfill";

export default {
  data() {
    return {
      works: [],
      searchItem: null,
      filterItem: null,
      radioPayload: {},
      playlist: [],
      shufflePlaylist: [],
      loading: false,
      selectedWork: null,
      visibility: true,
      message: "Select from the options above to create your own customized radio",
    };
  },
  methods: {
      rountToNearest5(num){
        if (num > 15) {
          return Math.round(num / 5) * 5;
        } else {
          return num;
        }
      },
      duration(ms){
        let seconds = Math.floor(ms / 1000);
        let hours = Math.round(seconds / 3600 * 10) / 10;
        let minutes = Math.round(seconds / 60);

        if(hours > 1){
          return hours + "h";
        } else {
          return this.rountToNearest5(minutes) + "m"
        }
    },
    noWorks(){
      if(!this.loading && this.works.length < 1 ){
        if(!this.$view.mode && !this.$config.composer){
          this.message = `Select a composer to view works`;
        }
        if(!this.$view.mode && this.$config.composer){
          this.message = `No works found for ${this.$config.composer}`;
        }
        if(this.$view.mode == 'performer' && this.$config.artist){
          this.message = `Select a composer to view performances by ${this.$config.artist.name}`;
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
      // browse mode
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
          this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);
          this.visibility = true;
          this.loading = false;
          this.setGenre(this.$config.genre);
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
          this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);
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
        const path = "api/artistworks?artist=" + this.$config.artist.id + "&composer=" + this.$config.composer;
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
    scrollToWork(genre) {
      // scrolling animation for when collapsible expanded
      const timeout = 0;
      smoothscroll.polyfill(); // for Safari smooth scrolling

      setTimeout(() => {
        try {
          const card = this.$refs[genre][0];
          const row = this.$refs[this.selectedWork][0];
          const height = this.$refs[genre][0].offsetParent.offsetHeight / 2;
          const top = card.offsetTop + row.offsetTop - height + 100;
          let scrollBox = {};
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
    scrollToPanel(genre) {
      // scrolling animation for when collapsible expanded
      const timeout = 0;
      smoothscroll.polyfill(); // for Safari smooth scrolling
      
      setTimeout(() => {
        try {
          const card = this.$refs[genre][0]
          const top = card.offsetTop - 5
          let scrollBox = {};
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
          this.scrollToWork(genre);
          // this.scrollToPanel(genre);
        }
      }
    },
    getRadioWorks(genres, filter, search, artist, radioType) {
      if (genres.length < 1) {
        // clear works and albums on no genre selected
        this.loading = false;
        this.$view.radioPlaying = false;
        this.$view.enableRadio = false;
        this.$view.enableExport = false;
        this.works = [];

        eventBus.$emit("clearAlbumsList");
      
      } else {
        // retrieve specified works
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
            this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);

            // collapse cards if too many works and disable playlist export
            if (this.playlist.length > 300) {
              this.visibility = false;
              this.$view.enableRadio = true;
              this.$view.enableExport = false;

            // no works
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
      // used in radio mode to export playlist to Spotify
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
      // used in performer mode
      this.loading = true;
      this.$config.composer = composer;
      localStorage.setItem("config", JSON.stringify(this.$config));

      const path = "api/artistworks?artist=" + artist + "&composer=" + composer;
      axios
        .get(path)
        .then((res) => {
          this.works = res.data.works;
          this.playlist = res.data.playlist;
          this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);
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
        // browse mode
        eventBus.$emit("requestAlbums", workId);

      } else if (this.$view.mode == "performer") {
        // performer mode
        eventBus.$emit("requestAlbums", workId, this.$config.artist.name);

      } else if (this.$view.mode == "favorites") {
        // favorites mode
        eventBus.$emit("requestFavoritesAlbums", workId);

      } else {
        // radio mode, play automatically
        if (this.$config.artist) {
          eventBus.$emit("requestAlbumsAndPlay", workId, this.$config.artist.name);

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

      if ((this.$view.mode == "performer") || (this.$config.artist && this.$view.mode == "radio")) {
        // performer mode or radio performer mode
        eventBus.$emit("requestAlbumsAndPlay", workId, this.$config.artist.name);

      } else {
        // browse, favorites or standard radio mode
        eventBus.$emit("requestAlbumsAndPlay", workId);
      }
    },
    toggleOpen(genre) {
      if (genre == this.$config.genre){
        this.$config.genre = null; // closes the panel
      } else {
        this.$config.genre = genre; // opens the panel
      }
      localStorage.setItem("config", JSON.stringify(this.$config));
      
    },
    selectRow(workId) {
      this.selectedWork = workId;
    },
    setRecommended(workRecommended){
      this.$config.workRecommended = workRecommended;
      localStorage.setItem("config", JSON.stringify(this.$config));
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
          this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);
          this.setGenre(this.$config.genre);
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    scrollToTop() {
      let scrollBox = {};
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
          this.shufflePlaylist = [...this.playlist].sort((a, b) => a.shuffle - b.shuffle);
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
    clearWorksList() {
      this.works = [];
      this.message = "Select from the options above to create your own customized radio";
    },
    nextWork() {
      eventBus.$emit("changeWork");

      if (this.$view.shuffle) {

        for (var i = 0; i < this.shufflePlaylist.length; i++) {
          if (this.shufflePlaylist[i]["id"] == this.selectedWork && i !== this.shufflePlaylist.length - 1) {
            this.selectRow(this.shufflePlaylist[i + 1]["id"]);
            this.setRecommended(this.shufflePlaylist[i + 1]["recommend"]);
            this.setGenre(this.shufflePlaylist[i + 1]["genre"]);
            this.getAlbumsAndPlay(this.shufflePlaylist[i + 1]["id"], this.shufflePlaylist[i + 1]["title"]);
            break;
          } else if (this.shufflePlaylist[i]["id"] == this.selectedWork && i === this.shufflePlaylist.length - 1){
            this.selectRow(this.shufflePlaylist[0]["id"]);
            this.setRecommended(this.shufflePlaylist[0]["recommend"]);
            this.setGenre(this.shufflePlaylist[0]["genre"]);
            this.getAlbumsAndPlay(this.shufflePlaylist[0]["id"], this.shufflePlaylist[0]["title"]);
            break;
          }
        }

      } else {
        for (var j = 0; j < this.playlist.length; j++) {
          if (this.playlist[j]["id"] == this.selectedWork && j !== this.playlist.length - 1) {
            this.selectRow(this.playlist[j + 1]["id"]);
            this.setRecommended(this.shufflePlaylist[j + 1]["recommend"]);
            this.setGenre(this.playlist[j + 1]["genre"]);
            this.getAlbumsAndPlay(this.playlist[j + 1]["id"], this.playlist[j + 1]["title"]);
            break;
          }
        }
      }
    },
    previousWork() {
      eventBus.$emit("changeWork");

      if (this.$view.shuffle) {
        for (var i = 0; i < this.shufflePlaylist.length; i++) {
          if (this.shufflePlaylist[i]["id"] == this.selectedWork && i !== 0) {
            this.selectRow(this.shufflePlaylist[i - 1]["id"]);
            this.setRecommended(this.shufflePlaylist[i - 1]["recommend"]);
            this.setGenre(this.shufflePlaylist[i - 1]["genre"]);
            this.getAlbumsAndPlay(this.shufflePlaylist[i - 1]["id"], this.shufflePlaylist[i - 1]["title"]);
            break;
          } else if (this.shufflePlaylist[i]["id"] == this.selectedWork && i === 0){
            this.selectRow(this.shufflePlaylist[this.shufflePlaylist.length - 1]["id"]);
            this.setRecommended(this.shufflePlaylist[i - 1]["recommend"]);
            this.setGenre(this.shufflePlaylist[this.shufflePlaylist.length - 1]["genre"]);
            this.getAlbumsAndPlay(this.shufflePlaylist[this.shufflePlaylist.length - 1]["id"], this.shufflePlaylist[this.shufflePlaylist.length - 1]["title"]);
            break;
          }
        }

      } else {
        for (var j = 0; j < this.playlist.length; j++) {
          if (this.playlist[j]["id"] == this.selectedWork && j !== 0) {
            this.selectRow(this.playlist[j - 1]["id"]);
            this.setRecommended(this.shufflePlaylist[j - 1]["recommend"]);
            this.setGenre(this.playlist[j - 1]["genre"]);
            this.getAlbumsAndPlay(this.playlist[j - 1]["id"], this.playlist[j - 1]["title"]);
            break;
          }
        }
      }
    },
    playRandomWork() {
      eventBus.$emit("changeWork");

      const rndInt = randomIntFromInterval(0, this.playlist.length - 1);
      this.selectRow(this.playlist[rndInt]["id"]);
      this.setRecommended(this.playlist[rndInt]["recommend"]);
      this.setGenre(this.playlist[rndInt]["genre"]);
      this.getAlbumsAndPlay(this.playlist[rndInt]["id"], this.playlist[rndInt]["title"]);
    },
    getOmniSearchWork(work) {
      eventBus.$emit("changeWork");
      this.selectRow(work.id);
      this.setRecommended(work.recommend);
      this.setGenre(work.genre);
      this.getAlbums(work.id, work.title);
    },
  },
  created() {
    if (!this.$view.mode && !this.$route.query.search) {
      // only get works in browse mode
      if(this.$config.workRecommended == 1){
        this.getFilteredWorks('recommended');
      } else {
        this.getFilteredWorks('all');
      }
      this.selectRow(this.$config.work);
    }
    eventBus.$on("requestWorksList", this.requestWorksList);
    eventBus.$on("requestWorksListForArtist", this.getArtistWorks);
    eventBus.$on("fireWorkFilter", this.getFilteredWorks);
    eventBus.$on("fireWorkSearch", this.getSearchWorks);
    eventBus.$on("clearWorksList", this.clearWorksList);
    eventBus.$on("requestWorksForRadio", this.getRadioWorks);
    eventBus.$on("fireNextWork", this.nextWork);
    eventBus.$on("fireRandomWork", this.playRandomWork);
    eventBus.$on("firePreviousWork", this.previousWork);
    eventBus.$on("firePlaylistExport", this.preparePlaylist);
    eventBus.$on("fireRefreshWorks", this.refreshWorks);
    eventBus.$on("requestWorksListForFavorites", this.getFavoriteWorks);
    eventBus.$on("fireWorkScroll", this.setGenre);
    eventBus.$on("fireWorkOmniSearch", this.getOmniSearchWork);
  },
  beforeDestroy() {
    eventBus.$off("requestWorksList", this.requestWorksList);
    eventBus.$off("requestWorksListForArtist", this.getArtistWorks);
    eventBus.$off("fireWorkFilter", this.getFilteredWorks);
    eventBus.$off("fireWorkSearch", this.getSearchWorks);
    eventBus.$off("clearWorksList", this.clearWorksList);
    eventBus.$off("requestWorksForRadio", this.getRadioWorks);
    eventBus.$off("fireNextWork", this.nextWork);
    eventBus.$off("fireRandomWork", this.playRandomWork);
    eventBus.$off("firePreviousWork", this.previousWork);
    eventBus.$off("firePlaylistExport", this.preparePlaylist);
    eventBus.$off("fireRefreshWorks", this.refreshWorks);
    eventBus.$off("requestWorksListForFavorites", this.getFavoriteWorks);
    eventBus.$off("fireWorkScroll", this.setGenre);
    eventBus.$off("fireWorkOmniSearch", this.getOmniSearchWork);
  },
};

</script>

<style scoped>\
.narrow{
  font-family: Roboto Condensed !important;
 }
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
.td-style{
  white-space: nowrap; 
  text-overflow: ellipsis; 
  overflow: hidden; 
  max-width: 1px;
  color: grey;
}
.spinner {
    text-align: center;
}
.m-5 {
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
.plain-badge {
    color: var(--my-white);
    background-color: rgb(52, 58, 64, 0.7);
    border-radius: 7px;
    position: relative;
    top: -1px;
}
.liked-badge {
    color: var(--my-white);
    background-color: darkgoldenrod;
    border-radius: 7px;
    position: relative;
    top: -1px;
}
.no-works-found {
  font-size: 15px;
  color: #9da6af !important;
  text-align: center;
  font-family: Roboto Condensed !important;
}
</style>
