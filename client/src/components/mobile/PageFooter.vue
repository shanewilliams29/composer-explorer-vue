<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <PlayerControls />
      </b-col>
      <b-col v-if="false">
        <TrackListing />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import PlayerControls from '@/components/mobile/PlayerControls.vue'
import TrackListing from '@/components/subcomponents/TrackListing.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing
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
  height: 100px;
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
