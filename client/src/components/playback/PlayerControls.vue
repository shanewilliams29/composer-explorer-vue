<template>
  <b-container class="playback-container">
    <b-row class="buttons-row">
      <PlayerButtons v-if="!$view.mobile"/>
      <MobilePlayerButtons v-else/>
    </b-row>
    <b-row class="seekbar-row">
      <b-col class="text-center">
        <table class="seekbar-table" width="100%">
          <tr>
            <td class="footertable" width="10%">
              <div class="time" id="time-progress">{{ display_progress }}</div>
            </td>
            <td class="footertable" width="80%">
              <div class="slidecontainer">
                <b-form-input
                  class="slider"
                  id="progressbar"
                  step="1000"
                  v-model="$view.progress"
                  @input="setPlayback($view.progress, $view.duration); suspendTimer();"
                  @change="seek($view.progress)"
                  type="range"
                  min="0"
                  :max="Math.floor($view.duration/1000) * 1000"
                ></b-form-input>
              </div>
            </td>
            <td class="footertable" width="10%">
              <div class="time" id="time-duration">{{ display_duration }}</div>
            </td>
          </tr>
        </table>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import PlayerButtons from './PlayerButtons.vue'
import MobilePlayerButtons from '@/components/mobile/MobilePlayerButtons.vue'
import spotify from "@/SpotifyFunctions.js";
import {eventBus} from "@/main.js";
import axios from "axios";
import { prepareTracksForSpotify } from "@/HelperFunctions.js";


const debouncedNext = debounce(() => fireNextWork());
const debouncedHopForward = immediateDebounce((progress, duration) => hopForward(progress, duration));
const debouncedHopBackward = immediateDebounce((progress, duration) => hopBackward(progress, duration));


let allowNext = false;

// Debounces the given function
function debounce(func, timeout = 2000) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      func.apply(this, args);
    }, timeout);
  };
}

// Debounces the given function, but fires immediately on call
function immediateDebounce(func, timeout = 1000) {
  let timer;
  let immediateExecution = true;

  return (...args) => {
    const executeFunction = () => {
      func.apply(this, args);
      timer = null;
    };

    if (immediateExecution) {
      immediateExecution = false;
      executeFunction();
    }

    clearTimeout(timer);
    timer = setTimeout(() => {
      immediateExecution = true;
    }, timeout);
  };
}

// Advances playback to the next work in the playlist
function fireNextWork() {
  if (allowNext) {
    allowNext = false;
    eventBus.$emit("fireNextWork");
  }
}

function hopForward(progress, duration) {
  eventBus.$emit("fireTimeHopperForward", progress, duration);
}
function hopBackward(progress, duration) {
  eventBus.$emit("fireTimeHopperBackward", progress, duration);
}

