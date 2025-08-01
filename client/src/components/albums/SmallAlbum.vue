<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" :class="{'highlight': (album.id == selectedAlbum)}">
      
      <!-- ALBUM POPUP -->
      <Transition name="fade">
        <div v-if="!$view.mobile && !$view.banner">
          <div class="popup" :class="{'reveal': (showAlbum == album.id)}">
            <img class="album-cover" :ref="album.id" :src="album.img_big" />
            <div class="image-caption">
              <span class="album-major-artists">{{ album.artists }}</span><br />
              <span v-if="album.minor_artists" class="album-minor-artists">{{ album.minor_artists }}</span>
            </div>
          </div>
        </div>
      </Transition>

      <!-- ALBUM ITEM PANEL -->
      <div class="row" @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);" @mouseover="showCover = album.id" @mouseleave="showCover = false">
        <b-col cols="auto" class="album_columns">
          <img class="album-img-small" v-lazy="album.img_big" />
        </b-col>
        <b-col class="album_text_columns">
          <b-card-text>
            <table cellspacing="0">
              <tr>
                <td width="100%" class="td-style-black">
                  <span class="album-major-artists selected">
                    {{ album.artists.split(", ")[0] }}</span><br>
                </td>
              </tr>
              <tr>
                <td width="100%" class="td-style-black narrow">
                  <span class="label">℗ {{ album.release_date }} </span>
                  <span class="label"> {{ album.label }} </span>
                  <span v-if="album.duration" class="label">&nbsp;<span style='font-size: 9px; vertical-align: 1px;'>
                      <b-icon-clock></b-icon-clock>
                    </span>&nbsp;{{ duration(album.duration) }}&nbsp;{{ fullOrExerpt(album.full_performance) }}</span>
                </td>
              </tr>
              <tr v-if="album.minor_artists || album.artists.split(', ')[1]">
                <td width="100%" class="td-style narrow last-td wrap-text">
                  <span class="album-minor-artists selected">{{album.artists.split(", ")[1]}}<span v-if="album.minor_artists">,</span></span>
                  <span v-if="album.minor_artists" class="album-minor-artists selected">
                    {{album.minor_artists}}
                  </span>
                  <span v-else><br /></span>
                </td>
              </tr>
              <span class="likes">
                <AlbumLikes :likedAlbums="likedAlbums" :album="album" :selectedAlbum="selectedAlbum" />
              </span>
            </table>
          </b-card-text>
        </b-col>
      </div>
      <div v-if="!$view.mobile">
      <div v-if="album.id == selectedAlbum">
        <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id">
          <img class="spotify-icon" width="21px" :src="spotifyLogoURLWhite" />
        </a>
      </div>
      <div v-else>
        <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id">
          <img class="spotify-icon" width="21px" :src="spotifyLogoURLBlack" />
        </a>
      </div>
    </div>
    </b-card>
  </div>
</template>


<script>
import { staticURL } from "@/main.js";
import AlbumLikes from "./AlbumLikes.vue";
import { msToHMS } from "@/HelperFunctions.js";

