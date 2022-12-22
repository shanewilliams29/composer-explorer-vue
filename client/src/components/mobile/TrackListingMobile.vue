<template>
  <b-card no-body class="track-info-card shadow-sm">
    <b-card-text class="info-card-text-tracks" ref="scroll-box">
      <table>
        <tr v-for="(track, index) in album.tracks" 
          @click="selectTrack(track); playTracks(track[2]);" 
          :class="{'highlight-track': trackMatch(track)}" 
          :id="track[1]" 
          :key="track[1]">
          <td>
            <b-avatar v-if="trackMatch(track)" variant="warning" size="40px" :text="(index + 1).toString()">
            </b-avatar>
            <b-avatar v-if="!trackMatch(track)" size="40px" :text="(index + 1).toString()">
            </b-avatar>
          </td>
          <td class="info-td">
            <a clss="artist-name">
              <span v-if="genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'">
                {{ track[0].substring(track[0].lastIndexOf(' Act ') + 1).trim() }}</span>
              <span v-else>
                {{ track[0].substring(track[0].lastIndexOf(':') + 1) }}
              </span>
            </a>
            <br />
          </td>
        </tr>
      </table>
    </b-card-text>
  </b-card>
</template>

<script>
import {eventBus} from "@/main.js";
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
  computed:{
    panelShow(){
      return this.$view.panelVisible;
    }
  },
  watch: {
    panelShow(panelState) {
      if (panelState == true){
        this.selectTrack(this.selectedTrack);
      }
    }
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
      }
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.genre = this.$config.genre;
        this.album = album;
    })
    // eslint-disable-next-line
    eventBus.$on('firePlayerStateChanged', (track_data, position, duration, paused) => {
        let track = []
        track[1] = track_data['id'];
        track[0] = track_data['name'];
        this.selectTrack(track);
        this.stopMatch = false;
    })
  }
};
</script>

<style scoped>
td {
  padding-bottom: 5px;
}
a {
  color: black;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  cursor: pointer;
}
.heading-tr {
  vertical-align: middle;
  height: 62px !important;
}
.heading-td {
  padding-left: 10px;
  font-size: 16px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: var(--dark-gray);
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.track-info-card {
  padding: 15px;
  padding-top: 15px !important;
  padding-bottom: 10px;
  background-color: 343a40 !important;
  border: none !important;
}
.info-td {
  padding-left: 10px;
}
.highlight-track {
  color: var(--yellow) !important;
}
.disclaimer {
  margin-bottom: 11px;
}
.card-title {
  font-size: 16px;
  height: 62px;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}

.info-card-text-tracks {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: auto;
  padding-left: 2px;
}
table {
  margin-bottom: 6px;
}
.wiki-link {
  font-style: italic;
  color: grey;
}
.open-in-spotify {
  font-size: 12px;
}
.spotify-logo {
  width: auto;
  height: 20px;
}

/*scrollbars*/
.info-card-text-tracks {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--my-white);
}

.info-card-text-tracks {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
.info-card-text-tracks::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.info-card-text-tracks::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}

.info-card-text-tracks::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}


</style>

<!-- <style scoped>
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
  color: var(--medium-light-gray);
  padding-top: 6px;
  padding-bottom: 0px;
  padding-right: 10px;
}
.track-row:hover {
  cursor: pointer;
  color: var(--my-white);
}
.highlight-track {
  color: #ffc107 !important;
}

/*scrollbars*/
 .track-card {
        --scroll-bar-color: var(--medium-light-gray);
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
</style> -->