export default {
  components: {
    PlayerButtons,
    MobilePlayerButtons
  },
  data() {
    return {
      token: "",
      player: "",
      playing: false,
      display_duration: "00:00",
      display_progress: "00:00",
      suspend: true,
      delay: 1000,
      start: true,
      end: false,
      track_id: ""
    };
  },
  methods: {
    // play, pause, back, and next not used here. Button function is handled in the SpotifyPlayer.vue listeners
    // this works more reliably using the Spotify Playback SDK not the API endpoints.
    play() {
      spotify.pressPlay(this.$auth.clientToken, this.$auth.deviceID);
    },
    pause() {
      spotify.pauseTrack(this.$auth.clientToken);
    },
    timeHopperForward() {
      debouncedHopForward(this.$view.progress, this.$view.duration);
    },
    timeHopperBackward() {
      debouncedHopBackward(this.$view.progress, this.$view.duration);
    },
    back() {
      if (this.$view.progress > 2000) {
        spotify.beginningTrack(this.$auth.clientToken, this.$auth.deviceID);
        this.setPlayback(0, this.$view.duration);
      } else {
        let jsonTracks = prepareTracksForSpotify(this.$config.previousTracks)
        spotify.playTracks(this.$auth.clientToken, this.$auth.deviceID, jsonTracks);
      }
    },
    next() {
      spotify.nextTrack(this.$auth.clientToken);
    },
    suspendTimer() {
      this.suspend = true;
    },
    seek(progress) {
      spotify.seekToPosition(this.$auth.clientToken, progress);
    },
    setPlayback(progress, duration) {
      this.$view.progress = progress;
      this.$view.duration = duration;
      this.display_progress = this.msToHMS(progress);
      this.display_duration = this.msToHMS(duration);
    },
    msToHMS(duration) {
      if (duration < 0) {
        duration = 0;
      }
      var seconds = parseInt((duration / 1000) % 60),
        minutes = parseInt((duration / (1000 * 60)) % 60);
      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;
      return minutes + ":" + seconds;
    },
    playbackTimer() {
      if (!this.suspend) {
        this.$view.progress = parseInt(this.$view.progress) + 1000;
        this.setPlayback(this.$view.progress, this.$view.duration);

        if (this.$view.progress >= this.$view.duration) {
          this.setPlayback(this.$view.duration, this.$view.duration);
          this.suspend = true;
        }
        if (this.$view.progress < 0) {
          this.setPlayback(0, this.$view.duration);
        }
      }
    },
    startTimer() {
      this.suspend = false;
    },
    delayStartTimer() {
      this.suspend = true;
      setTimeout(this.startTimer, this.delay);
    },
    nextWork() {
      debouncedNext();
    },
    nextWorkNoDebounce() {
      allowNext = true;
      fireNextWork();
    },
    previousWork() {
      eventBus.$emit("firePreviousWork");
    },
    shufflePlayback() {
      this.$view.shuffle = !this.$view.shuffle;
    },
    playRandom() {
      this.$view.shuffle = true;
      this.nextWorkNoDebounce();
    },
    likeDatabase(albumID, action) {
      const path = `api/like/${albumID}/${action}`;
      axios
        .get(path)
        // eslint-disable-next-line
        .then((res) => {
          eventBus.$emit("fireRefreshWorks");
        })
        .catch((error) => {
          console.error(error);
        });
    },
    toggleLike() {
      if (this.$auth.clientToken) {
        this.$view.like = !this.$view.like;
        if (this.$view.like) {
          this.likeDatabase(this.$config.album, "like");
          eventBus.$emit("fireLikeAlbum");
        } else {
          this.likeDatabase(this.$config.album, "unlike");
          eventBus.$emit("fireUnlikeAlbum");
        }
      }
    },
  },
  created() {
    eventBus.$on("fireSeekToPosition", () => {
      if (this.playing === true) {
        this.delayStartTimer();
      } else {
        this.suspend = true;
      }
    });

    // Receives data from Spotify API with current playback data upon a player state change
    eventBus.$on("firePlayerStateChanged", (track_data, position, duration, paused) => {
        // debouncedSetDuration(duration, this);
      
        if (track_data.id == this.track_id){
          // console.log("SAME TRACK", track_data.id)
          this.end = true;
          this.start = false;
        } else {
          //console.log("NEW TRACK", track_data.id)
          this.end = false;
          this.start = true;
        }

      if (position == 0 && !paused && this.start) {
        // can delay timer here if glitchy
        //console.log (">> TRACK START <<", track_data.id)
        this.playing = true;
        this.startTimer();
        this.setPlayback(0, duration);
        this.start = false;
        this.end = true;
        this.track_id = track_data.id;

      } else if (position == 0 && paused && this.end) {
        // Advance to next work when play stops after current work complete
        // Spotify API spams function with requests when changing track, therefore function is debounced
        //console.log ("<< TRACK END >>", track_data.id)

        this.end = false;
        this.start = true;
        this.track_id = track_data.id;
        this.nextWork();
        

      } else if (paused){

        this.playing = !paused;
        this.suspend = true;

      // } else if (position > 0 && position < 3000 && !paused) {
      //   // used to need this, Spotify changed behavior to not need it though?
      //   allowNext = true;
      //   this.playing = true;
      //   this.startTimer();

      } else {
        this.playing = !paused;

        if (position > 0) {
          // prevent firefox crash
          allowNext = true;
        }

        if (this.playing == true) {
          this.startTimer();

        } else {
          this.suspend = true;
        }

        //debouncedSetProgress(this, position, duration);
        this.setPlayback(position, duration);
      }
      // update previousTracks
      let selectedTrack = track_data.uri;
      let allTracks = this.$config.allTracks.split(" ");

      let index = allTracks.indexOf(selectedTrack);
      let previousTracks = "";

      if (index == 0) {
        previousTracks = this.$config.allTracks;
      } else if (index < 0) {
        // occurs when spotify redirects, track not found in list
        previousTracks = this.$config.allTracks;
      } else {
        for (var i = index - 1; i < allTracks.length; i++) {
          previousTracks = previousTracks + " " + allTracks[i];
        }
      }
      this.$config.previousTracks = previousTracks.trim();
    });
  },
  mounted() {
    // Drives the playback progress bar
    setInterval(this.playbackTimer, 1000);
  },
};

</script>

<style scoped>
.playback-container {
  padding-top: var(--playerpadding) !important;
  padding: 13px;
  padding-bottom: 0px;
  font-size: 14px;
}
td {
  vertical-align: top;
}
.time {
  margin-top: 0.5px;
}

.slidecontainer {
  width: 100%;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 1px;
  padding-bottom: 0px;
}

input[type="range"] {
  -webkit-appearance: none !important;
  appearance: none !important;
  background: transparent !important;
  cursor: pointer !important;
  width: 100% !important;
  opacity: 0.85;
}

input[type="range"]::-webkit-slider-runnable-track {
  background: #787f87;
  height: 6px;
}
input[type="range"]::-moz-range-track {
  background: #787f87;
  height: 6px;
  border-radius: 0px;
}

input[type="range"]:hover {
  opacity: 1;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; /* Override default look */
  appearance: none;
  margin-top: -3px; /* Centers thumb on the track */
  background-color: var(--my-white);
  height: 0px;
  width: 0px;
}
input[type="range"]::-moz-range-thumb {
  border: none; /*Removes extra border that FF applies*/
  background-color: var(--my-white);
  height: 0px;
  width: 0px;
}

input[type="range"]:focus {
  outline: none;
}

/*Chrome*/
@media screen and (-webkit-min-device-pixel-ratio: 0) {
  input[type="range"]::-webkit-slider-runnable-track {
    overflow: hidden;
    height: 6px;
    color: var(--playback-color);
    margin-top: -3px;
  }

  input[type="range"]::-webkit-slider-thumb {
    box-shadow: -350px 0 0 350px var(--playback-color);
  }
}
/** FF*/
input[type="range"]::-moz-range-progress {
  background-color: var(--playback-color);
  height: 6px;
}
</style>
