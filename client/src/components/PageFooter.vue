<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <PlayerControls />
        <SpotifyModal />
      </b-col>
      <b-col>
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

import {eventBus} from "../main.js";

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
    SpotifyModal
  },
  methods:{
    notLoggedIn(){
      this.$bvModal.show('spotify-modal');
    }
  },
  mounted() {
    eventBus.$on('notLoggedIn', this.notLoggedIn);
  },
};
</script>

<style scoped>
.float{
  position:fixed;
}

.container-fluid {
  position: relative;
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
