<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
          <b-button class="info-panel-button" @click="togglePanel()" variant="warning">
          <span v-if="!$parent.showPanel"><b-icon-chevron-up></b-icon-chevron-up></span><span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL
        </b-button>
        <PlayerControls />
        <SpotifyModal />
        <AutoplayModal />
        <NotPremiumModal />
        <NotAvailableModal />
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
import NotAvailableModal from '@/components/subcomponents/NotAvailableModal.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing,
    SpotifyModal,
    AutoplayModal,
    NotPremiumModal,
    NotAvailableModal
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
