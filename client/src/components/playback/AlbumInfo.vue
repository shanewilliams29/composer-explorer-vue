<template>
  <b-card no-body v-show="!loading">
    <b-row no-gutters>
      <b-col cols="12" md="auto" class="album-cover-col">
        <b-card-img @click="goToAlbum(album.spotify_id)" :src="album.img_big" alt="Album Cover" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body class="info-card-body">
          <b-card-text>
            <div class="centered album-data">
              <a class="composer" @click="getSearchWork(work)">{{work.composer}}</a>
              <a class="title" style="font-weight: bold;" @click="getSearchWork(work)">{{work.title}}</a>
              <div class="artists-row">
              <span class="artist narrow" v-for="(artist, index) in artists" :key="index">
                <a class="artist narrow" @click="getArtistComposers(artist)">{{ artist.name }}</a><span v-if="index !== artists.length - 1">,&nbsp;</span>
              </span>
              </div>
            </div>
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
import axios from "axios";
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      album: [],
      title: "",
      work: {},
      hold_title: this.$config.workTitle,
      composer: '',
      artists:[]
    };
  },
  methods: {
    goToAlbum(album_id) {
      if (!this.$view.mobile) {
          this.$router.push("/albums?id=" + album_id);
      }
    },
    getSearchWork(work) {
        let delay = 0;
        if (this.$route.name != "home") {
          delay = 200;
          this.$router.push("/?search=" + work.id);
        }
        setTimeout(function(){
          eventBus.$emit("fireWorkOmniSearch", work);
        }, delay);
    },
    getArtistComposers(artist) {
      if (!this.$view.mobile) {
        this.$config.artist = artist;
        if (this.$route.name != "performers") {
          this.$router.push("/performers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
      }
    },
    getAlbumInfo(album_id) {
      this.loading = true;
      const path = "api/albuminfo/" + album_id;
      axios
        .get(path)
        .then((res) => {
          this.$config.albumData = res.data.album;
          localStorage.setItem("config", JSON.stringify(this.$config));
          eventBus.$emit("fireSetAlbum", res.data.album);
          this.album = res.data.album;
          this.work = res.data.work;
          this.title = this.work.title;
          this.artists = res.data.print_artists;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    getAlbumInfoHopper(album_id, track_no, percent_progress) {
      this.loading = true;
      const path = "api/albuminfo/" + album_id;
      axios
        .get(path)
        .then((res) => {
          this.$config.albumData = res.data.album;
          localStorage.setItem("config", JSON.stringify(this.$config));
          eventBus.$emit("fireSetAlbumHopper", res.data.album, track_no, percent_progress);
          this.album = res.data.album;
          this.composer = res.data.composer;
          this.work = res.data.work;
          this.title = this.work.title;
          this.artists = res.data.print_artists;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    holdTitle() {
      this.hold_title = this.$config.workTitle;
    },
  },
  created() {
    this.loading = true;
    eventBus.$on("requestAlbumData", this.getAlbumInfo);
    eventBus.$on("requestAlbumDataHopper", this.getAlbumInfoHopper);
    eventBus.$on("requestAlbums", this.holdTitle);
    eventBus.$on("requestFavoritesAlbums", this.holdTitle);
    eventBus.$on("requestAlbumsAndPlay", this.holdTitle);
    eventBus.$on("fireArtistAlbums", this.holdTitle);
  },
  beforeDestroy() {
    eventBus.$off("requestAlbumData", this.getAlbumInfo);
    eventBus.$off("requestAlbumDataHopper", this.getAlbumInfoHopper);
    eventBus.$off("requestAlbums", this.holdTitle);
    eventBus.$off("requestFavoritesAlbums", this.holdTitle);
    eventBus.$off("requestAlbumsAndPlay", this.holdTitle);
    eventBus.$off("fireArtistAlbums", this.holdTitle);
  },
};
</script>

<style scoped>
.rounded-0{
cursor: pointer;
}
.narrow {
  font-family: Roboto Condensed !important;
}
.album-cover-col {
  padding-right: 0px;
}
.info-card-body {
  background: var(--dark-gray) !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  height: 100px;
}
.card {
  border: none !important;
  background: var(--dark-gray) !important;
}
.card-img {
  height: 100%;
  width: auto;
  max-width: 100px;
  max-height: 100px;
}
.card-body {
  font-size: 14px;
  margin-right: 6px;
  padding-top: 0px;
  height: 100px;
  overflow-y: hidden;
}
.centered {
  padding-left: 8px;
  display: flex;
  flex-direction: column;
  column-gap: 0px;
  justify-content: center;
  height: 100px;
}
.album-data {
  padding-left: 12px;
  line-height: 130%;
}
.composer{
  color: var(--my-white);
  cursor: pointer;
}
.title{
  color: var(--my-white);
  cursor: pointer;
}
.artist{
  cursor: pointer;
  color: var(--medium-dark-gray);
  font-size: 13px;
  white-space: nowrap;
  display: inline;
}
.artists-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
</style>
