<template>
  <b-card class="album-info-card shadow-sm">
    <b-card-body class="card-body">
      <b-card-title class="card-title">
        <table v-if="album.release_date">
          <tr class="heading-tr" @click="goToAlbum(album)">
            <td>
              <b-avatar square size="60px" :src="album.images[0].url"></b-avatar>
            </td>
            <td class="heading-td">
              {{ album.name }}<br />
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
        <div v-show="!loading" v-for="result in results" :key="result[0]">
          <table>
            <tr>
              <td>
                <b-avatar button @click="getArtistComposers(result[0])" size="40px" :src="result[2]"></b-avatar>
              </td>
              <td class="info-td">
                <a class="artist-name" @click="getArtistComposers(result[0])">{{ result[0] }}</a><br />
                <span class="born-died">{{result[1]}}</span>
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
import spotify from "@/SpotifyFunctions.js";
import {getArtistDetails} from "@/HelperFunctions.js" 

export default {
  data() {
    return {
      artists: [],
      results: [],
      album: {},
      loading: true
    };
  },
  computed: {
    item_length: function () {
      return this.results.length;
    },
  },
  watch: {
    results: {
      handler: function () {
        // turn off loading when people results array is fully populated
        if (this.results.length == this.artists.length && this.artists.length > 0){
          this.loading = false;
        }
      },
      deep: true
    }
  },
  methods: {
    goToAlbum(album) {
      if (!this.$view.mobile) {
          this.$router.push("/albums?id=" + album.id);
      }
    },
    getArtistComposers(artist) {
      if (!this.$view.mobile) {
        eventBus.$emit("requestComposersForArtist", artist);
        this.$config.artist = artist;
        if (this.$route.name != "performers") {
          this.$router.push("/performers?artist=" + artist);
        }
      }
    },
    setSpotifyAlbum(album) {
      this.album = album;
    },
    fixArtists(artists){
      // Fixes string of artists that are wrong in Spotify (ie. Meier/Barenboim/Bohm as one artist)
       for (let i = 0; i < artists.length; i++) {
          if (artists[i].name.indexOf("/") !== -1) {
            let fixedArtists = artists[i].name.split("/");
            let artistDictList = fixedArtists.map(function(artistName) {
              return { name: artistName , img: "NA"};
            });
            artists.splice(i, 1);
            artists.push(...artistDictList);
          }
        }
        let uniqueList = artists.filter((dict, index, self) =>
            index === self.findIndex((d) => d.name === dict.name)
        );
        return uniqueList;
      },
    getSpotifyAlbumData(album) {
      this.loading = true;
      // retrieves data from Spotify. 'album' is database album object
      this.results = [];
      this.artists = album.artist_details;
      this.artists = this.fixArtists(this.artists);
      let album_id = album.album_uri.substring(album.album_uri.lastIndexOf(":") + 1);
      spotify.getSpotifyAlbum(this.$auth.appToken, album_id);
      this.artists.forEach((element) => getArtistDetails(element, this.results, this.$auth.knowledgeKey));
    }
  },
  created() {
    this.getSpotifyAlbumData(this.$config.albumData);
    eventBus.$on("fireSetAlbum", this.getSpotifyAlbumData); 
    eventBus.$on("fireSetAlbumHopper", this.getSpotifyAlbumData);
    eventBus.$on("fireSpotifyAlbumData", this.setSpotifyAlbum);
  },
  beforeDestroy() {
    eventBus.$off("fireSetAlbum", this.getSpotifyAlbumData);
    eventBus.$off("fireSetAlbumHopper", this.getSpotifyAlbumData);
    eventBus.$off("fireSpotifyAlbumData", this.setSpotifyAlbum);
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
