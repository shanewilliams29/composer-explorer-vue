<template>
  <div>
    <b-modal id="autoplay-modal" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h3>Your browser is blocking audio playback.</h3>
        <p>This is a problem affecting some browsers due to audio Autoplay restrictions. This website works best with Chrome or Firefox.</p>
        <p>
          If using Safari, enable Autoplay in site settings: <br />
          <span style="font-size: 12px;">Safari > Settings for composerexplorer.com... > Auto-Play > Allow All Auto-Play</span>
        </p>
        <b-button class="mt-4" @click="refreshPage()">Click to try again</b-button>
      </div>
    </b-modal>
  </div>
</template>

<script>
import { staticURL } from "@/main.js";
export default {
  data() {
    return {
      spotifyLogoURL: staticURL + "/assets/Spotify_Logo_RGB_Black.png",
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
