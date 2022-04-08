<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
  <div v-if="albums">
  <div class ="row">
    <b-card-group deck v-show="!loading">
      <b-card v-for="(album, index) in albums" :key="album.album_id" :id="album.album_id" :ref="index" no-body header-tag="header" @click="selectRow(album.album_id); getAlbumData(album.id);" :class="{'highlight': (album.album_id == selectedAlbum)}">
        <div class ="row">
        <b-col class="album_columns" cols="2">
          <b-avatar v-show="album.album_id != selectedAlbum" rounded="left" size="48px" :src="album.album_img"></b-avatar>
          <b-avatar v-show="album.album_id == selectedAlbum" variant="dark" icon="heart" rounded="left" size="48px"></b-avatar></b-col>
        <b-col class="album_text_columns" >
        <b-card-text>
        <table cellspacing="0">
          <tr>
            <td width="100%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a style="color:black; font-weight: 600;">{{ album.artists }} ({{ album.release_date }})</a></td>
          </tr>
          <tr>
            <td width="100%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a style="color:grey; font-style: italic;">{{ album.minor_artists }}</a></td>
          </tr>
        </table>
        </b-card-text>
      </b-col>
    </div>
      </b-card>
    </b-card-group>
  </div>
  </div>
  <div v-else>
    <div class ="row">
    <div class="text-center" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <span class="no-albums-found"><br>No albums found.</span>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      albums: [],
      loading: false,
      selectedAlbum: null
    };
  },
  methods: {
    getAlbums(id) {
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.albums;
          this.loading = false;
          this.selectRow(this.albums[0].album_id); // select first row
          eventBus.$emit('fireAlbumData', this.albums[0].id);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getAlbumData(album_id) {
        eventBus.$emit('fireAlbumData', album_id);
        //this.$refs.composer.selectColor = "blue";
    },
      selectRow(album){
        // console.log(this.$refs["1"][0].id);
        this.selectedAlbum = album;
    },
  },
  created() {
    this.getAlbums('BEETHOVEN00016');
      eventBus.$on('fireAlbums', (work_id) => {
            this.getAlbums(work_id);
    })
  },
  mounted() {
    // this.selectRow('3xjbqYLxvXHuanI63XGwri');
    //this.selectRow(this.$refs["0"][0].id); // selects first album
  },
};
</script>


<style scoped>
.spinner{
  text-align: center;
}
.badge-dark{
  background: none;
}
.m-5{
  color: #343a40;
}
.card-deck{
  display: flex;
  flex-direction: column;
  width: 100%;
}
.card{
  width: 100%;
}
td{
   padding: 0px;
   vertical-align: bottom;
/*   border-top: 1px dotted lightgray;*/
}
tr{
  border-bottom: 0px;
}
table{
   width: 100%;
   border-collapse: separate;
   font-size: 12px;
   padding: 0px;
   padding-top: 7px;
   padding-bottom: 2px;
}
.composer-img{
    border-radius: 50%;
    object-fit: cover;
}
header.card-header{
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0{
  font-size: 12px;
  font-weight: bold;
}
.card{
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card:hover {
  cursor: pointer;
}
.highlight {
  background-color: rgb(52, 58, 64, 0.7) !important;
  color: white !important;
}
.highlight a {
  color: white !important;
}
.card-deck{
  padding-left: 5px;
  padding-right: 5px;
}
.badge{
  color: #fff;
  background-color: #777777;
  border-radius: 7px;
}
.no-albums-found{
  font-size: 14px;
  color: grey;
  text-align: center;
}
.album_columns{
  padding-right: 0px;
}
.album_text_columns{
  padding-left: 0px;
}
</style>