export default {
  components: {
    AlbumLikes,
  },
  name: "SmallAlbum",
  props: {
    albums: Array,
    selectedAlbum: String,
    likedAlbums: Array,
  },
  data() {
    return {
      showCover: false,
      spotifyLogoURLWhite: staticURL + "/assets/Spotify_Icon_RGB_White.png",
      spotifyLogoURLBlack: staticURL + "/assets/Spotify_Icon_RGB_Black.png",
    };
  },
  computed: {
    showAlbum() {
      if (this.showCover) {
        const imageWidth = this.$refs[this.showCover][0].width;
        if (imageWidth == 0) {
          return false;
        }
        document.documentElement.style.setProperty("--imagewidth", imageWidth + 'px');
        return this.showCover;
      } else {
        return false;
      }
    }
  },
  methods: {
    fullOrExerpt(bool){ // add to albums list
      return bool ? "" : "(Excerpt)"
    },
    timeDisplay(milliseconds) {
      return msToHMS(milliseconds);
    },
    durationAlt(ms) {
      let seconds = Math.floor(ms / 1000);
      let hours = Math.floor(seconds / 3600);
      seconds = seconds - (hours * 3600);
      let minutes = Math.round(seconds / 60);

      if (hours > 1) {
        return hours + "h" + minutes + "m";
      } else {
        return minutes + "m"
      }
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
  },
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.15s;
}

.fade-enter {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}

.td-style-black {
  color: black;
}

.td-style-grey {
  color: grey;
}

.likes {
  position: relative;
  bottom: -2px;
}

.album-major-artists {
  color: black;
  font-weight: 600;
  font-size: 14px;
}

.album-major-artists2 {
  color: gray;
  font-weight: 600;
  font-size: 14px;
}

.album-minor-artists {
  color: gray;
  font-size: 12px;
}

.reveal {
  visibility: visible !important;
}

.popup {
  visibility: hidden;
  max-width: calc(var(--imagewidth));
  line-height: 16px;
  padding: 0px;
  position: fixed;
  top: calc(50% + 22.1px);
  left: 33%;
  transform: translate(-50%, -50%);
  box-shadow: rgba(0, 0, 0, 0.25) 0px 54px 55px, rgba(0, 0, 0, 0.12) 0px -12px 30px, rgba(0, 0, 0, 0.12) 0px 4px 6px, rgba(0, 0, 0, 0.17) 0px 12px 13px, rgba(0, 0, 0, 0.09) 0px -3px 5px;
  background-color: var(--dark-gray);
  z-index: 9999;
}

.popup>>>.album-major-artists {
  color: var(--my-white) !important;
}

.popup>>>.album-minor-artists {
  color: var(--medium-light-gray) !important;
}

.album-cover {
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
  max-height: calc(80vh - var(--workingheight));
  max-width: 50vw;
}

.image-caption {
  visibility: inherit;
  width: 100%;
  padding-top: 8.5px;
  padding-bottom: 10px;
  padding-left: 10px;
  padding-right: 10px;
}

.album-img-small {
  border-top-left-radius: 0.25rem;
  border-bottom-left-radius: 0.25rem;
  width: var(--album-size);
  height: 100%;
  min-height: var(--album-size);
  object-fit: cover;
}

.spotify-icon {
  position: absolute;
  right: 5px;
  bottom: 5px;
}

.badge-dark {
  background: none;
}

.card {
  width: 100%;
}

.label {
  font-size: 12px;
}

.gray {
  color: gray;
}

.narrow {
  font-family: Roboto Condensed !important;
}

tr {
  border-bottom: 0px;
}

table {
  width: 100%;
  border-collapse: separate;
  padding: 0px;
  padding-right: 5px;
  padding-top: 0px;
  padding-left: 0px;
  padding-bottom: 0px;
  font-size: 13px !important;
  line-height: 100%;
}
.wrap-text {
  color: gray;
  display: -webkit-box;
  -webkit-line-clamp: var(--line-clamp);
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}

header.card-header {
  background-color: var(--my-white);
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}

.card {
  background-color: var(--my-white);
  border: none;
  margin-top: 5px;
}

.card:hover {
  cursor: pointer;
}

.highlight .selected {
  color: var(--my-white) !important;
}

.highlight .label {
  color: var(--my-white) !important;
}

.album_columns {
  padding-right: 3px;
}

.album_text_columns {
  padding-left: 4px;
  padding-top: 4px;
  padding-bottom: 4px;
}

.row {
  display: flex;
  justify-content: center;
  align-items: center;
}

 .duration-badge{
  font-size: 10px;
  font-family: Roboto Condensed !important;
  color: var(--light-gray) !important;
  vertical-align: 0.5px;
}

>>>.badge {
  margin-bottom: 0px !important;
}
</style>
