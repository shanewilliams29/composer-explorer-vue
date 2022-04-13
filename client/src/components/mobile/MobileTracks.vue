<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col>
        Test
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {eventBus} from "../../main.js";
import spotify from '@/SpotifyFunctions.js'

export default {
  data() {
    return {
      album: [],
      title: "",
      selectedTrack: "",
      selectedTrackNo : "",
      numTracks: ""
    };
  },
  methods: {
    selectTrack(track){
        this.selectedTrack = track;
    },
    playTracks(tracks){
      let uriList = {}
      let jsonList = {}
      uriList['uris'] = tracks.split(' ');
      jsonList = JSON.stringify(uriList);
      spotify.playTracks(window.token, window.device_id, jsonList);
      // this.selectedTrackNo = this.numTracks - uriList['uris'].length;
      },
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.album = album;
        this.playTracks(album.tracks[0][2]);
        // this.selectTrack(album.tracks[0][1]);
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
        this.selectedTrack = track_data['id'];
    })
  },
};
</script>

<style scoped>
.track-card {
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
</style>
