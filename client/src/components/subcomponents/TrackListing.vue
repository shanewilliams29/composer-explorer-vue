<template>
  <b-card-group deck>
    <b-card no-body class="track-card">
      <b-card-text class="track-card-text">
        <div class="centered-tracks">
          <table class="track-table" cellspacing="0">
            <tr
              class="track-row"
              v-for="track in album.tracks"
              :key="track[1]"
              @click="selectTrack(track); playTracks(track[2]); "
              :class="{'highlight-track': trackMatch(track)}"
            >
              <td
                width="100%"
                style="
                  white-space: nowrap;
                  text-overflow: ellipsis;
                  overflow: hidden;
                  max-width: 1px;
                "
              >
                  <!-- {{ track[0] }} vs {{ selectedTrack }} -->
              ▶&nbsp; {{ track[0].substring(track[0].lastIndexOf(':') + 1) }}
              </td>
            </tr>
          </table>
        </div>
      </b-card-text>
    </b-card>
  </b-card-group>
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
      selectedTrack: "Track",
      selectedTrackNo : "",
      numTracks: "",
      stopMatch: false // necessary in case album has multiple tracks with the same name (would select them all)
    };
  },
  methods: {
    strFix(item){
      let fixed = item.replace(/[^A-Z0-9]+/ig, "");
      return fixed;
    },
    selectTrack(track){
        this.selectedTrack = track;
    },
    trackMatch(track){

        // match on IDs
        if (this.selectedTrack[1] == track[1]){
            this.stopMatch = true;
            return true;

        //match on name
        } else if (this.strFix(this.selectedTrack[0]) == this.strFix(track[0]) && this.stopMatch == false){
            this.stopMatch = false;
            return true;
        } else {
            return false;
        }
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
      //console.log(album.id);
        this.album = album;
        if(window.token && window.device_id){
          this.playTracks(album.tracks[0][2]);
          this.stopMatch = false;
        }
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
        let track = []
        track[1] = track_data['id'];
        track[0] = track_data['name'];
        this.selectTrack(track);
        this.stopMatch = false;
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
  border-radius: 3px !important;
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
