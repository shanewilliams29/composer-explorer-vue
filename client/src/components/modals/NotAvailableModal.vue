<template>
  <div>
    <b-modal id="not-available-modal" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h3>Recording Not Available</h3>
        <br />
        <p>We're sorry but Spotify has not made this recording available in your country. Let's try the next one!</p>
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
