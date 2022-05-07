<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" :class="{'highlight': (album.id == selectedAlbum)}">
      <div class="row">
        <b-col class="album_columns">
          <div class="album-titles" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);">
            <span style="color: black; font-weight: 600;">{{ album.artists }}</span><br />
            <span>℗ {{ album.release_date }}</span>

            <br />
            <span v-if="album.minor_artists" style="color: grey; font-size: 12px !important;">{{ album.minor_artists }}</span>
          </div>
          <div v-if="album.img_big" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);">
            <img class="album-cover" height="auto" v-lazy="album.img_big" />
          </div>
          <div v-else @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);"><img class="album-cover" height="auto" v-lazy="album.album_img" /></div>
          <div class="row">
          <b-col class="col" cols="4">
           <span class="likes" v-if="album.likes">&nbsp;
              <b-badge v-if="parseInt(album.likes) == 1 ">{{ album.likes }} Like</b-badge>
              <b-badge v-if="parseInt(album.likes) > 1 ">{{ album.likes }} Likes</b-badge>
            </span>
          </b-col>
          <b-col class="col footer" cols="8">
          <div v-if="album.id == selectedAlbum">
          <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><span class="open-in">Open in&nbsp; </span><img class="spotify-logo" width=70px :src="spotifyLogoURLWhite" /></a>
          </div>
          <div v-else>
          <a target="_blank" :href="'https://open.spotify.com/album/' + album.album_id"><img class="spotify-logo" width=70px :src="spotifyLogoURLBlack" /></a>
          </div>
       </b-col>
        </div>
        </b-col>
      </div>
    </b-card>
  </div>
</template>

<script>
import {staticURL} from "@/main.js";
export default {
  name: 'LargeAlbum',
  props: {
    albums: Array,
    selectedAlbum: String
  },
  data() {
    return {
      spotifyLogoURLWhite: staticURL + 'Spotify_Logo_RGB_White.png',
      spotifyLogoURLBlack: staticURL + 'Spotify_Logo_RGB_Black.png',
    }
  }
}
</script>

<style scoped>
  a:hover{
    text-decoration: none;
  }
  .footer{
    text-align: right;
    font-size: 13px;
  }
  .open-in{
    position:relative;
    top: -0.4px;
  }
  .likes{
    position:relative;
    top: -1px;
  }
.spotify-logo{
  padding-bottom: 5px;
  margin-right: 22px;
}
.card {
  width: 100%;
  background-color: #fff;
  border: none;
  margin-top: 5px;
}

.highlight {
  color: white;
}
.highlight span {
  color: white !important;
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
  color: #fff !important;
  background-color: goldenrod;
  margin-bottom: 2.5px;
  border-radius: 7px;
}
.highlight .badge {
  color: #000 !important;
  background-color: #fff;
}
</style>
