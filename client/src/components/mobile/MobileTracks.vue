<template>
  <div id="carouselIndicatorsID" class="carousel slide" data-ride="carousel">
    <ol class="carousel-indicators" v-if="album.id">
      <li data-target="carouselIndicatorsID" 
        :class="{'active': trackMatch(track)}" 
        :data-slide-to="track[1]" 
        v-for="track in album.tracks" 
        :key="track[1]" 
        @click="playTracks(track[2])" 
        v-show="album.tracks.length <= 12">
      </li>
      <span class="album-track-display" 
        v-show="album.tracks.length > 12 && trackIndex">Track {{trackIndex}} of {{album.tracks.length}}
      </span>
    </ol>
    <ol class="carousel-indicators" v-else>
      <!-- Dummy while loading -->
    </ol>
    <div class="carousel-inner">
      <div class="carousel-item" 
        :class="{'active': trackMatch(track)}" 
        v-for="track in album.tracks" 
        :key="track[1]">
        <table>
          <tr>
            <td width="100%" class="td-style">
              <span v-if="genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'">
                {{ track[0].substring(track[0].lastIndexOf(' Act ') + 1).trim() }}
              </span>
              <span v-else>
                {{ track[0].substring(track[0].lastIndexOf(':') + 1) }}
              </span>
            </td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";
import { trackMixin } from "@/components/playback/TrackListing.js"
import axios from 'axios';

export default {
  mixins: [trackMixin],
  computed: {
    trackIndex() {
      const tracks = this.album.tracks;
      const selectedTrackId = this.selectedTrack[1];

      const index = tracks.findIndex(track => track[1] === selectedTrackId);
      return index !== -1 ? index + 1 : null;
    }
  },
  methods: {
    selectTrack(track){
        this.selectedTrack = track;
    }
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
      } else {
        window.firstLoad = false;
      }
    })
    eventBus.$on("fireSetAlbumHopper", (album, track_no, percent_progress) => {
      
      this.$view.percentProgress = percent_progress;
      this.genre = this.$config.genre;
      this.$config.allTracks = album.tracks[0][2];
      
      try{
        this.$config.playTracks = album.tracks[track_no][2];
      } catch (error){
        this.$config.playTracks = album.tracks[0][2];
      }
      localStorage.setItem("config", JSON.stringify(this.$config));
      this.album = album;

      let playTrack = this.$config.playTracks.split(' ')[0].replace('spotify:track:', '');

      if (this.$auth.clientToken && this.$auth.deviceID && !window.firstLoad) {
        const path = 'https://api.spotify.com/v1/tracks/' + playTrack;
        axios({
          method: 'get',
          url: path,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + this.$auth.clientToken
          }
        }).then((res) => {
          let duration = res.data.duration_ms;
          let position = Math.round(duration * this.$view.percentProgress - 3000);
          if (position < 0){
            position = 0;
          }
          this.playTracks(this.$config.playTracks, position);
        }).catch((error) => {
          console.error(error);
        });
      } else {
        window.firstLoad = false;
      }
    });
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
.td-style{
  white-space: nowrap; 
  text-overflow: ellipsis; 
  overflow: hidden; 
  max-width: 1px;
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
