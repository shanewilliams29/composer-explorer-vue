<template>
  <b-card class="album-info-card shadow-sm">
    <b-card-body class="card-body">
      <b-card-title class="card-title">
        <table v-if="album.release_date">
          <tr class="heading-tr" @click="goToAlbum(album)">
            <td>
              <b-avatar square size="60px" :src="album.album_img"></b-avatar>
            </td>
            <td class="heading-td">
              {{ album.album_name }}<br />
              <span class="born-died">
                ℗ {{album.release_date.slice(0,4)}} · {{ album.label }}
              </span>
            </td>
          </tr>
        </table>
      </b-card-title>
      <b-card-text class="info-card-text">
        <div class="spinner" v-show="loading" role="status">
          <b-spinner class="m-5"></b-spinner>
        </div>
        <div v-show="!loading" v-for="artist in artists" :key="artist.id">
          <table>
            <tr>
              <td>
                <b-avatar button @click="getArtistComposers(artist)" size="40px" :src="artist.img"></b-avatar>
              </td>
              <td class="info-td">
                <a class="artist-name" @click="getArtistComposers(artist)">{{ artist.name }}</a><br />
                <span v-if="artist.description != 'NA'" class="born-died">{{artist.description}}</span>
              </td>
            </tr>
          </table>
        </div>
      </b-card-text>
    </b-card-body>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      artists: [],
      album: {},
      loading: false
    };
  },
  methods: {
    goToAlbum(album) {
      if (!this.$view.mobile) {
          this.$router.push("/albums?id=" + album.album_id);
      } else {
        this.$router.push("/mobilealbums?id=" + album.album_id);
        this.$emit('togglePanel');
      }
    },
    getArtistComposers(artist) {
      if (!this.$view.mobile) {
        this.$config.artist = artist;
        if (this.$route.name != "performers") {
          this.$router.push("/performers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
      } else {
        this.$config.artist = artist;
        if (this.$route.name != "mobileperformers") {
          this.$router.push("/mobileperformers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
        this.$emit('togglePanel');
      }
    },
    setAlbumInfo(album) {
      this.album = album;
      this.artists = album.artist_details;
    }
  },
  created() {
    this.setAlbumInfo(this.$config.albumData);
    eventBus.$on("fireSetAlbum", this.setAlbumInfo); 
    eventBus.$on("fireSetAlbumHopper", this.setAlbumInfo);
  },
  beforeDestroy() {
    eventBus.$off("fireSetAlbum", this.setAlbumInfo);
    eventBus.$off("fireSetAlbumHopper", this.setAlbumInfo);
  },
};
</script>

<style scoped>
a {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}
.heading-tr {
  vertical-align: middle;
  height: 62px !important;
  cursor: pointer;
}
.heading-td {
  padding-left: 10px;
  font-size: 16px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: var(--dark-gray);
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.album-info-card {
  padding: 15px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.info-td {
  padding-left: 10px;
}
.disclaimer {
  margin-bottom: 11px;
}
.card-title {
  font-size: 16px;
  height: 62px;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
  padding-left: 2px;
}
table {
  margin-bottom: 6px;
}
.wiki-link {
  font-style: italic;
  color: grey;
}
.open-in-spotify {
  font-size: 12px;
}
.spotify-logo {
  width: auto;
  height: 20px;
}

/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--my-white);
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
