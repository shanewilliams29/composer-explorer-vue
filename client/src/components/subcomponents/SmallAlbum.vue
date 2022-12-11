<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" :class="{'highlight': (album.id == selectedAlbum)}" @mouseover="showCover = album.id" @mouseleave="showCover = false">
      <div class="popup" v-if="showCover == album.id">
        <img :src="album.img_big" />
      </div>
      <div class="row">
        <b-col cols="auto" class="album_columns">
          <img class="album-img-small" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);" v-lazy="album.album_img"/>
        </b-col>
        <b-col class="album_text_columns">
          <b-card-text>
            <table cellspacing="0" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);">
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span style="color: black; font-weight: 600; font-size: 13px;">{{ album.artists }} </span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span v-if="album.minor_artists" style="color: gray; font-size: 12px;">{{ album.minor_artists }}</span>
                  <span v-else><br /></span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span class="album-likes-class"> <AlbumLikes v-bind:likedAlbums="likedAlbums" v-bind:album="album" v-bind:selectedAlbum="selectedAlbum" /></span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;"><span class="label">℗ {{ album.release_date }}</span><span class="label"> · {{ album.label }}</span></td>
              </tr>
            </table>
            <div v-if="album.id == selectedAlbum">
              <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><img class="spotify-icon" width="21px" :src="spotifyLogoURLWhite" /></a>
            </div>
            <div v-else>
              <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><img class="spotify-icon" width="21px" :src="spotifyLogoURLBlack" /></a>
            </div>
          </b-card-text>
        </b-col>
      </div>
    </b-card>
  </div>
</template>

<script>
import { staticURL } from "@/main.js";
import AlbumLikes from "@/components/subcomponents/AlbumLikes.vue";

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
};
</script>

<style scoped>
.popup{
  position: fixed; 
  top: 50%; 
  left: 33%; 
  transform: translate(-50%, -50%);
  z-index: 9999;
  box-shadow: rgba(0, 0, 0, 0.25) 0px 54px 55px, rgba(0, 0, 0, 0.12) 0px -12px 30px, rgba(0, 0, 0, 0.12) 0px 4px 6px, rgba(0, 0, 0, 0.17) 0px 12px 13px, rgba(0, 0, 0, 0.09) 0px -3px 5px;
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
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.card {
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card:hover {
  cursor: pointer;
}
.highlight {
  color: white !important;
}
.highlight span {
  color: white !important;
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
