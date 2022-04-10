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
              @click="selectTrack(track[1]); playTracks(track[2]); "
              :class="{'highlight-track': (track[1] == selectedTrack)}"
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
                ▶&nbsp; {{ track[0].substring(track[0].indexOf(':') + 1) }}
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

export default {
  data() {
    return {
      album: [],
      title: "",
      selectedTrack: ""
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
      },
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.album = album;
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
