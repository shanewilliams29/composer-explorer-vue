<template>
  <b-card no-body bg-variant="dark" v-show="!loading">
    <b-row no-gutters>
      <b-col cols="12" md="auto" class="album-cover-col">
        <b-card-img :src="album.album_img" alt="Album Cover" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body class="info-card-body">
          <b-card-text>
            <div class="centered album-data">
              <span>{{composer}}</span>
              <span style="font-weight: bold;">{{title}}</span>
              <span style="font-style: italic; color: darkgray; font-size: 13px;">{{album.artists}}</span>
            </div>
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
import axios from "axios";
import { eventBus } from "../../main.js";

export default {
  data() {
    return {
      album: [],
      title: "",
      hold_title: this.$config.workTitle,
      composer: this.$config.composer,
    };
  },
  methods: {
    getAlbumInfo(album_id) {
      this.title = this.hold_title;
      this.loading = true;
      const path = "api/albuminfo/" + album_id;
      axios
        .get(path)
        .then((res) => {
          this.$config.albumData = res.data.album;
          localStorage.setItem("config", JSON.stringify(this.$config));
          eventBus.$emit("fireSetAlbum", res.data.album);
          this.album = res.data.album; // Change to local file
          this.composer = this.$config.composer;
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
    eventBus.$on("fireAlbumData", this.getAlbumInfo);
    eventBus.$on("fireAlbums", this.holdTitle);
    eventBus.$on("fireFavoritesAlbums", this.holdTitle);
    eventBus.$on("fireAlbumsAndPlay", this.holdTitle);
    eventBus.$on("fireArtistAlbums", this.holdTitle);
  },
  beforeDestroy() {
    eventBus.$off("fireAlbumData", this.getAlbumInfo);
    eventBus.$off("fireAlbums", this.holdTitle);
    eventBus.$off("fireFavoritesAlbums", this.holdTitle);
    eventBus.$off("fireAlbumsAndPlay", this.holdTitle);
    eventBus.$off("fireArtistAlbums", this.holdTitle);
  },
};
</script>

<style scoped>
.album-cover-col {
  padding-right: 0px;
}
.info-card-body {
  background: none !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  height: 100px;
}
.card {
  border: none !important;
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
</style>
