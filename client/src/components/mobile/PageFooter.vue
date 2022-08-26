<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <PlayerControls />
        <SpotifyModal />
        <AutoplayModal />
        <NotPremiumModal />
      </b-col>
      <b-col v-if="false">
        <TrackListing />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import PlayerControls from '@/components/subcomponents/PlayerControls.vue'
import TrackListing from '@/components/subcomponents/TrackListing.vue'
import SpotifyModal from '@/components/subcomponents/SpotifyModal.vue'
import AutoplayModal from '@/components/subcomponents/AutoplayModal.vue'
import NotPremiumModal from '@/components/subcomponents/NotPremiumModal.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
    SpotifyModal,
    AutoplayModal,
    NotPremiumModal
  },
};
</script>

<style scoped>
.container-fluid {
  position: relative;
  background-color: #343a40;
  padding-bottom: 0px;
  border-radius: 0px;
  border-radius: 0px;
}
.info-col {
  height: 83px;
  overflow-y: hidden;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  height: 83px;
  color: white;
}
.col {
  padding: 0px;
}
</style>
