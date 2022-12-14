<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="!loading && albums.length < 1 && !this.$view.mode" 
        class="m-4 col no-albums-found">
        No albums found.
      </span>
    </div>
    <div v-if="albums">
      <div class="row">
        <b-card-group deck v-show="!loading">
          <LargeAlbum 
            v-if="$config.albumSize == 'large' || $view.mode == 'radio'" 
            :albums="albums" 
            :selectedAlbum="selectedAlbum" 
            :likedAlbums="likedAlbums" 
            @selectAlbum="selectRow" 
            @getAlbum="getAlbumData"/>
          <SmallAlbum 
            v-else 
            :albums="albums" 
            :selectedAlbum="selectedAlbum" 
            :likedAlbums="likedAlbums" 
            @selectAlbum="selectRow" 
            @getAlbum="getAlbumData"/>
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
import LargeAlbum from "@/components/subcomponents/LargeAlbum.vue";
import SmallAlbum from "@/components/subcomponents/SmallAlbum.vue";
import axios from "axios";
import { eventBus } from "../main.js";

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
    };
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
          this.$config.composer = res.data.composer;
          localStorage.setItem("config", JSON.stringify(this.$config));
          this.albums = res.data.albums;
          this.likedAlbums = res.data.liked_albums;
          eventBus.$emit("fireArtistList", res.data.artists);
          this.loading = false;
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
          this.$config.composer = res.data.composer;
          localStorage.setItem("config", JSON.stringify(this.$config));
          this.albums = res.data.albums;
          this.likedAlbums = res.data.liked_albums;
          eventBus.$emit("fireArtistList", res.data.artists);
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    // gets albums and begins playback of first (for next and previous buttons)
    // used in Autoplay and the radio
    getAlbumsAndPlay(id, artist, sort) {
      function randomIntFromInterval(min, max) {
        // min and max included
        return Math.floor(Math.random() * (max - min + 1) + min);
      }

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

      var path = "";
      var favorites = this.$view.favoritesAlbums;
      if (this.$view.mode == "radio") {
        var limit = this.$view.radioTrackLimit;
        path = "api/albums/" + id + "?artist=" + artist + "&sort=" + sort + "&limit=" + limit + "&favorites=" + favorites;
      } else if (this.$view.mode == "favorites") {
        path = "api/albums/" + id + "?artist=" + artist + "&sort=" + sort + "&favorites=" + favorites;
      } else {
        path = "api/albums/" + id + "?artist=" + artist + "&sort=" + sort;
      }
      axios
        .get(path)
        .then((res) => {
          if (res.data.albums.length < 1) {
            this.$bvToast.show("no-tracks-toast");
            setTimeout(() => {
              eventBus.$emit("fireNextWork");
              this.$bvToast.hide("no-tracks-toast");
            }, 2000); // Bypass and continue to next work)
          } else {
            if (this.$view.mode == "radio") {
              // only one album in radiomode unless favorites
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
            this.selectRow(this.albums[0].id); // select first row on work selection
            this.$config.album = this.albums[0].id;
            this.likedAlbums = res.data.liked_albums;
            this.determineHeart(this.$config.album); //needed for first load as fireAlbumData misses
            this.$config.composer = res.data.composer;
            localStorage.setItem("config", JSON.stringify(this.$config));
            eventBus.$emit("fireArtistList", res.data.artists);
            eventBus.$emit("fireAlbumData", this.albums[0].id);
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
      const path = "api/albums/" + id;
      axios
        .get(path)
        .then((res) => {
          this.albums = res.data.albums;
          eventBus.artists = res.data.artists;
          this.likedAlbums = res.data.liked_albums;
          this.loading = false;
          this.selectRow(this.$config.album);
          this.determineHeart(this.$config.album); //necessary for first load only, misses fireAlbumData
          eventBus.$emit("fireAlbumData", this.$config.album);
          eventBus.$emit("fireArtistList", res.data.artists);
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getAlbumData(albumId) {
      eventBus.$emit("fireAlbumData", albumId);
      this.$config.album = albumId;
      localStorage.setItem("config", JSON.stringify(this.$config));
    },
    selectRow(album) {
      this.selectedAlbum = album;
      for (let i = 0; i < this.albums.length; i++) {
        if (this.albums[i].id == album) {
          this.currentAlbum = i;
          break;
        }
      }
    },
    clearAlbums() {
      this.albums = [];
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
        $state.complete();
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
      this.artistName = "";
      this.sort = "";
      this.page = 2;
      this.albums = [];
      this.infiniteId += 1;
    },
    playNextAlbum() {
      this.currentAlbum += 1;
      if (this.currentAlbum >= this.albums.length) {
        eventBus.$emit("fireNextWork");
      }
      this.selectRow(this.albums[this.currentAlbum].id); // select first row on work selection
      this.$config.album = this.albums[this.currentAlbum].id;
      eventBus.$emit("fireAlbumData", this.albums[this.currentAlbum].id);
    },
  },
  created() {
    if (!this.$view.mode) {
      // dont get albums in radio or performer mode
      this.initialGetAlbums(this.$config.work);
    }
    eventBus.$on("fireAlbums", this.getAlbums);
    eventBus.$on("fireAlbumsAndPlay", this.getAlbumsAndPlay);
    eventBus.$on("fireFavoritesAlbums", this.getFavoritesAlbums);
    eventBus.$on("fireClearAlbums", this.clearAlbums);
    eventBus.$on("fireNextAlbum", this.playNextAlbum);
  },
  beforeDestroy() {
    eventBus.$off("fireAlbums", this.getAlbums);
    eventBus.$off("fireAlbumsAndPlay", this.getAlbumsAndPlay);
    eventBus.$off("fireFavoritesAlbums", this.getFavoritesAlbums);
    eventBus.$off("fireClearAlbums", this.clearAlbums);
    eventBus.$off("fireNextAlbum", this.playNextAlbum);
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
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
