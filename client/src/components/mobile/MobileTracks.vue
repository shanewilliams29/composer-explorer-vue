<template>
  <div id="carouselExampleIndicators" class="carousel slide" data-ride="carousel">
    <ol class="carousel-indicators" v-if="album.id">
      <li data-target="carouselExampleIndicators" :class="{'active': trackMatch(track)}" :data-slide-to="track[1]" v-for="track in album.tracks" :key="track[1]" @click="playTracks(track[2])" v-show="album.tracks.length <= 12"></li>
      <span class="album-track-display" v-show="album.tracks.length > 12 && trackIndex">Track {{trackIndex}} of {{album.tracks.length}}</span>
    </ol>
    <ol class="carousel-indicators" v-else>
      <!-- Dummy while loading -->
    </ol>
    <div class="carousel-inner">
      <div class="carousel-item" :class="{'active': trackMatch(track)}" v-for="track in album.tracks" :key="track[1]">
        <table>
          <tr>
            <td width="100%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
              <span v-if="genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'">{{ track[0].substring(track[0].lastIndexOf(' Act ') + 1).trim() }}</span>
              <span v-else>{{ track[0].substring(track[0].lastIndexOf(':') + 1) }}</span>
            </td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import {eventBus} from "@/main.js";
import spotify from '@/SpotifyFunctions.js'

export default {
  data() {
    return {
      album: {},
      title: "",
      genre:"",
      selectedTrack: "Track",
      selectedTrackNo : "",
      numTracks: "",
      loading: true,
      slide: 0,
      sliding: null,
      stopMatch: false // necessary in case album has multiple tracks with the same name (would select them all)
    };
  },
  computed: {
    trackIndex() {
      var tracks = this.album.tracks;

      for (var i = 0; i < tracks.length; i++) {
        var matchTrack = tracks[i][1];
        // console.log(matchTrack);
        // console.log(this.selectedTrack[1]);
        if (matchTrack == this.selectedTrack[1]){
          return i + 1;
        } else {
          continue;
        }
      }
      return null;
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

        //match on name
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

      uriList['uris'] = tracks.split(' ');
      jsonList = JSON.stringify(uriList);

      spotify.playTracks(this.$auth.clientToken, this.$auth.deviceID, jsonList);
      },
    },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.$config.allTracks = album.tracks[0][2];
        this.$config.playTracks = album.tracks[0][2];
        localStorage.setItem('config', JSON.stringify(this.$config));
        this.genre = this.$config.genre;
        this.album = album;
        this.title = this.$config.workTitle;
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
table{
  width: 100%;
  margin-top: 17px;
  margin-bottom: 5px;
}
td{
  color: var(--my-white);
  padding-left: 50px;
  padding-right: 50px;
  text-align: center;
  vertical-align: middle;
}
.album-track-display{
  color: var(--medium-light-gray);
  font-size: 14px;
}
.carousel{
  border-top: solid 2px var(--medium-gray) !important;
}
.carousel-inner{
  width:100%;
  height: 60px !important;
  background: none;
}
.carousel-item{
  text-align: center;
}
.carousel-item{
        transition: -webkit-transform .6s ease;
        transition: transform .6s ease;
        transition: transform .6s ease,-webkit-transform .6s ease;
  }
.carousel-item >>> span{
  font-size: 16px !important;
}  
.carousel-indicators li{
  border-bottom-width: 7px;
  opacity: 0.25;
}

li.active {
  opacity: 1 !important;
}

.track-card {
  background: !important;
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
