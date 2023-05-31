<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="!loading && albums.length < 1 && !this.$view.mode && this.message" class="m-4 col no-albums-found">
        {{ message }}
      </span>
      <span v-show="!loading && albums.length < 1 && !this.$view.mode && !this.message" class="m-4 col no-albums-found">
        No albums found
      </span>
    </div>
    <div v-if="albums">
      <div class="row">
        <b-card-group deck v-show="!loading">
          <LargeAlbum v-if="$config.albumSize == 'large' || $view.mode == 'radio'" :albums="albums" :selectedAlbum="selectedAlbum" :likedAlbums="likedAlbums" @selectAlbum="selectRow" @getAlbum="playAlbumHop" />
          <SmallAlbum v-else :albums="albums" :selectedAlbum="selectedAlbum" :likedAlbums="likedAlbums" @selectAlbum="selectRow" @getAlbum="playAlbumHop" />
          <infinite-loading spinner="spiral" :identifier="infiniteId" @infinite="infiniteHandler">
            <div slot="no-more"></div>
            <div slot="no-results"></div>
          </infinite-loading>
        </b-card-group>
      </div>
    </div>
    <b-toast id="no-tracks-toast" no-close-button static no-auto-hide>
      No albums found for this work with the specified track limit. Advancing to next...
    </b-toast>
  </div>
</template>

<script>
import LargeAlbum from "./LargeAlbum.vue";
import SmallAlbum from "./SmallAlbum.vue";
import axios from "axios";
import { eventBus } from "@/main.js";
import { randomIntFromInterval } from "@/HelperFunctions.js";


