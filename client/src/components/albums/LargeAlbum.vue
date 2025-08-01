<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" :class="{'highlight': (album.id == selectedAlbum)}">
      <div class="row">
        <b-col class="album_columns">
          <div class="album-titles" @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);">
            <span style="font-size: 14px; color: black; font-weight: 600;">{{ album.artists }}</span><br />
            <span class="narrow">℗ {{ album.release_date }} {{ album.label }}</span>
            <span v-if="album.duration" class="label narrow">&nbsp;<span style='font-size: 9px; vertical-align: 1px;'>
                <b-icon-clock></b-icon-clock>
              </span>&nbsp;{{ duration(album.duration) }}&nbsp;{{ fullOrExerpt(album.full_performance) }}</span>
            <br />
            <span v-if="album.minor_artists" class="narrow" style="color: grey; font-size: 13px !important;">{{ album.minor_artists }}</span>
          </div>
          <div v-if="album.img_big" @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);">
            <img class="album-cover" height="auto" v-lazy="album.img_big" />
          </div>
          <div v-else @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);"><img class="album-cover" height="auto" v-lazy="album.album_img" /></div>
          <div class="row">
            <b-col class="col likes-col" cols="4">
              <AlbumLikes v-bind:likedAlbums="likedAlbums" v-bind:album="album" v-bind:selectedAlbum="selectedAlbum" />
            </b-col>
            <b-col class="col footer" cols="8">
              <div v-if="!$view.mobile">
              <div v-if="album.id == selectedAlbum">
                <a target="_blank" :href="`https://open.spotify.com/album/${album.album_id}`"><span class="open-in">Open in&nbsp; </span><img class="spotify-logo" width="70px" :src="spotifyLogoURLWhite" /></a>
              </div>
              <div v-else>
                <a target="_blank" :href="`https://open.spotify.com/album/${album.album_id}`"><img class="spotify-logo" width="70px" :src="spotifyLogoURLBlack" /></a>
              </div>
            </div>
            </b-col>
          </div>
        </b-col>
      </div>
    </b-card>
  </div>
</template>


<script>
import { staticURL } from "@/main.js";
import AlbumLikes from './AlbumLikes.vue';
import { msToHMS } from "@/HelperFunctions.js";

export default {
  components: {
    AlbumLikes
  },
  name: 'LargeAlbum',
  props: {
    albums: Array,
    selectedAlbum: String,
    likedAlbums: Array
  },
  data() {
    return {
      spotifyLogoURLWhite: staticURL + '/assets/Spotify_Logo_RGB_White.png',
      spotifyLogoURLBlack: staticURL + '/assets/Spotify_Logo_RGB_Black.png',
    }
  },
  methods: {
    fullOrExerpt(bool){ // add to albums list
      return bool ? "" : "(Excerpt)"
    },
    timeDisplay(milliseconds) {
      return msToHMS(milliseconds);
    },
    duration(ms) {
      let seconds = Math.floor(ms / 1000);
      let hours = Math.round(seconds / 3600 * 10) / 10;
      let minutes = Math.round(seconds / 60);

      if (hours > 1) {
        return hours + "h";
      } else {
        return minutes + "m"
      }
    },
  }
}
</script>

<style scoped>
a:hover {
    text-decoration: none;
}
.footer {
    text-align: right;
    font-size: 13px;
}
.open-in {
    position: relative;
    top: -0.4px;
}
.likes {
    position: relative;
    top: -1px;
}
.spotify-logo {
    padding-bottom: 5px;
    margin-right: 22px;
}
.card {
    width: 100%;
    background-color: var(--my-white);
    border: none;
    margin-top: 5px;
}
.highlight {
    color: var(--my-white);
}
.highlight span {
    color: var(--my-white) !important;
}
.album_columns {
    padding-right: 0px;
}
.album_text_columns {
    padding: 10px;
    padding-right: 20px;
    font-size: 13px;
}
.album-cover {
    margin: 5px;
    box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
    width: calc(100% - 25px);
}
.album-cover:hover {
    cursor: pointer;
}
.album-titles {
    margin-left: 8px;
    margin-top: 6px;
    margin-bottom: 0px;
    margin-right: 20px;
    font-size: 13px;
    line-height: 135%;
}
.album-titles:hover {
    cursor: pointer;
}
.minor-album-titles {
    margin-left: 8px;
    margin-top: 0px;
    margin-bottom: 8px;
    margin-right: 20px;
    font-size: 13px;
    color: grey;
}
.badge {
    vertical-align: middle;
    color: var(--my-white) !important;
    background-color: goldenrod;
    margin-bottom: 2.5px;
    border-radius: 7px;
}
.highlight .badge {
    color: #000 !important;
    background-color: var(--my-white);
}
.likes-col {
    padding-left: 20px;
}
.narrow{
  font-family: Roboto Condensed !important;
}
</style>
