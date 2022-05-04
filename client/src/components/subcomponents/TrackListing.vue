<template>
  <b-card-group deck>
    <b-card no-body class="track-card" ref="scroll-box">
      <b-card-text class="track-card-text">
        <div class="centered-tracks">
          <table class="track-table" cellspacing="0">
            <tr
              class="track-row"
              v-for="track in album.tracks"
              :id="track[1]"
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
              <b-icon icon="play-fill" aria-hidden="true"></b-icon>
              <span v-if="genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'">{{ track[0].substring(track[0].lastIndexOf(' Act ') + 1).trim() }}</span>
              <span v-else>{{ track[0].substring(track[0].lastIndexOf(':') + 1) }}</span>
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
      selectedTrack: "Track",
      selectedTrackNo : "",
      numTracks: "",
      genre: "",
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
        var trackId = track[1];
        var element = document.getElementById(trackId);
        var top = element.offsetTop;
        this.$refs['scroll-box'].scrollTo({
                                  top: top,
                                  left: 0,
                                  behavior: 'smooth'
                                });
    },
    trackMatch(track){
        // match on IDs
        if (this.selectedTrack[1] == track[1]){
            this.stopMatch = true;
            return true;

        //match on name if IDs are not valid (Spotify redirected track for licensing purposes)
        } else if (this.strFix(this.selectedTrack[0]) == this.strFix(track[0]) && this.stopMatch == false){
            return true;
        } else {
            return false;
        }
    },
    playTracks(tracks){
      let uriList = {}
      let jsonList = {}
      let selectedTrack = tracks.split(' ')[0];
      let allTracks = this.$config.allTracks.split(' ');

      let index = allTracks.indexOf(selectedTrack);
      let previousTracks = "";

      if (index == 0) {
          previousTracks = this.$config.allTracks;
      } else {
        for (var i = index - 1; i < allTracks.length; i++) {
          previousTracks = previousTracks + " " + allTracks[i];
        }
      }
      this.$config.previousTracks = previousTracks.trim();
      this.$config.playTracks = tracks;
      localStorage.setItem('config', JSON.stringify(this.$config));

      // ensure unnecessary whitespace in track list (gives spotify erors):
      var smushTracks = tracks.replace(/\s/g,'');
      var cleanTracks = smushTracks.replaceAll('spotify', ' spotify').trim();

      uriList['uris'] = cleanTracks.split(' ');
      jsonList = JSON.stringify(uriList);
      spotify.playTracks(this.$auth.clientToken, this.$auth.deviceID, jsonList);
      // this.selectedTrackNo = this.numTracks - uriList['uris'].length;
      },
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.genre = this.$config.genre;
        this.$config.allTracks = album.tracks[0][2];
        this.$config.playTracks = album.tracks[0][2];
        localStorage.setItem('config', JSON.stringify(this.$config));

        this.album = album;
        if(this.$auth.clientToken && this.$auth.deviceID && !window.firstLoad){
          this.playTracks(album.tracks[0][2]);
          this.stopMatch = false;
        } else {
          window.firstLoad = false;
        }
    })
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
  background-color: #454d54 !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  margin-right: 12px !important;
  margin-left: 20px !important;
  padding-left: 6px;
  right: 3px;
  height: 100px;
  border-radius: 0px !important;
}
.track-table {
  width: 100%;
  font-size: 13px;
  line-height: 155%;
}
.track-card-text {
  color: lightgray;
  padding-top: 6px;
  padding-bottom: 0px;
  padding-right: 10px;
}
.track-row:hover {
  cursor: pointer;
  color: white;
}
.highlight-track {
  color: #ffc107 !important;
}

/*scrollbars*/
 .track-card {
        --scroll-bar-color: lightgray;
        --scroll-bar-bg-color: #454d54;
    }

    .track-card{
        scrollbar-width: thin;
        scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
    }

    /* Works on Chrome, Edge, and Safari */
    .track-card::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .track-card::-webkit-scrollbar-track {
        background: var(--scroll-bar-bg-color) !important;
    }

    .track-card::-webkit-scrollbar-thumb {
        background-color: var(--scroll-bar-color);
        border-radius: 20px;
        border: 3px solid var(--scroll-bar-bg-color)!important;
    }

</style>
