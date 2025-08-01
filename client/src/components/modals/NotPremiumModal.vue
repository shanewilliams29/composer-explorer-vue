<template>
  <div>
    <b-modal id="not-premium-modal" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h3>A Spotify Premium account is required to play music.</h3>
        <br />
        <p>Playback, radio, and playlist functionality will not work without Spotify Premium.</p>
        <b-button variant="success" class="mt-4" target="_blank" href="https://www.spotify.com/get-spotify/overview/">Upgrade to Premium</b-button>
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
