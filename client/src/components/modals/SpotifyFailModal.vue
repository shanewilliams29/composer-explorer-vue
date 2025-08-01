<template>
  <div>
    <b-modal id="spotify-fail-modal" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h3>Spotify Playback Error</h3>
        <br />
        <p>Spotify playback is currently experiencing errors. Please try again later.</p>
      </div>
    </b-modal>
  </div>
</template>

<script>
import {staticURL} from "@/main.js";

export default {
  data() {
    return {
      spotifyLogoURL: staticURL + '/assets/Spotify_Logo_RGB_Black.png',
    };
  },
}
</script>


<style scoped>
.mt-4{
    margin: 2px;
}
</style>