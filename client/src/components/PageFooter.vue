<template>
  <div class="container-fluid">
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
                      <span style="font-style: italic; font-weight: bold; color:#a4a7a9;">{{album.artists}} ({{album.release_date}})</span>
                      <span style="font-style: italic; color:#a4a7a9;">{{album.minor_artists}}</span>
                    </div>
                  </b-card-text>
                </b-card-body>
              </b-col>
            </b-row>
          </b-card>
        </b-col>
        <b-col></b-col>
        <b-col>

    <b-card-group deck v-show="!loading">
      <b-card no-body class="track-card">
        <b-card-text class="track-card-text">
          <div class="centered-tracks">
        <table class="track-table" cellspacing="0">
          <tr class="track-row" v-for="track in album.tracks" :key="track[1]" @click="selectTrack(track[1]);" :class="{'highlight-track': (track[1] == selectedTrack)}">
            <td width="100%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;">▶&nbsp; {{ track[0].substring(track[0].indexOf(':') + 1) }}</td>
          </tr>
        </table>
      </div>
        </b-card-text>
      </b-card>
    </b-card-group>


        </b-col>
      </b-row>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      album: [],
      title: "",
      selectedTrack: ""
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
    selectTrack(track){
        this.selectedTrack = track;
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
    background-color: #343a40;
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
  padding-left: 8px;
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
.track-card{
  background-color: #484e53 !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  margin-top: 3px;
  margin-bottom: 3px;
  padding-left: 10px;
  right: 3px;
  height: 94px;
}
.track-table{
  width: 100%;
  font-size: 12px;
}
.track-card-text{
  padding-top: 6px;
  padding-bottom: 6px;
  padding-right: 10px;
}
.track-row:hover {
  cursor: pointer;
}
.highlight-track{
  color: #1DB954;
}
.col{
  padding:  0px;
}
</style>
