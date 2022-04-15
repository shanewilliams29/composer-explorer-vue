<template>
<div id="carouselExampleIndicators" class="carousel slide" data-ride="carousel">
  <ol class="carousel-indicators">
    <li data-target="carouselExampleIndicators" :class="{'active': (strFix(track[0]) == selectedTrack)}" :data-slide-to="strFix(track[0])" v-for="track in album.tracks" :key="strFix(track[0])" @click="playTracks(track[2])"></li>
  </ol>
  <div class="carousel-inner">
    <div class="carousel-item" :class="{'active': (strFix(track[0]) == selectedTrack)}" v-for="track in album.tracks" :key="strFix(track[0])">
    <table>
      <tr>
        <td width="100%"
            style="
              white-space: nowrap;
              text-overflow: ellipsis;
              overflow: hidden;
              max-width: 1px;
            ">
            {{ track[0].substring(track[0].lastIndexOf(':') + 1) }}
        </td>
      </tr>
    </table>
    </div>
    <div class="carousel-item">
      Test 2
    </div>
    <div class="carousel-item">
      Test 3
    </div>
  </div>
  <a class="carousel-control-prev" @click="previousTrack()" role="button" data-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="carousel-control-next" @click="nextTrack()" role="button" data-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a>
</div>
</template>

<script>
import {eventBus} from "../../main.js";
import spotify from '@/SpotifyFunctions.js'
import {currentConfig} from "../../main.js";

export default {
  data() {
    return {
      album: [],
      title: "",
      selectedTrack: "",
      selectedTrackNo : "",
      numTracks: "",
      slide: 0,
      sliding: null
    };
  },
  methods: {
    strFix(item){
      let fixed = item.replace(/[^A-Z0-9]+/ig, "");
      return fixed;
    },
    selectTrack(track){
        this.selectedTrack = this.strFix(track);
        //console.log(this.selectedTrack);
    },
    previousTrack(){
        spotify.previousTrack(window.token);
    },
    nextTrack(){
        spotify.nextTrack(window.token);
    },
    playTracks(tracks){
      let uriList = {}
      let jsonList = {}
      currentConfig.playTracks = tracks;
      localStorage.setItem('currentConfig', JSON.stringify(currentConfig));

      uriList['uris'] = tracks.split(' ');
      jsonList = JSON.stringify(uriList);
      spotify.playTracks(window.token, window.device_id, jsonList);
      // this.selectedTrackNo = this.numTracks - uriList['uris'].length;
      },
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.album = album;
        // console.log(album.tracks[0][0])
        this.selectTrack(album.tracks[0][0]);
        if(window.token && window.device_id){
          this.playTracks(album.tracks[0][2]);
        }
        // this.numTracks = album.tracks.length;
        // this.selectedTrackNo = 0;
    })
    // eventBus.$on('fireNextTrack', () => {
    //     if (this.selectedTrackNo < this.numTracks - 1) {
    //       this.selectedTrackNo = this.selectedTrackNo + 1
    //       this.selectTrack(this.album.tracks[this.selectedTrackNo][1]);
    //     }
    //     else{
    //       eventBus.$emit('fireSetAlbum', this.album);
    //     }

    // })
    // eslint-disable-next-line
    eventBus.$on('firePlayerStateChanged', (track_data, position, duration, paused) => {
        this.selectTrack(track_data['name']);
        //console.log(this.selectedTrack);
    })
  },
};
</script>

<style scoped>
table{
  width: 100%;
  margin-top: 10px;
  margin-bottom: 5px;
}
td{
  color: white;
  padding-left: 50px;
  padding-right: 50px;
  text-align: center;
  vertical-align: middle;
}
.carousel-inner{
  width:100%;
  height: 50px !important;
  background-color: #343a40;
}
.carousel-item{
  text-align: center;
}
  .carousel-item{
        transition: -webkit-transform .6s ease;
        transition: transform .6s ease;
        transition: transform .6s ease,-webkit-transform .6s ease;
    }
.carousel-indicators li{
  border-bottom-width: 7px;
  opacity: 0.25;
}

li.active {
  opacity: 1 !important;
}

.track-card {
  background-color: #343a40 !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  margin-top: 3px;
  margin-bottom: 3px;
  padding-left: 10px;
  right: 3px;
  height: 94px;
}
.track-table {
  width: 100%;
  font-size: 12px;
  line-height: 120%;
}
.track-card-text {
  padding-top: 6px;
  padding-bottom: 6px;
  padding-right: 10px;
}
.track-row:hover {
  cursor: pointer;
}
.highlight-track {
  color: #1db954;
}
.carousel-indicators{
  margin-bottom: 0px !important;
}
.carousel-caption p{
  margin:  0px !important;
}
</style>
