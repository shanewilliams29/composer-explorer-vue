<template>
  <div v-if="albums">
  <div class ="row">
    <div class="text-center" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <b-card-group deck v-show="!loading">
      <b-card v-for="(album, index) in albums" :key="index" no-body header-tag="header">
        <div class ="row">
        <b-col class="album_columns" cols="2"><b-avatar square size="48px" :src="album.album_img"></b-avatar></b-col>
        <b-col class="album_text_columns" >
        <b-card-text>
        <table cellspacing="0">
          <tr>
            <td width="100%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a onclick='' style="cursor: pointer; color:black; font-weight: 600;">{{ album.artists }} ({{ album.release_date }})</a></td>
          </tr>
          <tr>
            <td width="100%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a onclick='' style="cursor: pointer; color:grey; font-style: italic;">{{ album.minor_artists }}</a></td>
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
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      albums: [],
      loading: false
    };
  },
  methods: {
    getAlbums(id) {
      this.loading = true;
      const path = 'http://localhost:5000/api/albums/' + id;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.albums;
          this.loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
  },
  created() {
    this.getAlbums('BEETHOVEN00005');
      eventBus.$on('fireAlbums', (work_id) => {
            this.getAlbums(work_id);
    })
  },
};
</script>


<style scoped>
td{
   padding: 1px;
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
   padding: 6px;
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
