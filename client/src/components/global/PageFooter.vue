<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <b-button class="info-panel-button" @click="$emit('togglePanel')">
          <span v-if="!showPanel"><b-icon-chevron-up></b-icon-chevron-up></span>
          <span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL
        </b-button>
        <PlayerControls />
      </b-col>
      <b-col class="last-col">
        <TrackListing />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import AlbumInfo from '@/components/playback/AlbumInfo.vue'
import PlayerControls from '@/components/playback/PlayerControls.vue'
import TrackListing from '@/components/playback/TrackListing.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
  },
  props: {
    showPanel: Boolean,
  }
};
</script>

<style scoped>
.container-fluid {
  bottom: 0px;
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--dark-gray);
  padding-bottom: 0px;
  border-radius: 0px;
}
.info-col {
  height: 100px;
  overflow-y: hidden;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  height: 100px;
  color: var(--my-white);
}
.col {
  padding: 0px;
}
.info-panel-button {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px !important;
  border-radius: 0px !important;
  padding-top: 1px !important;
  padding-bottom: 1px !important;
  bottom: 90px;
  z-index: 9999;
  background-color: var(--playback-color) !important;
  color: black !important;
  border: none;
  outline: none !important;
}
</style>
