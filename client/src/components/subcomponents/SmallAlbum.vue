<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" :class="{'highlight': (album.id == selectedAlbum)}">
      <div class="row">
        <b-col class="album_columns">
          <img @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);" rounded="left" width="65px" height="65px" v-lazy="album.album_img" />
        </b-col>
        <b-col class="album_text_columns">
          <b-card-text>
            <table cellspacing="0" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);">
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span style="color: black; font-weight: 600;">{{ album.artists }} </span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span v-if="album.minor_artists" style="color: gray; font-size: 12px;">{{ album.minor_artists }}</span>
                  <span v-else><br></span>
                </td>
              </tr>
              <tr>
             <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <AlbumLikes v-bind:likedAlbums="likedAlbums" v-bind:album="album" v-bind:selectedAlbum="selectedAlbum"/>
                  <span class="label">℗ {{ album.release_date }}</span><span class="label"> · {{ album.label }}</span>
                </td>
              </tr>
            </table>
            <div v-if="album.id == selectedAlbum">
             <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><img class="spotify-icon" width=21px :src="spotifyLogoURLWhite" /></a>
            </div>
            <div v-else>
              <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><img class="spotify-icon" width=21px :src="spotifyLogoURLBlack" /></a>
            </div>
          </b-card-text>
        </b-col>
      </div>
    </b-card>
  </div>
</template>

<script>
import {staticURL} from "@/main.js";
import AlbumLikes from '@/components/subcomponents/AlbumLikes.vue';

export default {
  components: {
    AlbumLikes
  },
  name: 'SmallAlbum',
  props: {
    albums: Array,
    selectedAlbum: String,
    likedAlbums: Array
  },
  data() {
    return {
      spotifyLogoURLWhite: staticURL + 'Spotify_Icon_RGB_White.png',
      spotifyLogoURLBlack: staticURL + 'Spotify_Icon_RGB_Black.png',
    }
  }
}
</script>

<style scoped>
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
  position:relative;
  top: -2px;
}
.gray{
  color: gray;
}
td {
  padding: 0px;
  vertical-align: bottom;
  /*   border-top: 1px dotted lightgray;*/
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  font-size: 13px;
  padding: 0px;
  padding-right: 5px;
  padding-top: 5px;
  padding-left: 2px;
  padding-bottom: 0px;
  line-height: 110%;
}
header.card-header {
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0 {
  font-size: 12px;
  font-weight: bold;
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
/*  background-color: rgb(52, 58, 64, 0.7) !important;*/
  color: white !important;
}
.highlight span {
  color: white !important;
}
.badge {
  color: #fff;
  background-color: #777777;
  border-radius: 7px;
}
.album_columns {
  padding-right: 5px;
  -ms-flex: 0 0 65px;
  flex: 0 0 65px;
}
.album_text_columns {
  padding-left: 0px;
}
.badge {
  vertical-align: middle;
  color: #fff !important;
  background-color: darkgoldenrod;
  margin-bottom: 2.5px;
  border-radius: 7px;
}
.highlight .badge {
  color: #000 !important;
  background-color: #fff;
}
</style>
