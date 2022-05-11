<template>
<div>
  <b-modal id="autoplay-modal" hide-footer>
    <template #modal-title>
      <img :src="spotifyLogoURL" alt="Spotify" height="32px"/>
    </template>
    <div class="m-2 text-center">
      <h3>Your browser is blocking audio playback.</h3>
      <p>This is a problem affecting some browsers due to audio Autoplay restrictions. This website works best with Chrome or Firefox.</p>
      <p>You may be able to correct this error by refreshing the page.</p>
      <b-button class="mt-4" @click="refreshPage()">Click to refresh</b-button>
    </div>
  </b-modal>
</div>
</template>

<script>
import {staticURL} from "@/main.js";
export default {
  data() {
    return {
      spotifyLogoURL: staticURL + 'Spotify_Logo_RGB_Black.png',
    };
  },
  methods: {
    refreshPage() {
        location.reload();
      },
  },
};
</script>




<style scoped>
  .mt-4{
    margin: 2px;
  }


</style>
