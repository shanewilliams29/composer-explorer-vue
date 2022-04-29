<template>
  <div>
    <b-card v-for="album in albums" :key="album.id" :id="album.id" no-body header-tag="header" @click="$parent.selectRow(album.id); $parent.getAlbumData(album.id);" :class="{'highlight': (album.id == selectedAlbum)}">
      <div class="row">
        <b-col class="album_columns">
          <img rounded="left" width="65px" height="65px" v-lazy="album.album_img" />
        </b-col>
        <b-col class="album_text_columns">
          <b-card-text>
            <table cellspacing="0">
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span style="color: black; font-weight: 600;">{{ album.artists }} </span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span>℗ {{ album.release_date }}</span>
                  <span v-if="album.likes">&nbsp;
                    <b-badge v-if="parseInt(album.likes) == 1 ">{{ album.likes }} Like</b-badge>
                    <b-badge v-if="parseInt(album.likes) > 1 ">{{ album.likes }} Likes</b-badge>
                  </span>
                </td>
              </tr>
              <tr>
                <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                  <span style="color: grey; font-style: italic;">{{ album.minor_artists }}</span>
                </td>
              </tr>
            </table>
          </b-card-text>
        </b-col>
      </div>
    </b-card>
  </div>
</template>

<script>
export default {
  name: 'SmallAlbum',
  props: {
    albums: Array,
    selectedAlbum: String
  }
}
</script>

<style scoped>
.badge-dark {
  background: none;
}
.card {
  width: 100%;
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
  padding-top: 3px;
  padding-left: 2px;
  padding-bottom: 2px;
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
  background-color: royalblue !important;
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
  background-color: #707479;
  margin-bottom: 2.5px;
  border-radius: 7px;
}
.highlight .badge {
  color: #007bff !important;
  background-color: #fff;
}
</style>

<!-- <style>
.last-col{
  -ms-flex: 0 0 33.3% !important;
  flex: 0 0 33.3% !important;
}
</style> -->
