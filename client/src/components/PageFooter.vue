<template>
<div class="container-fluid">
    <div class="overlay"></div>
    <div class="inner">
      <b-row class="footer-row">
        <b-col class="info-col">
    <div class="text-center" v-show="loading" role="status">
      <b-spinner class="m-4"></b-spinner>
    </div>
  <b-card no-body bg-variant="dark" v-show="!loading">
    <b-row no-gutters>
      <b-col cols="12" md="auto" class="album-cover-col">
        <b-card-img :src="album.album_img" alt="Album Cover" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body>
          <b-card-text>
            <div class="centered">
            <span style="font-weight: bold;">{{title}}</span>
            <span style="font-weight: bold; font-style: italic; color:silver;">{{album.artists}} ({{album.release_date}})</span>
            <span style="font-style: italic; color:darkgray;">{{album.minor_artists}}</span>
            </div>
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
        </b-col>
        <b-col></b-col>
        <b-col></b-col>
      </b-row>
    </div></div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      album: [],
      title: ""
    };
  },
  methods: {
    getAlbumInfo(album_id) {
        this.loading = true;
        this.title = eventBus.title;
        const path = 'http://localhost:5000/api/albuminfo/' + album_id;
        axios.get(path)
          .then((res) => {
            this.album = res.data.album; // Change to local file
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
    eventBus.title = "Piano Concerto No. 5 in E♭ major";
    this.getAlbumInfo("BEETHOVEN000163xjbqYLxvXHuanI63XGwri");
    eventBus.$on('fireAlbumData', (album_id) => {
        this.getAlbumInfo(album_id);
    })
  },
};
</script>

<style scoped>
.container-fluid {
    position: relative;
    background-image: linear-gradient(to bottom left, rgb(52,58,64, 0.9), rgb(52,58,64, 1));
    padding-bottom: 0px;
    border-radius: 0px;
    border-radius: 6px ;

}

.info-col{
  height: 100px;
  overflow-y: hidden;
}
.album-cover-col{
  padding-right: 10px;
}
.card{
  background: none !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  height: 100px;

}
.card-img{
    height: 100%;
    width: auto;
    max-width: 100px;
    max-height: 100px;
}
.card-body {
    font-size: 12px;
    padding-left: 2px;
    margin-right: 6px;
    padding-top: 0px;
    height: 100px;
    overflow-y: hidden;
}
.centered {
    display: flex;
    flex-direction: column;
    column-gap: 0px;
    justify-content: center;
    height: 100px;
}
.footer-row{
  height: 100px;
  color: white;

}
.col{
  padding:  0px;
}
</style>
