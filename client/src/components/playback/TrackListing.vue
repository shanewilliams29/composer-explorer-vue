<template>
  <b-card-group deck>
    <b-card no-body class="track-card" ref="scroll-box">
      <b-card-text class="track-card-text">
        <div class="centered-tracks">
          <table class="track-table" cellspacing="0">
            <tr class="track-row" v-for="track in album.tracks" :id="track[1]" :key="track[1]" 
              @click="selectTrack(track); playTracks(track[2]); " 
              :class="{'highlight-track': trackMatch(track)}">
              <td width="100%" class="td-class">
                <b-icon icon="play-fill" aria-hidden="true"></b-icon>
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
      </b-card-text>
    </b-card>
  </b-card-group>
</template>

<script>
import { trackMixin } from "./TrackListing.js"
import smoothscroll from "smoothscroll-polyfill";
import { eventBus } from "@/main.js";
import spotify from "@/SpotifyFunctions.js"; 

export default {
  data() {
    return {
      progress: 0,
    };
  },
  mixins: [trackMixin],
  computed: {
    durationChanged() {
      return this.$view.duration;
    },
  },
  watch: {
    durationChanged() {
      this.seektoDuration(this.progress);
    },
  },
  methods: {
    seektoDuration(progress){
      let progress_rounded = Math.round(progress)
      if (progress > 0){
        spotify.seekToPosition(this.$auth.clientToken, progress_rounded)
      }
    },
    selectTrack(track) {
      this.selectedTrack = track;
      smoothscroll.polyfill(); // for Safari smooth scrolling
      var trackId = track[1];
      try {
        var element = document.getElementById(trackId);
        var top = element.offsetTop;
        this.$refs["scroll-box"].scrollTo({
          top: top,
          left: 0,
          behavior: "smooth",
        });
      // eslint-disable-next-line
      } catch(error) {
        // No track ID match, Spotify is redirecting to a different track ID
      }
    },
  },
  created() {
    eventBus.$on("fireSetAlbum", (album) => {
      this.progress = 0;
      this.genre = this.$config.genre;
      this.$config.allTracks = album.tracks[0][2];
      this.$config.playTracks = album.tracks[0][2];
      localStorage.setItem("config", JSON.stringify(this.$config));
      this.album = album;
      if (this.$auth.clientToken && this.$auth.deviceID && !window.firstLoad) {
        this.playTracks(album.tracks[0][2], 0);
      } else {
        window.firstLoad = false;
      }
    });
    eventBus.$on("fireSetAlbumHopper", (album, track_no, percent_progress) => {
      this.progress = this.$view.duration * percent_progress;
      this.genre = this.$config.genre;
      this.$config.allTracks = album.tracks[0][2];
      this.$config.playTracks = album.tracks[track_no][2];
      localStorage.setItem("config", JSON.stringify(this.$config));
      this.album = album;
      if (this.$auth.clientToken && this.$auth.deviceID && !window.firstLoad) {
        this.playTracks(album.tracks[track_no][2], this.progress);
        

      } else {
        window.firstLoad = false;
      }
    });
  }
}
</script>

<style scoped>
.td-class{
  white-space: nowrap; 
  text-overflow: ellipsis; 
  overflow: hidden; 
  max-width: 1px;
}
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

.track-card {
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
  border: 3px solid var(--scroll-bar-bg-color) !important;
}
</style>
