<template>
  <div>
    <b-card 
      class="shadow-sm" 
      v-for="album in albums" 
      :key="album.id" 
      :id="album.id" 
      no-body 
      header-tag="header" 
      :class="{'highlight': (album.id == selectedAlbum)}">
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
      <div class="row" @mouseover="showCover = album.id" @mouseleave="showCover = false">
        <b-col cols="auto" class="album_columns">
          <img class="album-img-small" 
            @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);" 
            v-lazy="album.img_big" />
        </b-col>
        <b-col class="album_text_columns">
          <b-card-text>
            <table cellspacing="0" 
              @click="$emit('selectAlbum', album.id); $emit('getAlbum', album.id);">
              <tr>
                <td width="100%" class="td-style">
                  <span class="album-major-artists selected">
                    {{ album.artists }}
                  </span>
                </td>
              </tr>
              <tr>
                <td width="100%" class="td-style">
                  <span v-if="album.minor_artists" class="album-minor-artists selected">
                    {{ album.minor_artists }}
                  </span>
                  <span v-else><br /></span>
                </td>
              </tr>
              <tr>
                <td width="100%" class="td-style">
                  <span class="album-likes-class">
                    <AlbumLikes 
                      :likedAlbums="likedAlbums" 
                      :album="album" 
                      :selectedAlbum="selectedAlbum" />
                  </span>
                </td>
              </tr>
              <tr>
                <td width="100%" class="td-style">
                  <span class="label">℗ {{ album.release_date }}</span>
                  <span class="label"> · {{ album.label }}</span>
                  <span v-if="album.duration" class="label"> · {{ timeDisplay(album.duration) }}</span>
                </td>
              </tr>
            </table>
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
          </b-card-text>
        </b-col>
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
      spotifyLogoURLWhite: staticURL + "Spotify_Icon_RGB_White.png",
      spotifyLogoURLBlack: staticURL + "Spotify_Icon_RGB_Black.png",
    };
  },
  computed: {
    showAlbum() {
      if(this.showCover){
        const imageWidth = this.$refs[this.showCover][0].width;
        if (imageWidth == 0){
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
    timeDisplay(milliseconds) {
      return msToHMS(milliseconds);
    },
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.15s;
}
.fade-enter{
  opacity: 0;
}
.fade-leave-to {
  opacity: 0;
}
.td-style{
  white-space: nowrap; 
  text-overflow: ellipsis; 
  overflow: hidden; 
  max-width: 1px;
}
.album-major-artists{
  color: black; 
  font-weight: 600; 
  font-size: 13px;
}
.album-minor-artists{
  color: gray; 
  font-size: 12px;
}
.reveal{
  visibility: visible !important;
}
.popup{
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
.popup >>> .album-major-artists {
  color: var(--my-white) !important;
}
.popup >>> .album-minor-artists {
  color: var(--medium-light-gray) !important;
}
.album-cover {
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
  max-height: calc(80vh - var(--workingheight));
  max-width: 50vw;
}
.image-caption{
  visibility: inherit;
  width: 100%;
  padding-top: 8.5px;
  padding-bottom: 10px;
  padding-left: 10px;
  padding-right: 10px;
}
.album-img-small{
  border-top-left-radius: 0.25rem;
  border-bottom-left-radius: 0.25rem;
  width: 72px; 
  height: 100%;
}
.spotify-icon{
  position: absolute;
  right: 20px;
  bottom: 5px;
}
.badge-dark {
  background: none;
}
.card {
  width: 100%;
}
.label{
  font-size: 10px;
}
.gray{
  color: gray;
}
td {
  padding: 0px;
  height: 17px !important;
  vertical-align: middle;
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  padding: 0px;
  padding-right: 5px;
  padding-top: 3px;
  padding-left: 2px;
  padding-bottom: 0px;
  font-size: 14px !important;
  line-height: 120%;
  height: 70px;
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
.highlight .selected{
  color: var(--my-white) !important;
}
.highlight .label {
  color: var(--my-white) !important;
}
.album_columns {
  padding-right: 3px;
}
.album_text_columns {
  padding-left: 0px;
}
>>> .badge {
  margin-bottom: 0px !important;
}
</style>
