<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
          <b-button class="info-panel-button" @click="togglePanel()">
          <span><b-icon-info-circle></b-icon-info-circle></span>
        </b-button>
        <PlayerControls />
        <SpotifyModal />
        <AutoplayModal />
        <NotPremiumModal />
        <NotAvailableModal />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import PlayerControls from '@/components/subcomponents/PlayerControls.vue'
import SpotifyModal from '@/components/subcomponents/SpotifyModal.vue'
import AutoplayModal from '@/components/subcomponents/AutoplayModal.vue'
import NotPremiumModal from '@/components/subcomponents/NotPremiumModal.vue'
import NotAvailableModal from '@/components/subcomponents/NotAvailableModal.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
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
.info-panel-button {
  position: absolute;
  right: 10px;
  font-size: 20px !important;
  border-radius: 50% !important;
  padding-left: 2.8px !important;
  padding-right: 2.8px !important;
  padding-top: 1.2px;
  padding-bottom: 0px;
  bottom: 90px;
  z-index: 9999;
  background-color: #343a40 !important;
  border: none !important;
  color: var(--warning);
}
.info-panel-button:hover {
  color: var(--warning);
}
.info-panel-button:focus {
  color: var(--warning);
}
</style>
