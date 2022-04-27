<template>
<div>
  <b-modal id="autoplay-modal" hide-footer>
    <template #modal-title>
      <img src="@/assets/Spotify_Logo_RGB_Black.png" alt="Spotify" height="32px"/>
    </template>
    <div class="m-2 text-center">
      <h3>Your browser is blocking audio playback.</h3>
      <b-button variant="success" class="mt-4" @click="enableAutoplay()">Click to enable</b-button>
    </div>
  </b-modal>
</div>
</template>

<script>
export default {
  data() {
    return {
    };
  },
  methods: {
    enableAutoplay() {
        window.player.activateElement();
        console.log("ACTIVATED");
        this.$bvModal.hide('autoplay-modal')
      },
  },
};
</script>




<style scoped>
  .mt-4{
    margin: 2px;
  }


</style>
