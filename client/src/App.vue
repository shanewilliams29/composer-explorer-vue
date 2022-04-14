<template>
  <div id="app">
    <router-view/>
    <SpotifyPlayer/>
  </div>
</template>

<script>
import SpotifyPlayer from '@/components/SpotifyPlayer.vue'
export default {
  components: {
    SpotifyPlayer
  },
}
</script>


<style>
  html, body {
    height: 100% !important;
    max-height: -webkit-fill-available !important;
  }
  #app{
    height: 100% !important;
    max-height: -webkit-fill-available !important;
  }
</style>
