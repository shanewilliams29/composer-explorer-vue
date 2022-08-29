<template>
  <div v-if="$view.panelVisible && $view.mobile" class="container-fluid">
    <div class="footer-row">
      <b-row class="info-row">
        <ComposerInfo />
      </b-row>
      <b-row class="info-row">
        <WorkInfo />
      </b-row>
      <b-row class="info-row">
        <AlbumInfoPanel />
      </b-row>
      <b-row class="track-listing-mobile">
        <TrackListing />
      </b-row>
    </div>
  </div>
</template>

<script>
import ComposerInfo from '@/components/subcomponents/ComposerInfo.vue';
import WorkInfo from '@/components/subcomponents/WorkInfo.vue';
import AlbumInfoPanel from '@/components/subcomponents/AlbumInfoPanel.vue';
import TrackListing from '@/components/subcomponents/TrackListing.vue'

export default {
  components: {
    ComposerInfo,
    WorkInfo,
    AlbumInfoPanel,
    TrackListing
  }
};
</script>

<style scoped>
.container-fluid {
  background-color: #f1f2f4;
  padding-bottom: 0px;
  border-radius: 0px;
}
.footer-row {
  height: calc(100vh - 190px);
  color: black;
}
.col {
  padding: 5px;
  padding-right: 0px;
}
.last-col{
  padding-right: 5px;
}
.info-row{
 padding-left: 0px;
 padding-right: 0px;
 padding-top: 10px;
 padding-bottom: 0px;
 margin: 0px !important;
 height: auto !important;
}
.track-listing-mobile{
  width: 100%;
}
>>> .composer-info-card{
  padding: 15px;
  padding-bottom: 5px;
  background-color: white !important;
  border: none !important;
  width: 100%;
}
>>> .album-info-card{
  padding: 15px;
  padding-bottom: 5px;
  background-color: white !important;
  border: none !important;
  width: 100%;
}
>>> .info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: calc(100vh - 532px);
  padding-left: 2px;
}
>>> .card-deck{

}
>>> .track-card {
  width: 100vw;
  margin: 0px !important;
  padding-left: 6px;
  right: 3px;
  height: 94.58px;
  position: absolute;
  bottom: 0px;
  left: 0px;

}
</style>