<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <PlayerControls />
        <SpotifyModal />
        <AutoplayModal />
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
import SpotifyModal from './subcomponents/SpotifyModal.vue'
import AutoplayModal from './subcomponents/AutoplayModal.vue'

import {eventBus} from "../main.js";

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
    SpotifyModal,
    AutoplayModal
  },
  methods:{
    notLoggedIn(){
      this.$bvModal.show('spotify-modal');
    },
    autoplayDisabled(){
      this.$bvModal.show('autoplay-modal');
    },
  },
  mounted() {
    eventBus.$on('notLoggedIn', this.notLoggedIn);
    eventBus.$on('fireAutoplayFailed', this.autoplayDisabled);
  },
};
</script>

<style scoped>
.float{
  position:fixed;
}

.container-fluid {
  position: fixed;
  bottom: 0px;
  background-color: #343a40;
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
  color: white;
}
.col {
  padding: 0px;
}
</style>
