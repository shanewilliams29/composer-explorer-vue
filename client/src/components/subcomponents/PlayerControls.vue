<template>
  <div><button id="togglePlay" @click="play()">Toggle Play</button></div>
</template>

<script>
import spotify from '@/SpotifyFunctions.js'

export default {
  data() {
    return {
      token: "",
      player: ""
    };
  },
  methods: {
    play() {
      console.log(spotify.playTrack(window.token, window.device_id));
    },
  },
};
</script>
