<template>
  <div>
    <b-modal id="spotify-modal" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h3>Connect with your Spotify Premium account to play music.</h3>
        <b-button variant="success" class="mt-4" :href="spotifyURL">Log in</b-button>
        <b-button class="mt-4" target="_blank" href="https://www.spotify.com/get-spotify/overview/">Get Spotify</b-button>
      </div>
    </b-modal>
  </div>
</template>

<script>
import {baseURL, staticURL} from "@/main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      spotifyURL: baseURL + "connect_spotify",
      spotifyLogoURL: staticURL + '/assets/Spotify_Logo_RGB_Black.png',
    };
  },
  methods: {
    hideBanner(){
      this.$view.banner = false;
    }
  },
}
</script>


<style scoped>
.mt-4{
  margin: 2px;
}
</style>
