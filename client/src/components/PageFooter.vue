<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <b-button class="info-panel-button" @click="togglePanel()" variant="warning">
          <span v-if="!$parent.showPanel"><b-icon-chevron-up></b-icon-chevron-up></span><span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL
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
import AlbumInfo from './subcomponents/AlbumInfo.vue'
import PlayerControls from './subcomponents/PlayerControls.vue'
import TrackListing from './subcomponents/TrackListing.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
  },
  methods:{
    togglePanel(){
      this.$parent.togglePanel();
    }
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
  color: var(--white);
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
}
</style>
