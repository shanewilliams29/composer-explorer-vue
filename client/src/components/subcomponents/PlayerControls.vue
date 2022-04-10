<template>
 <b-row class="playback-row">
  <b-col class="text-center">

  <b-button class="playback-button" id="back-button"><b-icon-skip-start-fill></b-icon-skip-start-fill></b-button>
  <b-button class="playback-button" id="play-button" v-show="!playing" @click="play()"><b-icon-play-fill></b-icon-play-fill></b-button>
  <b-button class="playback-button" id="pause-button" v-show="playing" @click="pause()"><b-icon-pause-fill></b-icon-pause-fill></b-button>
  <b-button class="playback-button" id="forward-button"><b-icon-skip-end-fill></b-icon-skip-end-fill></b-button>

</b-col>
</b-row>
</template>

<script>
import spotify from '@/SpotifyFunctions.js'
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      token: "",
      player: "",
      playing: false
    };
  },
  methods: {
    play() {
      spotify.playTrack(window.token, window.device_id);
    },
    pause() {
      spotify.pauseTrack(window.token);
    },
  },
  created() {
    eventBus.$on('fireNowPlaying', () => {
          this.playing = true;
    })
    eventBus.$on('fireNowPaused', () => {
          this.playing = false;
    })
  },
};
</script>

<style>
.playback-row{
  padding: 30px;
}
.btn-secondary{
  background-color: #343a40 !important;
}
.btn:hover{
  background-color: #484e53 !important;
}
.btn{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
.btn:focus,.btn:active:focus,.btn.active:focus,
.btn.focus,.btn:active.focus,.btn.active.focus {
  border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background-color: none !important;
}
</style>