export default {
  components: {
    LargeAlbum,
    SmallAlbum,
  },
  data() {
    return {
      albums: [],
      loading: false,
      selectedAlbum: null,
      likedAlbums: [],
      page: 2,
      workId: "",
      artistName: "",
      sort: "",
      infiniteId: +new Date(),
      currentAlbum: 0,
      message: "",
      newWork: true
    };
  },
  computed: {
    genreChanged() {
      return this.$config.genre;
    },
  },
  watch: {
    genreChanged(newGenre) {
      // Opera albums are larger, allowing more space for lines of text
      if (newGenre == "Opera" || newGenre == "Stage Work") {
        document.documentElement.style.setProperty("--album-size", `108px`);
        document.documentElement.style.setProperty("--line-clamp", `3`);
      } else {
        document.documentElement.style.setProperty("--album-size", `96px`);
        document.documentElement.style.setProperty("--line-clamp", `2`);
      }
    },
  },
  methods: {
    getAlbums(id, artist, sort) {
      this.changeAlbums();

      this.workId = id;
      if (artist) {
        this.artistName = artist;
      } else {
        artist = "";
      }
      if (sort) {
        this.sort = sort;
      } else {
        sort = "";
      }
      this.loading = true;

      const path = "api/albums/" + id + "?artist=" + artist + "&sort=" + sort;
      axios
        .get(path)
        .then((res) => {
          this.loading = false;
          this.$config.composer = res.data.composer[0].name_short;
          this.$config.tier = res.data.composer[0].tier;
          this.albums = res.data.albums;
          this.likedAlbums = res.data.liked_albums;
          this.message = "";
          localStorage.setItem("config", JSON.stringify(this.$config));

          eventBus.$emit("sendArtistList", res.data.artists);

        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getFavoritesAlbums(id) {
      this.changeAlbums();

      this.workId = id;
      this.loading = true;

      const path = "api/albums/" + id + "?favorites=true";
      axios
        .get(path)
        .then((res) => {
          this.loading = false;
          this.$config.composer = res.data.composer[0].name_short;
          this.$config.tier = res.data.composer[0].tier;
          this.albums = res.data.albums;
          this.likedAlbums = res.data.liked_albums;
          this.message = "";
          localStorage.setItem("config", JSON.stringify(this.$config));

          eventBus.$emit("sendArtistList", res.data.artists);
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    // gets albums and begins playback of the first album immediately
    // used in Autoplay, the radio, and next/previous playback buttons
    getAlbumsAndPlay(id, artist, sort) {
      this.changeAlbums();

      this.workId = id;
      if (artist) {
        this.artistName = artist;
      } else {
        artist = "";
      }
      if (sort) {
        this.sort = sort;
      } else {
        sort = "";
      }
      this.loading = true;

      let path = "api/albums/" + id + "?artist=" + artist + "&sort=" + sort;
      const favorites = this.$view.favoritesAlbums;
      const limit = this.$view.radioTrackLimit;

      if (this.$view.mode == "radio") {
        if (favorites) { // no track limit in favorites mode
          path = path + "&favorites=true";
        } else {
          path = path + "&limit=" + limit;
        }
      }

      if (this.$view.mode == "favorites") {
        path = path + "&favorites=true";
      }

      axios
        .get(path)
        .then((res) => {
          this.message = "";
          // If no albums for this work, advance to next work
          if (res.data.albums.length < 1) {
            this.$bvToast.show("no-tracks-toast");

            setTimeout(() => {
              eventBus.$emit("fireNextWork");
              this.$bvToast.hide("no-tracks-toast");
            }, 2000);

          } else {
            if (this.$view.mode == "radio") {
              // display only one album in radio mode unless in favorites radio
              if (this.$view.randomAlbum) {
                const rndInt = randomIntFromInterval(0, res.data.albums.length - 1);
                this.albums = [res.data.albums[rndInt]];

              } else if (!this.$view.favoritesAlbums) {
                this.albums = [res.data.albums[0]];

              } else {
                this.albums = res.data.albums;
              }

            } else {
              this.albums = res.data.albums;
            }

            this.loading = false;
            this.likedAlbums = res.data.liked_albums;
            this.$config.album = this.albums[0].id;
            this.$config.composer = res.data.composer[0].name_short;
            this.$config.tier = res.data.composer[0].tier;
            localStorage.setItem("config", JSON.stringify(this.$config));

            this.selectRow(this.albums[0].id); // select first row
            this.determineHeart(this.$config.album); //needed for first load as requestAlbumData misses

            eventBus.$emit("sendArtistList", res.data.artists);
            eventBus.$emit("requestAlbumData", this.albums[0].id);
          }
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    // loads from localstorage on initial startup
    initialGetAlbums(id) {
      this.changeAlbums();

      this.workId = id;
      this.loading = true;
      this.message = "";

      const path = "api/albums/" + id;
      axios
        .get(path)
        .then((res) => {
          this.albums = res.data.albums;
          this.likedAlbums = res.data.liked_albums;
          this.loading = false;

          this.selectRow(this.$config.album);
          this.determineHeart(this.$config.album);

          eventBus.$emit("requestAlbumData", this.$config.album);
          eventBus.$emit("sendArtistList", res.data.artists);
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getAlbumData(albumId) {
      this.$config.album = albumId;
      localStorage.setItem("config", JSON.stringify(this.$config));

      eventBus.$emit("requestAlbumData", albumId);
    },
    selectRow(albumID) {
      this.selectedAlbum = albumID;
      for (let i = 0; i < this.albums.length; i++) {
        if (this.albums[i].id == albumID) {
          this.currentAlbum = i;
          break;
        }
      }
    },
    playAlbumHop(albumId) {
      if (this.newWork) {
        this.$view.progress = 0;
        this.$view.trackIndex = 0;
        this.newWork = false;
      }
      this.$config.album = albumId;
      this.determineHeart(this.$config.album);
      localStorage.setItem("config", JSON.stringify(this.$config));

      let track_no = this.$view.trackIndex;
      let percent_progress = this.$view.progress / this.$view.duration;

      eventBus.$emit("requestAlbumDataHopper", albumId, track_no, percent_progress);
    },
    clearAlbums() {
      this.albums = [];
      this.message = "Select a work to view albums."
    },
    determineHeart(albumId) {
      if (this.likedAlbums.includes(albumId)) {
        this.$view.like = true;
      } else {
        this.$view.like = false;
      }
    },
    infiniteHandler($state) {
      if (this.$view.mode) {
        $state.complete(); // only used in Browse mode ($view.mode = null)
      } else {
        const path = "api/albums/" + this.workId + "?artist=" + this.artistName + "&sort=" + this.sort + "&page=" + this.page;
        axios.get(path).then(({ data }) => {
          if (data.albums.length) {
            this.page += 1;
            this.albums.push(...data.albums);
            $state.loaded();
          } else {
            $state.complete();
          }
        });
      }
    },
    changeAlbums() {
      // reset these upon album change
      this.artistName = "";
      this.sort = "";
      this.page = 2;
      this.albums = [];
      this.infiniteId += 1;
    },
    setNewWork() {
      this.newWork = true;
    },
    playNextAlbum() {
      // advances to next album when the current album can't be played
      this.currentAlbum += 1;

      if (this.currentAlbum >= this.albums.length) {
        eventBus.$emit("fireNextWork");
      }

      this.selectRow(this.albums[this.currentAlbum].id);
      this.$config.album = this.albums[this.currentAlbum].id;
      this.determineHeart(this.$config.album);
      localStorage.setItem("config", JSON.stringify(this.$config));

      eventBus.$emit("requestAlbumData", this.albums[this.currentAlbum].id);
    },
    playTimeHopForward(progress, duration) {
      this.currentAlbum += 1;

      if (this.currentAlbum >= this.albums.length) {
        this.currentAlbum = this.albums.length - 1;
        return null;
      }

      this.selectRow(this.albums[this.currentAlbum].id);

      this.$config.album = this.albums[this.currentAlbum].id;
      this.determineHeart(this.$config.album);
      localStorage.setItem("config", JSON.stringify(this.$config));

      let track_no = this.$view.trackIndex;
      let percent_progress = progress / duration;

      eventBus.$emit("requestAlbumDataHopper", this.albums[this.currentAlbum].id, track_no, percent_progress);
    },
    playTimeHopBackward(progress, duration) {
      this.currentAlbum -= 1;

      if (this.currentAlbum < 0) {
        this.currentAlbum = 0;
        return null;
      }

      this.selectRow(this.albums[this.currentAlbum].id);

      this.$config.album = this.albums[this.currentAlbum].id;
      this.determineHeart(this.$config.album);
      localStorage.setItem("config", JSON.stringify(this.$config));

      let track_no = this.$view.trackIndex;
      let percent_progress = progress / duration;

      eventBus.$emit("requestAlbumDataHopper", this.albums[this.currentAlbum].id, track_no, percent_progress);
    },
  },
  created() {
    // only get albums in Browse ($view.mode = null) mode
    if (!this.$view.mode && !this.$route.query.search) { 
      this.initialGetAlbums(this.$config.work);
    }

    if (!this.$view.mobile && (this.$config.genre == "Opera" || this.$config.genre == "Stage Work")) {
      document.documentElement.style.setProperty("--album-size", `108px`);
      document.documentElement.style.setProperty("--line-clamp", `3`);
    } else if (this.$view.mobile) {
      document.documentElement.style.setProperty("--album-size", `96px`);
      document.documentElement.style.setProperty("--line-clamp", `2`);
    } else {
      document.documentElement.style.setProperty("--album-size", `96px`);
      document.documentElement.style.setProperty("--line-clamp", `2`);
    }

    eventBus.$on("requestAlbums", this.getAlbums);
    eventBus.$on("changeWork", this.setNewWork);
    eventBus.$on("requestAlbumsAndPlay", this.getAlbumsAndPlay);
    eventBus.$on("requestFavoritesAlbums", this.getFavoritesAlbums);
    eventBus.$on("clearAlbumsList", this.clearAlbums);
    eventBus.$on("advanceToNextAlbum", this.playNextAlbum);
    eventBus.$on("fireTimeHopperForward", this.playTimeHopForward);
    eventBus.$on("fireTimeHopperBackward", this.playTimeHopBackward);
  },
  beforeDestroy() {
    eventBus.$off("requestAlbums", this.getAlbums);
    eventBus.$off("changeWork", this.setNewWork);
    eventBus.$off("requestAlbumsAndPlay", this.getAlbumsAndPlay);
    eventBus.$off("requestFavoritesAlbums", this.getFavoritesAlbums);
    eventBus.$off("clearAlbumsList", this.clearAlbums);
    eventBus.$off("advanceToNextAlbum", this.playNextAlbum);
    eventBus.$off("fireTimeHopperForward", this.playTimeHopForward);
    eventBus.$on("fireTimeHopperBackward", this.playTimeHopBackward);
  },
};
</script>

<style scoped>
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
  padding-left: 5px;
  padding-right: 5px;
}
.no-albums-found {
  font-size: 15px;
  color: #9da6af !important;
  text-align: center;
  font-family: Roboto Condensed !important;
}
</style>
