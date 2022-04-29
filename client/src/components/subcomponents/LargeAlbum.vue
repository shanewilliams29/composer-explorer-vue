<template>
  <div>
    <b-card class="shadow-sm" v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);" :class="{'highlight': (album.id == selectedAlbum)}">
      <div class="row">
        <b-col class="album_columns">
          <div class="album-titles">
            <span style="color: black; font-weight: 600;">{{ album.artists }}</span><br />
            <span>℗ {{ album.release_date }}</span>
            <span v-if="album.likes">&nbsp;
              <b-badge v-if="parseInt(album.likes) == 1 ">{{ album.likes }} Like</b-badge>
              <b-badge v-if="parseInt(album.likes) > 1 ">{{ album.likes }} Likes</b-badge>
            </span>
            <br />
            <span v-if="album.minor_artists" style="color: grey; font-size: 12px !important;">{{ album.minor_artists }}</span>
          </div>
          <div v-if="album.img_big">
            <img class="album-cover" height="auto" v-lazy="album.img_big" />
          </div>
          <div v-else><img class="album-cover" height="auto" v-lazy="album.album_img" /></div>
        </b-col>
      </div>
    </b-card>
  </div>
</template>

<script>
export default {
  name: 'LargeAlbum',
  props: {
    albums: Array,
    selectedAlbum: String
  }
}
</script>

<style scoped>
.card {
  width: 100%;
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card:hover {
  cursor: pointer;
}
.highlight {
  background-color: #007bff !important;
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
.album-titles {
  margin-left: 8px;
  margin-top: 6px;
  margin-bottom: 0px;
  margin-right: 20px;
  font-size: 13px;
  line-height: 135%;
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
  background-color: #707479;
  margin-bottom: 2.5px;
  border-radius: 7px;
}
.highlight .badge {
  color: #007bff !important;
  background-color: #fff;
}
</style>
